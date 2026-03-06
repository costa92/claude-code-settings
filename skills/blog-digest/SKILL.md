---
name: blog-digest
description: 从 Karpathy 推荐的 90 个顶级技术博客抓取最新文章，Gemini AI 多维评分筛选，生成每日精选摘要（中英双语、Mermaid 图表）。需要 gemini_api_key。适合深度技术文章精读。用户说「技术博客精选」「每日文摘」「blog-digest」「/digest」时触发。
---

# Blog Digest — 技术博客精选

从 Karpathy 推荐的 90 个顶级技术博客抓取最新文章，通过 Gemini AI 多维评分筛选，生成每日精选摘要（中英双语、Mermaid 可视化图表）。

**脚本**：`~/.claude/skills/blog-digest/scripts/digest.ts`

## 配置

从 `~/.claude/env.json` 读取（无需重复询问）：

| 字段 | 用途 | 默认值 |
|------|------|--------|
| `gemini_api_key` | Gemini AI 评分（必需） | — |
| `openai_api_key` | Gemini 失败时降级 | — |
| `openai_api_base` | 降级接口地址 | `https://api.openai.com/v1` |
| `openai_model` | 降级模型名 | `gpt-4o-mini` |
| `digest_time_range` | 抓取时间范围（小时） | `48` |
| `digest_top_n` | 保留篇数 | `15` |
| `digest_language` | 输出语言（zh/en） | `zh` |

---

## Step 1：读取配置

```bash
jq '{gemini_api_key, openai_api_key, openai_api_base, openai_model,
     digest_time_range, digest_top_n, digest_language}' ~/.claude/env.json 2>/dev/null
```

**分支**：
- `gemini_api_key` 非空 → 展示当前配置，询问是否直接运行或修改参数
- `gemini_api_key` 为空 → 进入 Step 2 收集配置

---

## Step 2：收集配置（首次或 key 为空时）

**2a. 收集 Gemini API Key**（可在 https://aistudio.google.com/apikey 免费获取）：

```bash
jq --arg key "<用户输入>" '.gemini_api_key = $key' ~/.claude/env.json > ~/.claude/env.json.tmp \
  && mv ~/.claude/env.json.tmp ~/.claude/env.json
```

**2b. 收集运行偏好**（用 AskUserQuestion，可跳过使用默认值）：

- 时间范围：24h / 48h（推荐）/ 72h / 7天
- 精选数量：10 / 15（推荐）/ 20 篇
- 输出语言：中文（推荐）/ English

回写偏好到 env.json：

```bash
jq --argjson hours <hours> --argjson topn <topn> --arg lang "<lang>" \
  '.digest_time_range = $hours | .digest_top_n = $topn | .digest_language = $lang' \
  ~/.claude/env.json > ~/.claude/env.json.tmp \
  && mv ~/.claude/env.json.tmp ~/.claude/env.json
```

---

## Step 3：执行脚本

```bash
SKILL_DIR="$HOME/.claude/skills/blog-digest"

export GEMINI_API_KEY="$(jq -r '.gemini_api_key // empty' ~/.claude/env.json)"
export OPENAI_API_KEY="$(jq -r '.openai_api_key // empty' ~/.claude/env.json)"
export OPENAI_API_BASE="$(jq -r '.openai_api_base // empty' ~/.claude/env.json)"
export OPENAI_MODEL="$(jq -r '.openai_model // empty' ~/.claude/env.json)"

HOURS="$(jq -r '.digest_time_range // 48' ~/.claude/env.json)"
TOP_N="$(jq -r '.digest_top_n // 15' ~/.claude/env.json)"
LANG="$(jq -r '.digest_language // "zh"' ~/.claude/env.json)"
OUTPUT_DIR="$(jq -r '.blog_digest_output_dir // empty' ~/.claude/env.json)"

# OUTPUT_DIR 为空时默认当前目录下的 output/
OUTPUT_DIR="${OUTPUT_DIR:-./output}"
OUTPUT_DIR="${OUTPUT_DIR/#\~/$HOME}"   # 展开 ~ 为绝对路径
mkdir -p "$OUTPUT_DIR"

npx -y bun "${SKILL_DIR}/scripts/digest.ts" \
  --hours "$HOURS" \
  --top-n "$TOP_N" \
  --lang "$LANG" \
  --output-dir "$OUTPUT_DIR"
```

---

## Step 4：展示结果

成功时输出：
- 报告路径：`./output/digest-YYYYMMDD.md`
- 统计：扫描源数 → 抓取文章数 → 时间范围内 → 精选数
- Top 3 预览：中文标题 + 一句话摘要

**报告结构**（与 news-daily 格式一致，详见 `references/output-format.md`）：

| 板块 | 内容 |
|------|------|
| 标题 | `# Blog Digest · {年}年{月}月{日}日` |
| 核心摘要 | 3-5 条分条要点（`- `开头），提炼宏观趋势 |
| 📊 数据概览 | 统计表格 + Mermaid 分类饼图 + 关键词柱状图 |
| 分类文章列表 | 6 大分类：AI/ML、安全、工程、工具/开源、观点/杂谈、其他 |
| 每篇文章 | 中文标题 + 摘要 + `**关键信息**: tags` + `📎 原文链接: [source](url)` |
| 页脚 | `数据来源: ...` + `生成时间: YYYY-MM-DD HH:MM` |

---

## 故障排除

| 错误 | 原因 | 解决 |
|------|------|------|
| `GEMINI_API_KEY not set` | env.json 中 key 为空 | 重新运行填写 key |
| `Gemini 配额超限` | 免费额度用尽 | 自动降级到 openai_api_key |
| `Failed to fetch N feeds` | 部分 RSS 源不可用 | 正常现象，脚本跳过继续 |
| `No articles found` | 时间范围内无新文章 | 扩大 `digest_time_range`（如 72）|

---

## 信息源

90 个 RSS 源来自 [Hacker News Popularity Contest 2025](https://refactoringenglish.com/tools/hn-popularity/)，包括：

`simonwillison.net` · `paulgraham.com` · `overreacted.io` · `gwern.net` · `krebsonsecurity.com` · `antirez.com` · `daringfireball.net` · `eli.thegreenplace.net` 等。
