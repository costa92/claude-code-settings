---
name: content-remixer
description: 拆解爆款文章为可复用创意积木，挑选后组装新内容。当用户说「拆解爆款」「创意积木」「remix」「学习爆款写法」时使用。
---

# Content Remixer

**发现爆款 → 拆解 → 提取创意积木 → 组装新内容**

> 核心原则：**积木是模式不是内容** — 提取结构和手法的抽象模式，绝不复制原文文字。每个 Phase 切换都需要用户确认，不自动跳转。

---

## Execution Checklist

### 输入路由

根据用户输入自动选择入口：

- **给了 URL** → 跳过 Phase 0，直接进入 Phase 1 拆解
- **给了关键词**（如 "Rust""Agent""RAG"）→ 从 Phase 0 发现爆款开始

### Phase 0: 发现爆款（关键词触发）

0a. **[ ] Collect keyword** — 从用户输入提取主题关键词
0b. **[ ] Parallel search** — 并行搜索 4 个渠道（用 WebSearch / mcp__web-search-prime）：

| 渠道 | 搜索策略 |
|------|---------|
| 中文技术社区 | `关键词 site:juejin.cn OR site:infoq.cn OR site:sspai.com` |
| 微信公众号 | `关键词 site:mp.weixin.qq.com` |
| 海外技术社区 | `关键词 site:news.ycombinator.com OR site:reddit.com/r/programming OR site:dev.to` |
| 补充热榜 | `关键词 掘金热榜 OR InfoQ 热门 OR 技术博客` |

0c. **[ ] Deduplicate & present** — 去重，按渠道分组，输出候选列表：

```
## 爆款候选

### 中文技术社区
| # | 标题 | 来源 | URL |
|---|------|------|-----|
| 1 | xxx | 掘金 | https://... |
| 2 | xxx | InfoQ | https://... |

### 微信公众号
| # | 标题 | 来源 | URL |
|---|------|------|-----|
| 3 | xxx | 某公众号 | https://... |

### 海外技术社区
| # | 标题 | 来源 | URL |
|---|------|------|-----|
| 4 | xxx | Hacker News | https://... |
| 5 | xxx | dev.to | https://... |
```

0d. **[ ] User picks article** — AskUserQuestion 让用户选一篇，获得 URL → 进入 Phase 1

### Phase 1: 拆解爆款

1. **[ ] Fetch article** — 用 defuddle/WebFetch 抓取 URL 全文（降级链：defuddle → mcp__web-reader → WebFetch）
2. **[ ] Extract blocks** — 逐维度扫描，提取积木（参考 [block-taxonomy.md](references/block-taxonomy.md)）
3. **[ ] Present blocks** — 以表格形式展示积木清单给用户

**拆解输出格式**:

| # | 类型 | Pattern | 原文摘录 | 抽象描述 | 复用度 |
|---|------|---------|---------|---------|--------|
| 1 | hook | 痛点切入 | "每次部署都要手动…" | 以日常痛点开头，第二人称共鸣 | high |
| 2 | outline | 问题驱动 | — | 问题→分析→方案→实战→总结 | high |

（结构积木和手法积木分两个表格展示）

**拆解规则**:
- 每个维度至少提取 1 个积木，如果原文没有则标注"未检测到"
- `original` 字段摘录原文关键句（≤ 50 字），不复制大段内容
- `abstracted` 字段必须是脱离原文主题的通用描述
- 优先提取 reusability 为 high 的积木

### Phase 2: 挑选积木

4. **[ ] User selects blocks** — AskUserQuestion（multiSelect）让用户勾选想复用的积木编号
5. **[ ] User specifies topic** — AskUserQuestion 收集新主题 + 目标受众
6. **[ ] Confirm constraints** — 将选中积木编排为写作约束清单，展示给用户确认

**约束清单格式**:

```
## 写作约束（来自爆款拆解）

- **Hook**: [选中的 hook pattern + 抽象描述]
- **大纲骨架**: [选中的 outline pattern]
- **段落节奏**: [选中的 rhythm pattern]
- **章节衔接**: [选中的 transition pattern]
- **收尾模式**: [选中的 closing pattern]
- **写作手法**:
  - [选中的手法 1]
  - [选中的手法 2]
  - ...
```

### Phase 3: 组装新内容

7. **[ ] Invoke article-craft** — 调用 `/article-craft`，将写作约束注入 prompt
8. **[ ] article-craft takes over** — article-craft 正常执行其 Phase A/B/C

**调用格式**:

```
/article-craft 写一篇关于 [用户指定的新主题] 的文章，目标受众：[受众]

目标平台：[微信公众号/小红书/知乎/通用]（默认微信公众号）
文章深度：[快速入门/实战教程/深度解析]

写作约束（来自爆款拆解）：
- Hook: [约束]
- 大纲骨架: [约束]
- 段落节奏: [约束]
- 手法: [约束列表]
- 收尾: [约束]

平台注意事项：
- 微信：外部链接改为搜索指引（如「搜索 关键词」），必须填写 description
- 小红书：需要话题标签和表情
- 知乎：开头直接给结论，需要参考文献
```

**IF ANY REQUIRED CHECKBOX IS UNCHECKED, THE TASK IS INCOMPLETE.**

---

## 使用示例

### 示例 1: 关键词发现 → 完整流程

```
用户: /content-remixer Rust

→ Phase 0: 并行搜索 4 渠道，输出候选列表，用户选 #3
→ Phase 1: 抓取选中文章，拆解输出积木清单
→ Phase 2: 用户选择积木 #1 #2 #6 #7，指定新主题 "Go 错误处理"
→ Phase 3: 调用 /article-craft 写文章，注入选中的写作约束
```

### 示例 2: 直接给 URL（跳过 Phase 0）

```
用户: /content-remixer https://mp.weixin.qq.com/s/xxxxx

→ Phase 1: 拆解，输出积木清单
→ Phase 2: 用户选择积木 #1 #2 #6 #7，指定新主题 "Rust 入门"
→ Phase 3: 调用 /article-craft 写 Rust 入门文章，注入选中的写作约束
```

### 示例 3: 只拆解不组装

```
用户: /content-remixer https://mp.weixin.qq.com/s/xxxxx
用户: (Phase 2 选择"只看拆解结果，不生成文章")

→ 输出拆解报告，流程结束
```

---

## 关键约束

- **积木是模式不是内容** — 提取结构和手法的抽象模式，绝不复制原文文字
- **零耦合** — 不修改 article-craft 的任何文件，通过 prompt 注入衔接
- **交互优先** — 每个 Phase 切换都需要用户确认，不自动跳转

---

## 参考文档

- **[block-taxonomy.md](references/block-taxonomy.md)** — 积木分类体系完整定义
- **article-craft SKILL.md** — 写作流程（Phase 3 调用时遵循）
