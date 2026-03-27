#!/usr/bin/env python3
"""
Images Skill - 智能图片生成与上传
"""

import os
import sys
import argparse
import re
import subprocess
from pathlib import Path

def detect_best_model():
    """检测可用的Gemini模型"""
    try:
        result = subprocess.run(
            [sys.executable, str(Path.home() / ".claude/plugins/article-craft/scripts/generate_and_upload_images.py"), "--probe"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('BEST_MODEL:'):
                    return line.split(':')[1].strip()
    except Exception:
        pass
    return "gemini-3-pro-image-preview"  # 默认模型

def process_images_in_article(article_path, model="gemini-3-pro-image-preview", continue_on_error=False):
    """处理文章中的图片占位符"""
    print(f"🔍 正在处理文章: {article_path}")
    print(f"🎨 使用模型: {model}")

    # 检查是否有图片占位符
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()

    image_placeholders = re.findall(r'<!-- IMAGE: (.*?) -->', content)
    screenshot_placeholders = re.findall(r'<!-- SCREENSHOT: (.*?) -->', content)

    total = len(image_placeholders) + len(screenshot_placeholders)
    print(f"📊 发现 {len(image_placeholders)} 个图片占位符和 {len(screenshot_placeholders)} 个截图占位符")

    if total == 0:
        print("✅ 没有需要处理的图片占位符")
        return True

    # 运行图片处理脚本
    try:
        cmd = [
            sys.executable, str(Path.home() / ".claude/plugins/article-craft/scripts/generate_and_upload_images.py"),
            "--process-file", article_path,
            "--model", model,
            "--continue-on-error" if continue_on_error else ""
        ]
        # 过滤掉空字符串
        cmd = [arg for arg in cmd if arg]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"⚠️  警告: {result.stderr}", file=sys.stderr)

        if result.returncode == 0:
            print("✅ 图片处理完成")
            return True
        else:
            print(f"❌ 图片处理失败，返回码: {result.returncode}", file=sys.stderr)
            return False

    except Exception as e:
        print(f"❌ 图片处理发生异常: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="智能图片生成与上传技能")
    parser.add_argument("article_path", type=str, help="文章文件路径")
    parser.add_argument("--model", type=str, help="图片生成模型")
    parser.add_argument("--continue-on-error", action="store_true", help="出错时继续执行")
    parser.add_argument("--probe", action="store_true", help="仅检测可用模型")

    args = parser.parse_args()

    if args.probe:
        model = detect_best_model()
        print(f"✅ 检测到最佳模型: {model}")
        return 0

    if not args.article_path:
        print("❌ 必须提供文章文件路径", file=sys.stderr)
        return 1

    if not args.model:
        args.model = detect_best_model()

    success = process_images_in_article(
        args.article_path,
        args.model,
        args.continue_on_error
    )

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
