#!/usr/bin/env python3
"""
upload_draft.py - 一键上传 Markdown 文章到微信公众号草稿箱

自动化流程：
1. 解析 YAML frontmatter（title, description）
2. 调用 convert_to_wechat.py 转换 HTML（--no-preview-mode）
3. 扫描 HTML 中所有 <img> 外部链接
4. 逐个上传图片到微信素材库（调用 Go 后端 download_and_upload）
5. 替换 HTML 中的图片 URL（CDN → mmbiz.qpic.cn）
6. 提取封面图 media_id，从内容中移除封面图
7. 移除 h1 标题（避免与草稿标题重复）
8. 构建 draft JSON，调用 Go 后端 create_draft 上传

用法：
    python3 upload_draft.py article.md --theme coffee
    python3 upload_draft.py article.md --theme coffee --author 月影 --cover cover.jpg
"""

import sys
import os
import re
import json
import argparse
import subprocess
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_SCRIPT = os.path.join(SCRIPT_DIR, "md2wechat_backend.sh")


class FatalUploadError(Exception):
    """不可恢复的上传错误（如 IP 白名单），应立即终止"""
    pass


def extract_error_summary(output):
    """从 Go 后端输出中提取关键错误信息，过滤 stack trace 噪音

    返回: (error_type, error_msg)
        error_type: "IP_WHITELIST" | None
        error_msg: 人类可读的错误摘要
    """
    if not output:
        return None, "未知错误"

    # 检查 IP 白名单错误（不可恢复）
    ip_match = re.search(r'invalid ip (\S+)', output)
    if ip_match or 'not in whitelist' in output:
        ip = ip_match.group(1) if ip_match else "未知"
        return "IP_WHITELIST", ip

    # 提取 error 级别日志的关键消息（去重，过滤 stack trace）
    seen = set()
    error_msgs = []
    for line in output.split("\n"):
        if '"level":"error"' in line:
            msg_match = re.search(r'"error":"([^"]*?)(?:\\n|")', line)
            if msg_match and msg_match.group(1) not in seen:
                seen.add(msg_match.group(1))
                error_msgs.append(msg_match.group(1))

    if error_msgs:
        return None, error_msgs[0]

    # Fallback: 最后一行非空内容截断
    last_line = output.strip().split("\n")[-1]
    return None, last_line[:200]


# =============================================================================
# Step 1: 解析 YAML frontmatter
# =============================================================================

def parse_frontmatter(md_path):
    """解析 Markdown 文件的 YAML frontmatter，提取 title 和 description"""
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    metadata = {"title": "", "description": ""}

    match = re.match(r"^\s*---\n(.*?)\n---\n", content, re.DOTALL | re.MULTILINE)
    if not match:
        # 没有 frontmatter，尝试从第一个 h1 提取标题
        h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if h1_match:
            metadata["title"] = h1_match.group(1).strip()
        return metadata

    yaml_content = match.group(1)

    # 提取 title
    title_match = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', yaml_content, re.MULTILINE)
    if title_match:
        metadata["title"] = title_match.group(1).strip()

    # 提取 description
    desc_match = re.search(r'^description:\s*["\']?(.*?)["\']?\s*$', yaml_content, re.MULTILINE)
    if desc_match:
        metadata["description"] = desc_match.group(1).strip()

    return metadata


# =============================================================================
# Step 2: 调用 convert_to_wechat.py 转换 HTML
# =============================================================================

def convert_markdown(md_path, theme="coffee"):
    """调用 convert_to_wechat.py 将 Markdown 转换为微信 HTML（纯净模式）"""
    convert_script = os.path.join(SCRIPT_DIR, "convert_to_wechat.py")

    # 计算输出文件路径
    abs_input = os.path.abspath(md_path)
    output_path = os.path.splitext(abs_input)[0] + "_wechat.html"

    cmd = [
        sys.executable, convert_script,
        md_path,
        "--theme", theme,
        "--no-preview-mode",
        "--output", output_path,
    ]

    print(f"\n{'='*60}")
    print(f"📝 Step 1: 转换 Markdown → WeChat HTML")
    print(f"{'='*60}")
    print(f"  主题: {theme}")
    print(f"  输入: {md_path}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 转换失败:")
        print(result.stderr)
        sys.exit(1)

    print(f"  输出: {output_path}")
    print(f"✅ 转换成功")

    return output_path


