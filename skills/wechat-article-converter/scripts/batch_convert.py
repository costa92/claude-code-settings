#!/usr/bin/env python3
"""
批量转换 Markdown 文件为微信公众号格式
支持多文件、目录递归、主题统一应用
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Tuple

def find_markdown_files(directory: str, recursive: bool = False) -> List[str]:
    """查找目录中的所有 Markdown 文件"""
    md_files = []
    path = Path(directory)

    if recursive:
        # 递归查找所有 .md 文件
        md_files = list(path.rglob('*.md'))
    else:
        # 仅查找当前目录的 .md 文件
        md_files = list(path.glob('*.md'))

    return [str(f) for f in md_files]

def convert_file(input_file: str, theme: str, output_dir: str = None,
                custom_css: str = None) -> Tuple[bool, str]:
    """转换单个文件"""
    script_dir = Path(__file__).parent
    convert_script = script_dir / "convert_to_wechat.py"

    # 构建输出路径
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        input_path = Path(input_file)
        output_file = output_path / f"{input_path.stem}_wechat.html"
    else:
        # 默认输出到原文件同目录
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_wechat.html"

    # 构建转换命令
    cmd = [
        sys.executable,
        str(convert_script),
        input_file,
        "--theme", theme,
        "--output", str(output_file)
    ]

    if custom_css:
        cmd.extend(["--custom-css", custom_css])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, str(output_file)
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e.stderr}"

def main():
    parser = argparse.ArgumentParser(
        description="批量转换 Markdown 文件为微信公众号格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 转换当前目录所有 .md 文件，使用 Coffee 主题
  python3 batch_convert.py . --theme coffee

  # 递归转换子目录，输出到指定目录
  python3 batch_convert.py ./articles -r --theme tech --output ./wechat_output

  # 转换指定的多个文件
  python3 batch_convert.py file1.md file2.md file3.md --theme warm

  # 使用自定义样式批量转换
  python3 batch_convert.py ./posts --theme simple --custom-css custom.css
        """
    )

    parser.add_argument(
        'inputs',
        nargs='+',
        help='输入文件或目录路径（支持多个）'
    )

    parser.add_argument(
        '-t', '--theme',
        default='tech',
        choices=['coffee', 'tech', 'warm', 'simple', 'md2_classic', 'md2_dark', 'md2_purple'],
        help='应用的主题（默认: tech）'
    )

    parser.add_argument(
        '-o', '--output',
        help='输出目录路径（默认: 原文件同目录）'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='递归查找子目录中的 Markdown 文件'
    )

    parser.add_argument(
        '--custom-css',
        help='自定义 CSS 文件路径'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='预览模式：仅列出要转换的文件，不实际转换'
    )

    args = parser.parse_args()

    # 收集所有待转换的文件
    files_to_convert = []

    for input_path in args.inputs:
        path = Path(input_path)

        if path.is_file() and path.suffix == '.md':
            # 直接指定的 .md 文件
            files_to_convert.append(str(path))
        elif path.is_dir():
            # 目录：查找其中的 .md 文件
            md_files = find_markdown_files(str(path), args.recursive)
            files_to_convert.extend(md_files)
        else:
            print(f"⚠️  跳过无效路径: {input_path}")

    if not files_to_convert:
        print("❌ 未找到任何 Markdown 文件")
        return 1

    # 去重并排序
    files_to_convert = sorted(set(files_to_convert))

    print(f"\n📋 找到 {len(files_to_convert)} 个文件待转换")
    print(f"🎨 使用主题: {args.theme}")
    if args.output:
        print(f"📁 输出目录: {args.output}")
    print()

    # 预览模式
    if args.dry_run:
        print("🔍 预览模式 (--dry-run):")
        for i, file in enumerate(files_to_convert, 1):
            print(f"  {i}. {file}")
        print(f"\n总计: {len(files_to_convert)} 个文件")
        return 0

    # 批量转换
    success_count = 0
    fail_count = 0

    for i, input_file in enumerate(files_to_convert, 1):
        print(f"[{i}/{len(files_to_convert)}] 转换: {Path(input_file).name}")

        success, result = convert_file(
            input_file,
            args.theme,
            args.output,
            args.custom_css
        )

        if success:
            print(f"  ✅ 成功: {result}")
            success_count += 1
        else:
            print(f"  ❌ 失败: {result}")
            fail_count += 1

    # 总结
    print("\n" + "="*60)
    print(f"📊 转换完成:")
    print(f"  ✅ 成功: {success_count}")
    print(f"  ❌ 失败: {fail_count}")
    print(f"  📁 总计: {len(files_to_convert)}")
    print("="*60)

    return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
