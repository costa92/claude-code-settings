---
name: news-daily
description: 获取 AI 行业新闻（产品发布、论文、融资、政策），来源涵盖 smol.ai、Import AI、TLDR AI、量子位、ArXiv、Hacker News，Claude 智能分类摘要输出中文 Markdown。可选生成 HTML 网页与分享卡片图。无需额外 API key。用户询问 AI 新闻、每日资讯、news-daily 时触发。
---

# News Daily — AI 行业新闻

从 AI 行业 RSS 源获取新闻，智能分类摘要，输出中文 Markdown。可选生成 HTML 网页和分享卡片图。

## 可用来源

| 来源 ID | 名称 | 频率 | 说明 |
|---------|------|------|------|
| `smol` | smol.ai | 日更 | 默认来源，每日 AI 新闻摘要 |
| `tldrai` | TLDR Tech | 日更 | AI、创业、开发者新闻 |
| `importai` | Import AI | 周更 | Jack Clark 的 AI 研究与产业 newsletter |
| `lastweekinai` | Last Week in AI | 周更 | 每周 AI 新闻摘要 |
| `aheadofai` | Ahead of AI | 周更 | Sebastian Raschka 的 ML/AI 更新 |
| `qbitai` | 量子位 | 日更 | 中国领先 AI 科技媒体 |
| `arxiv_ai` | ArXiv AI | 日更 | cs.AI 最新论文 |
| `arxiv_ml` | ArXiv ML | 日更 | cs.LG 最新论文 |
| `hn_ai` | Hacker News AI | 实时 | HN 上 AI/LLM 讨论（30+ 分） |

## 进度清单

```
- [ ] Step 1: 解析日期和来源
- [ ] Step 2: 抓取 RSS
- [ ] Step 3: 验证内容存在
- [ ] Step 4: 提取分析内容
- [ ] Step 5: 输出结构化 Markdown（完成后主动询问是否生成海报）
- [ ] Step 6: 生成网页（可选）
- [ ] Step 7: 生成分享卡片（可选）
- [ ] Step 8: 生成海报（可选）
```

---

## Step 1：解析日期和来源

**日期解析**

| 用户输入 | 目标日期 |
|---------|---------|
| "昨天" | today - 1 day |
| "前天" | today - 2 days |
| "今天" | current date |
| "2026-01-13" | 直接解析 |

日期格式统一用 YYYY-MM-DD。

**来源解析**

| 用户输入 | 来源 ID |
|---------|---------|
| "Import AI" | importai |
| "TLDR AI" | tldrai |
| "量子位" | qbitai |
| "ArXiv" / "AI论文" | arxiv_ai |
| "ML论文" | arxiv_ml |
| "Hacker News" / "HN" | hn_ai |
| "所有渠道" / "综合" | --all-sources |
| （默认） | smol |

---

## Step 2：抓取 RSS

```bash
# 推荐：smart 模式（自动补充当天实时内容）
python ~/.claude/skills/news-daily/scripts/fetch_news.py --smart

# 指定来源
python ~/.claude/skills/news-daily/scripts/fetch_news.py --source importai --latest
python ~/.claude/skills/news-daily/scripts/fetch_news.py --all-sources --latest
python ~/.claude/skills/news-daily/scripts/fetch_news.py --source smol --date 2026-01-13
python ~/.claude/skills/news-daily/scripts/fetch_news.py --list-sources
```

**smart 模式逻辑**：
- 目标日期从 `~/.claude/env.json` 的 `news_daily_date` 读取（默认 `yesterday`，可改为 `today` / `day-before` / `YYYY-MM-DD`）
- 始终抓取 smol.ai 最新期（最权威日报）
- 若 smol 最新内容早于目标日期，自动补充 Hacker News 实时内容（48h 内）
- 输出 `note` 字段告知实际日期与来源

---

## Step 3：验证内容

无内容时自动 fallback 到 --latest，告知用户具体日期变化。

---

## Step 4：提取分析内容

用 Claude 内置能力：翻译为中文、生成 3-5 条要点、按分类整理、提取关键词、保留原文链接。

分类：模型发布、产品动态、研究论文、工具框架、融资并购、行业事件、技术社区。

---

## Step 5：输出 Markdown

