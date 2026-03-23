---
name: article-craft:write
description: "Generate technical article content with style guide, Obsidian format, and image placeholders. Use when writing a technical blog article."
---

# article-craft:write — Technical Article Writer

Generate a complete technical blog article in Markdown/Obsidian format, with YAML frontmatter, callouts, code examples, and image placeholders.

---

## Inputs

This skill accepts context from two sources:

### A. Orchestrated mode (from article-craft:requirements)

When invoked by the orchestrator, the requirements skill passes structured context:

- **topic** — what the article is about
- **audience** — target reader profile (beginner / intermediate / advanced)
- **depth** — article length class (see Word Count table below)
- **key_points** — specific points to cover
- **save_path** — target file path (if determined)

Use all provided fields directly. Do not re-ask the user.

### B. Standalone mode (user invokes directly)

If no requirements context is provided, apply the same **smart inference** as the requirements skill:

1. Analyze the topic for writing style, depth, and audience signals (see `requirements/SKILL.md` inference rules)
2. If topic provides clear signals (e.g., "Docker 教程" → style=A, depth=tutorial, audience=intermediate), use defaults directly
3. Only ask if genuinely ambiguous — show inferred values and let user adjust in one confirmation question

### Word Count Reference

| Article Type | Character Range | Trigger Words |
|---|---|---|
| Quick start | 500-1000 | "快速入门" "quick start" "简短" |
| Tutorial | 2000-3000 | default |
| Deep dive | 4000+ | "深度" "详细" "全面" |

> Word count is guided by user choice. Never truncate content to fit a platform limit — if the user chose deep dive, write 4000+ characters.

---

## Writing Style Selection

文章有 7 种写作风格，根据内容类型自动选择或由用户指定。

**完整风格定义见：** `references/writing-styles.md`

| 风格 | 适用场景 | 关键特征 |
|------|---------|---------|
| **A: 技术教程** | 教程、指南、入门 | Callouts + 完整代码 + 对比表格 |
| **B: 经验分享** | 工具分享、技巧清单、"N个..." | 极短段落 + 口语 + 高频截图 |
| **C: 深度长文** | 原理解析、源码分析 | 长段论述 + 架构图 + 源码 |
| **D: 评测对比** | 产品对比、框架选型 | 多维度表格 + 基准数据 + 明确推荐 |
| **E: 资讯快报** | 新版本发布、更新解读 | 极简段落 + 截图 + 链接密集 |
| **F: 项目复盘** | 踩坑记录、架构演进 | 叙事驱动 + before/after 数据 |
| **G: 观点输出** | 技术观点、趋势判断 | 鲜明立场 + 论据充分 + 预设反驳 |

### 自动判断规则

| 内容信号 | 推荐风格 |
|---------|---------|
| "教程"、"指南"、"入门"、"实战"、"部署" | A |
| "分享"、"推荐"、"技巧"、"隐藏"、标题含"N个" | B |
| "原理"、"源码"、"架构"、"设计"、"底层" | C |
| "对比"、"评测"、"vs"、"选型"、"哪个好" | D |
| "更新"、"发布"、"新版本"、"changelog" | E |
| "复盘"、"踩坑"、"迁移"、"优化了"、"从X到Y" | F |
| "为什么"、"我认为"、"不推荐"、"应该" | G |
| 来自 YouTube 视频转文章 | B |
| 默认 | A |

如果不确定，使用 AskQuestion 让用户选择风格。

**选定风格后，先读 `references/writing-styles.md` 中对应风格的完整规则，再开始写作。**

---

## Process

Follow these steps in order. Each step is mandatory unless marked optional.

### Step 1: Load Style Guide & Select Style

1. Read the style guide: `skills/write/style-guide.md`
2. Read the writing styles reference: `references/writing-styles.md`
3. **Determine the writing style** using the auto-judgment rules in the styles reference (or user specification)
4. Internalize the selected style's rules: opening pattern, section structure, image rhythm, tone, closing pattern

