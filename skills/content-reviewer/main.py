#!/usr/bin/env python3
"""
Content Reviewer - 7-dimensional article quality review
"""

import argparse
import sys
import re
from pathlib import Path

def count_words(text):
    """Count Chinese characters and English words"""
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
    return chinese_chars + english_words

def analyze_article(file_path):
    """Analyze article and generate review report"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove YAML frontmatter
    text = re.sub(r'^---.*?---\n?', '', content, flags=re.DOTALL)

    # Remove code blocks for word count
    text_without_code = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

    # Calculate metrics
    total_words = count_words(text_without_code)
    code_blocks = len(re.findall(r'```', content)) // 2

    # Find longest code block
    longest_code_block = 0
    code_block_matches = re.findall(r'```(.*?)\n(.*?)```', content, flags=re.DOTALL)
    for lang, code in code_block_matches:
        lines = code.strip().split('\n')
        if len(lines) > longest_code_block:
            longest_code_block = len(lines)

    # Count paragraphs
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text_without_code) if p.strip()]
    avg_paragraph_words = total_words / len(paragraphs) if paragraphs else 0

    # Count external links (excluding images)
    external_links = 0
    for match in re.finditer(r'https?://[^\s\)\]]+', content):
        prev_text = content[max(0, match.start()-20):match.start()]
        if '![' not in prev_text and '[' in prev_text:
            external_links += 1

    # Count heading levels
    headings = re.findall(r'^(#{1,6}) ', content, flags=re.MULTILINE)
    max_heading_level = max(len(h) for h in headings) if headings else 0

    # Count images
    images = len(re.findall(r'!\[.*?\]\(.*?\)', content))

    # Check red flag words
    red_flag_words = [
        '无缝', '赋能', '一站式', '综上所述', '总而言之',
        '值得注意的是', '不难发现', '深度解析', '全面梳理',
        '链路', '闭环', '抓手', '底层逻辑', '方法论',
        '降本增效', '实际上', '事实上', '显然', '众所周知',
        '不难看出'
    ]
    found_flags = [word for word in red_flag_words if word in content]

    # Print report
    print("=" * 60)
    print("量化预检报告")
    print("=" * 60)
    print(f"全文字数: {total_words} 字")
    print(f"代码块数量: {code_blocks} 个")
    print(f"最长代码块: {longest_code_block} 行")
    print(f"平均段落字数: {avg_paragraph_words:.1f} 字")
    print(f"外部链接数: {external_links} 个")
    print(f"标题最深层级: H{max_heading_level}")
    print(f"图片数量: {images} 张")
    print()

    if found_flags:
        print("⚠️  发现红旗词:")
        for flag in found_flags:
            print(f"   - {flag}")
        print()

    # Status indicators
    print("状态:")
    print(f"  字数: {'🟢 正常' if 1500 <= total_words <= 5000 else '🔴 超标'} (参考: 1500-5000)")
    print(f"  段落: {'🟢 正常' if avg_paragraph_words <= 150 else '🟡 偏长'} (参考: ≤150)")
    print(f"  代码块: {'🟢 正常' if longest_code_block <= 30 else '🟡 偏长'} (参考: ≤30)")
    print(f"  外部链接: {'🟢 正常' if external_links == 0 else '🔴 超标'} (参考: 0)")
    print(f"  图片: {'🟢 正常' if images >= (total_words // 800) else '🟡 偏少'} (参考: 每800字≥1)")
    print(f"  标题层级: {'🟢 正常' if max_heading_level <= 3 else '🟡 偏深'} (参考: ≤3)")
    print()

def main():
    parser = argparse.ArgumentParser(description="Content Reviewer - 7-dimensional article quality review")
    parser.add_argument('--article-path', type=str, required=True, help='Path to the article file')
    parser.add_argument('--platform', type=str, default='wechat', choices=['wechat', 'xiaohongshu', 'zhihu'], help='Target platform')
    parser.add_argument('--mode', type=str, default='quick', choices=['quick', 'full'], help='Review mode')

    args = parser.parse_args()

    if not Path(args.article_path).exists():
        print(f"❌ File not found: {args.article_path}")
        sys.exit(1)

    print(f"📄 分析文章: {args.article_path}")
    print(f"🎯 目标平台: {args.platform}")
    print(f"📋 审查模式: {args.mode}")
    print()

    analyze_article(args.article_path)

    print("=" * 60)
    print("提示: 这是一个简化的审查工具。")
    print("完整的审查需要人工进行 7 维评分。")
    print("=" * 60)

if __name__ == "__main__":
    main()
