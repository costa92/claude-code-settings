# Content Remixer — 设计文档

**日期**: 2026-03-04
**状态**: 已批准

## 概述

独立 Skill `content-remixer`，实现「拆解爆款 → 提取创意积木 → 组装新内容」三阶段工作流。

## 需求

- **输入**: URL（爬取爆款文章）
- **拆解维度**: 结构 + 写作手法
- **组装方式**: 交互式（用户挑选积木 + 指定新主题）
- **集成方式**: 独立 Skill，通过 prompt 注入调用 article-generator

## 积木分类体系

### 结构积木（Structural Blocks）

| 积木类型 | 说明 | 示例 |
|---------|------|------|
| `hook` | 开头钩子模式 | "痛点切入""反常识开头""数据震撼" |
| `outline` | 大纲骨架 | "问题→方案→实战→对比→总结" |
| `rhythm` | 段落节奏 | "短-长-短""代码-解释-代码" |
| `transition` | 章节衔接方式 | "承上启下句""悬念过渡""反问桥接" |
| `closing` | 收尾模式 | "行动指引""开放问题""回扣开头" |

### 手法积木（Technique Blocks）

| 积木类型 | 说明 | 示例 |
|---------|------|------|
| `analogy` | 类比/比喻手法 | "用烹饪比喻微服务" |
| `contrast` | 对比手法 | "before/after""新旧对比" |
| `storytelling` | 叙事手法 | "踩坑故事""时间线叙事" |
| `data-proof` | 数据论证策略 | "基准测试""性能对比表" |
| `reader-empathy` | 读者共鸣点 | "你是不是也遇到过…""想象一下…" |

### 单个积木输出格式

```yaml
- type: hook
  pattern: "痛点切入"
  original: "每次部署都要手动 SSH 上去改配置，你累了吗？"
  abstracted: "以读者日常痛点场景开头，用第二人称制造共鸣"
  reusability: high
```

## 三阶段流程

### Phase 1: 拆解

1. WebFetch/defuddle 抓取全文
2. 逐维度扫描，提取积木
3. 输出积木清单表格（展示给用户）

### Phase 2: 挑选

1. AskUserQuestion — 多选勾选想复用的积木
2. AskUserQuestion — 输入新主题 + 目标受众
3. （可选）用户可修改积木的抽象描述

### Phase 3: 组装

1. 将选中积木编排为「写作约束清单」
2. 调用 `/article-generator`，注入写作约束
3. article-generator 正常走 Phase B/C

### 约束注入格式

```
/article-generator 写一篇关于 [新主题] 的文章

写作约束（来自爆款拆解）：
- Hook: 痛点切入，以读者日常场景开头
- 大纲骨架: 问题→方案→实战→对比→总结
- 段落节奏: 短-长-短交替
- 手法: 每节用一个类比，before/after 对比贯穿
- 收尾: 行动指引 + 回扣开头
```

## 文件结构

```
~/.claude/skills/content-remixer/
├── SKILL.md                    # 核心指南 + Execution Checklist
└── references/
    └── block-taxonomy.md       # 积木分类体系详细定义
```

## 设计决策

| 维度 | 决策 | 理由 |
|------|------|------|
| 独立 Skill vs 新场景 | 独立 Skill | 职责分离，article-generator 不膨胀 |
| 与 article-generator 衔接 | prompt 注入 | 零耦合，不改 article-generator 代码 |
| 积木持久化 | 不持久化 | YAGNI，当前只需当次 session 使用 |
| 积木格式 | YAML-like 结构 | 人类可读，LLM 友好 |