### Step 2: Determine Save Path

1. Check if the working directory contains an Obsidian knowledge base (look for `02-技术/` directory).
2. If found, auto-match a subdirectory under `02-技术/` based on the article's technology category.
3. If no match, `mkdir -p` to create the appropriate subdirectory.
4. If no knowledge base detected, save to the user's current working directory.
5. If a `save_path` was provided by the requirements skill, use that directly.

See `references/knowledge-base-rules.md` for the full directory mapping.

### Step 3: Generate Article Content

Write the full article using the `Write` tool — **NEVER just display content in chat**. The article must follow this structure:

#### 3a. YAML Frontmatter (required)

Every article must begin with complete YAML frontmatter:

```yaml
---
title: "文章标题（15-25 字，含核心技术关键词和读者收益）"
date: YYYY-MM-DD
tags:
  - tag1
  - tag2
  - tag3
category: 分类名称
status: draft
aliases:
  - 别名1
description: "120 字以内摘要，用作微信文章摘要。必须是有意义的概括，不能照搬标题。"
---
```

**Required fields**: title, date, tags, category, status, description.
**Optional fields**: aliases.
**Series fields** (auto-injected when writing as part of a series):
```yaml
series: "系列名称"
series_order: 2
series_total: 5
```

The `description` field is critical — it serves as the WeChat article summary and must be a standalone abstract (max 120 Chinese characters).

#### 3b. Title + Cover Image Placeholder

```markdown
# 文章标题

<!-- IMAGE: cover - 封面图描述 (16:9) -->
<!-- PROMPT: Minimalist technical illustration describing the concept, isometric view, tech blue palette, clean lines -->
```

#### 3b-series. Series Navigation (only if series context is provided)

If writing as part of a series, inject navigation **after the cover image and before the hook**:

```markdown
> [!info] 📚 系列导航
> 本文是《系列名称》系列第 X/Y 篇。
> 上一篇：[上一篇标题](./filename.md) | 下一篇：[下一篇标题](./filename.md)
```

- First article: omit "上一篇"
- Last article: change "下一篇" to "合集：[系列合集](./series-collection.md)"（if exists）
- Visual style prefix: read from series.md, use for ALL image prompts in this article

#### 3c. Opening Hook

**按选定风格的开头模式写开头。** 每种风格的具体开头模板见 `references/writing-styles.md`。

快速参考：
- **A 教程 / D 评测**：痛点 → 方案 → 本文价值（100 字内）
- **B 经验分享**：真实故事/场景切入 → 引出主题 → "话不多说，我们开始"
- **C 深度长文**：结论先行 → 为什么重要 → 本文结构预览
- **E 资讯快报**：一句话说清更新内容 → "快速过一遍"
- **F 项目复盘**：结果先行 → 之前的状况 → 本文讲什么
- **G 观点输出**：争议性结论直接抛出 → 简短说明

**所有风格都禁止的开头**:
- "在当今...的时代" / "随着...的发展"
- 以定义开头: "XXX 是一个..."
- 套路式提问: "你是否也有这样的困扰？"

#### 3d. Core Abstract Callout

**Style A / C / D** — after the hook, include:

```markdown
> [!abstract] 核心要点
> - Point 1
> - Point 2
> - Point 3
```

**Style B / E / F / G** — skip this callout,直接进入正文。

#### 3e. Body Sections

**按选定风格的章节结构写正文。** 每种风格的具体章节模板见 `references/writing-styles.md`。

各风格的核心差异：

