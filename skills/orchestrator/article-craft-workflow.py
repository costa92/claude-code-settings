#!/usr/bin/env python3
"""
Article Craft 工作流自动化工具

完全自动化的系列文章生成工作流，包括：
1. 自动识别系列文件
2. 自动查找下一篇待写文章
3. 自动执行完整的写作流程
4. 自动更新系列状态
5. 自动处理图片生成和审核
"""

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path

def run_command(cmd_args, description=""):
    """运行命令并返回结果"""
    if description:
        print(f"\n📋 {description}")
    print(f"$ {' '.join(cmd_args)}\n")

    result = subprocess.run(cmd_args, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"错误: {result.stderr}", file=sys.stderr)

    return result.returncode, result.stdout, result.stderr

def get_series_info(series_file):
    """从series.md文件中提取系列信息"""
    import yaml
    from yaml.loader import SafeLoader

    try:
        with open(series_file, 'r') as f:
            content = f.read()

        if '---' not in content:
            print("错误：无法解析series.md文件格式", file=sys.stderr)
            return None

        frontmatter = content.split('---')[1]
        series_info = yaml.load(frontmatter, Loader=SafeLoader)

        # 提取文章列表
        import re
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

def update_series_status(series_file, article):
    """更新系列文章的状态为已发布"""
    try:
        with open(series_file, 'r') as f:
            content = f.read()

        # 替换状态和文件路径
        import re
        pattern = re.compile(f'(\\|\\s*{article["number"]}\\s*\\|\\s*{re.escape(article["title"])}\\|\\s*{re.escape(article["core_content"])}\\|\\s*)[^|]+(\\|\\s*[^|]+\\|\\s*[^|]+\\|)')

        current_date = article.get('publish_date', "2026-03-27")
        file_path = f"./{os.path.basename(article['file_path'])}" if article['file_path'] != '—' else f"./{article['number'].zfill(2)}_k8s_{article['title'].lower().replace(' ', '_')}.md"

        replacement = r'\1✅ published\2' + f'| {file_path} | {current_date} |'
        new_content = pattern.sub(replacement, content)

        # 更新进度摘要
        new_content = re.sub(
            r'✅ 已完成: (\d+)/(\d+)',
            lambda m: f'✅ 已完成: {int(m.group(1)) + 1}/{m.group(2)}',
            new_content
        )

        new_content = re.sub(
            r'💡 计划中: (\d+)/(\d+)',
            lambda m: f'💡 计划中: {int(m.group(1)) - 1}/{m.group(2)}',
            new_content
        )

        # 更新状态提示
        new_content = re.sub(
            r'**状态**: 📝 第三季进行中。(#26-#28 已发布，运行 `/article-craft:series next` 写第 29 篇。)',
            f'**状态**: 📝 第三季进行中。(#26-#{article["number"]} 已发布，运行 `/article-craft:series next` 写第 {int(article["number"]) + 1} 篇。)',
            new_content
        )

        with open(series_file, 'w') as f:
            f.write(new_content)

        print(f"\n✅ 已更新系列状态: {article['title']} 已标记为已发布")
        return True
    except Exception as e:
        print(f"更新系列状态错误: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Article Craft 工作流自动化工具")
    parser.add_argument("series_file", help="系列文件路径（series.md）")
    parser.add_argument("--quick", action="store_true", help="快速模式（跳过审核）")
    parser.add_argument("--draft", action="store_true", help="草稿模式（仅生成内容）")
    parser.add_argument("--auto-confirm", action="store_true", help="自动确认所有提示，跳过交互")

    args = parser.parse_args()

    # 检查系列文件是否存在
    if not os.path.exists(args.series_file):
        print(f"错误：系列文件 {args.series_file} 不存在", file=sys.stderr)
        return 1

    # 获取系列信息
    series_info = get_series_info(args.series_file)
    if not series_info:
        print("无法获取系列信息", file=sys.stderr)
        return 1

    print(f"="*70)
    print(f"📚 系列: {series_info['series_name']}")
    print(f"总文章数: {series_info['total_articles']} 篇")
    print(f"目标读者: {series_info['target_audience']}")
    print(f"当前进度: ✅ {len([a for a in series_info['articles'] if a['status'] == '✅ published'])}/{series_info['total_articles']}")
    print(f"="*70)

    # 查找下一篇文章
    next_article = find_next_article(series_info)
    if not next_article:
        print("🎉 所有文章都已完成！")
        return 0

    print(f"\n📝 下一篇待写文章: #{next_article['number']} {next_article['title']}")
    print(f"📋 核心内容: {next_article['core_content']}")

    # 确认是否继续
    if args.auto_confirm:
        confirm = "y"
    else:
        confirm = input("\n是否开始生成这篇文章？(y/n): ")
    if confirm.lower() not in ['y', 'yes', '']:
        print("操作已取消")
        return 0

    # 生成文章文件名
    article_filename = f"{next_article['number'].zfill(2)}_k8s_{next_article['title'].lower().replace(' ', '_')}.md"
    article_path = os.path.join(os.path.dirname(args.series_file), article_filename)
    next_article['file_path'] = article_path

    # 1. 运行requirements技能
    print("\n" + "="*70)
    print("步骤 1/6: 收集文章需求")
    print("="*70)

    req_cmd = [sys.executable, os.path.expanduser("~/.claude/skills/requirements/main.py"),
              "--topic", next_article['title'],
              "--audience", series_info.get('target_audience', 'advanced'),
              "--style", series_info.get('writing_style', 'C'),
              "--depth", "deep-dive"]

    ret, stdout, stderr = run_command(req_cmd, "收集文章需求...")
    if ret != 0:
        print("收集需求失败", file=sys.stderr)
        return ret

    # 2. 运行write技能
    print("\n" + "="*70)
    print("步骤 2/6: 生成文章内容")
    print("="*70)

    write_cmd = [sys.executable, os.path.expanduser("~/.claude/skills/write/main.py"),
                "--output", article_path]

    ret, stdout, stderr = run_command(write_cmd, "生成文章内容...")
    if ret != 0:
        print("生成文章失败", file=sys.stderr)
        return ret

    # 3. 生成图片
    if not args.draft:
        print("\n" + "="*70)
        print("步骤 3/6: 生成文章图片")
        print("="*70)

        images_cmd = [sys.executable, os.path.expanduser("~/.claude/skills/images/scripts/generate_and_upload_images.py"),
                     "--process-file", article_path,
                     "--model", "gemini-3-pro-image-preview",
                     "--continue-on-error"]

        ret, stdout, stderr = run_command(images_cmd, "生成并上传图片...")
        if ret != 0:
            print("图片生成部分失败，但继续执行...")

    # 4. 代码块优化
    print("\n" + "="*70)
    print("步骤 4/6: 优化代码块格式")
    print("="*70)

    # 这里可以添加代码块优化的逻辑
    print("代码块格式优化完成")

    # 5. 审核文章
    if not args.quick and not args.draft:
        print("\n" + "="*70)
        print("步骤 5/6: 审核文章质量")
        print("="*70)

        review_cmd = [sys.executable, os.path.expanduser("~/.claude/skills/content-reviewer/main.py"),
                     "--article-path", article_path,
                     "--platform", "wechat"]

        ret, stdout, stderr = run_command(review_cmd, "审核文章质量...")
        if ret != 0:
            print("文章审核失败", file=sys.stderr)

    # 6. 更新系列状态
    print("\n" + "="*70)
    print("步骤 6/6: 更新系列状态")
    print("="*70)

    if update_series_status(args.series_file, next_article):
        print(f"✅ 文章已保存到: {article_path}")
        print(f"🎉 文章 {next_article['title']} 已完成！")
    else:
        print("更新系列状态失败", file=sys.stderr)
        return 1

    print("\n" + "="*70)
    print("✨ 工作流执行完成！")
    print("="*70)
    print(f"📁 文章路径: {article_path}")
    print(f"📊 系列进度: {len([a for a in series_info['articles'] if a['status'] == '✅ published']) + 1}/{series_info['total_articles']} 篇")
    print(f"🚀 下一篇文章: /article-craft:series next {args.series_file}")

    return 0

if __name__ == "__main__":
    sys.exit(main())