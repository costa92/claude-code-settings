# Dev-Framework Bug 修复与优化计划

## Context

通过三轮系统性测试和代码审计，发现 orchestrator.py 中存在若干 bug、状态一致性问题、错误处理缺陷，以及 SKILL.md/agents 中的文档不一致。本计划按优先级修复所有问题。

## 涉及文件

| 文件 | 改动类型 |
|------|----------|
| `~/.claude/skills/dev-framework/orchestrator.py` | Bug 修复 + 优化 |
| `~/.claude/skills/dev-framework/agents/reviewer.md` | 文档修正 |
| `~/.claude/skills/dev-framework/SKILL.md` | 补充缺失文档 |

---

## 修复 1: 运算符优先级 Bug (HIGH)

**行 1068** — regex fallback 路径中文件路径过滤条件错误：

```python
# 当前（错误）：
if clean and '/' in clean or '.' in clean:
# 等价于: (clean and '/' in clean) or ('.' in clean)
# 任何含 . 的字符串（如空字符串 + 属性名）都会通过

# 修复：
if clean and ('/' in clean or '.' in clean):
```

---

## 修复 2: 缺失 `_update_state_md()` 调用 (HIGH)

两处修改 project.yaml 后未同步 STATE.md：

**2a — `cmd_parse_tasks` 行 1150**：写入 `total_waves`/`current_wave` 后缺少调用。
```python
_write_project(pd, project)
_update_state_md(args.project_dir)  # 新增
```

**2b — `cmd_complete_task` 行 1391**：wave 自动推进后缺少调用。
```python
project["current_wave"] = current_wave + 1
_write_project(pd, project)
# 不需要单独调用 — 行 1395 已有 _update_state_md()
# 但需确认 _write_project 在 _update_state_md 之前执行（当前顺序正确）
```

> 注意：2b 实际上后续行 1395 已调用 `_update_state_md`，只有 2a 需要修复。

---

## 修复 3: `cmd_next` 路由路径状态同步 (HIGH)

多个早期 return 路径不更新 project.yaml：

**3a — `_check_tasks` (reviewer PASS) 路径**（行 897-912）：返回 `next_agent: developer|tester` 但不更新 `current_agent`。

修复：在 reviewer PASS 路径中，对 `developer` 和 `tester` 两种结果分别更新 project.yaml：
```python
if task_num < total:
    next_task = f"Task {task_num + 1}"
    pd = _plan_dir(args.project_dir)
    project = _read_project(pd)
    project["current_task"] = next_task
    _write_project(pd, project)
    _output({...})
else:
    pd = _plan_dir(args.project_dir)
    project = _read_project(pd)
    project["current_agent"] = "tester"
    project["current_phase"] = "testing"
    _write_project(pd, project)
    _output({...})
```

**3b — `target == "done"` 路径**（行 984-993）：已更新 project.yaml 但最后的 `_update_state_md` 仅在未走早期 return 时执行。将 `_update_state_md` 调用移到 `_write_project` 之后，early return 之前。

**3c — 其他路径统一添加 `_update_state_md`**：`_from_route`, `_pm_next`, `_await_approval` 路径虽然不需要更新 project.yaml，但应确保调用 `_update_state_md()` 以保持 STATE.md 最新。

实现方式：将 `_update_state_md` 调用从末尾移到每个路径内部，或在函数入口/出口统一调用。推荐方式：在函数末尾保留，但每个 early return 前也调用一次。

---

## 修复 4: `cmd_extract_section` 异常处理 (MEDIUM)

**行 1405** — 文件读取无 try-except：
```python
# 当前：
content = open(artifact_path, encoding="utf-8").read()

# 修复：
try:
    with open(artifact_path, encoding="utf-8") as f:
        content = f.read()
except (IOError, OSError, UnicodeDecodeError) as e:
    _output({"section": args.section, "content": "", "found": False, "error": str(e)})
    return
```

---

## 修复 5: 错误处理风格统一 (MEDIUM)

`cmd_parse_tasks` 行 1000 用 `return`，`cmd_check_conflicts` 行 2020 用 `sys.exit(1)`。统一为 **return + error 字段**（不用 sys.exit），让调用方根据 JSON 中的 error 字段判断。

修改 `cmd_check_conflicts`：
```python
# 当前：
_output({"error": "design.md not found"})
sys.exit(1)

# 修复：
_output({"error": "design.md not found", "has_conflicts": False, "conflicts": [], "soft_conflicts": []})
return
```

---

## 修复 6: Reviewer Agent 文档修正 (MEDIUM)

**`agents/reviewer.md` 行 44, 51**：

当前 行 44 `"handoff_to": "tester|developer"` 和行 51 `handoff_to: "reviewer_pass"` 矛盾且后者不被 orchestrator 使用。

修正：
```markdown
---JSON---
{
  "status": "done",
  "artifact": ".plan/artifacts/review-report.md",
  "conclusion": "PASS|FAIL",
  "handoff_to": "developer",
  "current_task": "Task N",
  "summary": "审查概要",
  "context_for_next": "..."
}
---JSON---

- `conclusion: PASS` → orchestrator 决定下一步（进入下个 Task 的 Developer 或 Tester）
  - **PASS 时 handoff_to 字段会被 orchestrator 覆盖，可填任意值**
- `conclusion: FAIL` → `handoff_to: developer`
```

删除行 51 的 `"reviewer_pass"` 引用。

---

## 修复 7: `_normalize_task_id` 健壮性 (LOW)

**行 245-248** — 当正则不匹配时返回原字符串，可能导致大小写不一致。

```python
def _normalize_task_id(raw):
    """Task-1 / Task 1 / Task1 / task 1 → 'Task 1'"""
    m = re.match(r'[Tt]ask[- ]?(\d+)', raw.strip())
    return f"Task {m.group(1)}" if m else raw.strip()
```

改用 `raw.strip()` 避免前后空格问题，并明确 `[Tt]ask` 而非 `re.IGNORECASE`（保持确定性输出 `Task N`）。

---

## 修复 8: SKILL.md 补充缺失文档 (LOW)

**8a** — Phase 1 会话恢复部分补充 `resume` 返回字段 `resume_context` 和 `suggested_prompt`。

**8b** — 添加 `decision` 命令说明：Architect 完成设计后可选调用。

**8c** — 添加 `diagnose` 命令说明：用于排查项目状态异常。

---

## 实施顺序

1. **修复 1** — 运算符优先级（1 行改动）
2. **修复 2a** — parse_tasks 缺失 _update_state_md（1 行改动）
3. **修复 3** — cmd_next 路径状态同步（~30 行改动）
4. **修复 4** — extract_section 异常处理（5 行改动）
5. **修复 5** — 错误处理统一（2 行改动）
6. **修复 6** — reviewer.md 文档修正（~10 行改动）
7. **修复 7** — normalize_task_id（1 行改动）
8. **修复 8** — SKILL.md 文档补充（~20 行改动）

## 验证

每个修复完成后运行对应测试命令：

| 修复 | 验证方法 |
|------|----------|
| 1 | `parse-tasks` 对含 `.gitignore` 等文件名的 design.md |
| 2a | `parse-tasks` 后检查 STATE.md 包含 wave 信息 |
| 3 | `next` 各路径后检查 project.yaml current_agent 一致 |
| 4 | `extract-section` 对不可读文件返回 error 而非崩溃 |
| 5 | `check-conflicts` 对缺失 design.md 返回 JSON 而非 exit(1) |
| 6 | Reviewer 文档人工复核 |
| 7 | `normalize_task_id("task-1")` → `"Task 1"` |
| 8 | SKILL.md 文档人工复核 |