| 风格 | 段落长度 | 代码风格 | 图表 | 语气 |
|------|---------|---------|------|------|
| A 教程 | 100-150字 | 完整可运行 | Callouts + 表格 | 专业 |
| B 分享 | 1-2句/段 | 只贴命令 | 截图高频 | 口语化 |
| C 深度 | 150-200字 | 源码片段 | 架构图 | 严谨 |
| D 评测 | 80-120字 | 配置示例 | 多维对比表 | 客观有态度 |
| E 资讯 | 1-3句/段 | 命令摘要 | 截图为主 | 简洁直接 |
| F 复盘 | 80-150字 | 关键变更 | before/after | 复盘冷静 |
| G 观点 | 100-150字 | 少代码 | 少图 | 自信不傲慢 |

**所有风格通用的代码规则：**
- 代码块最长 30 行（移动端阅读）
- 两个代码块之间至少 2-3 句解释
- 不贴与主题无关的样板代码
- **描述流程、架构、数据流向时，使用 `<!-- IMAGE -->` 占位符，不要用代码块 + 箭头符号**
- **代码块必须标注语言**（如 ` ```bash `、` ```go `），没有语言标识的代码块只允许用于纯文本输出示例

#### 3f. Image Placeholders

Insert image placeholders throughout the article. The `article-craft:images` skill will process these later.

**完整风格指南见：** `skills/images/image-guide.md` 的 "Visual Style Guide" 部分。

**核心规则 — 设计 Token 一致性：**
1. 根据文章风格从 6 种视觉风格（S1-S6）中选择一种
2. 封面图的 PROMPT 确定**风格约束前缀**（色调 + 风格 + 背景）
3. 所有后续节奏图的 PROMPT **必须复用相同的风格约束前缀**
4. PROMPT 用英文写，结构：`[风格约束], [背景]. [主体内容], [细节]`

**Format**:
```markdown
<!-- IMAGE: name - description (ratio) -->
<!-- PROMPT: [style prefix from cover], [specific content for this image] -->
```

**Placement rules (by style)**:
- **Cover image**: all styles, immediately after `# Title`. Ratio: 16:9.
- **A 教程 / C 深度 / G 观点**: rhythm images every 400-600 words (Gemini 生成图)
- **B 分享 / E 资讯**: screenshots every 2-4 paragraphs (截图优先)
- **D 评测**: comparison charts and benchmark screenshots
- **F 复盘**: before/after data visualizations + architecture diagrams
- Use unique, descriptive names per image.
- **Do NOT place two images with the same purpose** in the same section.

**Screenshot placeholders** (for referencing external content):
```markdown
<!-- SCREENSHOT: url=https://example.com selector=.main-content width=1200 -->
```

#### 3g. Inline Reference Links

All reference links must use inline format at the point of first mention:

```markdown
See the [official documentation](https://example.com/docs) for details.
```

**NEVER** create a standalone "参考资料" or "参考链接" section at the end. The WeChat converter auto-generates footnote references from inline links; a manual section causes duplication.

**NEVER** use Obsidian wiki-style links: `[[Page Name]]` — always use standard Markdown `[Name](URL)`.

#### 3h. Closing Paragraph

**按选定风格的结尾模式收尾。** 每种风格的具体结尾模板见 `references/writing-styles.md`。

快速参考：
- **A 教程**：具体下一步操作（一条命令）
- **B 分享**："写在最后" + 情绪升华 + 互动号召
- **C 深度**：总结要点 + 延伸阅读
- **D 评测**：场景化推荐表格 + 个人选择
- **E 资讯**：值不值得升级 + 官方链接
- **F 复盘**：做对了/做错了/重来会怎么做
- **G 观点**：重申立场 + 承认局限 + 期待讨论

**所有风格禁止的结尾：**
- "希望本文对你有帮助"（Style B 的口语变体"希望能有点帮助。。"例外）
- 无上下文的模板化互动"如果有问题欢迎留言"

**系列文章结尾追加**（仅当 series context 存在时）：

在正常 closing paragraph 之后，追加下一篇预告：

```markdown
---

> [!tip] 📚 下一篇预告
> 《下一篇标题》— 下一篇的核心内容简介（1-2 句）。
```

- 最后一篇：改为系列回顾 + 合集链接

