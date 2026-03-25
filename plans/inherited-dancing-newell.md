# Pipeline 优化计划：修复 7 个工作流问题

## Context

在执行 K8s 系列第 26 篇的完整 pipeline（series next → orchestrator → write → images → review → publish）过程中，发现 7 个问题导致重试和效率损失。本计划修复所有问题，确保下次 pipeline 一次通过。

## 修复清单

### Fix 1: Write skill — IMAGE 占位符格式强制规范 [P0]

**问题**: write skill 生成的占位符缺少 `(ratio)` 和 `<!-- PROMPT: -->` 行，导致 images 脚本无法识别。

**根因**: write skill SKILL.md 已定义正确格式，但 Post-Write Validation（Step 7）未检查占位符格式合规性。

**修改文件**: `/home/hellotalk/.claude/plugins/article-craft/skills/write/SKILL.md`

**改动**:
- 在 Step 7 Post-Write Validation 中新增一条检查规则：验证所有 `<!-- IMAGE:` 占位符必须匹配 images 脚本的正则格式
- 正则: `<!--\s*IMAGE:\s*(.*?)\s*-\s*(.*?)\s*\((.*?)\)\s*-->(?:\s*|\n)*<!--\s*PROMPT:\s*(.*?)\s*-->`
- 不匹配的占位符必须在 validation 阶段自动修复（补 ratio 默认 16:9，补 PROMPT 行）

### Fix 2: Orchestrator — images 脚本路径统一 [P0]

**问题**: 尝试了错误路径 `~/.claude/scripts/generate_and_upload_images.py`，实际位于 `~/.claude/plugins/article-craft/scripts/`。

**修改文件**: `/home/hellotalk/.claude/plugins/article-craft/skills/orchestrator/SKILL.md`

**改动**:
- 在 Step 3.5 Images 节中明确写入脚本绝对路径：`~/.claude/plugins/article-craft/scripts/generate_and_upload_images.py`
- 同时在 images skill 中也统一路径声明

**修改文件**: `/home/hellotalk/.claude/plugins/article-craft/skills/images/SKILL.md`
- 确认路径声明一致

### Fix 3: Content-reviewer — 快速模式评分阈值适配 [P1]

**问题**: 快速模式跳过"事实准确性"（-10 分），满分实际 60，但阈值仍为 55/70，导致 6 维高分文章（53/60=88%）仍被判不达标。

**修改文件**: `/home/hellotalk/.claude/skills/content-reviewer/SKILL.md`

**改动**:
- 快速模式评分公式改为：`综合分 = 6 维总分 × (70/60)`，换算为 /70 制后再与 55 比较
- 或等价地：快速模式阈值从 55/70 调整为 48/60（保持同等比例 78.6%）
- 在输出格式中明确标注"6 维评分（事实准确性跳过）"
- 方案选择：采用换算方案（`总分 × 70/60`），阈值不变仍为 55/70，对用户更直观

### Fix 4: Orchestrator — verify 结果反馈到 write [P1]

**问题**: verify agent 在后台运行，结果（工具版本号等）未反馈到 write 阶段。

**修改文件**: `/home/hellotalk/.claude/plugins/article-craft/skills/orchestrator/SKILL.md`

**改动**:
- Step 3.2 verify 改为前台阻塞执行（不用 `run_in_background`），确保结果在 write 之前可用
- Step 3.3 write 新增指令：如果 verify 返回了工具版本号，写作时应引用这些版本号
- 如果 verify 超时（>60s），降级为后台继续，write 使用 WebSearch 结果

### Fix 5: Review — 自动修改一次批量处理所有低分维度 [P1]

**问题**: 3 轮修改每轮只改一个维度，效率低。

**修改文件**: `/home/hellotalk/.claude/skills/content-reviewer/SKILL.md`

**改动**:
- 自动修改策略从"每轮按优先级改一个"改为"第一轮扫描所有 <8 分维度，一次性批量修复"
- 修改"自动修改机制"节中的优先级表：改为"第一轮同时处理所有优先级的修改项"
- 保留最多 3 轮限制，但预期 1 轮就够

### Fix 6: Series next — 简化参数传递 [P2]

**问题**: series next 手动拼 8 个参数给 orchestrator，冗余且容易出错。

**修改文件**:
- `/home/hellotalk/.claude/plugins/article-craft/skills/series/SKILL.md`
- `/home/hellotalk/.claude/skills/series/SKILL.md`（同步）

**改动**:
- Mode 2 Step 2 中明确：调用 orchestrator 时只传 `--series SERIES_FILE` 一个参数
- orchestrator 内部负责解析 series.md、提取 topic/audience/visual_prefix/save_path
- 删除"自动传入以下参数给 orchestrator"的逐一列举，改为"orchestrator 通过 `--series` 模式自动读取所有配置"

### Fix 7: Self-check 与 review 合并执行 [P2]

**问题**: review 流程中 self-check 和 content-reviewer 独立运行，红旗词等规则重复扫描。

**修改文件**: `/home/hellotalk/.claude/plugins/article-craft/skills/orchestrator/SKILL.md`

**改动**:
- Step 3.6 Review 中明确：self-check 是 review 的内置前置步骤，不需要单独调用
- 删除"运行 self-check 脚本"的独立步骤，改为"调用 /article-craft:review 时自动执行 self-check + content-reviewer"
- review skill 本身已经包含 Phase 1（self-check）和 Phase 2（content-reviewer），不需要 orchestrator 重复调

## 修改文件汇总

| 文件 | Fix # | 改动量 |
|------|-------|--------|
| `plugins/article-craft/skills/write/SKILL.md` | Fix 1 | 新增 ~15 行 validation 规则 |
| `plugins/article-craft/skills/orchestrator/SKILL.md` | Fix 2, 4, 7 | 修改 ~20 行 |
| `skills/content-reviewer/SKILL.md` | Fix 3, 5 | 修改 ~25 行 |
| `plugins/article-craft/skills/series/SKILL.md` | Fix 6 | 修改 ~10 行 |
| `skills/series/SKILL.md` | Fix 6 | 同步修改 ~10 行 |
| `plugins/article-craft/skills/images/SKILL.md` | Fix 2 | 确认路径 ~2 行 |

共 6 个文件，预计改动 ~80 行。

## 验证方式

修复完成后，运行 `/article-craft:series next`（生成第 27 篇），验证：
1. write 生成的 IMAGE 占位符直接被 images 脚本识别（无需手动修格式）
2. images 脚本一次调用成功（路径正确）
3. review 评分合理（快速模式不再因跳过维度而虚低）
4. 自动修改 1 轮完成（不再 3 轮）
5. series next 不再手动拼参数