# =============================================================================
# Step 3-4: 上传图片到微信素材库
# =============================================================================

def run_backend_command(args):
    """调用 Go 后端命令，返回 stdout"""
    cmd = ["bash", BACKEND_SCRIPT] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None, result.stderr
    return result.stdout, None


def parse_backend_json(output):
    """从 Go 后端输出中提取最后一个 JSON 块

    Go 后端混合输出 log + JSON，需要找到最后一个 {"success":...} 块
    """
    # 逐行查找所有 JSON 行，取最后一个
    last_json = None
    for line in output.strip().split("\n"):
        line = line.strip()
        if line.startswith("{") and "success" in line:
            try:
                parsed = json.loads(line)
                last_json = parsed
            except json.JSONDecodeError:
                continue

    return last_json


def upload_image(url):
    """上传单个图片 URL 到微信素材库

    调用 Go 后端 download_and_upload 命令
    返回: (media_id, wechat_url) 或 (None, None)
    抛出: FatalUploadError - IP 白名单等不可恢复错误
    """
    stdout, stderr = run_backend_command(["download_and_upload", url])
    if stdout is None:
        error_type, error_msg = extract_error_summary(stderr or "")
        if error_type == "IP_WHITELIST":
            raise FatalUploadError(
                f"当前 IP ({error_msg}) 不在微信白名单\n"
                f"  → 登录 mp.weixin.qq.com → 设置与开发 → 基本配置 → IP 白名单 → 添加 {error_msg}"
            )
        print(f"    ❌ 上传失败: {error_msg}")
        return None, None

    data = parse_backend_json(stdout)
    if data and data.get("success"):
        media_id = data.get("media_id", "")
        wechat_url = data.get("wechat_url", "")
        return media_id, wechat_url

    # stdout 有内容但解析失败，也检查 IP 白名单
    error_type, error_msg = extract_error_summary(stdout)
    if error_type == "IP_WHITELIST":
        raise FatalUploadError(
            f"当前 IP ({error_msg}) 不在微信白名单\n"
            f"  → 登录 mp.weixin.qq.com → 设置与开发 → 基本配置 → IP 白名单 → 添加 {error_msg}"
        )
    print(f"    ❌ 解析响应失败: {error_msg}")
    return None, None


def upload_local_image(file_path):
    """上传本地图片到微信素材库

    调用 Go 后端 upload_image 命令
    返回: (media_id, wechat_url) 或 (None, None)
    抛出: FatalUploadError - IP 白名单等不可恢复错误
    """
    stdout, stderr = run_backend_command(["upload_image", file_path])
    if stdout is None:
        error_type, error_msg = extract_error_summary(stderr or "")
        if error_type == "IP_WHITELIST":
            raise FatalUploadError(
                f"当前 IP ({error_msg}) 不在微信白名单\n"
                f"  → 登录 mp.weixin.qq.com → 设置与开发 → 基本配置 → IP 白名单 → 添加 {error_msg}"
            )
        print(f"    ❌ 上传失败: {error_msg}")
        return None, None

    data = parse_backend_json(stdout)
    if data and data.get("success"):
        media_id = data.get("media_id", "")
        wechat_url = data.get("wechat_url", "")
        return media_id, wechat_url

    error_type, error_msg = extract_error_summary(stdout)
    if error_type == "IP_WHITELIST":
        raise FatalUploadError(
            f"当前 IP ({error_msg}) 不在微信白名单\n"
            f"  → 登录 mp.weixin.qq.com → 设置与开发 → 基本配置 → IP 白名单 → 添加 {error_msg}"
        )
    print(f"    ❌ 解析响应失败: {error_msg}")
    return None, None


