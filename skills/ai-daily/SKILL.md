---
name: ai-daily-news
description: Fetches AI news from multiple sources (smol.ai, Import AI, Last Week in AI, Ahead of AI, TLDR AI) and generates structured markdown with intelligent summarization and categorization. Optionally creates beautiful HTML webpages with Apple-style themes and shareable card images. Use when user asks about AI news, daily tech updates, or wants news organized by date or category.
---

# AI Daily News

Fetches AI industry news from multiple sources, intelligently summarizes and categorizes using built-in Claude AI capabilities, outputs structured markdown, and optionally generates themed webpages and shareable card images.

## Available Sources

### English Daily Sources
| Source ID | Name | Frequency | Description |
|-----------|------|-----------|-------------|
| `smol` | smol.ai | Daily | Daily AI news digest (default) |
| `tldrai` | TLDR Tech | Daily | Daily tech newsletter covering AI, startups, and dev news |

### English Weekly Sources
| Source ID | Name | Frequency | Description |
|-----------|------|-----------|-------------|
| `importai` | Import AI | Weekly | Jack Clark's newsletter on AI research, policy, and industry |
| `lastweekinai` | Last Week in AI | Weekly | Weekly text and audio summaries of AI news |
| `aheadofai` | Ahead of AI | Weekly | Sebastian Raschka's ML/AI research updates |

### Chinese Sources (中文渠道)
| Source ID | Name | Frequency | Description |
|-----------|------|-----------|-------------|
| `qbitai` | 量子位 | Daily | 中国领先的AI科技媒体，报道AI前沿动态 |

### Academic Sources (学术论文)
| Source ID | Name | Frequency | Description |
|-----------|------|-----------|-------------|
| `arxiv_ai` | ArXiv AI | Daily | Latest AI research papers (cs.AI) |
| `arxiv_ml` | ArXiv ML | Daily | Latest Machine Learning papers (cs.LG) |

### Tech Communities (技术社区)
| Source ID | Name | Frequency | Description |
|-----------|------|-----------|-------------|
| `hn_ai` | Hacker News AI | Realtime | AI discussions from HN (30+ points) |

## Quick Start

```bash
# Yesterday's news (default source: smol.ai)
昨天AI资讯

# From specific source
Import AI 最新资讯
获取 Last Week in AI 的内容

# Chinese source (中文渠道)
量子位最新资讯
获取量子位的AI新闻

# Academic papers (学术论文)
ArXiv 今天的AI论文
最新的机器学习论文

# Tech community (技术社区)
Hacker News 上的AI讨论

# From all sources
获取所有渠道的AI新闻

# Specific date
2026-01-13的AI新闻

# By category
昨天的模型发布相关资讯

# Generate webpage
昨天AI资讯，生成网页

# Generate shareable card image
昨天AI资讯，生成分享图片
```

## Supported Query Types

| Type | Examples | Description |
|------|----------|-------------|
| **相对日期** | "昨天AI资讯" "前天的新闻" "今天的AI动态" | Yesterday, day before, today |
| **绝对日期** | "2026-01-13的新闻" | YYYY-MM-DD format |
| **指定来源** | "Import AI资讯" "量子位新闻" "ArXiv论文" | Fetch from specific source |
| **中文渠道** | "量子位资讯" | Chinese AI news |
| **学术论文** | "ArXiv AI论文" "最新ML论文" | Academic papers from ArXiv |
| **技术社区** | "HN上的AI讨论" | Hacker News AI discussions |
| **多源获取** | "所有渠道的新闻" "综合AI资讯" | Fetch from all sources |
| **分类筛选** | "模型相关资讯" "产品动态" | Filter by category |
| **网页生成** | "生成网页" "制作HTML页面" | Optional webpage generation |
| **图片生成** | "生成图片" "生成分享卡片" "制作日报卡片" | Generate shareable card image |

---

## Workflow

Copy this checklist to track progress:

```
Progress:
- [ ] Step 1: Parse date and source from user request
- [ ] Step 2: Fetch RSS from selected source(s)
- [ ] Step 3: Check if content exists for target date
- [ ] Step 4: Extract and analyze content
- [ ] Step 5: Generate structured markdown
- [ ] Step 6: Ask about webpage generation (if requested)
- [ ] Step 7: Generate shareable card image (if requested)
```

---

## Step 1: Parse Date and Source

