# Dev-Framework 优化计划

## Context

在 wechat-account 项目上实际运行 dev-framework 后，发现 7 个问题：Tester 被跳过、review-report/test-report 缺失、project.yaml 状态不一致、completed_tasks 未追踪、Phase 4.5 集成验证未执行、前端 14 个构建错误未被捕获、早期 handoff 字段不完整。

**根因**：orchestrator.py 只是状态机（强制转换规则），不是流程验证器。SKILL.md 的指令可以被执行者忽略而不触发任何错误。

## 修改文件

| 文件 | 改动量 |
|------|--------|
| `~/.claude/skills/dev-framework/orchestrator.py` | 6 处修改 + 1 个新命令 |
| `~/.claude/skills/dev-framework/SKILL.md` | 4 处修改 |
| `~/.claude/skills/dev-framework/agents/reviewer.md` | 1 处修改 |
| `~/.claude/skills/dev-framework/agents/tester.md` | 1 处修改 |

## Step 1: orchestrator.py — 添加 import 和常量

**文件**: `orchestrator.py` 第 13 行后

- 添加 `import subprocess`
- 在 `PHASE_MAP` 字典后（第 41 行后）添加 `REQUIRED_ARTIFACTS` 常量：

```python
REQUIRED_ARTIFACTS = {
    "reviewer": {"file": "review-report.md", "agent_name": "Reviewer"},
    "tester": {"file": "test-report.md", "agent_name": "Tester"},
}
```

## Step 2: orchestrator.py — cmd_next 添加 Artifact 前置检查

**文件**: `orchestrator.py` 第 517 行后（`if target is None` 错误块之后，`if target == "_rollback"` 之前）

插入 artifact 存在性验证：当 `current_agent` 是 reviewer 或 tester 时，验证对应 report 文件存在。不存在则报错退出，阻止流程推进。

这是**最关键的修改**，直接解决 Issue 1（Tester 被跳过）和 Issue 2（report 缺失）。

## Step 3: orchestrator.py — cmd_next _check_tasks 添加 complete-task 门控

**文件**: `orchestrator.py` 第 583 行（`if current_task:` 块内）

在 regex 解析 task 编号之前，验证 `current_task` 在 `completed_tasks` 列表中。不在则报错。

解决 Issue 4（completed_tasks 未追踪）。

## Step 4: orchestrator.py — cmd_handoff 添加字段验证

**文件**: `orchestrator.py` 第 402 行后（`project = _read_project(pd)` 之后）

两项验证：
1. full 模式下 developer/reviewer/tester 的 handoff 必须提供 `--current-task`
2. developer handoff 时验证 current_task 已通过 complete-task 标记

解决 Issue 7（handoff 字段不完整）。

## Step 5: orchestrator.py — cmd_status 修复状态一致性

**文件**: `orchestrator.py` 第 383-396 行

在 `_output(result)` 之前：
1. 当 trace 最后事件为 "done" 时，覆写 response 中的 `current_agent` 为 "done"
2. 添加 `missing_artifacts` 字段，列出当前阶段应有但缺失的 artifact

解决 Issue 3（project.yaml 状态不一致）。

## Step 6: orchestrator.py — 新增 validate-build 命令

**文件**: `orchestrator.py`

添加辅助函数 `_run_build_cmd` 和命令 `cmd_validate_build`：
- 根据 project.yaml 的 language/has_frontend 自动运行对应构建命令
- Go: `go build ./...`
- Python: `python3 -m compileall -q {pkg}`
- TypeScript: `npx tsc --noEmit`
- 前端: 自动查找 web/frontend/client 子目录运行 `npm run build`
- 返回 `{success: bool, results: [...]}`，失败时 exit(1)

在 main() argparser 和 commands dict 中注册。

解决 Issue 5（Phase 4.5 无执行方式）和 Issue 6（前端构建错误未捕获）。

## Step 7: orchestrator.py — 增强 cmd_diagnose

**文件**: `orchestrator.py` 第 1006-1055 行

替换现有 diagnose 为更全面的验证：
- 检查 trace/project.yaml 状态一致性
- 按阶段检查预期 artifact 是否存在
- 检查 completed_tasks 与 current_task 一致性
- 检查 handoff 文件完整性
- 返回 `{status, issues, warnings, suggestions}`

## Step 8: SKILL.md — Phase 3 添加 Artifact 验证步骤

**文件**: `SKILL.md` 第 98-103 行之间（步骤 7 和 8 之间）

插入步骤 7.5：对 reviewer/tester，验证对应 artifact 文件已创建。未创建则重试 Agent，不调用 next。与 orchestrator.py 的检查形成双重保险。

## Step 9: SKILL.md — Phase 3.5 强化 complete-task 顺序

**文件**: `SKILL.md` 第 140-144 行

修改步骤 6 的措辞，明确"必须在 handoff 之前调用"，并注明"跳过会导致 handoff 和 next 报错"。

## Step 10: SKILL.md — Phase 4.5 使用 validate-build 命令

**文件**: `SKILL.md` 第 169-179 行

将模糊的"由主 Agent 直接执行"替换为具体的 orchestrator.py 调用：
```bash
python3 ~/.claude/skills/dev-framework/orchestrator.py validate-build --project-dir {PWD}
```
失败则修复后重试，通过后写 trace 并继续。

## Step 11: SKILL.md — Phase 5 添加完成前验证

**文件**: `SKILL.md` 第 206-212 行

在 trace done 之前，检查 review-report.md 和 test-report.md 存在（full 模式必须）。缺失则回退到对应阶段。

## Step 12: agents/reviewer.md — 强调 Artifact 必须先于 JSON

**文件**: `agents/reviewer.md` 第 34 行

将第 6 步改为强调 review-report.md **必须在输出 JSON 之前创建**，并注明 orchestrator 会验证文件存在。

## Step 13: agents/tester.md — 强调 Artifact 必须先于 JSON

**文件**: `agents/tester.md` 第 31 行

同上，强调 test-report.md **必须在输出 JSON 之前创建**。

## 问题覆盖矩阵

| 问题 | Steps |
|------|-------|
| 1: Tester 被跳过 | Step 2 (artifact 门控) |
| 2: report 缺失 | Step 2, 8, 12, 13 (多层防护) |
| 3: project.yaml 不一致 | Step 5 (status 修复) |
| 4: completed_tasks 未追踪 | Step 3, 4, 9 (门控+验证+指令) |
| 5: Phase 4.5 未执行 | Step 6, 10 (新命令+SKILL.md 调用) |
| 6: 前端构建错误 | Step 6, 10 (validate-build 运行 npm run build) |
| 7: handoff 字段不完整 | Step 4 (handoff 验证) |

## 验证方案

1. 单元验证：在 wechat-account 项目上运行各 orchestrator.py 命令测试错误检查
   - `orchestrator.py next --current-agent reviewer --conclusion PASS` → 应报错（缺 review-report.md）
   - `orchestrator.py validate-build` → 应报告前端构建失败
   - `orchestrator.py diagnose` → 应列出所有已知问题
2. 删除 wechat-account/.plan/ 后完整重新运行 dev-framework，验证全流程
