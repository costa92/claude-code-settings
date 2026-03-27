#!/usr/bin/env python3
"""
Article Craft Orchestrator - 统一的文章生成工作流

Usage:
    article-craft [--series FILE] [--quick] [--draft] [TOPIC]
    article-craft --upgrade FILE
    article-craft:requirements [--series FILE]
    article-craft:write [--series FILE]
    article-craft:images FILE
    article-craft:review FILE
    article-craft:publish FILE
"""

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path

def run_skill(skill_name, args):
    """运行指定的技能"""
    cmd = [sys.executable, f"{os.path.expanduser('~')}/.claude/skills/{skill_name}/main.py"] + args
    print(f"\n=== Running {skill_name} ===")
    print(f"Command: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    return result.returncode

def get_series_info(series_file):
    """从series.md文件中提取系列信息"""
    import yaml
    from yaml.loader import SafeLoader

    with open(series_file, 'r') as f:
        # 读取frontmatter部分
        content = f.read()
        if '---' not in content:
            return None

        frontmatter = content.split('---')[1]
        series_info = yaml.load(frontmatter, Loader=SafeLoader)

        # 提取文章列表
        import re
        article_list = []
        article_pattern = re.compile(r'\|\s*(\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|')
        for match in article_pattern.finditer(content):
            if match.group(4).strip() in ['💡 planned', '✅ published']:
                article_list.append({
                    'number': match.group(1).strip(),
                    'title': match.group(2).strip(),
                    'core_content': match.group(3).strip(),
                    'status': match.group(4).strip(),
                    'file_path': match.group(5).strip(),
                    'publish_date': match.group(6).strip()
                })

        series_info['articles'] = article_list
        return series_info

def find_next_article(series_info):
    """找到系列中第一篇状态为planned的文章"""
    for article in series_info['articles']:
        if article['status'] == '💡 planned':
            return article
    return None

def update_series_status(series_file, article_number, file_path, publish_date):
    """更新系列文章的状态"""
    with open(series_file, 'r') as f:
        content = f.read()

    # 替换状态和文件路径
    import re
    pattern = re.compile(f'(\\|\\s*{article_number}\\s*\\|\\s*[^|]+\\|\\s*[^|]+\\|\\s*)[^|]+(\\|\\s*[^|]+\\|\\s*[^|]+\\|)')
    replacement = r'\1✅ published\2' + f'| ./{os.path.basename(file_path)} | {publish_date} |'
    new_content = pattern.sub(replacement, content)

    # 更新进度摘要
    new_content = re.sub(
        r'✅ 已完成: (\d+)/(\d+)',
        lambda m: f'✅ 已完成: {int(m.group(1)) + 1}/{m.group(2)}',
        new_content
    )

    with open(series_file, 'w') as f:
        f.write(new_content)

    print(f"\n=== Updated series status for article #{article_number} ===")

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Article Craft Orchestrator")
    parser.add_argument("--series", type=str, help="系列文件路径")
    parser.add_argument("--quick", action="store_true", help="快速模式（跳过审核和发布）")
    parser.add_argument("--draft", action="store_true", help="草稿模式（仅生成内容）")
    parser.add_argument("--upgrade", type=str, help="升级现有文章到标准模式")
    parser.add_argument("topic", nargs="?", help="文章主题")

    args = parser.parse_args(argv)

    # 系列模式
    if args.series:
        series_info = get_series_info(args.series)
        if not series_info:
            print("无法读取系列文件")
            return 1

        print(f"=== 系列: {series_info['series_name']} ===")
        print(f"总文章数: {series_info['total_articles']}")
        print(f"目标读者: {series_info['target_audience']}")

        next_article = find_next_article(series_info)
        if not next_article:
            print("没有找到待写的文章")
            return 0

        print(f"\n=== 下一篇文章: #{next_article['number']} {next_article['title']} ===")
        print(f"核心内容: {next_article['core_content']}")

        # 运行requirements技能
        if run_skill("requirements", ["--topic", next_article['title']]):
            return 1

        # 运行write技能
        article_filename = f"{next_article['number'].zfill(2)}_k8s_{next_article['title'].lower().replace(' ', '_').replace('：', '_').replace(':', '_')}.md"
        article_path = os.path.join(os.path.dirname(args.series), article_filename)
        if run_skill("write", ["--topic", next_article['title'], "--output", article_path, "--audience", series_info['target_audience'], "--style", series_info['writing_style'], "--depth", "deep-dive"]):
            return 1

        # 快速模式跳过后续步骤
        if args.quick or args.draft:
            return 0

        # 运行images技能
        if run_skill("images", [sys.argv[-1]]):
            print("警告：图片生成失败，但继续执行")

        # 运行review技能
        if run_skill("review", [sys.argv[-1]]):
            return 1

        # 运行publish技能
        if run_skill("publish", [sys.argv[-1]]):
            return 1

        # 更新系列状态
        update_series_status(
            args.series,
            next_article['number'],
            sys.argv[-1],
            "2026-03-27"  # 应该使用实际日期
        )

        print("\n=== 文章生成完成！ ===")
        print(f"文章路径: {sys.argv[-1]}")
        print(f"下一篇文章: /article-craft:series next {args.series}")

        return 0

    # 单独技能调用
    if len(sys.argv) >= 2:
        if sys.argv[1] == "requirements":
            return run_skill("requirements", sys.argv[2:])
        elif sys.argv[1] == "write":
            return run_skill("write", sys.argv[2:])
        elif sys.argv[1] == "images":
            return run_skill("images", sys.argv[2:])
        elif sys.argv[1] == "review":
            return run_skill("review", sys.argv[2:])
        elif sys.argv[1] == "publish":
            return run_skill("publish", sys.argv[2:])

    # 默认模式
    print("使用帮助: article-craft --help")
    return 0

if __name__ == "__main__":
    sys.exit(main())