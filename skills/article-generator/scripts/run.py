#!/usr/bin/env python3
"""
Article Generator CLI Wrapper
简化 article-generator 的调用流程，提供交互式菜单和智能默认值。
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATE_SCRIPT = os.path.join(SCRIPT_DIR, "generate_and_upload_images.py")

def print_header():
    print("\n" + "=" * 50)
    print("   🚀 Article Generator CLI   ")
    print("=" * 50 + "\n")

def get_article_file():
    """交互式获取文章文件路径"""
    # 1. 检查命令行参数是否提供了文件
    # 2. 检查当前目录下的 .md 文件
    md_files = list(Path(".").glob("*.md"))

    # 排除掉 README.md 等非文章文件
    md_files = [f for f in md_files if f.name.lower() not in ["readme.md", "license.md", "install.md"]]

    if not md_files:
        print("❌ 当前目录下未找到 Markdown 文章文件 (.md)")
        path = input("👉 请输入文章文件的绝对路径: ").strip()
        return path

    print("📄 发现以下文章文件:")
    for i, f in enumerate(md_files, 1):
        print(f"  {i}. {f.name}")
    print(f"  0. 输入其他路径")

    choice = input("\n👉 请选择文件 (默认 1): ").strip()

    if not choice:
        return str(md_files[0].resolve())

    try:
        idx = int(choice)
        if idx == 0:
            return input("👉 请输入文章文件的绝对路径: ").strip()
        if 1 <= idx <= len(md_files):
            return str(md_files[idx-1].resolve())
    except ValueError:
        pass

    print("❌ 无效选择")
    return None

def main():
    print_header()

    parser = argparse.ArgumentParser(description="Article Generator Simplified CLI")
    parser.add_argument("file", nargs="?", help="Article file path")
    parser.add_argument("--fast", action="store_true", help="Fast mode (no enhancement)")
    args = parser.parse_args()

    # 1. 获取文件路径
    file_path = args.file
    if not file_path:
        file_path = get_article_file()

    if not file_path or not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        sys.exit(1)

    file_path = os.path.abspath(file_path)
    print(f"\n✅ 选定文件: {file_path}")

    # 2. 确认增强模式
    enhance_mode = True
    if not args.fast:
        print("\n🎨 图片生成模式:")
        print("  1. 智能增强 (推荐) - AI 自动优化提示词，画质更好")
        print("  2. 快速直出 - 使用原始提示词，速度更快")

        choice = input("\n👉 请选择 (默认 1): ").strip()
        if choice == "2":
            enhance_mode = False
            print("🚀 已选择: 快速直出模式")
        else:
            print("✨ 已选择: 智能增强模式")
    else:
        enhance_mode = False
        print("🚀 快速模式已启用")

    # 3. 构建命令
    cmd = ["python3", GENERATE_SCRIPT, "--process-file", file_path, "--resolution", "2K"]

    if enhance_mode:
        cmd.append("--enhance")

    print("\n" + "-" * 50)
    print("🔨 开始执行...")
    print("-" * 50)

    # 4. 执行核心脚本
    try:
        subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ 全部完成！")
        print("=" * 50 + "\n")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 执行失败 (Exit code: {e.returncode})")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\n⚠️  用户取消")
        sys.exit(130)

if __name__ == "__main__":
    main()
