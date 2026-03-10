# News Daily 优化：去重 + 海报字体放大

## Context

连续两天运行 `/news-daily`，输出内容大量重复（smol.ai 更新慢、HN 48h 窗口重叠）。根因：`fetch_news.py` 完全无状态，无去重机制。同时海报字体偏小（卡片描述 13px、看点列表 13.5px），移动端阅读体验不佳。

## 改动 1：fetch_news.py 增加已读去重

**文件**: `~/.claude/skills/news-daily/scripts/fetch_news.py`

### 新增函数（约 50 行）

```python
HISTORY_FILE = OUTPUT_DIR / "seen_history.json"
HISTORY_DAYS = 7  # 保留天数

def load_history() -> dict:
    """加载已读历史 {date: [url1, url2, ...]}"""

def save_history(history: dict):
    """保存历史，自动清理超过 HISTORY_DAYS 的记录"""

def dedup_entries(entries: list, history: dict) -> list:
    """过滤已展示过的条目（按 link 字段匹配）"""

def record_shown(entries: list, date_str: str, history: dict):
    """将本次展示的条目 URL 追加到历史"""
```

### 插入点

| 位置 | 行号区间 | 说明 |
|------|---------|------|
| `smart_fetch()` smol entries | ~520 | `entries = dedup_entries(entries, history)` |
| `smart_fetch()` HN entries | ~560 | `hn_entries = dedup_entries(hn_entries, history)` |
| 多来源模式 entries | ~637, ~662 | 同上 |
| 单来源模式 entries | ~701 | 同上 |
| JSON 输出前 | ~603, ~678, ~707 | `record_shown()` + `save_history()` |

### 补充逻辑

- smart 模式下若 smol.ai 全部已读，自动扩大到 tldrai、qbitai 补充新内容
- 输出 JSON 新增 `"dedup": {"filtered": N, "total": M}` 元数据
- `--no-dedup` 参数：跳过去重（调试用）

## 改动 2：海报 HTML 字体放大

**文件**: `~/.claude/skills/news-daily/SKILL.md`（CSS 规范段落）

| 元素 | 当前 | 调整后 | 说明 |
|------|------|--------|------|
| h1 主标题 | 36px | 40px | 更醒目 |
| .highlights li 看点列表 | 14px | 16px | 核心信息放大 |
| .card-title 卡片标题 | 15px | 17px | 提升扫描性 |
| .card-desc 卡片描述 | 13px | 15px | 移动端舒适阅读 |
| .card-category 分类标签 | 12px | 13px | 微调 |
| .badge 徽章 | 11px | 12px | 微调 |
| .subtitle 副标题 | 15px | 16px | 微调 |
| .highlights h3 | 16px | 18px | 区块标题更突出 |
| .section-title | 18px | 20px | 区块标题更突出 |

## 不改动

- RSS 来源配置、抓取逻辑、HTML 主题、输出格式模板

## 验证

1. 连续运行两次 `python fetch_news.py --smart`，第二次应过滤掉第一次已展示的条目
2. 检查 `data/seen_history.json` 文件生成且格式正确
3. 用 `--no-dedup` 参数确认可跳过去重
4. 生成新海报 HTML，对比字体变化，Playwright 截图验证
