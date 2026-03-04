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
