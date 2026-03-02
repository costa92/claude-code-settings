---
name: article-generator
description: Generate technical blog articles with authentic, non-AI style. Outputs Markdown format with YAML frontmatter, Obsidian callouts, code examples, and CDN images. Avoids marketing fluff and fake engagement. Supports image generation via Gemini API and automatic upload to PicGo image hosting.
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
6. **[ ] Image generation (if requested)** — 先执行 Gemini 探针测试（见下方），失败则保留占位符跳过
7. **[ ] Update article with CDN URLs** — 截图和 AI 图分开处理，截图通常不受 Gemini 影响

### Phase C: 写作后（按场景裁剪）
8. **[ ] Self-check** — 跑 reviewer 前快速自检常见扣分项：
   - 有收尾行动指引段落？（不是"希望对你有帮助"）
   - 有红旗词？（搜索"无缝""赋能""一站式""综上所述"等）
   - 每个章节有足够深度？（≥2 条命令或代码 + 解释，不能只有 1 条命令 1 句话）
   - 开头 Hook 在 100 字内？环境声明用 callout 包裹？
9. **[ ] Verify content depth** — 字数要求见下表
10. **[ ] Quality gate** — 按场景选择审查模式：
   - **发布模式**（默认）：运行 `/content-reviewer` ≥ 48/60，运行 `/wechat-seo-optimizer`
   - **草稿/测试模式**（用户说"测试""草稿""先看看"）：自行快速检查事实准确性和链接，跳过 reviewer 和 SEO
11. **[ ] Confirm completion** — 用简洁表格汇总，必须包含以下信息：
    - **文件绝对路径**（方便跨 session 接手）
    - **图片状态**：已上传数 / 总数，如有未生成的占位符需列出具体数量和待执行命令
    - **审查结果**：评分和状态

**字数要求：**

| 文章类型 | 字数范围 | 触发词 |
|---------|---------|--------|
| 快速入门 | 500-1000 字 | "快速入门""quick start""简短" |
| 实战教程 | 2000-3000 字 | 默认 |
| 深度解析 | 4000+ 字 | "深度""详细""全面" |

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
```bash
# 步骤 1：用默认模型（pro）探针
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "test" --size 1024x1024 --output /tmp/gemini_probe.jpg
# 成功 → 用默认模型继续 --process-file

# 步骤 2：pro 失败（503/429）→ 降级到 flash
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "test" --size 1024x1024 --output /tmp/gemini_probe.jpg \
  --model gemini-2.5-flash-image
# 成功 → 用 flash 模型继续 --process-file --model gemini-2.5-flash-image

# 步骤 3：flash 也失败（503/429/No data received）→ 跳过 AI 图片，保留占位符
```

**模型降级链**：`gemini-3-pro-image-preview`（默认，质量最高）→ `gemini-2.5-flash-image`（速度快，可用性高）→ 保留占位符

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
  6. Gemini 探针 → 可用则 --process-file，不可用则保留占位符
  7. 截图始终执行（不依赖 Gemini）

Phase C: 写作后（按场景裁剪）
  8. Self-check（收尾段落、红旗词、章节深度、Hook 长度）
  9. 发布模式：/content-reviewer ≥ 48 → /wechat-seo-optimizer
     草稿模式：自行快速检查，跳过 reviewer 和 SEO
 10. 简洁表格汇总（绝对路径 + 图片状态含未解决占位符 + 评分）
```

### Article-Only Workflow (Fast Track)

Same as standard but skip step 6-7 (images). Include placeholders for later:
```markdown
<!-- IMAGE: cover - 封面图 (16:9) -->
<!-- PROMPT: your image generation prompt here -->
```

---

## Best Practices

### Writing Style
- **No AI flavor:** No marketing fluff, fake engagement, exclamation overuse
- **No emoji in headings:** NEVER use emoji in article title or section headings
- **Direct and technical:** Focus on accuracy over readability

### Structure
- YAML frontmatter required on every article
- Obsidian callouts for key information
- Single reference section at end, **参考资料区是纯文字列表，禁止放置图片**
- No redundant sections: 避免"互动环节""写在最后""下期预告"

### Code & Links
- Code must be runnable with type annotations and error handling
- Explicit links: `**Name**: https://url` — NEVER `[[double brackets]]`
- Verify all links return HTTP 200
- Technical comparisons use parameter tables (cost, latency, memory)

### Images
- 1 cover + 4-6 rhythm images per 3000-word article
- Unique filenames per article (e.g., `ollama_cover.jpg`)
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

# 2. Set API Key (https://aistudio.google.com/apikey)
export GEMINI_API_KEY="your_api_key_here"

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

**Version:** 3.0 (Refactored 2026-03-02)
**Changes:** Split large SKILL.md into core instructions + 4 reference files per Agent Skills spec (<5000 tokens body)
