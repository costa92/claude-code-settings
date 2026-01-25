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

# 配置
NANOBANANA_PATH = os.path.expanduser("~/.claude/skills/nanobanana-skill/nanobanana.py")
IMAGES_DIR = "./images"
PICGO_CMD = "picgo"


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


def check_dependencies():
    """检查依赖工具"""
    errors = []

    # 检查 nanobanana
    if not os.path.exists(NANOBANANA_PATH):
        errors.append(f"❌ nanobanana 脚本未找到: {NANOBANANA_PATH}")

    # 检查 GEMINI_API_KEY
    if not os.getenv("GEMINI_API_KEY"):
        errors.append("❌ 环境变量 GEMINI_API_KEY 未设置")

    # 检查 picgo
    try:
        subprocess.run([PICGO_CMD, "--version"],
                      capture_output=True,
                      check=True,
                      timeout=5)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        errors.append(f"❌ PicGo CLI 未安装或未配置\n   请运行: npm install -g picgo")

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

    # 映射 aspect_ratio 到 nanobanana 的 size 参数
    aspect_ratio_map = {
        "1:1": "1024x1024",
        "3:2": "1152x896",
        "2:3": "896x1152",
        "16:9": "1344x768",
        "9:16": "768x1344",
        "4:3": "1184x864",
        "3:4": "864x1184",
    }

    size = aspect_ratio_map.get(config.aspect_ratio, "1152x896")

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
            timeout=120
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
        print(f"   ❌ 生成超时（120秒）")
        return False
    except Exception as e:
        print(f"   ❌ 生成失败: {str(e)}")
        return False


def upload_to_picgo(image_path: str) -> Optional[str]:
    """
    使用 PicGo 上传图片到图床

    Args:
        image_path: 本地图片路径

    Returns:
        str: CDN URL，失败返回 None
    """
    print(f"\n📤 上传图片: {image_path}")

    try:
        # 使用 picgo upload 命令
        result = subprocess.run(
            [PICGO_CMD, "upload", image_path],
            capture_output=True,
            text=True,
            timeout=60
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

            print(f"   ⚠️ 上传可能成功，但无法解析 URL")
            print(f"   输出: {output[:200]}")
            return None
        else:
            print(f"   ❌ 上传失败")
            if result.stderr:
                print(f"   错误: {result.stderr[:200]}")
            return None

    except subprocess.TimeoutExpired:
        print(f"   ❌ 上传超时（60秒）")
        return None
    except Exception as e:
        print(f"   ❌ 上传失败: {str(e)}")
        return None


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

    for i, config in enumerate(configs, 1):
        print(f"\n[{i}/{len(configs)}] 处理: {config.name}")
        print("-" * 70)

        # 生成图片
        if generate_image(config, resolution):
            results["generated"] += 1

            # 上传到图床
            if upload and config.local_path:
                time.sleep(1)  # 避免请求过快
                cdn_url = upload_to_picgo(config.local_path)

                if cdn_url:
                    config.cdn_url = cdn_url
                    results["uploaded"] += 1
        else:
            results["failed"] += 1

        # 记录结果
        results["images"].append({
            "name": config.name,
            "filename": config.filename,
            "local_path": config.local_path,
            "cdn_url": config.cdn_url,
            "prompt": config.prompt
        })

        # 避免请求过快
        if i < len(configs):
            time.sleep(2)

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

    # 批量处理
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