参考 references/output-format.md。标题格式：News Daily · 2026年1月19日。

**输出完成后，主动询问用户**：「要生成海报图片吗？」（触发 Step 8）。不要等用户说触发词，直接提示。

---

## Step 6：生成网页（可选）

触发词：「生成网页」「制作HTML页面」

询问主题（苹果风 / 深海蓝 / 秋日暖阳），详见 references/html-themes.md。
保存到 docs/{date}.html。

---

## Step 7：生成分享卡片（可选）

触发词：「生成图片」「生成分享卡片」

调用 POST https://fireflycard-api.302ai.cn/api/saveImg，保存到 docs/images/{date}.png。

---

## Step 8：生成海报（可选）

触发词：「生成海报」「做成海报」「海报」「海报图」「要」（回应 Step 5 主动询问时）

### 设计规范

参考风格：暖米色卡片海报（类微信科普图风格）

| 属性 | 值 |
|------|----|
| 画布尺寸 | 750 × 1200 px |
| 背景色 | `#F5EED8`（暖米色） |
| 主字体 | system-ui, "PingFang SC", "Microsoft YaHei" |
| 卡片背景 | `#FFFFFF`，圆角 16px，阴影 `0 4px 16px rgba(0,0,0,0.08)` |
| 强调色 | `#2D3A4A`（深藏蓝，图标背景）/ `#E8A838`（金黄，徽章）/ `#4CAF82`（绿，标签） |

### 海报结构

```
┌─────────────────────────────────┐
│  [标签] AI 日报 · YYYY年M月D日  │  ← 顶部标签行（金黄底白字）
│                                 │
│   今日 AI 速报                  │  ← 大标题（32px bold）
│   X 条精选 · 来源: smol.ai      │  ← 副标题（灰色）
├─────────────────────────────────┤
│                                 │
│  ✦ 今日看点（3 条）             │  ← 要点区块（浅蓝底）
│  • ...                          │
│  • ...                          │
│  • ...                          │
├────────────┬────────────────────┤
│ [📦 模型]  │  [🚀 产品]        │  ← 2列卡片网格（每类最多2条）
│ 标题 ...   │  标题 ...         │
│ 摘要       │  摘要             │
│ [查看原文] │  [查看原文]       │
├────────────┼────────────────────┤
│ [📄 论文]  │  [🔧 工具]        │
│ ...        │  ...              │
├────────────┴────────────────────┤
│ [QR码] 扫码关注     公众号      │  ← 底部：左侧二维码 + 右侧文字
│         懂点儿AI                │
└─────────────────────────────────┘
```

### 内容映射

| 海报区块 | 来源字段 |
|----------|---------|
| 标题 | `News Daily · {date}` |
| 副标题 | `{N} 条精选 · 来源: {source}` |
| 今日看点 | **列出所有精选新闻**（与副标题 N 条一致），每条格式：`{分类图标} {一句话摘要}`；不要只写 3 条宏观趋势，要覆盖全部卡片内容 |
| 卡片网格 | 各分类取前 2 条，显示：中文标题 + 一句话摘要 |
| 分类图标 | 模型发布🧠 产品动态🚀 研究论文📄 工具框架🔧 融资并购💰 行业事件📢 技术社区🔍 |

### 生成步骤

**1. 读取 QR 码 URL 与账号名**

从 `~/.claude/env.json` 读取：
- `wechat_qr_url`：已有的公众号二维码图片 URL（直接嵌入 HTML）；若为空则降级为纯文字水印
- `wechat_account_name`：公众号名称，默认 `CostaLong`
- `news_daily_output_dir`：输出根目录；**若为空则使用当前工作目录**（即运行 Claude Code 时所在目录）

输出路径解析规则：
```
output_dir = env["news_daily_output_dir"] 或 "."（当前目录）
poster_dir = {output_dir}/docs/posters/
html_file  = {poster_dir}/{date}.html
png_file   = {poster_dir}/{date}.png
```

**2. 生成 HTML 文件**

将海报内容写入 `docs/posters/{date}.html`，完整内嵌 CSS（无外部依赖）。

