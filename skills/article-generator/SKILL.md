---
name: article-generator
description: 生成技术博客文章（Markdown/Obsidian 格式），含 Gemini 配图和 CDN 上传。当用户要写文章、写教程、写技术博客时使用。
---

# Article Generator

**专注于生成技术博客文章（Markdown/Obsidian 格式）**

> 查看 [快速开始指南 (5分钟)](QUICKSTART.md) | [完整示例](examples/)

---

## Execution Checklist (Read This FIRST)

### Phase A: 写作前（尽量并行，减少 bash 调用次数）
1. **[ ] Clarify requirements** — 用户明确指定时可跳过 AskUserQuestion
2. **[ ] Feature discovery** — 写工具类文章时，必须先摸清工具的完整功能面（**新文章和更新旧文章都必须执行**）：
   - **已安装**：运行 `tool --help` 查看所有子命令，逐个 `subcommand --help` 了解新功能
   - **未安装**：Docker 临时环境（`docker run --rm -it`，真实数据+可截图）→ GitHub README → 官方文档 CLI 参考页 → `gh api repos/.../releases` 查最近版本
   - **官方博客/Changelog**：用 curl 抓取最近博客标题，识别新功能
   - **对比已知 vs 实际**：列出差异，新功能必须纳入章节规划
3. **[ ] Batch verify** — 所有验证**合并为尽量少的 bash 调用**：
   - **链接**：多个 URL 放在一条 bash 命令中并行验证（`curl ... & curl ... & wait`）
   - **命令**：有依赖关系的命令用 `&&` 链式执行，无依赖的用多个并行 bash 调用
   - **只报告失败项**，通过的不输出
   - 详见 [verification-checklist.md](references/verification-checklist.md)

### Phase B: 写作（先文章后图片）
4. **[ ] Save article to file** — Use `Write` tool，NEVER just display in chat
5. **[ ] SCREENSHOT placeholders** — 引用外部内容时必须插入（截图是事实素材）
6. **[ ] Mermaid → image** — 文章中的流程图、架构图等 Mermaid 图表必须渲染为图片：
   - 将 Mermaid 代码写入 `.mmd` 文件
   - 用 `npx @mermaid-js/mermaid-cli mmdc -i input.mmd -o output.png -b transparent` 渲染
   - 上传 CDN，替换文章中的 Mermaid 代码块为 `![描述](CDN_URL)`
   - **禁止在最终文章中保留 Mermaid 代码块**（微信等平台不支持渲染）
7. **[ ] Image auto-process** — 文章保存后**立即自动执行**图片生成流程（不得留给用户手动处理）：
   - **批量处理脚本**：`generate_and_upload_images.py`（支持 `--process-file`），**不是** `nanobanana.py`（仅支持单张生成）
   - **截图**（shot-scraper）：不依赖 Gemini，始终执行，`generate_and_upload_images.py --process-file` 会自动处理 `<!-- SCREENSHOT -->` 标签
   - **AI 图**：Gemini 探针测试（见下方降级链），探针成功则立即执行 `generate_and_upload_images.py --process-file` 替换所有 `<!-- IMAGE -->` 占位符
   - **降级链**：默认模型 → flash 模型 → 两者都失败时才保留占位符
   - **关键**：探针成功后必须在同一 session 内执行 `generate_and_upload_images.py --process-file`，不得只记录命令让用户后续手动执行
   - **注意**：若不用 `generate_and_upload_images.py` 而是用 `nanobanana.py` 逐张生成，需先 `mkdir -p` 创建输出目录（`nanobanana.py` 不会自动创建目录）
8. **[ ] Verify image replacement** — 检查文章中是否还有残留的 `<!-- IMAGE:` 占位符：
   - 无残留 → 完成
   - 有残留（Gemini 完全不可用）→ 在完成汇总中列出数量和可执行命令

