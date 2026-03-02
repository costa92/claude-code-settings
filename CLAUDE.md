# Claude Code 配置与技能中心

本项目是 Claude Code 的配置仓库，包含 skills（技能）、agents（代理）、commands（命令）和 MCP 服务器配置。

## 架构概览

```
~/.claude/
├── settings.json          # 全局配置（权限、环境变量、插件）
├── agents/                # Agent 定义
│   ├── ui-engineer.md     # 前端开发 agent
│   └── content-pipeline.md # 内容流水线编排 agent
├── skills/                # Skill 定义（41 个）
│   ├── article-generator/ # 文章生成（核心）
│   ├── content-planner/   # 选题规划
│   ├── content-reviewer/  # 内容审核（6 维评分）
│   ├── content-repurposer/# 多平台分发
│   ├── content-analytics/ # 数据分析
│   ├── wechat-article-converter/ # 微信格式转换
│   ├── wechat-seo-optimizer/    # SEO 优化
│   └── ...                # 其他 skill
└── commands/              # 自定义命令
```

## 内容流水线（核心工作流）

```
content-planner → article-generator → content-reviewer → wechat-seo-optimizer
       选题              写作              审核（≥48 分）        标题/摘要优化
                                                                      ↓
content-analytics ← content-repurposer ← wechat-article-converter
     数据复盘            多平台分发           微信格式转换/上传草稿箱
```

**编排 agent**: `content-pipeline` — 当需要端到端执行时使用

## 关键约定

- **默认作者**: 月影（在 wechat-article-converter/SKILL.md 中配置）
- **图片 CDN**: jsDelivr + GitHub 后端（costa92/article-images），通过 PicGo 上传
- **图片生成**: Gemini API（nanobanana.py），必须使用绝对路径
- **微信 API**: WECHAT_APPID / WECHAT_SECRET 在 shell 环境变量中配置
- **文章质量门槛**: content-reviewer 综合评分 ≥ 48/60 方可发布

## Skill 命名规范

- Skill 目录名即为调用名：`/skill-name`
- 交叉引用时使用实际 skill 目录名，不用别名
- 例：微信转换 skill 统一叫 `wechat-article-converter`，不叫 `md2wechat`（后者是 Go 后端二进制名）