# =============================================================================
# Step 5-6: 处理 HTML 中的图片
# =============================================================================

def process_images(html_content):
    """扫描 HTML 中的 img 标签，上传外部图片，替换 URL，提取封面

    返回: (processed_html, cover_media_id)
    """
    # 找到所有 img 标签
    img_pattern = re.compile(r'<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*/?\s*>', re.IGNORECASE)
    imgs = list(img_pattern.finditer(html_content))

    if not imgs:
        print("  ⚠️  未找到图片")
        return html_content, None

    print(f"\n{'='*60}")
    print(f"🖼️  Step 2: 上传图片到微信素材库")
    print(f"{'='*60}")
    print(f"  找到 {len(imgs)} 张图片")

    cover_media_id = None
    cover_img_match = None  # 记录封面图的 match 对象

    # 逐个上传（串行，避免 Go 后端临时文件竞态）
    replacements = []  # (old_url, new_url, media_id, is_cover)
    for i, match in enumerate(imgs):
        src = match.group(1)
        full_tag = match.group(0)

        # 获取 alt 属性
        alt_match = re.search(r'alt=["\']([^"\']*)["\']', full_tag, re.IGNORECASE)
        alt_text = alt_match.group(1) if alt_match else ""

        print(f"\n  [{i+1}/{len(imgs)}] {src[:80]}...")

        # 跳过已经是微信 CDN 的图片
        if "mmbiz.qpic.cn" in src:
            print(f"    ✅ 已是微信 CDN，跳过")
            # 如果这是封面图，提取 media_id（但通常不会有）
            continue

        # 跳过 data URI
        if src.startswith("data:"):
            print(f"    ⚠️  跳过 data URI")
            continue

        # 上传图片
        try:
            media_id, wechat_url = upload_image(src)
        except FatalUploadError as e:
            print(f"\n  🚫 致命错误，终止图片上传:")
            print(f"    {e}")
            print(f"\n  📊 上传统计: {len(replacements)}/{len(imgs)} 张成功")
            # 应用已完成的替换后返回
            for old_src, new_url, mid, is_c, m in reversed(replacements):
                old_tag = m.group(0)
                new_tag = old_tag.replace(old_src, new_url)
                html_content = html_content[:m.start()] + new_tag + html_content[m.end():]
            return html_content, None

        if media_id and wechat_url:
            print(f"    ✅ 上传成功")
            print(f"    📎 media_id: {media_id[:8]}...{media_id[-4:]}")

            # 判断是否为封面图
            is_cover = False
            if cover_media_id is None:
                # 封面识别规则：alt 含"封面"，或者第一张图
                if "封面" in alt_text or "cover" in alt_text.lower() or i == 0:
                    cover_media_id = media_id
                    cover_img_match = match
                    is_cover = True
                    print(f"    🎨 标记为封面图")

            replacements.append((src, wechat_url, media_id, is_cover, match))
        else:
            print(f"    ⚠️  上传失败，保留原始 URL")

    # 替换 URL（从后往前替换，避免位置偏移）
    for src, wechat_url, media_id, is_cover, match in reversed(replacements):
        old_tag = match.group(0)
        new_tag = old_tag.replace(src, wechat_url)
        html_content = html_content[:match.start()] + new_tag + html_content[match.end():]

    # 移除封面图（微信草稿单独显示封面）
    if cover_img_match and cover_media_id:
        # 重新查找封面图（URL 已被替换）
        # 找到包含封面图的整个元素（可能被 <p> 或 <figure> 包裹）
        # 先用替换后的 URL 查找
        cover_src = None
        for src, wechat_url, media_id, is_cover, match in replacements:
            if is_cover:
                cover_src = wechat_url
                break

        if cover_src:
            # 移除包含封面图的段落
            # 先尝试移除 <figure>...</figure>
            html_content = re.sub(
                r'<figure[^>]*>.*?<img[^>]*src=["\']' + re.escape(cover_src) + r'["\'][^>]*/?\s*>.*?</figure>',
                '',
                html_content,
                count=1,
                flags=re.DOTALL | re.IGNORECASE
            )
            # 再尝试移除 <p><img>...</p>
            html_content = re.sub(
                r'<p[^>]*>\s*<img[^>]*src=["\']' + re.escape(cover_src) + r'["\'][^>]*/?\s*>\s*</p>',
                '',
                html_content,
                count=1,
                flags=re.DOTALL | re.IGNORECASE
            )

    print(f"\n  📊 上传统计: {len(replacements)}/{len(imgs)} 张成功")

    return html_content, cover_media_id