### Phase C: 写作后（按场景裁剪）
9. **[ ] Self-check** — 跑 reviewer 前快速自检常见扣分项：
   - 有收尾行动指引段落？（不是"希望对你有帮助"）
   - 有红旗词？（用 Grep 搜索以下词：`无缝|赋能|一站式|综上所述|总而言之|值得注意的是|不难发现|深度解析|全面梳理|链路|闭环|抓手|底层逻辑|方法论|降本增效|实际上|事实上|显然|众所周知|不难看出`）
   - 每个章节有足够深度？（≥2 条命令或代码 + 解释，不能只有 1 条命令 1 句话）
   - 开头 Hook 在 100 字内？环境声明用 callout 包裹？
   - frontmatter `description` 字段已填写？（120 字以内摘要，微信必须）
   - 同一章节内无重复图片？（同一 section 不应出现两张功能相同的配图）
   - 微信平台：外部链接已转为搜索指引？（如 `搜索「关键词」`，微信不支持外链）
   - 文章中无残留 Mermaid 代码块？（流程图/架构图必须已渲染为图片）
   - 参考链接已内联到正文？（格式：`[名称](url)`，禁止在末尾设独立参考资料区）
10. **[ ] Verify content depth** — 字数要求见下表
11. **[ ] Quality gate** — 按场景选择审查模式：
   - **发布模式**（默认）：运行 `/content-reviewer` ≥ 55/70，运行 `/wechat-seo-optimizer`
   - **草稿/测试模式**（用户说"测试""草稿""先看看"）：自行快速检查事实准确性和链接，跳过 reviewer 和 SEO
12. **[ ] Confirm completion** — 用简洁表格汇总，必须包含以下信息：
    - **文件绝对路径**（方便跨 session 接手）
    - **图片状态**：已上传数 / 总数，如有未生成的占位符需列出具体数量和待执行命令
    - **审查结果**：评分和状态

**字数要求：**

| 文章类型 | 字数范围 | 触发词 |
|---------|---------|--------|
| 快速入门 | 500-1000 字 | "快速入门""quick start""简短" |
| 实战教程 | 2000-3000 字 | 默认 |
| 深度解析 | 4000+ 字 | "深度""详细""全面" |

> **字数由用户选择决定**，上表仅为参考范围。不要因平台限制自行截断内容，如果用户选择了深度解析，就按 4000+ 字写。

### 速度优化规则

**1. 批量验证（减少 bash 调用）**
```bash
# 链接验证：一次 bash 调用验证所有 URL（含 HEAD→GET 降级）
for url in URL1 URL2 URL3; do
  code=$(curl -sI -o /dev/null -w "%{http_code}" --max-time 10 "$url")
  if [ "$code" = "405" ] || [ "$code" = "000" ]; then
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url")
  fi
  [ "$code" != "200" ] && echo "FAIL $code $url"
done

# 命令验证：有依赖的链式执行
cd /tmp && uv init --name test && uv add requests && uv run python -c "import requests; print(requests.__version__)" && uv tree
```

**2. Gemini 探针测试 + 模型降级链**

> **重要**：探针用 `nanobanana.py`（单张生成），批量处理用 `generate_and_upload_images.py`（支持 `--process-file`）。两个是不同脚本，不要混淆。

```bash
# 步骤 1：用默认模型（pro）探针（nanobanana.py 仅用于探针）
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "test" --size 1024x1024 --output /tmp/gemini_probe.jpg
# 成功 → 用 generate_and_upload_images.py --process-file 批量生成
python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py \
  --process-file /absolute/path/to/article.md

# 步骤 2：pro 失败（503/429）→ 降级到 flash 探针
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "test" --size 1024x1024 --output /tmp/gemini_probe.jpg \
  --model gemini-2.5-flash-image
# 成功 → 用 flash 模型继续批量生成
python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py \
  --process-file /absolute/path/to/article.md --model gemini-2.5-flash-image

# 步骤 3：flash 也失败（503/429/No data received）→ 跳过 AI 图片，保留占位符
```

**备选方案：用 nanobanana.py 逐张生成**（当 generate_and_upload_images.py 不可用时）：
```bash
# 必须先创建输出目录（nanobanana.py 不会自动创建）
mkdir -p /path/to/images/
# 逐张生成，每张指定 --prompt 和 --output
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "your prompt" --size 1344x768 --output /path/to/images/cover.jpg
# 生成后需手动上传 CDN 并替换文章中的占位符
```

**模型降级链**：`env.json:gemini_image_model`（默认，质量最高）→ `gemini-3.1-flash-image-preview`（中间降级）→ `gemini-2.5-flash-image`（速度快，可用性高）→ 保留占位符

**3. 截图与 AI 图解耦**
- 截图（shot-scraper）不依赖 Gemini API，始终可执行
- AI 图依赖 Gemini，可能不可用
- 图片生成时：先跑截图部分，再跑 AI 图。Gemini 不可用时截图照常完成

