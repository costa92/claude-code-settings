# Claude Code 设置/命令/技能 — Vibe Coding 工具箱

[English](README.md) | **中文**

一套精选的 Claude Code 配置、自定义命令、技能和子代理，用于增强开发工作流。包含功能开发（规格驱动工作流）、代码分析、GitHub 集成和知识管理等专用工具。

> OpenAI Codex 的设置和自定义提示词请参考 [feiskyer/codex-settings](https://github.com/feiskyer/codex-settings)。

## 目录

- [安装](#安装)
  - [插件安装（推荐）](#通过-claude-code-插件安装)
  - [手动安装](#手动安装)
  - [跨机器初始化](#跨机器初始化-setupsh)
  - [MCP 配置](#快速开始mcp-配置)
- [命令](#命令)
- [技能](#技能)
  - [开发工具插件](#开发工具插件)
  - [内容创作流水线](#内容创作流水线微信--博客)
  - [本地技能](#本地技能)
- [子代理](#子代理)
- [配置模板](#配置模板)
- [MCP 服务器配置](#mcp-服务器配置)
- [常见问题](#常见问题)

---

## 安装

### 通过 Claude Code 插件安装

```sh
# 添加 marketplace
/plugin marketplace add feiskyer/claude-code-settings

# 安装主插件（包含命令、代理和技能）
/plugin install claude-code-settings

# 或者按需单独安装技能
/plugin install codex-skill               # Codex 自动化
/plugin install autonomous-skill          # 长时任务自动化
/plugin install nanobanana-skill          # AI 图片生成
/plugin install kiro-skill                # Kiro 工作流
/plugin install spec-kit-skill            # Spec-Kit 工作流
/plugin install youtube-transcribe-skill  # YouTube 字幕提取
```

也可以通过 [Claude Plugins CLI](https://claude-plugins.dev) 一键安装（跳过 marketplace 设置）：

```bash
npx claude-plugins install @feiskyer/claude-code-settings/claude-code-settings
```

**注意：** [~/.claude/settings.json](settings.json) 不会通过插件自动配置，需要手动设置。

### 手动安装

```sh
# 备份已有配置
mv ~/.claude ~/.claude.bak

# 克隆仓库
git clone https://github.com/feiskyer/claude-code-settings.git ~/.claude

# 安装 LiteLLM 代理
pip install -U 'litellm[proxy]'

# 启动 LiteLLM 代理（监听 http://0.0.0.0:4000）
litellm -c ~/.claude/guidances/litellm_config.yaml

# 后台运行（推荐用 tmux）
# tmux new-session -d -s copilot 'litellm -c guidances/litellm_config.yaml'
```

启动后会提示：

```
Please visit https://github.com/login/device and enter code XXXX-XXXX to authenticate.
```

打开链接，登录并授权 GitHub Copilot 账号。

**注意：**

1. 默认配置使用 [LiteLLM Proxy Server](https://docs.litellm.ai/docs/simple_proxy) 作为 LLM 网关连接 GitHub Copilot。也可以使用 [copilot-api](https://github.com/ericc-ch/copilot-api)（端口改为 4141）。
2. 确保账号中以下模型可用，否则替换为你自己的模型名：
   - ANTHROPIC_DEFAULT_SONNET_MODEL: claude-sonnet-4.5
   - ANTHROPIC_DEFAULT_OPUS_MODEL: claude-opus-4
   - ANTHROPIC_DEFAULT_HAIKU_MODEL: gpt-5-mini

### 跨机器初始化 (setup.sh)

在新机器上克隆仓库后，运行 `setup.sh` 重建 `.gitignore` 排除的内容（settings、marketplace、插件缓存、权限、依赖）：

```sh
cd ~/.claude
bash setup.sh              # 交互模式 — 提示输入 API 密钥和可选依赖
bash setup.sh --skip-python # 跳过 Python 依赖安装
bash setup.sh --force       # 强制重建插件缓存
```

**8 步初始化流程：**

| 步骤 | 说明 |
|------|------|
| 1. 环境检测 | 验证 `git`、`jq`、`python3` |
| 2. settings.json | 从 `settings.json.example` 复制（不覆盖已有） |
| 3. Marketplace 仓库 | 克隆/更新 marketplace Git 仓库 + 生成 `known_marketplaces.json` |
| 4. 插件缓存 | 通过 `claude plugin install` 重建，失败时手动回退 |
| 5. 路径修正 | 将 `installed_plugins.json` 中的绝对路径 `/home/user/...` 统一为 `~/...`，避免跨机器加载失败 |
| 6. 权限修复 | 对 `status-line.sh` 和所有 skill 脚本执行 `chmod +x` |
| 7. Python 依赖 | 可选安装 `pip install` + Playwright |
| 8. 系统软件包 | 检查 LibreOffice、Poppler、npm 工具 |

### 快速开始：MCP 配置

创建 `~/.claude/.mcp.json` 启用 MCP 服务器：

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

详细配置参见 [MCP 服务器配置](#mcp-服务器配置) 部分。

---

## 命令

`commands/` 目录包含[自定义斜杠命令](https://code.claude.com/docs/en/slash-commands)，通过 `/<命令名> [参数]` 调用。

### 分析与反思

| 命令 | 说明 | 用法 |
|------|------|------|
| `/think-harder` | 增强分析性思考 | `/think-harder 如何优化这个数据库查询` |
| `/think-ultra` | 超深度综合分析（7 阶段） | `/think-ultra 微服务架构迁移方案` |
| `/reflection` | 分析并改进 CLAUDE.md 指令 | `/reflection` |
| `/reflection-harder` | 全面会话分析与经验提取 | `/reflection-harder` |
| `/eureka` | 记录技术突破 | `/eureka 通过请求批处理将 API 响应时间从 2s 降到 100ms` |

### GitHub 集成

| 命令 | 说明 | 用法 |
|------|------|------|
| `/gh:review-pr` | 全面审查 PR 代码 | `/gh:review-pr 78` |
| `/gh:fix-issue` | 完整的 Issue 修复工作流 | `/gh:fix-issue 42` |

### 工具

| 命令 | 说明 | 用法 |
|------|------|------|
| `/cc:create-command` | 创建新的自定义命令 | `/cc:create-command deploy-check 部署前检查` |
| `/translate` | 翻译英文/日文技术内容为中文 | `/translate This is a test` |

---

## 技能

技能以独立插件形式分发，按需安装。

### 开发工具插件

<details>
<summary>codex-skill — 将任务交给 OpenAI Codex/GPT 执行</summary>

非交互自动化模式，使用 OpenAI Codex/GPT 模型执行任务。适合将 Claude 设计的方案交给 GPT 实现。

**触发词：** "codex"、"use gpt"、"gpt-5"、"用codex"、"让gpt实现"

```sh
/plugin install codex-skill
```

**功能：**
- 多种执行模式（只读、工作区写入、完全访问）
- 模型选择（gpt-5、gpt-5.2、gpt-5.2-codex 等）
- 无需审批的自主执行
- JSON 结构化输出
- 可恢复会话

**依赖：** 安装 Codex CLI（`npm i -g @openai/codex` 或 `brew install codex`）

</details>

<details>
<summary>autonomous-skill — 长时任务自动化</summary>

跨多个会话执行复杂长时任务，使用双代理模式（初始化器 + 执行器）自动续接。

**触发词：** "autonomous"、"long-running task"、"自主执行"、"长时任务"

```sh
/plugin install autonomous-skill
```

**功能：**
- 双代理模式（初始化器创建任务列表，执行器逐个完成）
- 跨会话自动续接 + 进度追踪
- 每个任务独立目录（`.autonomous/<任务名>/`）
- 通过 `task_list.md` 和 `progress.md` 持久化进度

**用法：**

```text
你：请用 autonomous skill 构建一个 Todo 应用的 REST API
Claude：[创建 .autonomous/build-rest-api-todo/，初始化任务列表，开始执行]
```

**依赖：** 安装 Claude CLI

</details>

<details>
<summary>nanobanana-skill — Google Gemini AI 图片生成</summary>

通过 nanobanana 调用 Google Gemini API 生成或编辑图片。

**触发词：** "nanobanana"、"生成图片"、"AI绘图"、"图片编辑"

```sh
/plugin install nanobanana-skill
```

**功能：**
- 多种宽高比（正方形、竖屏、横屏、超宽）
- 多分辨率（1K/2K/4K）
- 图片编辑能力
- 多模型选择（gemini-3-pro-image-preview、gemini-2.5-flash-image）

**依赖：**
- `GEMINI_API_KEY` 配置在 `~/.nanobanana.env`
- Python3 + google-genai、Pillow、python-dotenv

</details>

<details>
<summary>youtube-transcribe-skill — YouTube 字幕提取</summary>

从 YouTube 视频链接提取字幕/文字记录。

**触发词：** "youtube transcript"、"视频字幕"、"字幕提取"、"YouTube转文字"

```sh
/plugin install youtube-transcribe-skill
```

**功能：**
- 双提取方式：CLI（快速）和浏览器自动化（备选）
- 自动选择字幕语言（zh-Hans、zh-Hant、en）
- 保存到本地文本文件

**依赖：** `yt-dlp`（CLI 方式）或 `chrome-devtools-mcp`（浏览器方式）

</details>

<details>
<summary>kiro-skill — 交互式规格驱动开发</summary>

从想法到实现的交互式工作流，生成 EARS 需求文档、设计文档和任务列表。

**触发词：** "kiro"、"feature spec"、"需求文档"、"设计文档"、"实现计划"

```sh
/plugin install kiro-skill
```

**工作流：**

1. **需求** → 定义要构建什么（EARS 格式 + 用户故事）
2. **设计** → 确定如何构建（架构、组件、数据模型）
3. **任务** → 创建可执行的实现步骤（测试驱动、增量式）
4. **执行** → 逐个实现任务

**存储：** `.kiro/specs/{功能名}/` 目录

</details>

<details>
<summary>spec-kit-skill — 宪法式规格驱动开发</summary>

GitHub Spec-Kit 集成，基于宪法原则的 7 阶段规格驱动开发工作流。

**触发词：** "spec-kit"、"constitution"、"specify"、"规格驱动开发"、"需求规格"

```sh
/plugin install spec-kit-skill
```

**前置安装：**

```sh
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify init . --ai claude
```

**7 阶段工作流：**

1. **宪法** → 建立治理原则
2. **规格** → 定义功能需求
3. **澄清** → 消除歧义（最多 5 个问题）
4. **规划** → 制定技术策略
5. **任务** → 生成依赖排序的任务
6. **分析** → 验证一致性（只读）
7. **实现** → 执行实施

</details>

### 内容创作流水线（微信 / 博客）

从选题到多平台分发的全周期内容生产流水线，专为微信公众号和技术博客设计。

```
选题 → 大纲 → 写作 → 审查 → SEO优化 → 排版转换 → 数据分析 → 多平台分发
```

| 阶段 | 技能 | 触发方式 | 输出 |
|------|------|----------|------|
| 1. 选题 | `content-planner` | `/content-planner` | 选题库 + 内容日历 + 排期 |
| 2. 大纲 | `article-outline-agent` | 写作前自动触发 | 读者画像 + 论点 + 结构 |
| 3. 写作 | `article-generator` | `/article-generator` | Markdown 技术博文 + 配图 |
| 4. 审查 | `content-reviewer` | 写作后自动触发 | 6 维评分 + 修改清单 |
| 5. SEO | `wechat-seo-optimizer` | `/wechat-seo-optimizer` | 标题/摘要/关键词优化 |
| 6. 排版 | `wechat-article-converter` | `/wechat-article-converter` | 微信公众号 HTML |
| 7. 数据 | `content-analytics` | `/content-analytics` | 阅读/互动/增长分析 |
| 8. 分发 | `content-repurposer` | `/content-repurposer` | 小红书/Twitter/短视频/Newsletter/知乎 |

**快速开始 — 写一篇文章：**

```text
# 最简路径：一条命令生成文章
你：/article-generator 写一篇关于 Docker 多阶段构建优化的技术博文

# 完整流水线：逐步执行
你：/content-planner                            # 第 1 步：选题规划
你：我选了 Docker 多阶段构建这个选题              # 第 2 步：自动生成大纲
你：/article-generator 根据大纲写作              # 第 3 步：写作
你：文章写好了，帮我审查一下                       # 第 4 步：自动审查
你：/wechat-seo-optimizer 优化标题和摘要          # 第 5 步：SEO 优化
你：/wechat-article-converter 转换为微信格式       # 第 6 步：排版转换
你：/content-repurposer 一鱼多吃转成小红书和Twitter  # 第 7 步：多平台分发
```

<details>
<summary>各技能详细说明</summary>

#### content-planner — 选题规划与内容日历

计划内容选题，管理编辑日历，构建内容发布管线。

**触发词：** "选题"、"内容规划"、"内容日历"、"发布计划"、"选题库"

**功能：**
- 8 大来源渠道的选题库（热点追踪、痛点挖掘、竞品分析等）
- 选题四象限评估（实用性 x 传播力 → 爆款区/口碑区/话题区/填充区）
- 月度内容日历 + 发布时间建议
- 管线看板：Backlog → 进行中 → 审核 → 完成

#### article-generator — 技术博文生成

生成真实风格的技术博文。输出 Markdown 格式，含 YAML frontmatter、Obsidian callouts、代码示例和 CDN 图片。

**触发词：** `/article-generator`、"写一篇文章"、"写一篇关于...的文章"

**功能：**
- 反 AI 风格检测（禁止营销用语、禁止虚假互动）
- Gemini API 图片生成（1K/2K/4K）+ 自动上传到 PicGo/S3
- 内容深度：>2000 字，必须包含真实案例
- 写作前验证：所有技术内容通过官方文档核实

**依赖：**
- `pip install -r skills/article-generator/requirements.txt`
- `pip install shot-scraper && shot-scraper install`（网页截图）
- `GEMINI_API_KEY` 环境变量（图片生成，可选）

#### wechat-seo-optimizer — 标题/关键词/摘要优化

优化微信文章标题、摘要和关键词以最大化触达。

**触发词：** "标题优化"、"SEO"、"取标题"、"提高阅读量"

**功能：**
- 8 种公式生成 5 个标题方案（数字锚点、悬念缺口、痛点直击等）
- 标题核检：15-25 字，含核心关键词，无标题党
- 摘要优化：<=120 字，4 种策略类型
- 关键词密度分析（1-3%）+ 长尾词建议
- 封面图指引（头条 900x383px / 次条 200x200px）

#### wechat-article-converter — Markdown 转微信 HTML

将 Markdown 文章转换为微信公众号兼容的 HTML。

**触发词：** "转换为微信格式"、"去除AI痕迹"、"生成封面图"

**功能：**
- **Python 引擎**（7 种主题）：Coffee、Tech、Warm、Simple、MD2 Classic/Dark/Purple
- **Go 后端**（9 种主题 + AI 主题）：更多高级功能
- 草稿箱直推：直接推送到微信草稿箱
- AI 封面图生成
- 写作助手 + 创作者风格模板（Dan Koe 等）
- AI 痕迹去除 / 人性化处理（24 种模式检测，3 级强度）
- 批量转换 + 本地预览服务器

**依赖：**
- Python：`pip install markdown premailer pygments beautifulsoup4 lxml cssutils`
- Go 后端：自动下载二进制；草稿箱上传需 `WECHAT_APPID` + `WECHAT_SECRET`

#### content-analytics — 微信文章数据分析

从导出的 CSV/Excel 文件分析微信公众号文章表现数据。

**触发词：** "数据分析"、"文章数据"、"阅读量分析"、"粉丝分析"、"公众号数据"

**功能：**
- 6 大分析模块：概览、内容效能、时间规律、读者行为、增长分析、竞争力诊断
- 代码计算指标（绝不估算）
- 可视化图表：折线/柱状/热力/饼图/散点图，保存为 PNG
- 6 维健康评分（阅读趋势、互动率、发布频率、忠诚度、传播力、搜索价值）
- 可执行策略建议（即时/短期/长期）

**依赖：** Python + pandas、matplotlib、seaborn

#### content-repurposer — 一鱼多吃多平台分发

将一篇文章转化为多个平台特定格式。

**触发词：** "一鱼多吃"、"多平台分发"、"转成小红书"、"repurpose"

**支持平台：**

| 平台 | 格式 | 输出文件 |
|------|------|----------|
| 小红书 | emoji 标题，500-1000 字，10-15 个话题标签 | `*-xiaohongshu.md` |
| Twitter/X | 5-12 条推文线程，每条 280 字符 | `*-twitter-thread.md` |
| 短视频脚本 | 1-3 分钟，hook→痛点→方案→CTA | `*-video-script.md` |
| Newsletter | BLUF 风格，150-300 字，3 个要点 | `*-newsletter.md` |
| 知乎 | 结论先行，800-2000 字 | `*-zhihu.md` |
| 微信朋友圈 | <=200 字，1 个核心观点 + 1 个问题 | `*-moments.md` |

</details>

### 本地技能

`skills/` 目录还包含 28 个内置本地技能（自动加载，无需安装）。上方[内容创作流水线](#内容创作流水线微信--博客)中的 6 个技能已单独说明。

<details>
<summary>设计与视觉（7 个）</summary>

| 技能 | 说明 |
|------|------|
| [canvas-design](skills/canvas-design) | 用设计哲学创建 .png/.pdf 视觉艺术 — 海报、设计稿、静态作品 |
| [frontend-design](skills/frontend-design) | 创建高品质、生产级前端界面，拒绝 AI 套路风格 |
| [ui-ux-pro-max](skills/ui-ux-pro-max) | UI/UX 设计智库 — 50 种风格、21 色板、50 字体搭配、20 图表、9 技术栈 |
| [algorithmic-art](skills/algorithmic-art) | 用 p5.js 创建生成艺术 — 种子随机、交互参数、流场粒子系统 |
| [brand-guidelines](skills/brand-guidelines) | 应用 Anthropic 官方品牌色彩和字体到各类产出物 |
| [theme-factory](skills/theme-factory) | 产出物主题工厂 — 10 种预设主题（幻灯片、文档、Landing Page） |
| [slack-gif-creator](skills/slack-gif-creator) | 创建 Slack 优化的动态 GIF — 约束、验证、动画概念 |

</details>

<details>
<summary>Web 开发（4 个）</summary>

| 技能 | 说明 |
|------|------|
| [web-artifacts-builder](skills/web-artifacts-builder) | 创建多组件 HTML Artifact（React + Tailwind + shadcn/ui） |
| [react-best-practices](skills/react-best-practices) | Vercel 工程团队的 React/Next.js 性能优化指南 |
| [vue-best-practices](skills/vue-best-practices) | Vue 3 TypeScript 最佳实践 — vue-tsc、Volar、Props 提取 |
| [webapp-testing](skills/webapp-testing) | 用 Playwright 测试本地 Web 应用 — 截图、浏览器日志 |

</details>

<details>
<summary>文档处理（5 个）</summary>

| 技能 | 说明 |
|------|------|
| [docx](skills/docx) | 创建、读取、编辑 Word 文档 — 目录、页眉、格式化 |
| [pdf](skills/pdf) | 读取、提取、合并、拆分、旋转、水印、创建 PDF |
| [pptx](skills/pptx) | 创建、读取 PowerPoint 文件 — 幻灯片、路演 Deck |
| [xlsx](skills/xlsx) | 读写电子表格（.xlsx/.xlsm/.csv/.tsv）— 公式、图表 |
| [revealjs](skills/revealjs) | 创建 reveal.js HTML 演示文稿 — 主题、动画、演讲者备注 |

</details>

<details>
<summary>Obsidian（4 个）</summary>

| 技能 | 说明 |
|------|------|
| [obsidian-cli](skills/obsidian-cli) | 与 Obsidian 库交互 — 读写搜索笔记、插件/主题开发 |
| [obsidian-bases](skills/obsidian-bases) | 创建/编辑 .base 文件 — 类数据库视图、过滤器、公式、汇总 |
| [obsidian-markdown](skills/obsidian-markdown) | Obsidian 风格 Markdown — 双向链接、嵌入、Callout、属性、标签 |
| [json-canvas](skills/json-canvas) | 创建/编辑 JSON Canvas（.canvas）— 可视画布、思维导图、流程图 |

</details>

<details>
<summary>内容与知识（5 个）</summary>

| 技能 | 说明 |
|------|------|
| [ai-daily](skills/ai-daily) | 从多个来源抓取 AI 新闻，生成结构化 Markdown 摘要 |
| [defuddle](skills/defuddle) | 从网页提取干净 Markdown — 替代 WebFetch 用于 URL 阅读 |
| [doc-coauthoring](skills/doc-coauthoring) | 文档协作工作流 — 技术规格、提案、决策文档 |
| [internal-comms](skills/internal-comms) | 撰写内部沟通文档 — 状态报告、领导层更新、3P 更新 |
| [medical-imaging-review](skills/medical-imaging-review) | 撰写医学影像 AI 研究综述（CT、MRI、X-ray） |

</details>

<details>
<summary>开发工具（3 个）</summary>

| 技能 | 说明 |
|------|------|
| [mcp-builder](skills/mcp-builder) | MCP 服务器开发指南 — Python (FastMCP) 或 Node/TypeScript |
| [skill-creator](skills/skill-creator) | 技能开发指南 — 创建扩展 Claude 能力的自定义技能 |
| [vercel-deploy-claimable](skills/vercel-deploy-claimable) | 部署应用到 Vercel — 预览和生产环境部署 |

</details>

---

## 子代理

`agents/` 目录包含扩展 Claude Code 能力的专用 AI [子代理](https://docs.anthropic.com/en/docs/claude-code/sub-agents)。

- **ui-engineer** — 专业 UI/前端开发者，用于创建、修改或审查前端代码、UI 组件和用户界面

> **说明：** 以下子代理因与已有命令功能重复已被移除：
>
> | 已移除的子代理 | 替代命令 | 功能 |
> |---|---|---|
> | `deep-reflector` | `/reflection-harder` | 会话分析与经验提取 |
> | `instruction-reflector` | `/reflection` | 分析改进 CLAUDE.md |
> | `insight-documenter` | `/eureka` | 技术突破文档化 |
> | `command-creator` | `/cc:create-command` | 创建自定义命令 |
> | `github-issue-fixer` | `/gh:fix-issue` | 修复 GitHub Issue |
> | `pr-reviewer` | `/gh:review-pr` | 审查 GitHub PR |

---

## 配置模板

[配置模板目录](settings/README.md) — 预置了多种模型提供商的配置。

| 配置文件 | 说明 |
|----------|------|
| [copilot-settings.json](settings/copilot-settings.json) | GitHub Copilot 代理（localhost:4141） |
| [litellm-settings.json](settings/litellm-settings.json) | LiteLLM 网关（localhost:4000） |
| [deepseek-settings.json](settings/deepseek-settings.json) | DeepSeek v3.1（官方 Anthropic 兼容 API） |
| [qwen-settings.json](settings/qwen-settings.json) | 通义千问（DashScope API + claude-code-proxy） |
| [siliconflow-settings.json](settings/siliconflow-settings.json) | SiliconFlow API（Kimi-K2-Instruct） |
| [vertex-settings.json](settings/vertex-settings.json) | Google Cloud Vertex AI |
| [azure-settings.json](settings/azure-settings.json) | Azure AI（Anthropic 兼容端点） |
| [azure-foundry-settings.json](settings/azure-foundry-settings.json) | Azure AI Foundry 原生模式 |
| [minimax.json](settings/minimax.json) | MiniMax API（MiniMax-M2） |
| [openrouter-settings.json](settings/openrouter-settings.json) | OpenRouter API（多模型统一接口） |

---

## MCP 服务器配置

Claude Code 支持 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 服务器来扩展功能。

### 配置文件位置

```
~/.claude/.mcp.json
```

**注意：** 这是 `~/.claude/` 目录下的**隐藏文件**（以 `.` 开头），不要与以下文件混淆：

- `~/.claude/config.json` — 主配置
- `~/.claude/settings.json` — 环境变量
- `~/.claude.json` — 全局用户设置（在 Home 目录）

### 配置示例

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "type": "stdio"
    },
    "n8n-mcp": {
      "command": "npx",
      "args": ["n8n-mcp"],
      "env": {
        "MCP_MODE": "stdio",
        "N8N_API_KEY": "<你的 n8n API 密钥>",
        "N8N_API_URL": "https://your-n8n-instance.com"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "type": "stdio"
    }
  }
}
```

### 常用 MCP 服务器

| 类别 | 服务器 | 说明 |
|------|--------|------|
| 文档查询 | [Context7](https://github.com/nicepkg/context7) | 查询最新库文档 |
| 搜索 | [Tavily MCP](https://docs.tavily.com/documentation/mcp) | AI 优化搜索 API |
| 搜索 | [Brave MCP](https://github.com/brave/brave-search-mcp-server) | 隐私搜索 |
| 搜索 | [Firecrawl MCP](https://docs.firecrawl.dev/mcp-server) | 网页抓取 + 搜索 |
| 工作流 | [n8n MCP](https://github.com/czlonkowski/n8n-mcp) | n8n 工作流管理 |
| 浏览器 | [Playwright MCP](https://github.com/nicepkg/playwright-mcp) | 浏览器自动化测试 |
| 浏览器 | [Chrome DevTools MCP](https://github.com/nicepkg/chrome-devtools-mcp) | Chrome 调试 |

### 配置文件结构

```
~/.claude/                              # Claude Code 目录
│
├── .mcp.json                           # MCP 服务器配置
├── config.json                         # 主配置（API 密钥）
├── settings.json                       # 环境变量 + 插件开关
│
├── commands/                           # 自定义斜杠命令
├── skills/                             # 技能插件
├── agents/                             # 子代理
└── debug/latest                        # 调试日志

~/.claude.json                          # 全局配置（Home 目录）
└── customApiKeyResponses.approved      # API 密钥审批
```

### 验证 MCP 配置

```bash
# 检查 MCP 服务器是否加载
cat ~/.claude/debug/latest | grep -i "mcp"

# 验证 JSON 格式
python3 -c "import json; json.load(open('$HOME/.claude/.mcp.json'))" && echo "JSON 格式正确"

# 查看已配置的服务器
cat ~/.claude/.mcp.json | python3 -c "import sys, json; print('\n'.join(json.load(sys.stdin)['mcpServers'].keys()))"
```

---

## 限制

**WebSearch** 工具是 [Anthropic 专有工具](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/web-search-tool)，非官方 Anthropic API 不可用。如需搜索功能，请配置外部搜索 MCP 服务器（见上方 MCP 配置部分）。

---

## 常见问题

<details>
<summary>VSCode 中 Claude Code 2.0+ 扩展登录问题</summary>

如果你不使用 Claude.ai 订阅，需要在 VSCode settings.json 中手动配置环境变量：

```json
{
  "claude-code.environmentVariables": [
    { "name": "ANTHROPIC_BASE_URL", "value": "http://localhost:4000" },
    { "name": "ANTHROPIC_AUTH_TOKEN", "value": "sk-dummy" },
    { "name": "ANTHROPIC_MODEL", "value": "opusplan" },
    { "name": "ANTHROPIC_DEFAULT_SONNET_MODEL", "value": "claude-sonnet-4.5" },
    { "name": "ANTHROPIC_DEFAULT_OPUS_MODEL", "value": "claude-opus-4" },
    { "name": "ANTHROPIC_DEFAULT_HAIKU_MODEL", "value": "gpt-5-mini" },
    { "name": "DISABLE_NON_ESSENTIAL_MODEL_CALLS", "value": "1" },
    { "name": "DISABLE_TELEMETRY", "value": "1" },
    { "name": "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC", "value": "1" }
  ]
}
```

同时需要 [~/.claude/config.json](config.json) 的内容来跳过 claude.ai 登录。

</details>

<details>
<summary>API 密钥缺失或无效</summary>

确保 `ANTHROPIC_AUTH_TOKEN` 中配置的密钥已添加到 `~/.claude.json` 的审批列表：

```json
{
  "customApiKeyResponses": {
    "approved": ["sk-dummy"],
    "rejected": []
  }
}
```

</details>

---

## 参考指南

- [Claude Code with GitHub Copilot as Model Provider](guidances/github-copilot.md)
- [Claude Code with LLM Gateway (LiteLLM) as Model Provider](guidances/llm-gateway-litellm.md)

## 参考链接

- [Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code/overview) — 必读
- [anthropics/skills](https://github.com/anthropics/skills) — 官方 Claude Code 技能列表
- [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) — 命令、CLAUDE.md、CLI 工具精选
- [wshobson/agents](https://github.com/wshobson/agents) — Claude Code 子代理合集

## 许可证

本项目使用 MIT 许可证发布 — 详见 [LICENSE](LICENSE)。