Extract the target date and source from user request.

### Date Parsing

| User Input | Target Date | Calculation |
|------------|-------------|-------------|
| "昨天AI资讯" | Yesterday | today - 1 day |
| "前天AI资讯" | Day before yesterday | today - 2 days |
| "2026-01-13的新闻" | 2026-01-13 | Direct parse |
| "今天的AI动态" | Today | Current date |

**Date format**: Always use `YYYY-MM-DD` format (e.g., `2026-01-13`)

### Source Parsing

| User Input | Source ID | Notes |
|------------|-----------|-------|
| "Import AI资讯" | `importai` | Jack Clark's newsletter |
| "TLDR AI新闻" | `tldrai` | Daily quick summaries |
| "Last Week in AI" | `lastweekinai` | Weekly roundup |
| "Ahead of AI" | `aheadofai` | Sebastian Raschka |
| "量子位资讯" / "量子位新闻" | `qbitai` | Chinese AI media |
| "ArXiv AI论文" | `arxiv_ai` | AI papers (cs.AI) |
| "ArXiv ML论文" / "机器学习论文" | `arxiv_ml` | ML papers (cs.LG) |
| "Hacker News AI" / "HN讨论" | `hn_ai` | Tech community |
| "所有渠道" / "综合资讯" | `--all-sources` | Fetch from all |
| (default) | `smol` | smol.ai daily digest |

---

## Step 2: Fetch RSS

### Single Source (Default)

```bash
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --source SOURCE_ID --latest
```

Examples:
```bash
# Default source (smol.ai)
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --latest

# Import AI
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --source importai --latest

# TLDR AI
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --source tldrai --latest
```

### Multiple Sources

```bash
# Specific sources
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --sources smol importai tldrai --latest

# All sources
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --all-sources --latest
```

### List Available Sources

```bash
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --list-sources
```

### Get Specific Date

```bash
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --source SOURCE_ID --date 2026-01-13
```

### Check Available Dates

```bash
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --source SOURCE_ID --date-range
```

---

## Step 3: Check Content

Verify if content exists for the target date.

### When Content Exists

Continue to Step 4.

### When Content NOT Found

**Auto-fallback**: If the target date has no content, automatically use `--latest` to get the most recent available content, and inform the user:

```markdown
注意：{target_date} 暂无资讯，已自动获取最新可用日期 {latest_date} 的内容。
```

Then continue with the latest content.

**User experience principles**:
1. Auto-fallback to latest available content
2. Inform user about the date change
3. Never leave user stuck with no options

---

## Step 4: Extract and Analyze Content

Use built-in Claude AI capabilities to:

1. **Extract full content** from the RSS entry
2. **Translate to Chinese** - 将所有英文内容翻译成中文
3. **Generate summary** - 3-5 key takeaways (中文)
4. **Categorize** items by topic:
   - Model Releases (模型发布)
   - Product Updates (产品动态)
   - Research Papers (研究论文)
   - Tools & Frameworks (工具框架)
   - Funding & M&A (融资并购)
   - Industry Events (行业事件)
   - Tech Community (技术社区) - for HN discussions
5. **Extract keywords** - Companies, products, technologies
6. **Preserve original links** - 保留每条新闻的原文链接

**Prompt Template**:

```
分析以下 AI 新闻内容并整理输出：

要求：
1. 将所有英文内容翻译成中文
2. 生成 3-5 条核心要点（每条一句话，中文）
3. 按分类整理：模型发布、产品动态、研究论文、工具框架、融资并购、行业事件、技术社区
4. 提取 5-10 个关键词
5. 每条新闻必须附上原文链接，格式：📎 原文链接: [来源名称](URL)

原始内容：
{content}
```

---

## Step 5: Generate Markdown

Output structured markdown following the format in [output-format.md](references/output-format.md).

**重要要求**：
1. **全部中文输出** - 所有标题、摘要、内容必须是中文
2. **保留原链接** - 每条新闻后附上 `📎 原文链接: [来源](URL)`

**Key sections**:
- Title with date (中文格式：AI Daily · 2026年1月19日)
- Core summary (中文要点)
- Categorized news items (中文内容 + 原文链接)
- Keywords (中英文混合)
- Footer with source info

**Example output**:

```markdown
# AI Daily · 2026年1月19日

## 核心摘要

- OpenAI 开始在 ChatGPT 中植入广告以缓解资金压力
- GPT-5.2 Pro 独立完成了一个 45 年未解决的数论猜想证明
- Hacker News 热议：AI 编程工具对 COBOL 开发者的影响

## 产品动态

### ChatGPT 引入广告系统

OpenAI 开始在 ChatGPT 中引入广告功能，这一决定的背后是公司持续增长的运营成本压力。

**关键信息**: OpenAI, ChatGPT, 广告, 商业化

📎 原文链接: [量子位](https://www.qbitai.com/2026/01/370285.html)

## 研究论文

### HPV 疫苗接种 AI 代理系统设计

研究人员开发了一个双重用途的 AI 代理系统，用于解决日本 HPV 疫苗接种犹豫问题。

**关键信息**: AI 代理, HPV 疫苗, RAG, 公共卫生

📎 原文链接: [ArXiv](https://arxiv.org/abs/2601.10718)

## 技术社区

### COBOL 开发者如何看待 AI 编程工具

Hacker News 热帖讨论了 AI 编程工具对 COBOL/大型机开发者的影响。

**关键信息**: COBOL, 大型机, AI 编程, 就业影响

📎 原文链接: [Hacker News](https://news.ycombinator.com/item?id=46678550)

## 关键词

#OpenAI #ChatGPT #ArXiv #HackerNews #COBOL

---
数据来源: 量子位, ArXiv AI, Hacker News AI
```

---

## Step 6: Webpage Generation (Optional)

**Only trigger when user explicitly says**:

- "生成网页"
- "制作HTML页面"
- "生成静态网站"

### Ask User Preferences

```
是否需要生成精美的网页？

可选主题:
- [苹果风](command:使用苹果风主题) - 简洁专业，适合技术内容
- [深海蓝](command:使用深海蓝主题) - 商务风格，适合产品发布
- [秋日暖阳](command:使用秋日暖阳主题) - 温暖活力，适合社区动态
```

### Theme Prompt Templates

See [html-themes.md](references/html-themes.md) for detailed prompt templates for each theme.

**Apple Style Theme** (Key Points):

```markdown
Generate a clean, minimalist HTML page inspired by Apple's design:

**Design**:
- Pure black background (#000000)
- Subtle blue glow from bottom-right (#0A1929 → #1A3A52)
- Generous white space, content density ≤ 40%
- SF Pro Display for headings, SF Pro Text for body
- Smooth animations and hover effects

**Structure**:
- Header: Logo icon + Date badge
- Main: Summary card + Category sections
- Footer: Keywords + Copyright

**Colors**:
- Title: #FFFFFF
- Body: #E3F2FD
- Accent: #42A5F5
- Secondary: #B0BEC5
```

### Save Webpage

Save to `docs/{date}.html`:

```bash
# Save webpage
cat > docs/2026-01-13.html << 'EOF'
{generated_html}
EOF
```

---

## Step 7: Shareable Card Image Generation (Optional)

**Trigger when user explicitly requests**:

- "生成图片"
- "生成分享卡片"
- "制作日报卡片"
- "生成卡片图片"
- "生成分享图"

### Image Generation Process

1. **Build condensed Markdown** for card display:
   - Title and date
   - Core summary (3-5 items)
   - Top items per category (3 items each)
   - Keywords

2. **Call Firefly Card API**:
   - API: `POST https://fireflycard-api.302ai.cn/api/saveImg`
   - Body contains `content` field with Markdown
   - Returns binary image stream (`Content-Type: image/png`)

3. **Save and display result**:
   - Save to `docs/images/{date}.png`
   - Display preview or download link

### API Request Format

```json
{
  "content": "# AI Daily\\n## 2026年1月13日\\n...",
  "font": "SourceHanSerifCN_Bold",
  "align": "left",
  "width": 400,
  "height": 533,
  "fontScale": 1.2,
  "ratio": "3:4",
  "padding": 30,
  "switchConfig": {
    "showIcon": false,
    "showTitle": false,
    "showContent": true,
    "showTranslation": false,
    "showAuthor": false,
    "showQRCode": false,
    "showSignature": false,
    "showQuotes": false,
    "showWatermark": false
  },
  "temp": "tempBlackSun",
  "textColor": "rgba(0,0,0,0.8)",
  "borderRadius": 15,
  "color": "pure-ray-1"
}
```