# =============================================================================
# Step 7: 移除 h1 标题
# =============================================================================

def remove_h1(html_content):
    """移除 HTML 中的第一个 h1 标签（避免与草稿标题重复）"""
    return re.sub(r'<h1[^>]*>.*?</h1>', '', html_content, count=1, flags=re.DOTALL)


# =============================================================================
# Step 8: 提取 wechat-container 内容
# =============================================================================

def extract_wechat_content(html_content):
    """从 HTML 中提取 wechat-container div 的内容"""
    # 查找 wechat-container div
    match = re.search(
        r'<div\s+class=["\']wechat-container["\'][^>]*>(.*?)</div>\s*</body>',
        html_content,
        re.DOTALL | re.IGNORECASE
    )
    if match:
        return match.group(1).strip()

    # 如果没有 wechat-container，尝试提取 body 内容
    match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # 最后返回原始内容
    return html_content


# =============================================================================
# Step 9: 构建并上传草稿
# =============================================================================

def build_and_upload_draft(html_content, metadata, cover_media_id, author="月影"):
    """构建 draft JSON 并调用 Go 后端 create_draft 上传"""
    print(f"\n{'='*60}")
    print(f"📤 Step 3: 上传到微信公众号草稿箱")
    print(f"{'='*60}")

    title = metadata.get("title", "未命名文章")
    digest = metadata.get("description", "")

    # 截断摘要到 120 字符
    if len(digest) > 120:
        digest = digest[:117] + "..."

    print(f"  标题: {title}")
    print(f"  作者: {author}")
    if digest:
        print(f"  摘要: {digest[:50]}...")
    if cover_media_id:
        print(f"  封面: {cover_media_id[:8]}...{cover_media_id[-4:]}")
    else:
        print(f"  ⚠️  无封面图（将使用微信默认封面）")

    # 构建 draft JSON
    article = {
        "title": title,
        "author": author,
        "content": html_content,
        "digest": digest,
    }

    if cover_media_id:
        article["thumb_media_id"] = cover_media_id
        article["show_cover_pic"] = 1

    draft_data = {"articles": [article]}

    # 写入临时 JSON 文件
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", prefix="wechat_draft_", delete=False, encoding="utf-8"
    ) as f:
        json.dump(draft_data, f, ensure_ascii=False, indent=2)
        json_path = f.name

    print(f"  JSON: {json_path}")

    # 调用 Go 后端 create_draft
    stdout, stderr = run_backend_command(["create_draft", json_path])

    # 清理临时文件
    try:
        os.unlink(json_path)
    except OSError:
        pass

    if stdout is None:
        error_type, error_msg = extract_error_summary(stderr or "")
        if error_type == "IP_WHITELIST":
            print(f"\n❌ 草稿上传失败: 当前 IP ({error_msg}) 不在微信白名单")
            print(f"  → 登录 mp.weixin.qq.com → 设置与开发 → 基本配置 → IP 白名单 → 添加 {error_msg}")
        else:
            print(f"\n❌ 草稿上传失败: {error_msg}")
        sys.exit(1)

    data = parse_backend_json(stdout)
    if data and data.get("success"):
        draft_media_id = data.get("media_id", "")
        print(f"\n{'='*60}")
        print(f"✅ 草稿上传成功！")
        print(f"{'='*60}")
        print(f"  📎 draft media_id: {draft_media_id}")
        print(f"  💡 请登录微信公众号后台查看草稿箱")
        print(f"{'='*60}\n")
        return draft_media_id
    else:
        error_type, error_msg = extract_error_summary(stdout)
        print(f"\n❌ 草稿上传失败: {error_msg}")
        sys.exit(1)


