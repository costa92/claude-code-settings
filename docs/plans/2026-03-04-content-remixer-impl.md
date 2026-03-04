# Content Remixer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a `content-remixer` skill that deconstructs viral articles into reusable creative building blocks, lets users pick blocks, and assembles new content via article-generator.

**Architecture:** Independent skill with two files — SKILL.md (execution checklist + 3-phase workflow) and references/block-taxonomy.md (building block definitions). Zero coupling with article-generator; integration via prompt injection.

**Tech Stack:** Pure Markdown skill files, no scripts.

---

### Task 1: Create block-taxonomy.md reference

**Files:**
- Create: `skills/content-remixer/references/block-taxonomy.md`

**Step 1: Create directory structure**

Run: `mkdir -p ~/.claude/skills/content-remixer/references`
Expected: directory created, no output

**Step 2: Write block-taxonomy.md**

Write the following to `skills/content-remixer/references/block-taxonomy.md`:

```markdown
# 创意积木分类体系

本文档定义了 content-remixer 拆解爆款文章时提取的所有积木类型。

---

## 结构积木（Structural Blocks）

### hook — 开头钩子

**定义**: 文章前 100 字的注意力抓取模式。

**常见 pattern**:

| Pattern | 描述 | 适用场景 |
|---------|------|---------|
| 痛点切入 | 以读者日常痛点开头，第二人称制造共鸣 | 工具教程、效率提升 |
| 反常识 | 抛出违反直觉的结论，激发好奇 | 技术深度、原理解析 |
| 数据震撼 | 用震撼数据开场 | 性能对比、行业分析 |
| 场景还原 | 描述一个具体的工作场景 | 实战教程、问题排查 |
| 故事引入 | 用一个真实小故事开头 | 踩坑总结、经验分享 |

### outline — 大纲骨架

**定义**: 文章整体结构的逻辑框架。

**常见 pattern**:

| Pattern | 结构 | 适用场景 |
|---------|------|---------|
| 问题驱动 | 问题→分析→方案→实战→总结 | 技术方案选型 |
| 渐进式 | 入门→进阶→高级→最佳实践 | 工具教程 |
| 对比式 | 背景→选手介绍→多维对比→结论 | 技术对比 |
| 时间线 | 起因→经过→踩坑→解决→复盘 | 踩坑总结 |
| 清单式 | 引言→要点1→要点2→...→总结 | 最佳实践、技巧合集 |

### rhythm — 段落节奏

**定义**: 段落之间的长短交替和信息密度变化。

**常见 pattern**:

| Pattern | 描述 |
|---------|------|
| 短-长-短 | 短结论 → 长论证 → 短总结，紧凑有力 |
| 代码-解释-代码 | 代码块和文字解释交替，适合教程 |
| 叙事-技术-叙事 | 故事和技术内容交织，保持可读性 |
| 递进加深 | 每段比前一段深入一层，适合原理解析 |

### transition — 章节衔接

**定义**: 章节之间的过渡方式。

**常见 pattern**:

| Pattern | 描述 |
|---------|------|
| 承上启下 | 用一句话连接上下文 |
| 悬念过渡 | 在章节末提出疑问，下章解答 |
| 反问桥接 | "但是，这样就够了吗？" |
| 场景切换 | "回到我们的实际项目中…" |

### closing — 收尾模式

**定义**: 文章最后一节的收束方式。

**常见 pattern**:

| Pattern | 描述 |
|---------|------|
| 行动指引 | 给读者 3 个可立即执行的下一步 |
| 开放问题 | 留一个值得思考的问题 |
| 回扣开头 | 回应开头的痛点/问题，形成闭环 |
| 展望式 | 指向更大的话题或趋势 |

---

## 手法积木（Technique Blocks）

### analogy — 类比/比喻

**定义**: 用熟悉事物解释陌生概念。

**示例**:
- 用"交通系统"类比微服务架构
- 用"图书馆"类比数据库索引
- 用"厨房流水线"类比 CI/CD pipeline

**提取格式**: 记录源域（熟悉事物）和目标域（技术概念），以及映射关系。

### contrast — 对比手法

**定义**: 通过对比突出差异和优势。

**常见形式**:
- Before/After：改造前后效果对比
- 新旧对比：旧方案 vs 新方案
- 参数表对比：多维度量化对比
- 代码对比：两种实现方式并排

### storytelling — 叙事手法

**定义**: 用叙事包装技术内容。

**常见形式**:
- 踩坑故事："上周生产环境出了一个诡异的 bug…"
- 时间线叙事：按时间推进展开
- 人物视角：从某个角色的视角讲述
- 探索之旅："我们来一步步看看它是怎么工作的"

### data-proof — 数据论证

**定义**: 用数据支撑论点。

**常见形式**:
- 基准测试结果
- 性能对比表（延迟、内存、吞吐量）
- 用户调研数据
- GitHub Star / 下载量趋势

### reader-empathy — 读者共鸣

**定义**: 让读者感到"说的就是我"。

**常见形式**:
- "你是不是也遇到过…"
- "想象一下这个场景…"
- "如果你和我一样…"
- 预判读者的疑问并主动回答

---

## 单个积木的输出格式

```yaml
- type: hook          # 积木类型（上述分类之一）
  pattern: "痛点切入"  # 具体 pattern 名
  original: "原文摘录" # 爆款文章中的原文片段
  abstracted: "抽象描述" # 可复用的模式描述
  reusability: high    # high / medium / low