**IF ANY REQUIRED CHECKBOX IS UNCHECKED, THE TASK IS INCOMPLETE.**

---

## Knowledge Base Integration

**当工作目录是 Obsidian 知识库时，文章必须保存到对应分类目录。** 详见 [knowledge-base-rules.md](references/knowledge-base-rules.md)

快速规则：
- 检测 `02-技术/` 目录存在 → 自动匹配子目录
- 目录不存在 → `mkdir -p` 创建
- 微信 HTML → `03-创作/已发布/<年月>/`

---

## User Interaction

**必须使用 AskUserQuestion 收集需求，每次只问一个问题。** 详见 [user-interaction-guide.md](references/user-interaction-guide.md)

交互流程：Topic → Audience → Depth → Images → Additional Info

---

## Core Capabilities

### 1. Technical Article Creation
- YAML frontmatter (title, date, tags, category, status, aliases)
- Obsidian callouts (`> [!info]`, `> [!warning]`, `> [!tip]`)
- Complete, runnable code examples with type annotations
- Verified technical accuracy (no hallucinated commands)
- Explicit reference links with working URLs

### 2. Image Generation & Integration
- Cover: 16:9 (1344x768), Rhythm: 3:2 (1248x832) every 400-600 words
- Auto-upload to PicGo/GitHub CDN, embed CDN URLs
- **ASCII Diagram → AI Image Replacement**: Replace ASCII art architecture diagrams (box-drawing characters ┌──┐│└──┘) with AI-generated architecture illustrations
- Details: [image-generation-guide.md](references/image-generation-guide.md)

### 3. Content Optimization
- Refine existing articles for clarity and accuracy
- Replace broken links, add missing code examples

---

## Workflow

> 详细流程请查看 **[WORKFLOW.md](./WORKFLOW.md)**

### Standard Flow

```
Phase A: 写作前（并行优化）
  1. Clarify Requirements（用户明确指定时跳过）
  1a. Determine Save Directory（knowledge base auto-match）
  2. Feature Discovery（工具类文章必须：--help 全量扫描 + 官方博客/Changelog）
  3. Batch Verify（链接并行 curl + 命令链式验证，合并为最少 bash 调用）

Phase B: 写作（先文章后图片）
  4. Content Generation → Write tool 保存文件
  5. SCREENSHOT placeholders（引用外部内容时必须）
  6. Mermaid → image（流程图/架构图渲染为 PNG，禁止保留代码块）
  7. Image auto-process（探针用 nanobanana.py → 批量用 generate_and_upload_images.py --process-file，截图始终执行）
  8. Verify image replacement（检查残留占位符，仅 Gemini 完全不可用时才保留）

Phase C: 写作后（按场景裁剪）
  9. Self-check（收尾段落、红旗词、章节深度、Hook 长度、description、重复图片、外链、Mermaid 残留）
 10. Verify content depth（字数由用户选择决定）
 11. 发布模式：/content-reviewer ≥ 55/70 → /wechat-seo-optimizer
     草稿模式：自行快速检查，跳过 reviewer 和 SEO
 12. 简洁表格汇总（绝对路径 + 图片状态含未解决占位符 + 评分）
```

### Article-Only Workflow (Fast Track)

Same as standard but skip step 6-8 (Mermaid/images). Include placeholders for later:
```markdown
<!-- IMAGE: cover - 封面图 (16:9) -->
<!-- PROMPT: your image generation prompt here -->
```

### ASCII Diagram Replacement Workflow

**自动流程（推荐）**：

文章中的 ASCII 图表（含 `┌ ─ │ └ ▼` 等字符）现在会在图片自动处理阶段被自动识别和替换：

```markdown
<!-- IMAGE: architecture - 系统架构图 (1248x832) -->
<!-- PROMPT: 技术架构图，包含用户界面层、核心引擎层、上下文管理层、基础存储层，使用蓝色调扁平设计 -->
```

**手动流程（可选）**：

