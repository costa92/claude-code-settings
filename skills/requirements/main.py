#!/usr/bin/env python3
"""
Requirements Gathering Skill - 智能需求分析
"""

import os
import sys
import argparse
import re

def analyze_topic_for_style(topic):
    """从主题中分析写作风格"""
    style_markers = {
        'A': ['教程', '指南', '入门', '实战', '部署'],
        'B': ['分享', '推荐', '技巧', '隐藏', '个'],
        'C': ['原理', '源码', '架构', '设计', '底层'],
        'D': ['对比', '评测', 'vs', '选型', '哪个好'],
        'E': ['更新', '发布', '新版本', 'changelog'],
        'F': ['复盘', '踩坑', '迁移', '优化', '从.*到.*'],
        'G': ['为什么', '我认为', '不推荐', '应该']
    }

    for style, markers in style_markers.items():
        for marker in markers:
            if marker in topic:
                return style
    return 'C'  # 默认深度分析

def analyze_depth(topic):
    """从主题中分析深度"""
    if any(word in topic for word in ['快速', '简短', '入门']):
        return 'tutorial'
    if any(word in topic for word in ['深度', '详细', '全面']):
        return 'deep-dive'
    return 'deep-dive'  # 默认深度

def analyze_audience(topic):
    """从主题中分析目标读者"""
    if any(word in topic for word in ['入门', '初学者', '基础']):
        return 'beginner'
    if any(word in topic for word in ['高级', '深入', '专家']):
        return 'advanced'
    return 'advanced'  # 默认高级

def main():
    parser = argparse.ArgumentParser(description="智能需求收集技能")
    parser.add_argument("--topic", type=str, required=True, help="文章主题")
    parser.add_argument("--audience", type=str, help="目标读者 (自动识别)")
    parser.add_argument("--style", type=str, help="写作风格 (自动识别)")
    parser.add_argument("--depth", type=str, help="文章深度 (自动识别)")

    args = parser.parse_args()

    # 智能分析需求
    if not args.style:
        args.style = analyze_topic_for_style(args.topic)
    if not args.depth:
        args.depth = analyze_depth(args.topic)
    if not args.audience:
        args.audience = analyze_audience(args.topic)

    # 输出收集到的需求
    style_names = {
        'A': '技术教程', 'B': '经验分享', 'C': '深度解析',
        'D': '评测对比', 'E': '资讯快报', 'F': '项目复盘', 'G': '观点输出'
    }

    depth_names = {
        'overview': '快速概览', 'tutorial': '教程', 'deep-dive': '深度解析'
    }

    audience_names = {
        'beginner': '初级读者', 'intermediate': '中级读者', 'advanced': '高级读者'
    }

    print("## 收集到的需求")
    print(f"- 主题: {args.topic}")
    print(f"- 写作风格: {args.style} ({style_names.get(args.style, '未识别')})")
    print(f"- 目标读者: {args.audience} ({audience_names.get(args.audience, '未识别')})")
    print(f"- 深度: {args.depth} ({depth_names.get(args.depth, '未识别')})")
    print()
    print("需求收集完成，正在写入文章...")

    return 0

if __name__ == "__main__":
    sys.exit(main())
