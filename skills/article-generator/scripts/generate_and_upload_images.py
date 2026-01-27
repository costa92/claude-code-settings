#!/usr/bin/env python3
"""
文章配图生成和上传工具
支持使用 Gemini API 生成图片，并通过 PicGo 上传到图床
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import hashlib
from datetime import datetime

# 尝试导入 requests（用于 GitHub Token 验证）
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from tqdm import tqdm
except ImportError:
    # 如果 tqdm 未安装，提供一个简单的替代
    class tqdm:
        def __init__(self, iterable=None, desc=None, total=None):
            self.iterable = iterable
            self.desc = desc
            self.total = total or (len(iterable) if iterable else 0)

        def __iter__(self):
            return iter(self.iterable)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

# 配置
# Use nanobanana.py from the same directory as this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NANOBANANA_PATH = os.path.join(SCRIPT_DIR, "nanobanana.py")
IMAGES_DIR = "./images"
PICGO_CMD = "picgo"

# Gemini API 定价（基于 2024 年定价）
# 参考: https://ai.google.dev/pricing
GEMINI_PRICING = {
    "gemini-3-pro-image-preview": {
        "1K": 0.10,  # $0.10 per image
        "2K": 0.20,  # $0.20 per image
        "4K": 0.40,  # $0.40 per image
    },
    "gemini-2.5-flash-image": {
        "1K": 0.04,  # $0.04 per image (cheaper, faster)
        "2K": 0.08,
        "4K": 0.16,
    },
}

# 平均生成时间估算（秒）
AVG_GENERATION_TIME = {
    "1K": 15,
    "2K": 25,
    "4K": 45,
}
AVG_UPLOAD_TIME = 5  # 平均上传时间（秒）


class ThreadStatusTracker:
    """线程状态跟踪器 - 监控并发任务执行状态"""

    def __init__(self, max_workers: int):
        self.max_workers = max_workers
        self.thread_status = {}  # 线程ID -> 状态信息
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.total_tasks = 0
        self.completed_tasks = 0

    def start_task(self, thread_id: int, task_name: str):
        """记录线程开始处理任务"""
        with self.lock:
            self.thread_status[thread_id] = {
                "task": task_name,
                "start_time": time.time(),
                "status": "working"
            }

    def complete_task(self, thread_id: int, success: bool = True):
        """记录线程完成任务"""
        with self.lock:
            if thread_id in self.thread_status:
                self.thread_status[thread_id]["status"] = "idle"
                self.thread_status[thread_id]["task"] = None
                self.completed_tasks += 1

    def get_status_summary(self) -> str:
        """获取状态摘要"""
        with self.lock:
            working = sum(1 for s in self.thread_status.values() if s["status"] == "working")

            elapsed = time.time() - self.start_time
            # 并发效率 = 完成任务数 / (时间 * 线程数) * 100
            if elapsed > 0.1 and self.completed_tasks > 0:
                max_possible = (elapsed / 30) * self.max_workers  # 假设平均30秒/任务
                efficiency = min(100, (self.completed_tasks / max_possible * 100))
            else:
                efficiency = 0

            summary = f"🧵 线程: {working}/{self.max_workers} 工作中"
            if efficiency > 0:
                summary += f" | 效率: {efficiency:.1f}%"

            return summary

    def get_thread_details(self) -> List[str]:
        """获取线程详细状态"""
        with self.lock:
            details = []
            for thread_id, status in self.thread_status.items():
                if status["status"] == "working" and status["task"]:
                    elapsed = time.time() - status["start_time"]
                    details.append(f"  - 线程{thread_id}: {status['task'][:30]} ({elapsed:.1f}s)")
            return details


class CheckpointManager:
    """检查点管理器 - 实现断点续传功能（简化版）"""

    def __init__(self, config_path: str, checkpoint_dir: str = ".checkpoints"):
        self.config_path = config_path
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)

        # 生成检查点文件名（基于配置文件路径的哈希）
        config_hash = hashlib.md5(config_path.encode()).hexdigest()[:8]
        self.checkpoint_file = self.checkpoint_dir / f"checkpoint_{config_hash}.json"

    def save_checkpoint(self, completed: List[str], failed: List[str],
                       uploaded: List[str], total: int):
        """保存检查点"""
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "config": self.config_path,
            "total": total,
            "completed": completed,  # 已成功生成的图片文件名
            "failed": failed,        # 生成失败的图片文件名
            "uploaded": uploaded     # 已上传的图片文件名
        }

        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)

    def load_checkpoint(self) -> Optional[Dict]:
        """加载检查点"""
        if not self.checkpoint_file.exists():
            return None

        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)

            # 验证检查点配置是否匹配
            if checkpoint.get("config") != self.config_path:
                return None

            return checkpoint
        except Exception as e:
            print(f"⚠️  加载检查点失败: {e}")
            return None

    def clear_checkpoint(self):
        """清除检查点文件"""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()

    def get_resume_info(self) -> Dict:
        """获取恢复信息"""
        checkpoint = self.load_checkpoint()

        if not checkpoint:
            return {
                "has_checkpoint": False,
                "completed": [],
                "failed": [],
                "uploaded": [],
                "remaining": 0
            }

        completed = set(checkpoint.get("completed", []))
        failed = set(checkpoint.get("failed", []))
        uploaded = set(checkpoint.get("uploaded", []))
        total = checkpoint.get("total", 0)

        return {
            "has_checkpoint": True,
            "timestamp": checkpoint.get("timestamp"),
            "completed": list(completed),
            "failed": list(failed),
            "uploaded": list(uploaded),
            "remaining": total - len(completed)
        }


# Import shared configuration
try:
    from config import ASPECT_RATIO_TO_SIZE, TIMEOUTS
except ImportError:
    # Fallback if config.py not found
    ASPECT_RATIO_TO_SIZE = {
        "1:1": "1024x1024",
        "2:3": "832x1248",
        "3:2": "1248x832",
        "3:4": "864x1184",
        "4:3": "1184x864",
        "4:5": "896x1152",
        "5:4": "1152x896",
        "9:16": "768x1344",
        "16:9": "1344x768",
        "21:9": "1536x672",
    }
    TIMEOUTS = {"image_generation": 120, "upload": 60}


class ImageConfig:
    """图片配置"""
    def __init__(self, name: str, prompt: str, aspect_ratio: str = "3:2", filename: str = None):
        self.name = name
        self.prompt = prompt
        self.aspect_ratio = aspect_ratio
        self.filename = filename or f"{name}.jpg"
        self.local_path = None
        self.cdn_url = None


def ensure_images_dir():
    """确保图片目录存在"""
    images_dir = Path(IMAGES_DIR)
    images_dir.mkdir(exist_ok=True)
    return images_dir


def validate_github_token(config_path: str = "~/.picgo/config.json") -> Dict[str, any]:
    """
    验证GitHub Token权限（通过API测试）

    Args:
        config_path: PicGo配置文件路径

    Returns:
        dict: 验证结果
            - valid: bool - Token是否有效
            - error: str - 错误信息（如果有）
            - repo: str - 仓库名称
            - http_code: int - HTTP状态码
    """
    result = {
        "valid": False,
        "error": None,
        "repo": None,
        "http_code": None
    }

    # 检查 requests 库是否可用
    if not REQUESTS_AVAILABLE:
        result["error"] = "requests 库未安装，跳过 GitHub Token 验证"
        result["valid"] = None  # None 表示无法验证
        return result

    try:
        # 读取 PicGo 配置文件
        config_file = Path(config_path).expanduser()

        if not config_file.exists():
            result["error"] = f"PicGo 配置文件不存在: {config_file}"
            return result

        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 检查当前上传器是否为 GitHub
        current_uploader = config.get("picBed", {}).get("current")

        if current_uploader != "github":
            # 非 GitHub 图床，跳过验证
            result["valid"] = None
            result["error"] = f"当前图床为 {current_uploader}，跳过 GitHub 验证"
            return result

        # 获取 GitHub 配置
        github_config = config.get("picBed", {}).get("github", {})
        repo = github_config.get("repo")
        token = github_config.get("token")

        if not repo:
            result["error"] = "GitHub 仓库未配置 (picBed.github.repo)"
            return result

        if not token:
            result["error"] = "GitHub Token 未配置 (picBed.github.token)"
            return result

        result["repo"] = repo

        # 测试 GitHub API 权限
        try:
            response = requests.get(
                f"https://api.github.com/repos/{repo}",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=10
            )

            result["http_code"] = response.status_code

            if response.status_code == 200:
                result["valid"] = True
                return result
            elif response.status_code == 401:
                result["error"] = "GitHub Token 无效或已过期 (401 Unauthorized)"
                return result
            elif response.status_code == 403:
                # 403 可能是权限不足或 API 限流
                error_data = response.json() if response.text else {}
                error_message = error_data.get("message", "")

                if "API rate limit exceeded" in error_message:
                    result["error"] = "GitHub API 限流，请稍后重试"
                else:
                    result["error"] = (
                        f"GitHub Token 权限不足 (403 Forbidden)\n"
                        f"      常见原因: Token 缺少 'repo' 权限\n"
                        f"      解决方法: https://github.com/settings/tokens 重新生成 Token\n"
                        f"      必须选中: ✓ repo (Full control of private repositories)"
                    )
                return result
            elif response.status_code == 404:
                result["error"] = f"GitHub 仓库不存在或 Token 无访问权限: {repo} (404 Not Found)"
                return result
            else:
                result["error"] = f"GitHub API 返回异常状态码: {response.status_code}"
                return result

        except requests.exceptions.Timeout:
            result["error"] = "GitHub API 请求超时（网络问题）"
            return result
        except requests.exceptions.ConnectionError:
            result["error"] = "无法连接到 GitHub API（网络问题）"
            return result
        except Exception as e:
            result["error"] = f"GitHub API 请求失败: {str(e)}"
            return result

    except json.JSONDecodeError as e:
        result["error"] = f"PicGo 配置文件格式错误: {str(e)}"
        return result
    except Exception as e:
        result["error"] = f"验证过程出错: {str(e)}"
        return result


def check_dependencies():
    """检查依赖工具"""
    errors = []

    # 检查 nanobanana
    if not os.path.exists(NANOBANANA_PATH):
        errors.append(f"❌ nanobanana 脚本未找到: {NANOBANANA_PATH}")

    # 检查 GEMINI_API_KEY（先检查环境变量，再检查 .env 文件）
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Check in ~/.nanobanana.env file
        env_file = os.path.expanduser("~/.nanobanana.env")
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY="):
                            api_key = line.split("=", 1)[1].strip()
                            if api_key:  # Non-empty value
                                break
            except Exception:
                pass  # If file read fails, treat as not found

        if not api_key:
            errors.append(
                "❌ GEMINI_API_KEY 未设置\n"
                "   请创建 ~/.nanobanana.env 文件并添加: GEMINI_API_KEY=your_key_here\n"
                "   或设置环境变量: export GEMINI_API_KEY=your_key_here"
            )

    # 检查 picgo
    picgo_installed = False
    try:
        subprocess.run([PICGO_CMD, "--version"],
                      capture_output=True,
                      check=True,
                      timeout=5)
        picgo_installed = True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        errors.append(
            "❌ PicGo CLI 未安装\n"
            "   请运行: npm install -g picgo"
        )

    # 如果PicGo已安装，检查配置
    if picgo_installed:
        try:
            # 直接读取配置文件检查上传器配置
            config_file = Path("~/.picgo/config.json").expanduser()

            if not config_file.exists():
                errors.append(
                    "⚠️  PicGo 配置文件不存在\n"
                    "   请运行以下命令配置:\n"
                    "   1. picgo set uploader (选择图床: github/smms/qiniu等)\n"
                    "   2. 根据提示配置Token和仓库信息\n"
                    "   \n"
                    "   GitHub图床配置要点:\n"
                    "   - Token权限: 必须包含 'repo' 权限\n"
                    "   - 仓库格式: username/repo-name\n"
                    "   - 分支: 通常为 main 或 master\n"
                    "   \n"
                    "   配置文档: https://picgo.github.io/PicGo-Core-Doc/zh/guide/config.html"
                )
            else:
                # 读取配置文件
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                current_uploader = config.get("picBed", {}).get("current")

                if not current_uploader:
                    errors.append(
                        "⚠️  PicGo 未配置上传器\n"
                        "   请运行: picgo set uploader\n"
                        "   配置文档: https://picgo.github.io/PicGo-Core-Doc/zh/guide/config.html"
                    )
                else:
                    # PicGo已配置上传器，进一步验证GitHub Token（如果是GitHub图床）
                    print(f"✅ PicGo 当前上传器: {current_uploader}")

                    token_validation = validate_github_token()

                    if token_validation["valid"] is False:
                        # Token验证失败
                        error_msg = f"❌ GitHub Token 验证失败\n"
                        if token_validation.get("repo"):
                            error_msg += f"   仓库: {token_validation['repo']}\n"
                        if token_validation.get("http_code"):
                            error_msg += f"   HTTP状态码: {token_validation['http_code']}\n"
                        error_msg += f"   错误: {token_validation['error']}"
                        errors.append(error_msg)
                    elif token_validation["valid"] is True:
                        # Token验证成功，打印确认信息（但不加入errors）
                        print(f"✅ GitHub Token 验证成功: {token_validation['repo']}")
                    elif token_validation["valid"] is None:
                        # 无法验证或非GitHub图床，显示警告信息
                        if token_validation["error"] and "requests 库未安装" in token_validation["error"]:
                            # 缺少 requests 库，给出警告
                            print(f"⚠️  {token_validation['error']}")
                        elif token_validation["error"]:
                            print(f"ℹ️  {token_validation['error']}")

        except json.JSONDecodeError:
            errors.append(
                "⚠️  PicGo 配置文件格式错误\n"
                "   请检查 ~/.picgo/config.json 是否为有效的JSON格式"
            )
        except Exception as e:
            # 配置检查失败，给出警告但不阻止运行
            print(f"⚠️  无法验证PicGo配置: {str(e)}")

    return errors


def generate_image(config: ImageConfig, resolution: str = "2K") -> bool:
    """
    使用 Gemini API 生成图片

    Args:
        config: 图片配置
        resolution: 分辨率 (1K, 2K, 4K)

    Returns:
        bool: 是否成功
    """
    images_dir = ensure_images_dir()
    output_path = images_dir / config.filename

    # Use shared aspect ratio mapping
    size = ASPECT_RATIO_TO_SIZE.get(config.aspect_ratio, "1248x832")

    print(f"\n🎨 生成图片: {config.name}")
    print(f"   提示词: {config.prompt[:60]}...")
    print(f"   宽高比: {config.aspect_ratio} ({size})")
    print(f"   分辨率: {resolution}")

    try:
        cmd = [
            "python3",
            NANOBANANA_PATH,
            "--prompt", config.prompt,
            "--size", size,
            "--resolution", resolution,
            "--output", str(output_path)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUTS.get("image_generation", 120)
        )

        if result.returncode == 0 and output_path.exists():
            config.local_path = str(output_path)
            print(f"   ✅ 生成成功: {output_path}")
            return True
        else:
            print(f"   ❌ 生成失败")
            if result.stderr:
                print(f"   错误: {result.stderr[:200]}")
            return False

    except subprocess.TimeoutExpired:
        timeout_val = TIMEOUTS.get("image_generation", 120)
        print(f"   ❌ 生成超时（{timeout_val}秒）")
        return False
    except Exception as e:
        print(f"   ❌ 生成失败: {str(e)}")
        return False


def upload_to_picgo(image_path: str) -> str:
    """
    使用 PicGo 上传图片到图床

    Args:
        image_path: 本地图片路径

    Returns:
        str: CDN URL

    Raises:
        RuntimeError: 上传失败时抛出异常（fail fast）
    """
    print(f"\n📤 上传图片: {image_path}")

    try:
        # 使用 picgo upload 命令
        result = subprocess.run(
            [PICGO_CMD, "upload", image_path],
            capture_output=True,
            text=True,
            timeout=TIMEOUTS.get("upload", 60)
        )

        if result.returncode == 0:
            # 解析输出获取 URL
            # PicGo 输出格式通常包含 URL
            output = result.stdout

            # 尝试从输出中提取 URL
            for line in output.split('\n'):
                if line.startswith('http://') or line.startswith('https://'):
                    cdn_url = line.strip()
                    print(f"   ✅ 上传成功: {cdn_url}")
                    return cdn_url

            # 如果没有直接找到 URL，尝试解析 JSON
            try:
                data = json.loads(output)
                if isinstance(data, dict) and 'url' in data:
                    cdn_url = data['url']
                    print(f"   ✅ 上传成功: {cdn_url}")
                    return cdn_url
                elif isinstance(data, list) and len(data) > 0 and 'url' in data[0]:
                    cdn_url = data[0]['url']
                    print(f"   ✅ 上传成功: {cdn_url}")
                    return cdn_url
            except json.JSONDecodeError:
                pass

            # 无法解析 URL - 立即失败
            error_msg = f"PicGo 上传返回成功但无法解析 URL。输出: {output[:200]}"
            print(f"   ❌ {error_msg}")
            raise RuntimeError(error_msg)
        else:
            # 上传失败 - 立即失败
            error_msg = f"PicGo 上传失败 (exit code {result.returncode})"
            if result.stderr:
                error_msg += f": {result.stderr[:200]}"
            print(f"   ❌ {error_msg}")
            raise RuntimeError(error_msg)

    except subprocess.TimeoutExpired:
        error_msg = f"PicGo 上传超时（{TIMEOUTS.get('upload', 60)}秒）"
        print(f"   ❌ {error_msg}")
        raise RuntimeError(error_msg)
    except RuntimeError:
        # 重新抛出我们自己的错误
        raise
    except Exception as e:
        error_msg = f"PicGo 上传异常: {str(e)}"
        print(f"   ❌ {error_msg}")
        raise RuntimeError(error_msg) from e


def dry_run_preview(configs: List[ImageConfig],
                    upload: bool = True,
                    resolution: str = "2K",
                    model: str = "gemini-3-pro-image-preview") -> None:
    """
    预览将要生成的图片，显示成本和时间估算

    Args:
        configs: 图片配置列表
        upload: 是否上传到图床
        resolution: 图片分辨率
        model: 使用的模型
    """
    print("=" * 70)
    print("🔍 Dry-Run 模式 - 预览生成计划")
    print("=" * 70)

    total_images = len(configs)

    # 成本估算
    cost_per_image = GEMINI_PRICING.get(model, {}).get(resolution, 0.20)
    total_cost = total_images * cost_per_image

    # 时间估算
    gen_time_per_image = AVG_GENERATION_TIME.get(resolution, 25)
    upload_time_per_image = AVG_UPLOAD_TIME if upload else 0
    total_time_per_image = gen_time_per_image + upload_time_per_image + 2  # +2s for delays
    total_time_seconds = total_images * total_time_per_image
    total_time_minutes = total_time_seconds / 60

    print(f"\n📊 总览:")
    print(f"   图片数量: {total_images}")
    print(f"   分辨率: {resolution}")
    print(f"   模型: {model}")
    print(f"   上传模式: {'是' if upload else '否'}")

    print(f"\n💰 成本估算:")
    print(f"   单张成本: ${cost_per_image:.2f}")
    print(f"   总成本: ${total_cost:.2f}")

    print(f"\n⏱️  时间估算:")
    print(f"   单张耗时: ~{total_time_per_image}秒 (生成{gen_time_per_image}s + 上传{upload_time_per_image}s + 延迟2s)")
    print(f"   总耗时: ~{total_time_minutes:.1f}分钟 ({total_time_seconds}秒)")

    print(f"\n📋 图片清单:")
    for i, config in enumerate(configs, 1):
        print(f"\n  [{i}] {config.name}")
        print(f"      文件名: {config.filename}")
        print(f"      宽高比: {config.aspect_ratio}")
        print(f"      提示词: {config.prompt[:80]}{'...' if len(config.prompt) > 80 else ''}")

    print("\n" + "=" * 70)
    print("💡 提示: 移除 --dry-run 参数以开始实际生成")
    print("=" * 70)


def generate_and_upload_batch(configs: List[ImageConfig],
                               upload: bool = True,
                               resolution: str = "2K") -> Dict:
    """
    批量生成和上传图片

    Args:
        configs: 图片配置列表
        upload: 是否上传到图床
        resolution: 图片分辨率

    Returns:
        dict: 结果统计
    """
    print("=" * 70)
    print("📸 开始批量生成和上传图片")
    print("=" * 70)

    results = {
        "total": len(configs),
        "generated": 0,
        "uploaded": 0,
        "failed": 0,
        "images": []
    }

    # Use tqdm for progress tracking
    with tqdm(configs, desc="📸 生成和上传图片", unit="image") as pbar:
        for i, config in enumerate(pbar, 1):
            pbar.set_description(f"📸 处理 {i}/{len(configs)}: {config.name}")
            print(f"\n[{i}/{len(configs)}] 处理: {config.name}")
            print("-" * 70)

            # 生成图片
            if generate_image(config, resolution):
                results["generated"] += 1

                # 先记录结果（确保即使上传失败也有记录）
                results["images"].append({
                    "name": config.name,
                    "filename": config.filename,
                    "local_path": config.local_path,
                    "cdn_url": None,  # 上传成功后会更新
                    "prompt": config.prompt
                })

                # 上传到图床
                if upload and config.local_path:
                    time.sleep(1)  # 避免请求过快
                    # Fail-fast: 上传失败会停止整个批量处理
                    # 匹配原始 SKILL.md "If ANY step fails, STOP" 的要求
                    cdn_url = upload_to_picgo(config.local_path)
                    config.cdn_url = cdn_url
                    results["uploaded"] += 1
                    # 更新刚才添加的记录中的 cdn_url
                    results["images"][-1]["cdn_url"] = cdn_url
            else:
                results["failed"] += 1
                # 即使生成失败也记录，方便调试
                results["images"].append({
                    "name": config.name,
                    "filename": config.filename,
                    "local_path": None,
                    "cdn_url": None,
                    "prompt": config.prompt
                })

            # 避免请求过快
            if i < len(configs):
                time.sleep(2)

    return results


def generate_and_upload_parallel(configs: List[ImageConfig],
                                   upload: bool = True,
                                   resolution: str = "2K",
                                   max_workers: int = 2,
                                   fail_fast: bool = True) -> Dict:
    """
    并行批量生成和上传图片（性能优化版本）

    Args:
        configs: 图片配置列表
        upload: 是否上传到图床
        resolution: 图片分辨率
        max_workers: 最大并行工作线程数（默认2，避免API限流）
        fail_fast: 遇到错误立即停止（True）或继续处理（False）

    Returns:
        dict: 结果统计
    """
    print("=" * 70)
    print(f"📸 开始并行批量生成和上传图片（{max_workers} 个并发线程）")
    if fail_fast:
        print("⚠️  Fail-Fast 模式：任意错误将立即停止")
    else:
        print("🔄 容错模式：遇到错误继续处理其他图片")
    print("=" * 70)

    results = {
        "total": len(configs),
        "generated": 0,
        "uploaded": 0,
        "failed": 0,
        "errors": [],  # 新增：记录所有错误详情
        "images": []
    }

    # 线程安全的结果锁
    from threading import Lock
    results_lock = Lock()

    def process_single_image(config: ImageConfig) -> Dict:
        """处理单张图片的生成"""
        result = {
            "name": config.name,
            "filename": config.filename,
            "local_path": None,
            "cdn_url": None,
            "prompt": config.prompt,
            "success": False,
            "error": None,
            "error_type": None  # 新增：错误类型分类
        }

        try:
            # 生成图片
            if generate_image(config, resolution):
                result["local_path"] = config.local_path
                result["success"] = True

                with results_lock:
                    results["generated"] += 1
            else:
                result["error"] = "生成失败（未知原因）"
                result["error_type"] = "generation_failed"

                with results_lock:
                    results["failed"] += 1
                    results["errors"].append({
                        "image": config.name,
                        "stage": "generation",
                        "error": result["error"]
                    })

        except FileNotFoundError as e:
            result["error"] = f"文件系统错误: {str(e)}"
            result["error_type"] = "filesystem_error"
            with results_lock:
                results["failed"] += 1
                results["errors"].append({
                    "image": config.name,
                    "stage": "generation",
                    "error": result["error"],
                    "type": "FileNotFoundError"
                })

        except subprocess.TimeoutExpired as e:
            result["error"] = f"生成超时: {str(e)}"
            result["error_type"] = "timeout"
            with results_lock:
                results["failed"] += 1
                results["errors"].append({
                    "image": config.name,
                    "stage": "generation",
                    "error": result["error"],
                    "type": "TimeoutError"
                })

        except Exception as e:
            result["error"] = f"未知错误: {str(e)}"
            result["error_type"] = "unknown"
            with results_lock:
                results["failed"] += 1
                results["errors"].append({
                    "image": config.name,
                    "stage": "generation",
                    "error": result["error"],
                    "type": type(e).__name__
                })

        return result

    # 阶段1: 并行生成所有图片
    print(f"\n🎨 阶段 1/2: 并行生成图片 (max_workers={max_workers})")

    generated_results = []
    generation_failed = False

    # 统计信息
    start_time = time.time()
    completed_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有生成任务
        future_to_config = {
            executor.submit(process_single_image, config): config
            for config in configs
        }

        # 使用 tqdm 显示进度
        with tqdm(
            total=len(configs),
            desc="🎨 生成图片",
            unit="image",
            bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        ) as pbar:
            for future in as_completed(future_to_config):
                config = future_to_config[future]
                completed_count += 1

                try:
                    result = future.result()
                    generated_results.append(result)

                    # 计算实时统计
                    elapsed = time.time() - start_time
                    avg_time = elapsed / completed_count if completed_count > 0 else 0
                    remaining = (len(configs) - completed_count) * avg_time

                    # 更新进度条描述
                    if result["success"]:
                        status_emoji = "✅"
                        pbar.set_description(
                            f"{status_emoji} [{completed_count}/{len(configs)}] {result['name'][:20]}"
                        )
                    else:
                        status_emoji = "❌"
                        pbar.set_description(
                            f"{status_emoji} [{completed_count}/{len(configs)}] {result['name'][:20]} - 失败"
                        )

                        if fail_fast:
                            # Fail-fast: 立即停止
                            generation_failed = True
                            pbar.close()
                            executor.shutdown(wait=False, cancel_futures=True)

                            print(f"\n❌ 生成失败（Fail-Fast 模式）: {result['name']}")
                            print(f"   错误: {result['error']}")
                            raise RuntimeError(f"图片生成失败: {result['name']} - {result['error']}")

                    # 更新进度条
                    pbar.update(1)

                    # 更新后缀显示统计信息
                    pbar.set_postfix({
                        '成功': f"{results['generated']}/{completed_count}",
                        '平均': f"{avg_time:.1f}s/图",
                        '剩余': f"{int(remaining)}s"
                    })

                except Exception as e:
                    if fail_fast:
                        # Fail-fast: 任意严重错误立即停止
                        pbar.set_description(f"💥 严重错误: {config.name}")
                        pbar.close()

                        # 取消所有未完成的任务
                        executor.shutdown(wait=False, cancel_futures=True)

                        print(f"\n❌ 并行生成失败: {str(e)}")
                        raise
                    else:
                        # 容错模式：记录错误但继续
                        pbar.set_description(f"⚠️  错误（已跳过）: {config.name}")
                        with results_lock:
                            results["failed"] += 1
                            results["errors"].append({
                                "image": config.name,
                                "stage": "generation",
                                "error": str(e),
                                "type": type(e).__name__
                            })
                        pbar.update(1)

    # 阶段2: 串行上传图片（避免并发上传问题）
    if upload and not generation_failed:
        print(f"\n📤 阶段 2/2: 串行上传图片到 PicGo")

        successful_results = [r for r in generated_results if r["success"]]

        if len(successful_results) == 0:
            print("⚠️  没有成功生成的图片需要上传")
        else:
            # 上传阶段统计
            upload_start_time = time.time()
            upload_count = 0

            with tqdm(
                total=len(successful_results),
                desc="📤 上传图片",
                unit="image",
                bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
            ) as pbar:
                for idx, result in enumerate(successful_results, 1):
                    if result["local_path"]:
                        pbar.set_description(f"📤 [{idx}/{len(successful_results)}] {result['name'][:20]}")

                        try:
                            # 记录单次上传开始时间
                            upload_item_start = time.time()

                            # 上传到图床
                            cdn_url = upload_to_picgo(result["local_path"])
                            result["cdn_url"] = cdn_url

                            # 计算上传耗时
                            upload_duration = time.time() - upload_item_start

                            with results_lock:
                                results["uploaded"] += 1

                            upload_count += 1

                            # 计算统计信息
                            upload_elapsed = time.time() - upload_start_time
                            avg_upload_time = upload_elapsed / upload_count if upload_count > 0 else 0
                            remaining_uploads = len(successful_results) - upload_count
                            remaining_time = remaining_uploads * avg_upload_time

                            pbar.set_description(f"✅ [{idx}/{len(successful_results)}] {result['name'][:20]}")

                            # 更新后缀显示统计信息
                            pbar.set_postfix({
                                '成功': f"{upload_count}/{idx}",
                                '平均': f"{avg_upload_time:.1f}s/图",
                                '本次': f"{upload_duration:.1f}s",
                                '剩余': f"{int(remaining_time)}s"
                            })

                            pbar.update(1)

                        except Exception as e:
                            # 上传失败处理
                            error_msg = f"上传失败: {str(e)}"

                            with results_lock:
                                results["errors"].append({
                                    "image": result['name'],
                                    "stage": "upload",
                                    "error": error_msg,
                                    "type": type(e).__name__
                                })

                            if fail_fast:
                                # Fail-fast: 上传失败立即停止
                                pbar.close()
                                print(f"\n❌ 上传失败（Fail-Fast 模式）: {result['name']}")
                                print(f"   错误: {error_msg}")
                                raise RuntimeError(f"上传 {result['name']} 失败: {str(e)}") from e
                            else:
                                # 容错模式：记录错误但继续
                                pbar.set_description(f"⚠️ [{idx}/{len(successful_results)}] {result['name'][:20]} - 失败")
                                pbar.update(1)

                        # 避免请求过快
                        time.sleep(1)

    # 将结果添加到最终统计
    for result in generated_results:
        results["images"].append({
            "name": result["name"],
            "filename": result["filename"],
            "local_path": result["local_path"],
            "cdn_url": result["cdn_url"],
            "prompt": result["prompt"]
        })

    return results


def print_summary(results: Dict):
    """打印结果摘要"""
    print("\n" + "=" * 70)
    print("✨ 处理完成!")
    print("=" * 70)
    print(f"\n📊 统计:")
    print(f"   总数: {results['total']}")
    print(f"   生成成功: {results['generated']}")
    print(f"   上传成功: {results['uploaded']}")
    print(f"   失败: {results['failed']}")

    # 新增：错误报告
    if results.get('errors') and len(results['errors']) > 0:
        print(f"\n⚠️  错误报告: ({len(results['errors'])} 个错误)")
        print("-" * 70)
        for idx, error in enumerate(results['errors'], 1):
            print(f"\n  [{idx}] {error['image']} - {error['stage'].upper()}")
            print(f"      类型: {error.get('type', 'Unknown')}")
            print(f"      错误: {error['error']}")

    print(f"\n📋 图片清单:")
    for img in results["images"]:
        print(f"\n🖼️  {img['name']}")
        print(f"   文件名: {img['filename']}")
        if img['local_path']:
            print(f"   本地路径: {img['local_path']}")
        if img['cdn_url']:
            print(f"   CDN URL: {img['cdn_url']}")
            print(f"   Markdown: ![{img['name']}]({img['cdn_url']})")
        else:
            print(f"   ⚠️  未上传到图床")


def generate_markdown_output(results: Dict) -> str:
    """生成 Markdown 格式的输出"""
    lines = ["# 文章配图清单\n"]

    for img in results["images"]:
        lines.append(f"## {img['name']}\n")
        lines.append(f"**文件名**: {img['filename']}  ")

        if img['local_path']:
            lines.append(f"**本地路径**: `{img['local_path']}`  ")

        if img['cdn_url']:
            lines.append(f"**CDN URL**: {img['cdn_url']}  ")
            lines.append(f"\n**Markdown引用**:")
            lines.append(f"```markdown")
            lines.append(f"![{img['name']}]({img['cdn_url']})")
            lines.append(f"```\n")

        lines.append(f"**提示词**: {img['prompt']}\n")
        lines.append("---\n")

    return "\n".join(lines)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="文章配图生成和上传工具")
    parser.add_argument("--config", help="配置文件路径 (JSON)")
    parser.add_argument("--no-upload", action="store_true", help="只生成不上传")
    parser.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"],
                       help="图片分辨率")
    parser.add_argument("--output", help="输出 Markdown 文件路径")
    parser.add_argument("--check", action="store_true", help="检查依赖")
    parser.add_argument("--dry-run", action="store_true",
                       help="预览模式：显示成本和时间估算，不实际生成图片")
    parser.add_argument("--model", default="gemini-3-pro-image-preview",
                       choices=["gemini-3-pro-image-preview", "gemini-2.5-flash-image"],
                       help="使用的 Gemini 模型（仅用于 dry-run 成本估算）")
    parser.add_argument("--parallel", action="store_true",
                       help="启用并行生成模式（提升速度，但可能触发API限流）")
    parser.add_argument("--max-workers", type=int, default=2,
                       help="并行模式下的最大工作线程数（默认2，避免API限流）")
    parser.add_argument("--continue-on-error", action="store_true",
                       help="容错模式：遇到错误继续处理其他图片（默认Fail-Fast立即停止）")
    parser.add_argument("--resume", action="store_true",
                       help="从检查点恢复未完成的任务（实验性功能）")
    parser.add_argument("--checkpoint-dir", default=".checkpoints",
                       help="检查点文件保存目录（默认: .checkpoints）")

    args = parser.parse_args()

    # 检查依赖
    if args.check:
        print("🔍 检查依赖...")
        errors = check_dependencies()
        if errors:
            print("\n".join(errors))
            sys.exit(1)
        else:
            print("✅ 所有依赖已就绪")
            sys.exit(0)

    errors = check_dependencies()
    if errors:
        print("\n".join(errors))
        print("\n请先解决以上问题，或使用 --check 参数检查依赖")
        sys.exit(1)

    # 加载配置
    if args.config:
        with open(args.config, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        configs = []
        for item in config_data.get("images", []):
            configs.append(ImageConfig(
                name=item["name"],
                prompt=item["prompt"],
                aspect_ratio=item.get("aspect_ratio", "3:2"),
                filename=item.get("filename")
            ))
    else:
        print("❌ 请提供配置文件: --config config.json")
        print("\n配置文件示例:")
        print(json.dumps({
            "images": [
                {
                    "name": "封面图",
                    "prompt": "清晨阳光透过窗户，手绘插画风格，温暖色调",
                    "aspect_ratio": "16:9",
                    "filename": "cover.jpg"
                }
            ]
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    # Dry-run 模式：仅预览，不实际生成
    if args.dry_run:
        dry_run_preview(
            configs=configs,
            upload=not args.no_upload,
            resolution=args.resolution,
            model=args.model
        )
        sys.exit(0)

    # 批量处理：根据参数选择串行或并行模式
    if args.parallel:
        # 并行模式
        print(f"\n🚀 使用并行模式（{args.max_workers} 个工作线程）")
        results = generate_and_upload_parallel(
            configs=configs,
            upload=not args.no_upload,
            resolution=args.resolution,
            max_workers=args.max_workers,
            fail_fast=not args.continue_on_error  # 容错模式控制
        )
    else:
        # 串行模式（默认）
        results = generate_and_upload_batch(
            configs=configs,
            upload=not args.no_upload,
            resolution=args.resolution
        )

    # 打印摘要
    print_summary(results)

    # 输出 Markdown
    if args.output:
        markdown = generate_markdown_output(results)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"\n📝 Markdown 输出已保存: {args.output}")


if __name__ == "__main__":
    main()
