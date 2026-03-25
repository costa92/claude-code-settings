# article-craft 工作流优化计划

## Context

在批量生产 K8s 深度学习系列 23 篇文章的过程中，发现 article-craft 工作流存在 6 个需要优化的问题。本次修改聚焦于 self-check 脚本和 write skill 的改进，提升批量文章生产的质量和效率。

## 修改清单

### 1. review_selfcheck.py — Rule 11 扩展检测范围

**文件**: `~/.claude/plugins/article-craft/scripts/review_selfcheck.py`
**行号**: 392-412 (check_rule_11)

**当前问题**: Rule 11 只检测 `<!-- IMAGE:` 和 `<!-- SCREENSHOT:` 两种占位符格式，遗漏了 agent 生成的其他格式。

**修改内容**:
- 增加检测 `IMAGE_PLACEHOLDER` 文本（agent 自创格式）
- 增加检测引用不存在的本地图片路径 `![...](images/xxx)` 或 `![...](placeholder-xxx)`
- 保持 GATE 性质不变

### 2. review_selfcheck.py — Rule 6 开头章节豁免

**文件**: `~/.claude/plugins/article-craft/scripts/review_selfcheck.py`
**行号**: 277-298 (check_rule_6)

**当前问题**: 所有 `##` 章节都要求 ≥2 个代码块，但"为什么需要 X"/"挑战"/"争议"等动机章节天然以叙述为主，触发误报。

**修改内容**:
- 对文章的前 2 个 `##` 章节（排除导言/总结），将代码块阈值从 2 降为 1
- 或者对标题含特定关键词（为什么/挑战/争议/背景/动机/现实）的章节降低阈值
- 采用方案：标题关键词匹配，更精确

### 3. review_selfcheck.py — 新增 Rule 12 模板化摘要检测

**文件**: `~/.claude/plugins/article-craft/scripts/review_selfcheck.py`
**行号**: ALL_CHECKS 列表后新增

**当前问题**: "本文从...出发，完整拆解...，通过...，最后..." 等 AI 模板化摘要句式通过了 self-check 但在 content-reviewer 中扣分。

**修改内容**:
- 新增 `check_rule_12()` 函数
- 匹配模式：
  - `本文从.*出发.*拆解`
  - `本文将.*详细.*介绍`
  - `接下来.*我们将.*逐一`
  - `下面.*章节.*将.*逐一`
- 非阻断规则（非 GATE），标记为 warning

### 4. write skill — 添加 post-write 自动验证步骤

**文件**: `~/.claude/plugins/article-craft/skills/write/SKILL.md`
**行号**: 末尾新增步骤

**当前问题**: write skill 生成文章后不运行任何验证，红旗词和格式问题直到 review 阶段才发现。

**修改内容**:
- 在 write skill 的"输出"步骤后新增 "Post-Write Validation" 步骤
- 自动运行 `review_selfcheck.py` 的 Rule 1（红旗词）和 Rule 11（占位符格式）
- 如果 Rule 1 发现红旗词，自动修复后重新保存
- 如果 Rule 11 发现非标准占位符，自动转换为标准 `<!-- IMAGE: -->` 格式

### 5. write skill — 强化禁用词列表可见性

**文件**: `~/.claude/plugins/article-craft/skills/write/SKILL.md`
**行号**: 红旗词检查部分

**当前问题**: 禁用词列表在 write skill 中以 grep 命令形式存在，agent 写作时不够显眼。

**修改内容**:
- 在 write skill 的 "写作规则" 章节顶部，用醒目的 callout 格式列出完整禁用词
- 添加"写作时主动避免"的指令，而非仅依赖事后 grep

### 6. series skill — 添加批量生成入口

**文件**: `~/.claude/plugins/article-craft/skills/series/SKILL.md`

**当前问题**: series skill 只支持逐篇生成，没有批量生成工作流。

**修改内容**:
- 新增 "批量生成模式" 章节
- 支持指定范围（如 `#16-#23`）
- 流程：逐篇在主会话中生成 → self-check → 修复 → 保存 → 下一篇
- 单篇失败不阻塞后续（记录失败列表，最后汇总）
- 不使用 agent（避免超时），直接在主会话中执行

## 验证方式

1. 对修改后的 `review_selfcheck.py` 运行现有的第二季文章，确认：
   - Rule 6 不再对开头章节误报
   - Rule 11 能检测 `IMAGE_PLACEHOLDER` 格式
   - Rule 12 能检测模板化摘要
2. 对 write skill 修改后，模拟生成一篇短文验证 post-write validation 是否自动触发
3. 运行 `python3 review_selfcheck.py --help` 确认新 rule 已注册

## 修改优先级

| 顺序 | 文件 | 修改 | 风险 |
|------|------|------|------|
| 1 | review_selfcheck.py | Rule 11 扩展 | 低 |
| 2 | review_selfcheck.py | Rule 6 豁免 | 低 |
| 3 | review_selfcheck.py | Rule 12 新增 | 低 |
| 4 | write/SKILL.md | post-write 验证 | 低 |
| 5 | write/SKILL.md | 禁用词可见性 | 低 |
| 6 | series/SKILL.md | 批量生成 | 中 |