```
1. 识别 ASCII 图表：使用正则表达式定位含框线字符的代码块
2. 设计提示词：描述架构层次、连接关系、配色方案（使用中文，简单直接）
3. 生成图片：使用 `generate_and_upload_images.py` 脚本处理
4. 替换内容：替换整个 ``` 代码块为 Markdown 图片链接
```

**关键改进**：
- **自动识别**：脚本现在能自动识别和处理 ASCII 架构图
- **提示词优化**：添加了更清晰的提示词设计指南
- **批量处理**：支持与其他图片同时批量处理
- **容错机制**：失败时保留原始 ASCII 图表

**Prompt 设计要点**：
- 描述架构层次和组件关系
- 说明数据流向和连接方式
- 指定设计风格（如"蓝色调扁平设计"）
- 包含关键标签和术语

---

## Best Practices

### Writing Style
- **No AI flavor:** No marketing fluff, fake engagement, exclamation overuse
- **No emoji in headings:** NEVER use emoji in article title or section headings
- **Direct and technical:** Focus on accuracy over readability

### Structure
- YAML frontmatter required on every article, **必须包含 `description` 字段**（120 字以内摘要）
- Obsidian callouts for key information
- **禁止在文章末尾设置独立的「参考资料」区域**——所有参考链接必须以 `[名称](url)` 格式内联到正文中首次提及的位置（微信转换器会自动提取为尾注引用，独立区域会导致重复）
- No redundant sections: 避免"互动环节""写在最后""下期预告"
- **同一章节内不放两张功能相同的配图**（如同一流程图的两个版本）

### Code & Links
- Code must be runnable with type annotations and error handling
- Reference links use inline format: `[Name](https://url)` — NEVER `[[double brackets]]`
- Verify all links return HTTP 200
- Technical comparisons use parameter tables (cost, latency, memory)
- **微信平台：外部链接改为搜索指引**（如「搜索 关键词」），微信公众号不支持外链跳转

### Images
- 1 cover + 4-6 rhythm images per 3000-word article
- Unique filenames per article (e.g., `ollama_cover.jpg`)
- ASCII architecture diagrams → AI images: replace ```` ``` ```` code blocks containing box-drawing characters with generated illustrations
- **Mermaid 图表（flowchart/sequence/gantt 等）必须渲染为 PNG 图片**，不得以代码块形式留在文章中。渲染命令：`npx mmdc -i file.mmd -o file.png -b transparent`。注意 Mermaid 节点标签中 `\n` 不会渲染换行，须改用 `<br/>`
- **普通代码块（bash/json/yaml/python 等）保留原样**，不需要转图片
- Screenshot rules: see [image-generation-guide.md](references/image-generation-guide.md)

### Project Disambiguation
- When user mentions a project, FIRST search using WebSearch/GitHub API
- If multiple projects found, list all candidates and ask user to confirm
- NEVER assume which project the user means

### Output
- Save to knowledge base directory when detected, otherwise user's pwd
- Use relative paths when displaying to user, absolute paths for scripts
- Never hardcode paths

---

## Setup

### Quick Start (2 min)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API Key (unified config)
# All keys are stored in ~/.claude/env.json (see env.example.json for template)
# The Python scripts auto-load from env.json via load_env.py
# Or set shell env: export GEMINI_API_KEY="your_key" (legacy, still works)

# 3. Start using
@article-generator 写一篇关于 Docker 的技术文章
```

For advanced config, see [INSTALL.md](./INSTALL.md)

---

## Documentation Map

- **SKILL.md** (this file) — Core guide and quick reference
- **[WORKFLOW.md](./WORKFLOW.md)** — Detailed workflow, interaction patterns, scenarios
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** — Error diagnosis and solutions
- **[INSTALL.md](./INSTALL.md)** — Installation and configuration

### references/
- **[knowledge-base-rules.md](references/knowledge-base-rules.md)** — Obsidian KB directory mapping
- **[verification-checklist.md](references/verification-checklist.md)** — Pre-writing verification steps
- **[user-interaction-guide.md](references/user-interaction-guide.md)** — AskUserQuestion templates
- **[image-generation-guide.md](references/image-generation-guide.md)** — Image config, scripts, placeholders
- **[technical_blog_style_guide.md](references/technical_blog_style_guide.md)** — Writing rules
- **[gemini_image_generation.md](references/gemini_image_generation.md)** — Gemini API guide
- **[picgo_setup_guide.md](references/picgo_setup_guide.md)** — PicGo configuration

### scripts/ & assets/
- `scripts/` — Python scripts (image generation, upload)
- `assets/` — Templates

---

**Version:** 3.3 (2026-03-19)
**Changes:** Fixed image placeholder regex to support multi-line, added duplicate reference protection, improved ASCII diagram handling workflow, clarified documentation format requirements