```

**reusability 判定标准**:
- **high**: 与主题无关，可直接迁移到任何文章
- **medium**: 需要适配新主题，但模式可复用
- **low**: 与原文主题强相关，迁移需大幅改造
```

**Step 3: Commit**

```bash
git add skills/content-remixer/references/block-taxonomy.md
git commit -m "feat(content-remixer): add block taxonomy reference"
```

---

### Task 2: Create SKILL.md

**Files:**
- Create: `skills/content-remixer/SKILL.md`

**Step 1: Write SKILL.md**

Write the following to `skills/content-remixer/SKILL.md`:

```markdown
---
name: content-remixer
description: Deconstruct viral articles into reusable creative building blocks, let users pick blocks, and assemble new content via article-generator. Use when user says "拆解爆款", "创意积木", "remix 文章", "学习爆款写法", or provides a URL asking to learn from its writing style.
---

# Content Remixer

**拆解爆款 → 提取创意积木 → 组装新内容**

---

## Execution Checklist

### Phase 1: 拆解爆款

1. **[ ] Fetch article** — 用 defuddle/WebFetch 抓取 URL 全文（降级链：defuddle → mcp__web-reader → WebFetch）
2. **[ ] Extract blocks** — 逐维度扫描，提取积木（参考 [block-taxonomy.md](references/block-taxonomy.md)）
3. **[ ] Present blocks** — 以表格形式展示积木清单给用户

**拆解输出格式**:

```
## 拆解报告

**来源**: [文章标题](URL)

### 结构积木

| # | 类型 | Pattern | 原文摘录 | 抽象描述 | 复用度 |
|---|------|---------|---------|---------|--------|
| 1 | hook | 痛点切入 | "每次部署都要手动…" | 以日常痛点开头，第二人称共鸣 | high |
| 2 | outline | 问题驱动 | — | 问题→分析→方案→实战→总结 | high |
| ... | | | | | |

### 手法积木

| # | 类型 | Pattern | 原文摘录 | 抽象描述 | 复用度 |
|---|------|---------|---------|---------|--------|
| 6 | analogy | 交通系统 | "微服务就像城市交通…" | 用交通系统类比分布式架构 | medium |
| 7 | contrast | Before/After | "优化前 3s → 优化后 200ms" | 用量化数据做改造前后对比 | high |
| ... | | | | | |
```

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

7. **[ ] Invoke article-generator** — 调用 `/article-generator`，将写作约束注入 prompt
8. **[ ] article-generator takes over** — article-generator 正常执行其 Phase A/B/C

**调用格式**:

```
/article-generator 写一篇关于 [用户指定的新主题] 的文章，目标受众：[受众]

写作约束（来自爆款拆解）：
- Hook: [约束]
- 大纲骨架: [约束]
- 段落节奏: [约束]
- 手法: [约束列表]
- 收尾: [约束]
```

**IF ANY REQUIRED CHECKBOX IS UNCHECKED, THE TASK IS INCOMPLETE.**

---

## 使用示例

### 示例 1: 完整流程

```
用户: /content-remixer https://mp.weixin.qq.com/s/xxxxx

→ Phase 1: 拆解，输出积木清单
→ Phase 2: 用户选择积木 #1 #2 #6 #7，指定新主题 "Rust 入门"
→ Phase 3: 调用 /article-generator 写 Rust 入门文章，注入选中的写作约束
```

### 示例 2: 只拆解不组装

```
用户: /content-remixer https://mp.weixin.qq.com/s/xxxxx
用户: (Phase 2 选择"只看拆解结果，不生成文章")

→ 输出拆解报告，流程结束
```

---

## 关键约束

- **积木是模式不是内容** — 提取结构和手法的抽象模式，绝不复制原文文字
- **零耦合** — 不修改 article-generator 的任何文件，通过 prompt 注入衔接
- **交互优先** — 每个 Phase 切换都需要用户确认，不自动跳转

---

## 参考文档

- **[block-taxonomy.md](references/block-taxonomy.md)** — 积木分类体系完整定义
- **article-generator SKILL.md** — 写作流程（Phase 3 调用时遵循）
```

**Step 2: Commit**

```bash
git add skills/content-remixer/SKILL.md
git commit -m "feat(content-remixer): add main skill definition"
```

---

### Task 3: Update CLAUDE.md skill registry

**Files:**
- Modify: `CLAUDE.md` — 在架构概览的 skills 列表和内容流水线中注册新 skill

**Step 1: Add to skills directory listing**

In `CLAUDE.md`, after the line `│   ├── content-analytics/ # 数据分析`, add:

```
│   ├── content-remixer/   # 爆款拆解→创意积木→组装新内容
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: register content-remixer in CLAUDE.md"
```

---

### Task 4: Verify skill discovery

**Step 1: Run /find-skill to verify**

```
/find-skill content-remixer
```

Expected: skill is listed and loadable.

**Step 2: Quick smoke test**

Invoke `/content-remixer` with a test URL to verify Phase 1 works end-to-end.

---