### Output Example

```markdown
📸 分享卡片已生成

图片已保存到: docs/images/2026-01-13.png

[预览图片](docs/images/2026-01-13.png)

你可以将此图片分享到社交媒体！
```

---

## Configuration

No configuration required. Uses built-in RSS fetching and Claude AI capabilities.

**Available RSS Sources**:

**English Daily:**
- smol.ai: `https://news.smol.ai/rss.xml` (default)
- TLDR Tech: `https://tldr.tech/rss`

**English Weekly:**
- Import AI: `https://importai.substack.com/feed`
- Last Week in AI: `https://lastweekin.ai/feed`
- Ahead of AI: `https://magazine.sebastianraschka.com/feed`

**Chinese (中文):**
- 量子位: `https://www.qbitai.com/feed`

**Academic (学术):**
- ArXiv AI: `https://rss.arxiv.org/rss/cs.AI`
- ArXiv ML: `https://rss.arxiv.org/rss/cs.LG`

**Tech Communities (社区):**
- Hacker News AI: `https://hnrss.org/newest?q=AI+OR+LLM&points=30`

**Date Calculation**: Uses current UTC date, subtracts days for relative queries.

---

## Complete Examples

### Example 1: Yesterday's News (Basic)

**User Input**: "昨天AI资讯"

**Process**:
1. Calculate yesterday's date: `2026-01-14`
2. Fetch RSS from default source (smol.ai)
3. Check content exists
4. Analyze and categorize
5. Output markdown

**Output**: Structured markdown with all categories

### Example 2: From Specific Source

**User Input**: "Import AI 最新资讯"

**Process**:
1. Identify source: `importai`
2. Fetch RSS from Import AI
3. Get latest entries
4. Analyze and categorize
5. Output markdown

### Example 3: From All Sources

**User Input**: "获取所有渠道的AI新闻"

**Process**:
1. Identify: all sources requested
2. Fetch RSS from all 5 sources in parallel
3. Merge and deduplicate content
4. Analyze and categorize by source
5. Output combined markdown

### Example 4: By Category

**User Input**: "昨天的模型发布相关资讯"

**Process**:
1. Calculate yesterday's date
2. Fetch RSS
3. Analyze and filter for "Model Releases" category
4. Output filtered markdown

### Example 5: With Webpage Generation

**User Input**: "昨天AI资讯，生成网页"

**Process**:
1-5. Same as Example 1
6. Ask: "Which theme?"
7. User selects: "苹果风"
8. Generate HTML with Apple-style theme
9. Save to `docs/2026-01-14.html`

### Example 6: Content Not Found

**User Input**: "2026-01-15的资讯"

**Output**:
```markdown
抱歉，2026-01-15 暂无资讯

可用日期范围: 2026-01-10 ~ 2026-01-13

建议:
- 查看 [2026-01-13](command:查看2026-01-13的资讯) 的资讯
- 查看 [2026-01-12](command:查看2026-01-12的资讯) 的资讯
```

---

## References

- [Output Format](references/output-format.md) - Markdown output structure
- [HTML Themes](references/html-themes.md) - Webpage theme prompts

---

## Troubleshooting

### RSS Fetch Fails

**Error**: "Failed to fetch RSS from [source]"

**Solution**:
- Check network connectivity
- Try a different source: `--source importai`
- List available sources: `--list-sources`

### Date Parsing Fails

**Error**: "Invalid date format"

**Solution**: Use `YYYY-MM-DD` format or relative terms like "昨天"

### No Content for Date

**Output**: Friendly message with available dates (see Step 3)

### Webpage Save Fails

**Error**: "Cannot save to docs/"

**Solution**: Ensure `docs/` directory exists:
```bash
mkdir -p docs
```

---

## CLI Reference

```bash
# List all available sources
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --list-sources

# Get latest from default source (smol.ai)
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --latest

# Get latest from specific source
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --source importai --latest
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --source tldrai --latest
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --source lastweekinai --latest
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --source aheadofai --latest

# Get from multiple sources
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --sources smol importai tldrai --latest

# Get from all sources
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --all-sources --latest

# Limit number of entries per source
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --all-sources --latest --limit 5

# Get available date range for a source
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --source importai --date-range

# Get specific date content
python ~/.claude/skills/ai-daily/scripts/fetch_news.py --source smol --date 2026-01-13
```
