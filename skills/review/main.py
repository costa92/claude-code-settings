#!/usr/bin/env python3
"""
Review Skill - 智能文章审查
"""

import os
import sys
import argparse
import subprocess
import re
from pathlib import Path

def run_content_reviewer(article_path, platform="wechat", quick_mode=False):
    """调用content-reviewer进行文章审查"""
    print(f"🔍 正在使用 {platform} 平台规范审查文章")

    # 检查content-reviewer是否可用
    if not Path(os.path.expanduser("~/.claude/skills/content-reviewer/main.py")).exists():
        print("❌ content-reviewer未找到，使用简化审查模式")
        return simple_review(article_path, platform, quick_mode)

    cmd = [
        sys.executable, os.path.expanduser("~/.claude/skills/content-reviewer/main.py"),
        "--article-path", article_path,
        "--platform", platform
    ]

    if quick_mode:
        cmd.append("--quick")

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True
        )

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(f"⚠️  警告: {result.stderr}")

        return result.returncode == 0

    except Exception as e:
        print(f"❌ 调用content-reviewer时发生错误: {e}")
        return simple_review(article_path, platform, quick_mode)

def simple_review(article_path, platform, quick_mode):
    """简化版审查"""
    print("📝 执行简化版文章审查")

    try:
        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()

        issues = []

        # 检查基本内容完整性
        if len(content.strip()) < 500:
            issues.append("文章内容过短")

        # 检查标题长度
        frontmatter = content.split('---')[1]
        title_match = re.search(r'title:\s*["\']?(.*?)["\']?\s*($|\n)', frontmatter)
        if title_match:
            title = title_match.group(1)
            if len(title) < 5 or len(title) > 50:
                issues.append(f"标题长度不合适: {len(title)} 字符")

        # 检查图片占位符
        image_placeholders = re.findall(r'<!-- IMAGE:.*?-->', content)
        screenshot_placeholders = re.findall(r'<!-- SCREENSHOT:.*?-->', content)

        if not quick_mode and len(image_placeholders) + len(screenshot_placeholders) == 0:
            issues.append("未发现图片内容")

        # 检查核心章节
        if not quick_mode and not re.search(r'## 核心概念|## 架构|## 实现', content):
            issues.append("缺少核心内容章节")

        if issues:
            print("⚠️  发现以下问题:")
            for issue in issues:
                print(f"  - {issue}")
            return False

        print("✅ 简化审查通过")
        return True

    except Exception as e:
        print(f"❌ 简化审查失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="智能文章审查技能")
    parser.add_argument("article_path", type=str, help="文章文件路径")
    parser.add_argument("--platform", type=str, default="wechat",
                        choices=["wechat", "zhihu", "juejin", "csdn"],
                        help="目标平台规范 (wechat/zhihu/juejin/csdn，默认: wechat)")
    parser.add_argument("--quick", action="store_true", help="快速模式 (跳过详细检查)")

    args = parser.parse_args()

    # 验证文件存在
    if not os.path.exists(args.article_path):
        print(f"❌ 文件不存在: {args.article_path}")
        return 1

    # 执行审查
    if run_content_reviewer(args.article_path, args.platform, args.quick):
        print("\n✅ 文章审查通过")
        return 0
    else:
        print("\n❌ 文章审查未通过")
        return 1

if __name__ == "__main__":
    sys.exit(main())