底部水印区块 HTML（有 QR 码图片时）：
```html
<div class="footer">
  <div class="footer-inner">
    <img class="qr-code" src="{wechat_qr_url}" alt="扫码关注">
    <div class="footer-text">
      <div class="footer-label">扫码关注</div>
      <div class="footer-name">{account_name}</div>
      <div class="footer-sub">公众号 · 每日 AI 资讯</div>
    </div>
  </div>
</div>
```

底部水印区块 HTML（无 QR 码降级时）：
```html
<div class="footer">公众号 · {account_name}</div>
```

关键 CSS：
```css
body { background: #F5EED8; width: 750px; margin: 0; font-family: system-ui, "PingFang SC", "Microsoft YaHei", sans-serif; }
.poster { padding: 40px 32px; min-height: 1200px; }
.header-tag { background: #E8A838; color: #fff; border-radius: 20px; padding: 6px 18px; font-size: 14px; display: inline-block; }
h1 { font-size: 36px; font-weight: 900; color: #1A1A2E; margin: 16px 0 8px; }
.subtitle { color: #888; font-size: 15px; }
.highlights { background: #EBF4FF; border-radius: 12px; padding: 20px 24px; margin: 24px 0; }
.highlights h3 { color: #2563EB; margin: 0 0 12px; font-size: 16px; }
.highlights li { color: #374151; font-size: 14px; line-height: 1.8; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 16px 0; }
.card { background: #fff; border-radius: 16px; padding: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.card-icon { background: #2D3A4A; color: #fff; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; margin-bottom: 12px; }
.card-title { font-size: 15px; font-weight: 700; color: #1A1A2E; margin-bottom: 8px; line-height: 1.4; }
.card-desc { font-size: 13px; color: #6B7280; line-height: 1.6; }
.badge { display: inline-block; background: #4CAF82; color: #fff; font-size: 11px; border-radius: 6px; padding: 2px 8px; margin-top: 10px; }
/* 底部水印 */
.footer { margin-top: 32px; padding-top: 20px; border-top: 1px solid #E8DCC0; }
.footer-inner { display: flex; align-items: center; gap: 16px; }
.qr-code { width: 80px; height: 80px; border-radius: 8px; }
.footer-label { font-size: 12px; color: #AAAAAA; }
.footer-name { font-size: 18px; font-weight: 700; color: #2D3A4A; }
.footer-sub { font-size: 12px; color: #AAAAAA; margin-top: 2px; }
```

**3. 截图为 PNG**

优先使用 Playwright（webapp-testing），备用 Python：

```bash
# 方案一：Playwright（推荐，已验证）
python3 -c "
from playwright.sync_api import sync_playwright
import os, json

env = json.load(open(os.path.expanduser('~/.claude/env.json')))
base = env.get('news_daily_output_dir') or '.'
poster_dir = os.path.join(os.path.expanduser(base), 'docs', 'posters')
os.makedirs(poster_dir, exist_ok=True)

html_path = os.path.join(poster_dir, '{date}.html')
out_path  = os.path.join(poster_dir, '{date}.png')
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 750, 'height': 1400})
    page.goto(f'file://{os.path.abspath(html_path)}')
    page.wait_for_timeout(1500)
    page.screenshot(path=out_path, full_page=True)
    browser.close()
print('海报已保存:', out_path)
"

# 方案二：chromium-browser（若已安装）
chromium-browser --headless --screenshot={poster_dir}/{date}.png \
  --window-size=750,1400 {poster_dir}/{date}.html
```

**4. 输出**

告知用户海报路径：`docs/posters/{date}.png`，并提示可直接发朋友圈/公众号。

---

## 故障排除

| 问题 | 解决 |
|------|------|
| RSS 抓取失败 | 检查网络；换来源 --source importai |
| 日期无内容 | 自动 fallback，或用 --date-range 查可用日期 |
| 网页保存失败 | mkdir -p docs |
| 海报截图失败 | 安装 playwright：`pip install playwright && playwright install chromium` |
| QR 码不显示 | 确认 env.json 中 `wechat_qr_url` 非空且图片 URL 可访问 |
| 海报中文乱码 | 确认系统已安装中文字体（PingFang SC / Noto Sans CJK）|
| 海报保存到了错误目录 | 检查 `news_daily_output_dir`：空=当前工作目录；可设为绝对路径如 `~/docs` |
| 图片被截断 | Playwright viewport height 已设为 1400px + full_page=True，若仍截断可调大 height |
