#!/usr/bin/env python3
"""
Series Skill Main Entry Point
"""

import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from orchestrator.main import main as orchestrator_main

def get_series_info(series_file):
    """从series.md文件中提取系列信息"""
    import yaml
    from yaml.loader import SafeLoader
    import re

    try:
        with open(series_file, 'r') as f:
            content = f.read()

        if '---' not in content:
            print("错误：无法解析series.md文件格式", file=sys.stderr)
            return None

        frontmatter = content.split('---')[1]
        series_info = yaml.load(frontmatter, Loader=SafeLoader)

        article_list = []
        article_pattern = re.compile(r'\|\s*(\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|')

        for match in article_pattern.finditer(content):
            status = match.group(4).strip()
            if status in ['💡 planned', '✅ published']:
                article_list.append({
                    'number': match.group(1).strip(),
                    'title': match.group(2).strip(),
                    'core_content': match.group(3).strip(),
                    'status': status,
                    'file_path': match.group(5).strip(),
                    'publish_date': match.group(6).strip()
                })

        series_info['articles'] = article_list
        return series_info
    except Exception as e:
        print(f"读取系列文件错误: {e}", file=sys.stderr)
        return None

def find_next_article(series_info):
    """找到系列中第一篇状态为planned的文章"""
    for article in series_info['articles']:
        if article['status'] == '💡 planned':
            return article
    return None

def main():
    parser = argparse.ArgumentParser(description="Series Skill")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Next command
    next_parser = subparsers.add_parser("next", help="Write the next article in the series")
    next_parser.add_argument("series_file", help="Path to series.md file")

    # Status command
    status_parser = subparsers.add_parser("status", help="Check series progress")
    status_parser.add_argument("series_file", help="Path to series.md file")

    args = parser.parse_args()

    if args.command == "next":
        series_info = get_series_info(args.series_file)
        if not series_info:
            print("无法获取系列信息", file=sys.stderr)
            return 1

        next_article = find_next_article(series_info)
        if not next_article:
            print("🎉 所有文章都已完成！")
            return 0

        print(f"📝 下一篇待写文章: #{next_article['number']} {next_article['title']}")
        print(f"📋 核心内容: {next_article['core_content']}")

        # Call the orchestrator
        from orchestrator.main import main as orchestrator_main
        orchestrator_args = ["--series", args.series_file]
        return orchestrator_main(orchestrator_args)

    elif args.command == "status":
        series_info = get_series_info(args.series_file)
        if not series_info:
            print("无法获取系列信息", file=sys.stderr)
            return 1

        total_articles = len(series_info['articles'])
        completed = len([a for a in series_info['articles'] if a['status'] == '✅ published'])
        progress = (completed / total_articles) * 100

        print(f"📚 系列: {series_info['series_name']}")
        print(f"进度: {completed}/{total_articles} 篇 ({progress:.1f}%)")
        print()

        # Progress bar
        bar_length = 10
        completed_bars = int(progress / 10)
        remaining_bars = bar_length - completed_bars
        progress_bar = "█" * completed_bars + "░" * remaining_bars
        print(f"{progress_bar} {progress:.1f}%")
        print()

        print("文章状态：")
        for article in series_info['articles']:
            if article['status'] == '✅ published':
                print(f"✅ 第 {article['number']} 篇：{article['title']} ({article['publish_date']})")
            elif article['status'] == '💡 planned':
                print(f"💡 第 {article['number']} 篇：{article['title']}")

        print()
        next_article = find_next_article(series_info)
        if next_article:
            print(f"下一步：运行 /article-craft:series next {args.series_file} 写第 {next_article['number']} 篇")

        return 0

    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())