# =============================================================================
# 处理用户指定的封面图
# =============================================================================

def handle_cover_image(cover_path):
    """处理用户指定的封面图文件，上传并返回 media_id"""
    if not cover_path:
        return None

    abs_path = os.path.abspath(cover_path)
    if not os.path.exists(abs_path):
        print(f"⚠️  封面图文件不存在: {abs_path}")
        return None

    print(f"\n  🎨 上传封面图: {abs_path}")
    media_id, wechat_url = upload_local_image(abs_path)
    if media_id:
        print(f"    ✅ 封面图上传成功")
        print(f"    📎 media_id: {media_id[:8]}...{media_id[-4:]}")
        return media_id
    else:
        print(f"    ❌ 封面图上传失败")
        return None


# =============================================================================
# 主流程
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="一键上传 Markdown 文章到微信公众号草稿箱",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 upload_draft.py article.md --theme coffee
  python3 upload_draft.py article.md --theme tech --author 月影
  python3 upload_draft.py article.md --theme coffee --cover cover.jpg
        """
    )
    parser.add_argument("file", help="Markdown 文件路径")
    parser.add_argument("--theme", default="coffee", help="转换主题 (默认: coffee)")
    parser.add_argument("--author", default="月影", help="文章作者 (默认: 月影)")
    parser.add_argument("--cover", default=None, help="封面图文件路径（可选，默认使用文章第一张图）")

    args = parser.parse_args()

    # 验证输入文件
    if not os.path.exists(args.file):
        print(f"❌ 文件不存在: {args.file}")
        sys.exit(1)

    # 检查 Go 后端是否可用
    if not os.path.exists(BACKEND_SCRIPT):
        print(f"❌ Go 后端脚本不存在: {BACKEND_SCRIPT}")
        sys.exit(1)

    # 检查环境变量
    if not os.environ.get("WECHAT_APPID") or not os.environ.get("WECHAT_SECRET"):
        print("❌ 缺少微信 API 配置")
        print("  请设置环境变量:")
        print("    export WECHAT_APPID='your_appid'")
        print("    export WECHAT_SECRET='your_secret'")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"🚀 微信公众号草稿上传工具")
    print(f"{'='*60}")
    print(f"  文件: {args.file}")
    print(f"  主题: {args.theme}")
    print(f"  作者: {args.author}")

    # Step 1: 解析 frontmatter
    metadata = parse_frontmatter(args.file)
    if metadata["title"]:
        print(f"  标题: {metadata['title']}")

    # Step 2: 转换 Markdown → HTML
    html_path = convert_markdown(args.file, theme=args.theme)

    # 读取 HTML
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 清理中间 HTML 文件（避免残留在源文件目录）
    try:
        os.unlink(html_path)
    except OSError:
        pass

    # Step 3: 提取正文内容
    content = extract_wechat_content(html_content)

    # Step 4-5: 处理图片（上传 + 替换 URL）
    content, auto_cover_media_id = process_images(content)

    # Step 6: 处理封面
    if args.cover:
        cover_media_id = handle_cover_image(args.cover)
        if not cover_media_id:
            # 用户指定封面上传失败，回退到自动检测
            cover_media_id = auto_cover_media_id
    else:
        cover_media_id = auto_cover_media_id

    # Step 7: 移除 h1 标题
    content = remove_h1(content)

    # Step 8: 上传草稿
    build_and_upload_draft(content, metadata, cover_media_id, author=args.author)


if __name__ == "__main__":
    main()