### Step 4: Apply Anti-AI Structure Rules

Before saving, verify the article does not read like AI-generated text:

**禁止 ASCII 流程图/架构图（硬规则）：**
- **绝不在代码块中画 ASCII 流程图、架构图、时序图、光谱图**（用 `│ ├ └ ┌ ─ ▼ ▶ ←→ ↓ ↑ ➜ ➡ ⇒ ⇐` 等箭头/制表符拼的图）
- 所有流程图、架构图、对比图、光谱图**必须使用 `<!-- IMAGE -->` 占位符**，由 images skill 生成图片
- 只有真正的**可执行代码**（bash/python/json 等）才允许放在代码块里
- 伪代码（如 `while True: ...`）是可以的，但如果它在描述一个流程/架构，优先用 IMAGE 占位符
- **没有语言标识的代码块**（` ``` ` 后无语言名）如果内容不是可执行代码或纯文本输出，必须替换为 IMAGE 占位符或改用有序列表

**自检方法：** 写完后扫描所有代码块，符合以下任一条件就必须替换为 IMAGE 占位符：
1. 代码块内包含 `│ ← → ↓ ↑ ▼ ▲ ▶ ◀ ┌ └ ├ ─ ➜ ➡ ⇒ ⇐` 中任意字符，且不是可执行代码
2. 代码块没有语言标识（` ``` ` 后无语言名），且内容描述的是流程、架构或数据流向

**Paragraph structure variation**:
- Consecutive paragraphs must NOT repeat the same structure (e.g., "concept -> explain -> code" twice in a row).
- Mix structures: code-first then reverse explanation, Q&A style, experience-then-principle, comparison table then conclusion.

**Personal perspective** (at least 2 per article):
- Bug/pitfall experience: "我在迁移旧项目时发现——"
- Choice rationale: "选 uv 而不是 poetry 的原因很简单——"
- Judgement: "这个功能设计得很克制，只做了该做的事"
- Real benchmarks: "本机实测，冷启动 2.1 秒"

**Diverse paragraph openings**:
- Never start 2 consecutive paragraphs with "此外" / "另外" / "同时" / "值得注意的是".
- Replace transition words with direct content — jump straight to the next point.

### Step 5: Run Self-Check

**Before saving the file**, apply ALL rules from `references/self-check-rules.md`. The full checklist:

1. **Red-flag words** — Grep the draft for: `无缝|赋能|一站式|综上所述|总而言之|值得注意的是|不难发现|深度解析|全面梳理|链路|闭环|抓手|底层逻辑|方法论|降本增效|实际上|事实上|显然|众所周知|不难看出`. Also flag: "颠覆" / "极致" / "完美解决" / "在当今快速发展的..." / "随着...的不断发展..." / "让我们一起探索...". Every match must be rewritten.

2. **Hook length** — First paragraph must be 100 Chinese characters or fewer (excluding code blocks).

3. **Closing paragraph** — Must be a concrete next-step or brief outlook. No generic well-wishes.

4. **Description field** — Must exist in frontmatter, max 120 characters, meaningful abstract.

5. **Anti-AI structure** — Verify varied paragraph structures, 2+ personal perspectives, diverse openings.

6. **Chapter depth** — Every technical section has at least 2 commands/code snippets plus explanatory text.

7. **Duplicate images** — No two images with the same purpose within the same `##` section.

8. **WeChat external links** — Replace external URLs in body text with search guidance (`搜索「关键词」`). Inline `[Name](url)` links are fine (converter handles them).

