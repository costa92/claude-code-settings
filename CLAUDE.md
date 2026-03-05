# Claude Code 配置与技能中心

本项目是 Claude Code 的配置仓库，包含 skills（技能）、agents（代理）、commands（命令）、plugins（插件）和 MCP 服务器配置。

## 架构概览

```
~/.claude/
├── settings.json          # 全局配置（权限、环境变量、插件）
├── env.json               # 共享密钥与偏好配置（gitignore，勿提交）
├── env.example.json       # env.json 模板（可提交，占位符值）
├── settings/              # 多 Provider 配置
│   ├── azure-settings.json
│   ├── openrouter-settings.json
│   ├── deepseek-settings.json
│   ├── vertex-settings.json
│   └── ...                # 其他 Provider 配置
├── agents/                # Agent 定义（2 个）
│   ├── ui-engineer.md     # 前端开发 agent
│   └── content-pipeline.md # 内容流水线编排 agent
├── skills/                # Skill 定义（44 个）
│   ├── article-generator/ # 文章生成（核心）
│   ├── content-planner/   # 选题规划
│   ├── content-reviewer/  # 内容审核（6 维评分）
│   ├── content-repurposer/# 多平台分发
│   ├── content-analytics/ # 数据分析
│   ├── content-remixer/  # 爆款拆解→创意积木→组装新内容
│   ├── wechat-article-converter/ # 微信格式转换
│   ├── wechat-seo-optimizer/    # SEO 优化
│   ├── code-review/       # 代码审查中枢
│   ├── vercel-deploy-claimable/ # Vercel 部署
│   └── ...                # 其他 skill
├── commands/              # 自定义命令
│   ├── cc/                # Claude Code 相关命令
│   ├── gh/                # GitHub 相关命令
│   ├── eureka.md          # 技术突破记录
│   ├── think-harder.md    # 增强分析思考
│   ├── think-ultra.md     # 超深度分析思考
│   ├── reflection.md      # 会话分析改进
│   ├── reflection-harder.md # 综合会话分析
│   └── translate.md       # 翻译
├── plugins/               # 已安装插件
│   ├── autonomous-skill/
│   ├── codex-skill/
│   ├── kiro-skill/
│   ├── nanobanana-skill/
│   ├── spec-kit-skill/
│   ├── youtube-transcribe-skill/
│   └── installed_plugins.json
├── scripts/               # 共享工具脚本
│   ├── load_env.sh        # Shell: source 后导出 env.json 为环境变量
│   └── load_env.py        # Python: from load_env import load_env
├── guidances/             # 指导文件
├── plans/                 # 计划文件
└── projects/              # 项目级配置与记忆
```

## 已启用的插件

| 插件 | 来源 | 说明 |
|------|------|------|
| superpowers | superpowers-marketplace | 开发工作流增强（TDD、调试、计划、代码审查等） |
| n8n-mcp-skills | n8n-mcp-skills | n8n 自动化工作流技能集 |
| kiro-skill | claude-code-settings | 交互式需求驱动开发 |
| ralph-wiggum | claude-code-plugins | Ralph Wiggum 循环技术 |

## 内容流水线（核心工作流）

```
content-planner → article-generator → content-reviewer → wechat-seo-optimizer
       选题              写作              审核（≥49 分）        标题/摘要优化
                                                                      ↓
content-analytics ← content-repurposer ← wechat-article-converter
     数据复盘            多平台分发           微信格式转换/上传草稿箱
```

**编排 agent**: `content-pipeline` — 当需要端到端执行时使用

## 关键约定

- **统一配置中心**: `~/.claude/env.json`（gitignore），模板为 `env.example.json`（可提交）
  - 所有 API Key（Gemini、OpenAI、WeChat、N8N 等）统一存放于此
  - skill 偏好参数（digest_*）也存于此文件
  - skill 读取配置时优先从 env.json 获取，避免重复询问用户
  - **Shell 脚本**: `source ~/.claude/scripts/load_env.sh` 自动导出为环境变量
  - **Python 脚本**: 直接读取 env.json，或 `sys.path.insert(0, os.path.expanduser("~/.claude/scripts")); from load_env import load_env`
  - 配置优先级: 环境变量 > env.json > 旧的散落配置文件（~/.nanobanana.env 等，兼容但不推荐）
- **默认作者**: 月影（在 wechat-article-converter/SKILL.md 中配置）
- **图片 CDN**: jsDelivr + GitHub 后端（costa92/article-images），通过 PicGo 上传
- **图片生成**: Gemini API（nanobanana.py），必须使用绝对路径
- **微信 API**: WECHAT_APPID / WECHAT_SECRET 统一在 env.json 中配置（wechat_appid / wechat_secret），Shell 使用 `source ~/.claude/scripts/load_env.sh` 导出
- **文章质量门槛**: content-reviewer 综合评分 ≥ 55/70 方可发布；未达标自动修改（最多 3 轮）
- **API 代理**: 本地代理 `http://127.0.0.1:5000`，通过 ANTHROPIC_BASE_URL 配置

## MCP 工具降级链

| 需求 | 首选 | 降级 |
|------|------|------|
| 网页搜索 | mcp__web-search-prime | WebSearch |
| 网页读取 | mcp__web-reader | WebFetch → defuddle |
| 文档查询 | mcp__context7 | WebFetch |
| GitHub 仓库 | mcp__zread | gh CLI |
| 思维链 | mcp__sequential-thinking-server | think-harder/think-ultra 命令 |

## Skill 命名规范

- Skill 目录名即为调用名：`/skill-name`
- 交叉引用时使用实际 skill 目录名，不用别名
- 例：微信转换 skill 统一叫 `wechat-article-converter`，不叫 `md2wechat`（后者是 Go 后端二进制名）
- 插件提供的 skill 使用 `插件名:skill名` 格式调用，如 `superpowers:brainstorming`
