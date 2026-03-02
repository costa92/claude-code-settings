---
name: article-generator
description: Generate technical blog articles with authentic, non-AI style. Outputs Markdown format with YAML frontmatter, Obsidian callouts, code examples, and CDN images. Avoids marketing fluff and fake engagement. Supports image generation via Gemini API and automatic upload to PicGo image hosting.
---

# Article Generator

**专注于生成技术博客文章（Markdown/Obsidian 格式）**

> 查看 [快速开始指南 (5分钟)](QUICKSTART.md) | [完整示例](examples/)

---

## Execution Checklist (Read This FIRST)

**Before you finish ANY article generation task, verify ALL items below:**

1. **[ ] Save article to file** — Use `Write` tool to save `.md` file，NEVER just display in chat
2. **[ ] Verify content** — Follow [verification-checklist.md](references/verification-checklist.md)
3. **[ ] Generate AI images (if requested)** — See [image-generation-guide.md](references/image-generation-guide.md)
4. **[ ] Generate screenshots for external content (MANDATORY)** — 即使用户说"不需要图片"，截图仍必须生成——截图是事实性素材，不是装饰性插图
5. **[ ] Update article with image URLs** — Replace placeholders with CDN URLs
6. **[ ] Verify content depth** — Word count > 2000 words (unless "quick start")
7. **[ ] Run content-reviewer skill** — 综合评分 ≥ 48 且无必须修改项
8. **[ ] Run wechat-seo-optimizer skill** — 生成标题方案 + 微信摘要 + 关键词策略
9. **[ ] Confirm completion to user** — Report file path, image status, review score

**IF ANY CHECKBOX IS UNCHECKED, THE TASK IS INCOMPLETE.**

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
1. Clarify Requirements (AskUserQuestion)
1a. Determine Save Directory (knowledge base auto-match)
2. Research & Verification (MANDATORY) — see references/verification-checklist.md
3. Content Generation (frontmatter, headings, code, callouts, links)
4. SAVE ARTICLE TO FILE (MANDATORY — Write tool)
5. Image Generation (if requested) — see references/image-generation-guide.md
5a. Screenshots for External Content (MANDATORY)
6. Final Review (links, code, no AI clichés)
7. Run /content-reviewer (≥ 48/60)
8. Run /wechat-seo-optimizer
```

### Article-Only Workflow (Fast Track)

Same as standard but skip step 5 (images). Include placeholders for later:
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