9. **Mermaid residue** — No ```` ```mermaid ```` code blocks should remain. All diagrams must be image placeholders.

10. **References inline** — No standalone reference section at article end.

**Quick self-check grep** (run after saving to catch remaining violations):

```bash
grep -nE '无缝|赋能|一站式|综上所述|总而言之|值得注意的是|不难发现|深度解析|全面梳理|链路|闭环|抓手|底层逻辑|方法论|降本增效|实际上|事实上|显然|众所周知|不难看出|希望本文|希望对你|欢迎留言|点个在看|转发给朋友|在当今|随着.*发展|让我们一起' /path/to/article.md
```

No output means all clear. If violations found, fix them and re-save.

### Step 6: Save Article

Use the `Write` tool to save `article.md` to the determined path from Step 2.

Print the absolute file path after saving so subsequent skills can find it.

---

## Outputs

| Output | Description |
|---|---|
| `article.md` | Complete Markdown article saved to disk |
| **Printed path** | Absolute file path displayed in chat for the next skill |

---

## Hand-off

After writing is complete:

- **Next skill**: `article-craft:images` — processes `<!-- IMAGE -->` and `<!-- SCREENSHOT -->` placeholders
- Pass the absolute file path to the images skill
- If the user explicitly says "no images" or "article only", skip the hand-off

In orchestrated mode, the orchestrator handles the hand-off automatically.

---

## Standalone Mode Behavior

When invoked directly (not via orchestrator):

1. Use AskQuestion to collect topic, audience, and length if not provided.
2. Skip the requirements skill — go straight to writing.
3. After saving, suggest the user run `article-craft:images` if the article contains image placeholders.
4. Provide a completion summary:

```
| Item | Value |
|---|---|
| File | /absolute/path/to/article.md |
| Words | ~NNNN characters |
| Images | N placeholders (cover + N-1 rhythm) |
| Status | draft — run article-craft:review for quality check |
```

---

## Style Guide Quick Reference

> The full style guide is at `skills/write/style-guide.md`. This section extracts the most critical rules.

### Title Formula

**按选定风格生成标题。** 各风格的标题模式见 `references/writing-styles.md`。

| 风格 | 标题模式 | 长度 | 示例 |
|------|---------|------|------|
| A 教程 | [量化]+[动作]+[技术词]+[收益] | 15-25字 | "5分钟用 Docker 部署你的第一个 Web 应用" |
| B 分享 | [分享/推荐]+[数字]+[好奇心] | 20-35字 | "分享10个你可能不知道的Claude Code隐藏命令" |
| C 深度 | [技术词]+[具体结果] | 15-30字 | "Go GC 调优：从 200ms 停顿降到 5ms" |
| D 评测 | [A] vs [B] — [维度] | 15-30字 | "Bun vs Deno vs Node.js 运行时终极对比" |
| E 资讯 | [产品]+[版本]+[N个亮点] | 15-30字 | "Claude Code 3.0：5个最值得关注的新功能" |
| F 复盘 | [我们如何]+[从X到Y] | 20-35字 | "我们如何将 API 响应时间从 2s 降到 50ms" |
| G 观点 | [为什么/不再]+[争议性结论] | 15-25字 | "为什么我不再推荐 TypeScript" |

### Readability Rhythm

- Paragraphs: max 150 characters, split if longer
- Between code blocks: at least 2-3 sentences of explanation (never two consecutive code blocks with no text between)
- Long sentences: max 60 characters, break if longer
- Insert a rhythm image every 400-600 words

### Forbidden / Allowed Content

**所有风格禁止：**
- "赋能" "颠覆" "极致" "一站式"
- "在当今快速发展的..." "综上所述..." "让我们一起探索..."
- "效率提升 300%" "彻底改变你的工作方式" "从入门到精通"
- 标题和章节标题中使用 emoji

**风格特定规则详见 `references/writing-styles.md` 最末"通用规则"部分。**

---

## Article Template Reference

A complete article template with all sections and placeholder patterns is at:

```
{SKILL_DIR}/skills/write/templates/article.md
```

Use it as a structural reference. Adapt sections to fit the specific article — not every section applies to every topic.

---

**Version:** 1.0 (2026-03-22)
**Ported from:** article-generator v3.3 (Phase B + style guide + self-check rules)
