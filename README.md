# Claude Code Settings/Commands/Skills for Vibe Coding

A curated collection of Claude Code settings, custom commands, skills and sub-agents designed for enhanced development workflows. This setup includes specialized commands, skills and subagents for feature development (spec-driven workflow), code analysis, GitHub integration, and knowledge management.

> For OpenAI Codex settings, configurations and custom prompts, please refer [feiskyer/codex-settings](https://github.com/feiskyer/codex-settings).

## Setup

### Using Claude Code Plugin

```sh
/plugin marketplace add feiskyer/claude-code-settings

# Install main plugin (commands, agents and skills)
/plugin install claude-code-settings

# Alternatively, install individual skills without commands/agents
/plugin install codex-skill               # Codex automation
/plugin install autonomous-skill          # Long-running task automation
/plugin install nanobanana-skill          # Image generation
/plugin install kiro-skill                # Kiro workflow
/plugin install spec-kit-skill            # Spec-Kit workflow
/plugin install youtube-transcribe-skill  # YouTube transcript extraction
```

Alternatively, run a one-command installation via the [Claude Plugins CLI](https://claude-plugins.dev) to skip the marketplace setup:

```bash
npx claude-plugins install @feiskyer/claude-code-settings/claude-code-settings
```

This automatically adds the marketplace and installs the plugin in a single step.

**Note:**

- [~/.claude/settings.json](settings.json) is not configured via Claude Code Plugin, you'd need to configure it manually.

### Manual Setup

```sh
# Backup original claude settings
mv ~/.claude ~/.claude.bak

# Clone the claude-code-settings
git clone https://github.com/feiskyer/claude-code-settings.git ~/.claude

# Install LiteLLM proxy
pip install -U 'litellm[proxy]'

# Start litellm proxy (which would listen on http://0.0.0.0:4000)
litellm -c ~/.claude/guidances/litellm_config.yaml

# For convenience, run litellm proxy in background with tmux
# tmux new-session -d -s copilot 'litellm -c guidances/litellm_config.yaml'
```

Once started, you'll see:

```sh
...
Please visit https://github.com/login/device and enter code XXXX-XXXX to authenticate.
...
```

Open the link, log in and authenticate your GitHub Copilot account.

**Note:**

1. The default configuration is leveraging [LiteLLM Proxy Server](https://docs.litellm.ai/docs/simple_proxy) as LLM gateway to GitHub Copilot. You can also use [copilot-api](https://github.com/ericc-ch/copilot-api) as the proxy as well (remember to change your port to 4141).
2. Make sure the following models are available in your account; if not, replace them with your own model names:

   - ANTHROPIC_DEFAULT_SONNET_MODEL: claude-sonnet-4.5

   - ANTHROPIC_DEFAULT_OPUS_MODEL: claude-opus-4

   - ANTHROPIC_DEFAULT_HAIKU_MODEL: gpt-5-mini

### Quick Start: MCP Configuration

To enable MCP servers, create `~/.claude/.mcp.json`:

```bash
cat > ~/.claude/.mcp.json << 'EOF'
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "type": "stdio"
    }
  }
}
EOF
```

See [MCP Servers Configuration](#mcp-servers-configuration) section for detailed setup and available servers.

## Commands

The `commands/` directory contains [custom slash commands](https://code.claude.com/docs/en/slash-commands) that extend Claude Code's slash commands, which could be invoked via `/<command-name> [arguments]`.

<details>
<summary>Analysis & Reflection</summary>

### Analysis & Reflection

- `/think-harder [problem]` - Enhanced analytical thinking
- `/think-ultra [complex problem]` - Ultra-comprehensive analysis
- `/reflection` - Analyze and improve Claude Code instructions
- `/reflection-harder` - Comprehensive session analysis and learning
- `/eureka [breakthrough]` - Document technical breakthroughs

</details>

<details>
<summary>GitHub Integration</summary>

### GitHub Integration

- `/gh:review-pr [PR_NUMBER]` - Comprehensive PR review and comments
- `/gh:fix-issue [issue-number]` - Complete issue resolution workflow

</details>

<details>
<summary>Documentation & Knowledge</summary>

### Documentation & Knowledge

- `/cc:create-command [name] [description]` - Create new Claude Code commands

</details>

<details>
<summary>Utilities</summary>

### Utilities

- `/translate [text]` - Translate English/Japanese tech content to Chinese

</details>

## Skills

Skills are now distributed as separate plugins for modular installation. Install only what you need:

<details>
<summary>codex-skill - Handoff tasks to OpenAI Codex/GPT</summary>

### [codex-skill](plugins/codex-skill)

Non-interactive automation mode for hands-off task execution using OpenAI Codex/GPT models. Use when you want to leverage gpt-5, gpt-5.2, or codex to implement features or plans designed by Claude.

**Triggered by**: "codex", "use gpt", "gpt-5", "gpt-5.2", "let openai", "full-auto", "用codex", "让gpt实现"

**Installation:**

```sh
/plugin marketplace add feiskyer/claude-code-settings
/plugin install codex-skill
```

**Key Features:**

- Multiple execution modes (read-only, workspace-write, danger-full-access)
- Model selection support (gpt-5, gpt-5.2, gpt-5.2-codex, etc.)
- Autonomous execution without approval prompts
- JSON output support for structured results
- Resumable sessions

**Requirements:** Codex CLI installed (`npm i -g @openai/codex` or `brew install codex`)

</details>

<details>
<summary>autonomous-skill - Long-running task automation</summary>

### [autonomous-skill](plugins/autonomous-skill)

Execute complex, long-running tasks across multiple sessions using a dual-agent pattern (Initializer + Executor) with automatic session continuation.

**Triggered by**: "autonomous", "long-running task", "multi-session", "自主执行", "长时任务", "autonomous skill"

**Installation:**

```sh
/plugin marketplace add feiskyer/claude-code-settings
/plugin install autonomous-skill
```

**Key Features:**

- Dual-agent pattern (Initializer creates a task list, Executor completes tasks)
- Auto-continuation across sessions with progress tracking
- Task isolation with per-task directories (`.autonomous/<task-name>/`)
- Progress persistence via `task_list.md` and `progress.md`
- Headless mode execution using Claude CLI

**Usage:**

```text
You: "Please use autonomous skill to build a REST API for a todo app"
Claude: [Creates .autonomous/build-rest-api-todo/, initializes task list, starts execution]
```

**Requirements:** Claude CLI installed

</details>

<details>
<summary>nanobanana-skill - AI image generation with Google Gemini</summary>

### [nanobanana-skill](plugins/nanobanana-skill)

Generate or edit images using Google Gemini API via nanobanana. Use when creating, generating, or editing images.

**Triggered by**: "nanobanana", "generate image", "create image", "edit image", "AI drawing", "图片生成", "AI绘图", "图片编辑", "生成图片"

**Installation:**

```sh
/plugin marketplace add feiskyer/claude-code-settings
/plugin install nanobanana-skill
```

**Key Features:**

- Image generation with various aspect ratios
- Image editing capabilities
- Multiple model options (gemini-3-pro-image-preview, gemini-2.5-flash-image)
- Resolution options (1K, 2K, 4K)
- Support for various aspect ratios (square, portrait, landscape, ultra-wide)

**Requirements:**

- GEMINI_API_KEY configured in `~/.nanobanana.env`
- Python3 with google-genai, Pillow, python-dotenv (install via `pip install -r requirements.txt` in the plugin directory)

</details>

<details>
<summary>youtube-transcribe-skill - Extract YouTube subtitles</summary>

### [youtube-transcribe-skill](plugins/youtube-transcribe-skill)

Extract subtitles/transcripts from a YouTube video link.

**Triggered by**: "youtube transcript", "extract subtitles", "video captions", "视频字幕", "字幕提取", "YouTube转文字", "提取字幕"

**Installation:**

```sh
/plugin marketplace add feiskyer/claude-code-settings
/plugin install youtube-transcribe-skill
```

**Key Features:**

- Dual extraction methods: CLI (fast) and Browser Automation (fallback)
- Automatic subtitle language selection (zh-Hans, zh-Hant, en)
- Efficient DOM-based extraction for browser method
- Saves transcripts to local text files

**Requirements:**

- `yt-dlp` (for CLI method)
- or `chrome-devtools-mcp` (for browser automation method)

</details>

<details>
<summary>kiro-skill - Interactive spec-driven feature development</summary>

### [kiro-skill](plugins/kiro-skill)

Interactive feature development workflow from idea to implementation with EARS requirements, design documents, and task lists.

**Triggered by**: "kiro", ".kiro/specs/", "feature spec", "需求文档", "设计文档", "实现计划"

**Installation:**

```sh
/plugin marketplace add feiskyer/claude-code-settings
/plugin install kiro-skill
```

**Workflow**:

1. **Requirements** → Define what needs to be built (EARS format with user stories)
2. **Design** → Determine how to build it (architecture, components, data models)
3. **Tasks** → Create actionable implementation steps (test-driven, incremental)
4. **Execute** → Implement tasks one at a time

**Storage**: Creates files in `.kiro/specs/{feature-name}/` directory

**Usage**:

```text
You: "I need to create a kiro feature spec for user authentication"
Claude: [Automatically uses kiro-skill]
```

</details>

<details>
<summary>spec-kit-skill - Constitution-based spec-driven development</summary>

### [spec-kit-skill](plugins/spec-kit-skill)

GitHub Spec-Kit integration for constitution-based spec-driven development with 7-phase workflow.

**Triggered by**: "spec-kit", "speckit", "constitution", "specify", ".specify/", "规格驱动开发", "需求规格"

**Installation:**

```sh
/plugin marketplace add feiskyer/claude-code-settings
/plugin install spec-kit-skill
```

**Prerequisites**:

```sh
# Install spec-kit CLI
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# Initialize project
specify init . --ai claude
```

**7-Phase Workflow**:

1. **Constitution** → Establish governing principles
2. **Specify** → Define functional requirements
3. **Clarify** → Resolve ambiguities (max 5 questions)
4. **Plan** → Create technical strategy
5. **Tasks** → Generate dependency-ordered tasks
6. **Analyze** → Validate consistency (read-only)
7. **Implement** → Execute implementation

**Storage**: Creates files in `.specify/specs/NNN-feature-name/` directory

**Usage**:

```text
You: "Let's create a constitution for this project"
Claude: [Automatically uses spec-kit-skill, detects CLI, guides through phases]
```

</details>

<details>
<summary>n8n-workflow-patterns - Proven n8n workflow patterns</summary>

### [n8n-workflow-patterns](skills/n8n-workflow-patterns)

Proven architectural patterns for building n8n workflows, covering the 5 most common workflow types.

**Triggered by**: "workflow pattern", "n8n pattern", "webhook processing", "http api", "database sync", "ai agent", "scheduled task", "workflow architecture"

**Installation:**

This skill is located in the `skills/` directory and is automatically available when using this repository setup.

**The 5 Core Patterns:**

1. **Webhook Processing** (Most Common - 35% of workflows)
   - Receive HTTP requests → Process → Respond
   - Pattern: Webhook → Validate → Transform → Respond/Notify

2. **HTTP API Integration** (892+ templates)
   - Fetch from REST APIs → Transform → Store/Use
   - Pattern: Trigger → HTTP Request → Transform → Action → Error Handler

3. **Database Operations** (456+ templates)
   - Read/Write/Sync database data
   - Pattern: Schedule → Query → Transform → Write → Verify

4. **AI Agent Workflow** (234+ templates, 270 AI nodes)
   - AI agents with tools and memory
   - Pattern: Trigger → AI Agent (Model + Tools + Memory) → Output

5. **Scheduled Tasks** (28% of workflows)
   - Recurring automation workflows
   - Pattern: Schedule → Fetch → Process → Deliver → Log

**Key Features:**

- Complete workflow creation checklist
- Common gotchas and solutions
- Data flow patterns (linear, branching, parallel, loops)
- Error handling strategies
- Integration with n8n MCP tools

**Files:**

- `SKILL.md` - Pattern overview and selection guide
- `webhook_processing.md` - Webhook patterns and data structure
- `http_api_integration.md` - REST APIs, pagination, rate limiting
- `database_operations.md` - DB operations, batch processing, security
- `ai_agent_workflow.md` - AI agents, tools, memory, connections
- `scheduled_tasks.md` - Cron schedules, timezone, monitoring

**Usage:**

```text
You: "How do I build a webhook workflow that processes Stripe payments?"
Claude: [Uses n8n-workflow-patterns to guide you through webhook processing pattern]
```

**Requirements:** n8n-mcp MCP server configured for n8n API access

</details>

### Content Creation Pipeline (WeChat / Blog)

A full-cycle content production pipeline from topic planning to multi-platform distribution, designed for WeChat Official Account and technical blog workflows.

```
选题 → 大纲 → 写作 → 审查 → SEO优化 → 排版转换 → 发布 → 数据分析 → 多平台分发
```

| Stage | Skill / Agent | Trigger | Output |
|-------|--------------|---------|--------|
| 1. 选题 | `content-planner` | `/content-planner` | 选题库 + 内容日历 + 排期 |
| 2. 大纲 | `article-outline-agent` | 写作前自动触发 | 读者画像 + 论点 + 结构 |
| 3. 写作 | `article-generator` | `/article-generator` | Markdown 技术博文 + 配图 |
| 4. 审查 | `content-reviewer` | 写作后自动触发 | 6 维评分 + 修改清单 |
| 5. SEO | `wechat-seo-optimizer` | `/wechat-seo-optimizer` | 标题/摘要/关键词优化 |
| 6. 排版 | `wechat-article-converter` | `/wechat-article-converter` | 微信公众号 HTML |
| 7. 数据 | `content-analytics` | `/content-analytics` | 阅读/互动/增长分析 |
| 8. 分发 | `content-repurposer` | `/content-repurposer` | 小红书/Twitter/短视频/Newsletter/知乎 |

**Quick Start — Write a single article:**

```text
# Simplest path: one command to generate an article
You: /article-generator 写一篇关于 Docker 多阶段构建优化的技术博文

# Full pipeline: step by step
You: /content-planner                        # Step 1: plan topics
You: 我选了 Docker 多阶段构建这个选题            # Step 2: outline (auto)
You: /article-generator 根据大纲写作            # Step 3: write
You: 文章写好了，帮我审查一下                     # Step 4: review (auto)
You: /wechat-seo-optimizer 优化标题和摘要        # Step 5: SEO
You: /wechat-article-converter 转换为微信格式     # Step 6: format
You: /content-repurposer 一鱼多吃转成小红书和Twitter  # Step 7: repurpose
```

<details>
<summary>📖 Complete Example: "MCP 协议入门" from zero to published</summary>

#### End-to-End Walkthrough

> Scenario: Write an article about Model Context Protocol (MCP) for your WeChat Official Account, then repurpose it to Xiaohongshu and Twitter.

**Step 1 — 选题规划** (`content-planner`)

```text
You: /content-planner 我的公众号定位是 AI 工程化，目标读者是有 1-3 年经验的开发者，
     帮我围绕 MCP 协议做一期选题规划
```

Claude will ask clarifying questions (publish frequency, existing series, etc.), then output:

```
📋 选题库 (3 topics generated)
┌─────────────────────────────────┬────────┬──────┬──────┐
│ Topic                           │ Quadrant│ Priority│ Type │
├─────────────────────────────────┼────────┼──────┼──────┤
│ MCP 协议入门：5 分钟理解 AI 的  │ 爆款区 │  P0   │ 教程 │
│ "USB 接口"                      │        │       │      │
│ 手把手搭建你的第一个 MCP Server │ 口碑区 │  P1   │ 实战 │
│ MCP vs Function Calling 深度对比│ 口碑区 │  P1   │ 解析 │
└─────────────────────────────────┴────────┴──────┴──────┘

📅 建议排期
  Week 1 (周二 20:00): MCP 协议入门    ← 本次写这篇
  Week 2 (周四 20:00): 搭建 MCP Server
  Week 3 (周二 20:00): MCP vs Function Calling
```

**Step 2 — 生成大纲** (`article-outline-agent`)

```text
You: 我选 P0 那篇 "MCP 协议入门"，帮我出大纲
```

Claude auto-activates outline agent, outputs:

```
👤 读者画像: 1-3 年经验后端/全栈开发者，听过 MCP 但没用过
🎯 核心论点: MCP 是 AI 应用的标准化工具接口，就像 USB 统一了外设接口
📐 结构模板: C 教程实战型（结果预览 → 前置知识 → 逐步讲解 → 避坑 → 代码）

大纲:
  1. Hook: 你还在为每个 AI 应用单独写 API 适配层吗？(~150 字)
  2. 什么是 MCP：一句话 + USB 类比图 (~300 字)
  3. 核心概念拆解：Server / Client / Tool / Resource (~600 字)
  4. 5 分钟上手：用 TypeScript 写一个天气查询 MCP Server (~800 字)
  5. 实战避坑：3 个新手常踩的坑 (~400 字)
  6. MCP 生态现状 + 下期预告 (~200 字)

📎 素材清单: 官方 spec 文档, TypeScript SDK README, 架构图(需生成)
```

**Step 3 — 写作** (`article-generator`)

```text
You: /article-generator 根据上面的大纲写作，参考 MCP 官方文档，
     生成一张架构示意图
```

Claude writes `mcp-intro.md` (~2500 words) with:
- YAML frontmatter (title, tags, date)
- Code examples (TypeScript MCP Server)
- Gemini-generated architecture diagram auto-uploaded to CDN
- Obsidian callouts for tips/warnings

**Step 4 — 审查** (`content-reviewer`)

```text
You: 文章写好了，帮我审查一下
```

Output:

```
📊 审查评分
  可读性:     8/10  ✅ 段落节奏好，有一处长句建议拆分 (L47)
  逻辑连贯性: 9/10  ✅ 论证链完整
  标题与Hook: 7/10  ⚠️ 标题偏平，建议用数字锚点公式
  事实准确性: 9/10  ✅ 代码已验证，SDK 版本号正确
  AI 痕迹:    8/10  ✅ 未发现红旗词，第 3 节 "接下来让我们" 建议改为具体动作
  平台适配:   8/10  ✅ 字数合适，代码块长度 OK

📋 修改清单 (3 items):
  1. L47: 拆分 52 字长句
  2. L12: 标题考虑加数字 → "5 分钟搞懂 MCP：AI 应用的 USB 接口"
  3. L78: "接下来让我们看看" → "打开编辑器，新建 server.ts"

🟢 Verdict: ⚠️ 修改后可发布
```

**Step 5 — SEO 优化** (`wechat-seo-optimizer`)

```text
You: /wechat-seo-optimizer 帮我优化标题和摘要
```

Output:

```
🏷️ 标题方案 (5 options)
  ⭐⭐⭐⭐⭐ "5 分钟搞懂 MCP 协议：AI 应用的 USB 接口"      [数字锚点+类比]
  ⭐⭐⭐⭐   "还在给每个 AI 单独写适配层？MCP 一招搞定"       [痛点直击]
  ⭐⭐⭐⭐   "MCP 协议入门：为什么大厂都在用这个 AI 标准"      [身份锚定]
  ⭐⭐⭐     "从 0 到 1 搭建 MCP Server，附完整代码"          [教程承诺]
  ⭐⭐⭐     "Function Calling 的终结者？聊聊 MCP 协议"        [悬念缺口]

📝 摘要 (108 chars)
  "MCP 让 AI 应用像 USB 一样即插即用。本文用一个天气查询案例，
   带你 5 分钟从概念到代码跑通第一个 MCP Server。"

🔑 关键词: MCP协议, Model Context Protocol, AI工具调用, MCP Server, Claude MCP
   核心词密度: 2.1% ✅
```

**Step 6 — 排版转换** (`wechat-article-converter`)

```text
You: /wechat-article-converter 用 Tech 主题转换 mcp-intro.md
```

Claude asks theme confirmation via interactive dialog, then:

```
✅ 转换完成: mcp-intro-wechat.html (Tech 主题)
🌐 预览服务器已启动: http://localhost:8080/preview
   请在浏览器中检查排版效果

💡 下一步:
   - 满意后复制 HTML 粘贴到微信编辑器
   - 或使用 --draft 直接推送到草稿箱
```

**Step 7 — 多平台分发** (`content-repurposer`)

```text
You: /content-repurposer 把这篇文章转成小红书和 Twitter thread
```

Claude generates two files:

```
📁 Output:
  mcp-intro-xiaohongshu.md
    "🔥 AI 开发者必知的 MCP 协议 | 5分钟入门指南
     还在为每个AI应用写适配代码？MCP协议就是AI界的USB接口..."
    #MCP协议 #AI开发 #Claude #大模型工具调用 ...

  mcp-intro-twitter-thread.md
    1/ MCP (Model Context Protocol) is the USB port for AI apps.
       Instead of writing custom adapters for every tool, you write ONE MCP server.
       Here's a 5-min crash course 🧵
    2/ The core idea: Server exposes Tools + Resources...
    ...
    8/ Full code + article (Chinese): [link]
       If you build AI apps, MCP is worth learning today. 🚀
```

#### File Tree After Full Pipeline

```
~/articles/mcp-intro/
├── mcp-intro.md                    # 原始 Markdown (Step 3)
├── images/
│   └── mcp-architecture.png        # AI 生成架构图 (Step 3)
├── mcp-intro-wechat.html           # 微信排版 (Step 6)
├── mcp-intro-xiaohongshu.md        # 小红书 (Step 7)
└── mcp-intro-twitter-thread.md     # Twitter (Step 7)
```

</details>

<details>
<summary>content-planner - Topic planning & editorial calendar</summary>

### [content-planner](skills/content-planner)

Plan content topics, manage editorial calendar, and build a content pipeline for WeChat Official Account and other platforms.

**Triggered by**: "选题", "内容规划", "内容日历", "发布计划", "content plan", "editorial calendar", "选题库", "内容排期"

**Key Features:**

- Topic library with 8 sourcing channels (trending, pain points, competitor analysis, etc.)
- Topic quadrant evaluation (utility × virality → 爆款区/口碑区/话题区/填充区)
- Monthly content calendar with publish time recommendations
- Pipeline kanban: Backlog → In Progress → Review → Done
- Series article planning with cross-promotion design

</details>

<details>
<summary>article-generator - Technical blog article writing</summary>

### [article-generator](skills/article-generator)

Generate technical blog articles with authentic, non-AI style. Outputs Markdown with YAML frontmatter, Obsidian callouts, code examples, and CDN images.

**Triggered by**: `/article-generator`, "写一篇文章", "写一篇关于...的文章"

**Key Features:**

- Anti-AI-style enforcement (no marketing language, no fake engagement)
- Image generation via Gemini API (1K/2K/4K) + auto-upload to PicGo/S3
- Content depth: >2000 words, must include real-world case study
- Pre-writing verification: all technical content verified via official docs
- Trusted tools whitelist (Docker, K8s, Git, Python, Go, etc.) skips web verification

**Requirements:**

- Python: `pip install -r skills/article-generator/requirements.txt`
- `GEMINI_API_KEY` env var for image generation (optional)
- PicGo or S3/R2 config for image hosting (optional)

</details>

<details>
<summary>wechat-seo-optimizer - Title, keyword & abstract optimization</summary>

### [wechat-seo-optimizer](skills/wechat-seo-optimizer)

Optimize WeChat article titles, abstracts, and keywords for maximum reach.

**Triggered by**: "标题优化", "SEO", "取标题", "提高阅读量", "title optimization"

**Key Features:**

- Generates 5 title options using 8 proven formulas (数字锚点, 悬念缺口, 痛点直击, etc.)
- Title checklist: 15-25 chars, must include core keyword, no clickbait
- Abstract optimization: ≤120 chars, 4 strategy types
- Keyword density analysis (1-3%) with long-tail suggestions
- Cover image guidance (900×383px headline / 200×200px secondary)
- Publish time recommendations by article type

</details>

<details>
<summary>wechat-article-converter - Markdown → WeChat HTML conversion</summary>

### [wechat-article-converter](skills/wechat-article-converter)

Convert Markdown articles to WeChat Official Account compatible HTML with theme selection, preview, and draft upload.

**Triggered by**: "转换为微信格式", "去除AI痕迹", "生成封面图", `/wechat-article-converter`

**Key Features:**

- **Python engine** (7 themes): Coffee, Tech, Warm, Simple, MD2 Classic/Dark/Purple
- **Go backend** (9 themes + AI themes): additional features below
- Draft box upload: push directly to WeChat draft box
- AI image generation for cover images
- Writing assistant with creator styles (Dan Koe, etc.)
- AI trace removal / Humanizer (24 pattern detection, 3 intensity levels)
- Batch conversion + local preview server

**Requirements (Python):** `pip install markdown premailer pygments beautifulsoup4 lxml cssutils`
**Requirements (Go backend):** auto-downloads binary; `WECHAT_APPID` + `WECHAT_SECRET` for draft upload

</details>

<details>
<summary>content-analytics - WeChat article performance analysis</summary>

### [content-analytics](skills/content-analytics)

Analyze WeChat Official Account article performance data from exported CSV/Excel files.

**Triggered by**: "数据分析", "文章数据", "阅读量分析", "粉丝分析", "公众号数据", "content analytics"

**Key Features:**

- 6 analysis modules: performance overview, content effectiveness, time patterns, reader behavior, growth analysis, competitiveness diagnosis
- Code-computed metrics (never estimated) with Python calculation
- Visualizations: line/bar/heatmap/pie/scatter charts saved as PNG
- 6-dimension health score (read trend, engagement, consistency, loyalty, virality, search value)
- Actionable strategy recommendations (immediate / short-term / long-term)

**Requirements:** User exports data from WeChat backend (CSV/Excel); Python with pandas, matplotlib, seaborn

</details>

<details>
<summary>content-repurposer - One article → multi-platform distribution</summary>

### [content-repurposer](skills/content-repurposer)

Repurpose a single article into multiple platform-specific formats.

**Triggered by**: "一鱼多吃", "多平台分发", "转成小红书", "repurpose", "convert to thread"

**Supported Platforms:**

| Platform | Format | Output |
|----------|--------|--------|
| 小红书 | emoji title, 500-1000 chars, 10-15 hashtags | `*-xiaohongshu.md` |
| Twitter/X | 5-12 tweets thread, 280 chars each | `*-twitter-thread.md` |
| 短视频脚本 | 1-3 min, hook→pain→solution→CTA | `*-video-script.md` |
| Newsletter | BLUF style, 150-300 chars, 3 bullets | `*-newsletter.md` |
| 知乎 | Lead with conclusion, 800-2000 chars | `*-zhihu.md` |
| 微信朋友圈 | ≤200 chars, 1 core point + 1 question | `*-moments.md` |

</details>

## Agents

The `agents/` directory contains specialized AI [subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents) that extend Claude Code's capabilities.

<details>
<summary>Available Agents</summary>

- **pr-reviewer** - Expert code reviewer for GitHub pull requests
- **github-issue-fixer** - GitHub issue resolution specialist
- **instruction-reflector** - Analyzes and improves Claude Code instructions
- **deep-reflector** - Comprehensive session analysis and learning capture
- **insight-documenter** - Technical breakthrough documentation specialist
- **ui-engineer** - UI/UX development specialist
- **command-creator** - Expert at creating new Claude Code custom commands

</details>

## Settings

[Sample Settings](settings/README.md) - Pre-configured settings for various model providers and setups.

<details>
<summary>Available Settings</summary>

### [copilot-settings.json](settings/copilot-settings.json)

Using Claude Code with GitHub Copilot proxy. Points to localhost:4141 for the Anthropic API base URL.

### [litellm-settings.json](settings/litellm-settings.json)

Using Claude Code with LiteLLM gateway. Points to localhost:4000 for the Anthropic API base URL.

### [deepseek-settings.json](settings/deepseek-settings.json)

Using Claude Code with DeepSeek v3.1 (via DeepSeek's official Anthropic-compatible API).

### [qwen-settings.json](settings/qwen-settings.json)

Using Claude Code with Qwen models via Alibaba's DashScope API. Uses the Qwen3-Coder-Plus model through a claude-code-proxy.

### [siliconflow-settings.json](settings/siliconflow-settings.json)

Using Claude Code with SiliconFlow API. Uses the Moonshot AI Kimi-K2-Instruct model.

### [vertex-settings.json](settings/vertex-settings.json)

Using Claude Code with Google Cloud Vertex AI. Uses Claude Opus 4 model with Google Cloud project settings.

### [azure-settings.json](settings/azure-settings.json)

Configuration for using Claude Code with Azure AI (Anthropic-compatible endpoint). Points to Azure AI services endpoint.

### [azure-foundry-settings.json](settings/azure-foundry-settings.json)

Configuration for using Claude Code with Azure AI Foundry native mode. Uses `CLAUDE_CODE_USE_FOUNDRY` flag with Claude Opus 4.1 + Sonnet 4.5 model.

### [minimax.json](settings/minimax.json)

Configuration for using Claude Code with MiniMax API. Uses the MiniMax-M2 model.

### [openrouter-settings.json](settings/openrouter-settings.json)

Using Claude Code with OpenRouter API. OpenRouter provides access to many models through a unified API. Note: `ANTHROPIC_API_KEY` must be blank while `ANTHROPIC_AUTH_TOKEN` contains your OpenRouter API key.

</details>

## MCP Servers Configuration

Claude Code supports [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers to extend functionality with external tools and services.

### Configuration File Location

MCP servers are configured in:

```
~/.claude/.mcp.json
```

**Note**: This is a hidden file (starts with `.`) inside the `~/.claude/` directory, not to be confused with:

- `~/.claude/config.json` (main configuration)
- `~/.claude/settings.json` (environment variables)
- `~/.claude.json` (global user settings in home directory)

**Create the file**:

```bash
# Method 1: Using cat with heredoc
cat > ~/.claude/.mcp.json << 'EOF'
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "type": "stdio"
    }
  }
}
EOF

# Method 2: Using your editor
vim ~/.claude/.mcp.json   # or code/nano/etc.

# Method 3: Copy from template (if you cloned this repo)
cp ~/.claude/.mcp.json.example ~/.claude/.mcp.json  # Edit as needed
```

### Setup MCP Servers

Create or edit `~/.claude/.mcp.json` to configure MCP servers:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "type": "stdio",
      "env": {}
    },
    "n8n-mcp": {
      "command": "npx",
      "args": ["n8n-mcp"],
      "env": {
        "MCP_MODE": "stdio",
        "N8N_API_KEY": "<your-n8n-api-key>",
        "N8N_API_URL": "https://your-n8n-instance.com"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "type": "stdio",
      "env": {}
    }
  }
}
```

### Popular MCP Servers

<details>
<summary>Documentation & Search</summary>

**Context7** - Query latest library documentation

```json
{
  "context7": {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp"],
    "type": "stdio"
  }
}
```

**Web Search Servers** (alternatives to Anthropic's WebSearch tool):

- [Tavily MCP](https://docs.tavily.com/documentation/mcp) - AI-optimized search API
- [Brave MCP](https://github.com/brave/brave-search-mcp-server) - Privacy-focused search
- [Firecrawl MCP](https://docs.firecrawl.dev/mcp-server) - Web scraping and search
- [DuckDuckGo MCP](https://github.com/nickclyde/duckduckgo-mcp-server) - Privacy search

</details>

<details>
<summary>Workflow Automation</summary>

**n8n MCP** - n8n workflow management

```json
{
  "n8n-mcp": {
    "command": "npx",
    "args": ["n8n-mcp"],
    "env": {
      "N8N_API_KEY": "<your-api-key>",
      "N8N_API_URL": "https://your-instance.com"
    }
  }
}
```

</details>

<details>
<summary>Browser Automation</summary>

**Playwright MCP** - Browser automation and testing

```json
{
  "playwright": {
    "command": "npx",
    "args": ["@playwright/mcp@latest"],
    "type": "stdio"
  }
}
```

**Chrome DevTools MCP** - Chrome debugging

```json
{
  "chrome": {
    "command": "npx",
    "args": ["chrome-devtools-mcp@latest"],
    "type": "stdio"
  }
}
```

</details>

### Configuration File Structure

Understanding the Claude Code configuration files:

```
~/.claude/                              # Claude Code directory
│
├── .mcp.json                           # 🎯 MCP servers configuration
│   └── Defines: context7, n8n-mcp, playwright, chrome
│
├── config.json                         # Main configuration
│   └── primaryApiKey: "sk-dummy"
│
├── settings.json                       # Environment variables
│   ├── ANTHROPIC_BASE_URL
│   ├── ANTHROPIC_AUTH_TOKEN
│   └── enabledPlugins
│
├── commands/                           # Custom commands
├── skills/                             # Skills plugins
├── agents/                             # Sub-agents
└── debug/latest                        # Debug logs

~/.claude.json                          # Global config (in home dir)
└── customApiKeyResponses.approved      # API key approvals
```

**Key Points**:

- `.mcp.json` - MCP servers only
- `config.json` - Primary API key
- `settings.json` - API endpoint, auth token, plugins
- `.claude.json` - Global user preferences (different location!)

### Verify MCP Configuration

After creating `.mcp.json`, restart Claude Code and check debug logs:

```bash
# Check if MCP servers are loaded
cat ~/.claude/debug/latest | grep -i "mcp"

# Should see messages like:
# [DEBUG] MCP server "context7": Successfully connected to stdio server
# [DEBUG] MCP server "n8n-mcp": Connection established with capabilities
```

### Troubleshooting

**MCP servers not loading:**

1. Verify JSON syntax: `cat ~/.claude/.mcp.json | python3 -m json.tool`
2. Check `npx` is installed: `which npx`
3. Ensure `config.json` is valid (no trailing commas)
4. Check debug logs: `~/.claude/debug/latest`
5. Verify file location: `ls -la ~/.claude/.mcp.json`

**Editing MCP configuration:**

```bash
# Open in editor
vim ~/.claude/.mcp.json   # or code/nano

# View current config
cat ~/.claude/.mcp.json

# Validate JSON format
python3 -c "import json; json.load(open('$HOME/.claude/.mcp.json'))" && echo "✅ Valid JSON"

# Check which servers are configured
cat ~/.claude/.mcp.json | python3 -c "import sys, json; print('\n'.join(json.load(sys.stdin)['mcpServers'].keys()))"
```

**Adding a new MCP server:**

```bash
# Edit the file and add to mcpServers object
vim ~/.claude/.mcp.json

# Then restart Claude Code for changes to take effect
```

**API Key issues:**

Ensure your API key is approved in `~/.claude.json`:

```json
{
  "customApiKeyResponses": {
    "approved": ["sk-dummy"]
  }
}
```

## Limitations

**WebSearch** tool in Claude Code is an [Anthropic specific tool,](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/web-search-tool) and it is not available when you're not using the official Anthropic API. Hence, if you need web search, you'd need to connect Claude Code with external web search MCP servers (see MCP Servers Configuration section above).

## FAQs

<details>
<summary>Login Issue of Claude Code 2.0+ extension in VSCode</summary>

For Claude Code 2.0+ extension in VSCode, if you're not using a Claude.ai subscription, please put the environment variables manually in your vscode settings.json:

```json
{
  "claude-code.environmentVariables": [
    {
      "name": "ANTHROPIC_BASE_URL",
      "value": "http://localhost:4000"
    },
    {
      "name": "ANTHROPIC_AUTH_TOKEN",
      "value": "sk-dummy"
    },
    {
      "name": "ANTHROPIC_MODEL",
      "value": "opusplan"
    },
    {
      "name": "ANTHROPIC_DEFAULT_SONNET_MODEL",
      "value": "claude-sonnet-4.5"
    },
    {
      "name": "ANTHROPIC_DEFAULT_OPUS_MODEL",
      "value": "claude-opus-4"
    },
    {
      "name": "ANTHROPIC_DEFAULT_HAIKU_MODEL",
      "value": "gpt-5-mini"
    },
    {
      "name": "DISABLE_NON_ESSENTIAL_MODEL_CALLS",
      "value": "1"
    },
    {
      "name": "DISABLE_TELEMETRY",
      "value": "1"
    },
    {
      "name": "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
      "value": "1"
    }
  ]
}
```

Note that the contents of [~/.claude/config.json](config.json) are also required to skip claude.ai login.

</details>

<details>
<summary>Missing API Key and Invalid API Key issues</summary>

Ensure the API key you configured in `ANTHROPIC_AUTH_TOKEN` is added to approved API key in `~/.claude.json`, e.g.

```javascript
{
  "customApiKeyResponses": {
    "approved": [
      "sk-dummy"
    ],
    "rejected": []
  },
  ... (your other settings)
}
```

</details>

## Guidances

- [Claude Code with GitHub Copilot as Model Provider](guidances/github-copilot.md).
- [Claude Code with LLM Gateway (LiteLLM) as Model Provider](guidances/llm-gateway-litellm.md).

## References

- [Claude Code official document](https://docs.anthropic.com/en/docs/claude-code/overview) - must read official document.
- [anthropics/skills](https://github.com/anthropics/skills) - official list of Claude Code skills that teach Claude how to complete specific tasks in a repeatable way
- [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) - curated list of slash-commands, CLAUDE.md files, CLI tools, and other resources.
- [wshobson/agents](https://github.com/wshobson/agents) - a comprehensive collection of specialized AI subagents for Claude Code.

## LICENSE

This project is released under MIT License - See [LICENSE](LICENSE) for details.
