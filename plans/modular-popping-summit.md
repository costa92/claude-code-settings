# Dev-Framework GSD 设计思想升级计划

## Context

通过研读 GSD (Get Shit Done) 框架的设计哲学，提取其中高价值、可落地的设计理念，升级 dev-framework skill。GSD 的核心洞察是 **Context Rot 防治**（AI 上下文填满后质量退化）和 **Goal-Backward 验证**（从目标出发反向验证计划完整性）。本次不做全面重写，而是选取 6 项实用改进逐步集成。

## 改动总览

| # | 改进项 | 核心价值 | 涉及文件 |
|---|--------|----------|----------|
| 1 | Context Manifest（上下文注入清单） | 防 context rot | SKILL.md, orchestrator.py |
| 2 | 结构化 Task 元数据 | 消除脆弱正则 | templates/design.md, agents/architect.md, orchestrator.py |
| 3 | validate-plan 预执行验证 | 拦截低质量设计 | orchestrator.py, SKILL.md |
| 4 | Wave 执行升级 | 更精确的并行调度 | orchestrator.py, SKILL.md |
| 5 | Atomic Git Commit | 可追溯、可回滚 | orchestrator.py, SKILL.md |
| 6 | STATE.md + resume 命令 | 跨会话恢复 | orchestrator.py, SKILL.md |

---

## 改进 1: Context Manifest（上下文注入清单）

**GSD 原则**: 每个 Agent 只接收必需的 artifact，不注入无关历史，防止 context rot。

**现状问题**: SKILL.md Phase 3 step 3（行 74-96）的注入规则零散且宽泛，Developer 可能收到完整 PRD，Reviewer 可能收到所有旧 handoff。

### 改动 1a: SKILL.md — 插入 Context Manifest 表

在 Phase 3 step 3（行 74）前插入 Context Manifest 表，替代当前零散的条件注入逻辑（行 76-96）：

| Agent | MUST 注入 | MUST NOT 注入 | 条件注入 |
|-------|-----------|---------------|----------|
| pm | agents/pm.md, templates/prd.md, 最新 handoff, project.yaml(name/lang/fw) | design.md, profiles/, review-report.md, test-report.md | — |
| ui-designer | agents/ui-designer.md, templates/ui-design.md, 最新 handoff, prd.md | design.md, profiles/, review-report.md | — |
| architect | agents/architect.md, templates/design.md, prd.md(全文), project.yaml(全量), 最新 handoff | profiles/, review-report.md, test-report.md | ui-design.md(若存在) |
| developer | agents/developer.md, profiles/{lang}.md, **当前 Task section**(非全文 design.md), 最新 handoff | 全文 prd.md, test-report.md, 旧 handoff | review-report.md(仅退回时) |
| reviewer | agents/reviewer.md, profiles/{lang}.md, 当前 Task section + API 定义 section, prd.md 验收标准 section, 最新 handoff | 全文 prd.md, 全文 design.md, 旧 handoff, test-report.md | ui-design.md(need_browser_test 时) |
| tester | agents/tester.md, profiles/{lang}.md, 测试策略 + API 定义 section, prd.md 验收标准 section, 最新 handoff | 全文 prd.md, 全文 design.md, 旧 handoff | ui-design.md 测试选择器(need_browser_test 时) |

将当前 step 3 条件链改写为："查阅 Context Manifest 表，为 current_agent 注入 MUST 项，检查条件项，确认不包含 MUST NOT 项。使用 `extract-section` 命令提取指定 section。"

### 改动 1b: orchestrator.py — 新增 `extract-section` 命令

在 `cmd_detect_frontend_changes` 之后新增，约 20 行：

```python
def cmd_extract_section(args):
    """从 artifact 文件提取指定 section"""
    artifact_path = os.path.join(_plan_dir(args.project_dir), "artifacts", args.file)
    if not os.path.isfile(artifact_path):
        _output({"section": args.section, "content": "", "found": False})
        return
    content = open(artifact_path, encoding="utf-8").read()
    pattern = rf'(##{{1,3}}\s+{re.escape(args.section)}.*?)(?=\n##{{1,3}}\s|\Z)'
    m = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    _output({"section": args.section, "content": m.group(1).strip() if m else "", "found": bool(m)})
```

subparser: `--file design.md --section "Task 1"`

---

## 改进 2: 结构化 Task 元数据

**GSD 原则**: 机器可读的 YAML 元数据替代脆弱正则解析。

### 改动 2a: templates/design.md — Task List section（行 66-77）

替换为 HTML 注释包裹的 YAML 元数据格式：

```markdown
## Task List

### Task 1: {名称}
<!-- task-meta
files: [path/to/file1, path/to/file2]
deps: []
wave: 1
-->
- 描述: {要实现什么}

### Task 2: {名称}
<!-- task-meta
files: [path/to/file1, path/to/file3]
deps: [Task 1]
wave: 2
-->
- 描述: {要实现什么}
```

### 改动 2b: agents/architect.md — Task List 格式说明（行 42-58）

替换为新格式规范。输出护栏（行 70-77）新增检查项：
- `[ ] 每个 Task 包含 <!-- task-meta --> 块（files, deps, wave）`
- `[ ] wave 编号从 1 开始，无依赖的 Task 为 wave 1`

### 改动 2c: orchestrator.py — parse-tasks YAML 优先解析

在 `cmd_parse_tasks` 函数开头（现有正则之前）增加 ~45 行 YAML 优先路径：

```python
# YAML-first: 解析 <!-- task-meta ... --> 块
meta_pattern = re.compile(
    r'###\s+(Task[- ]?\d+)[：:]\s*(.+?)\n'
    r'<!-- task-meta\s*\n(.*?)\n-->',
    re.DOTALL
)
matches = meta_pattern.findall(content)
if matches:
    for raw_id, name, yaml_str in matches:
        tid = _normalize_task_id(raw_id)
        meta = _simple_yaml_load(yaml_str)
        tasks.append({
            "id": tid, "name": name.strip(),
            "files": meta.get("files", []),
            "deps": [_normalize_task_id(str(d)) for d in meta.get("deps", [])],
            "wave": meta.get("wave", 1),
        })
    # 从 wave 字段构建 waves dict + parallel_groups
    waves = {}
    for t in tasks:
        w = str(t.get("wave", 1))
        waves.setdefault(w, []).append(t["id"])
    parallel_groups = [waves[k] for k in sorted(waves.keys(), key=int)]
```

现有正则逻辑完整保留为 fallback（matches 为空时执行）。

输出新增字段：`waves`, `total_waves`, `parse_method`（`yaml_meta` 或 `regex_fallback`）。

---

## 改进 3: validate-plan 预执行验证

**GSD 原则**: Goal-backward verification — 执行前验证计划完整性。

### 改动 3a: orchestrator.py — 新增 `validate-plan` 命令（~100 行）

6 维度评分（满分 100）：

| 维度 | 满分 | 检查内容 |
|------|------|----------|
| Section 完整性 | 20 | 技术选型/数据模型/API 定义/Task List/目录结构 |
| Task 元数据完整 | 20 | 每个 Task 有 name + files（非空）+ deps |
| DAG 有效性 | 15 | 依赖引用合法、无环（拓扑排序） |
| 文件覆盖度 | 15 | 目录结构中的文件被 Task files 覆盖 |
| Wave 一致性 | 15 | task.wave > max(deps.wave) |
| PRD 对齐 | 15 | prd.md 验收标准 keywords 出现在 Task 描述中 |

输出: `{"score": N, "max_score": 100, "pass": bool, "dimensions": {...}, "blocking_issues": [...], "warnings": [...]}`

阈值: `score < 60` → `pass: false`

### 改动 3b: SKILL.md — Phase 3.5 增加验证步骤

在 `parse-tasks` 之后、首个 Developer dispatch 之前插入 ~8 行：

```
parse-tasks 完成后运行:
python3 orchestrator.py validate-plan --project-dir {PWD}

- pass == false → 退回 Architect，prompt 包含 blocking_issues
- score < 80 → 在 Phase 4 审批时展示 warnings
- score >= 80 → 直接继续
```

---

## 改进 4: Wave 执行升级

### 改动 4a: orchestrator.py — check-conflicts 全路径匹配

行 1309 `f.split("/")[-1]` → `f.strip()`（全路径匹配）。

新增目录级软冲突检测，输出增加 `soft_conflicts` 字段。

### 改动 4b: orchestrator.py — wave 进度追踪

`project.yaml` 新增 `current_wave: 1`, `total_waves: N`。

`cmd_complete_task` 中：同 wave 所有 task 完成 → 自动 `current_wave += 1`。

需要 `cmd_parse_tasks` 将 `total_waves` 写入 project.yaml（在 parse-tasks 成功返回时）。

### 改动 4c: SKILL.md — Phase 3.5 并行策略重写（行 143-188）

替换为 wave 术语：

```
Wave 执行策略：
1. parse-tasks 返回 waves: {1: [...], 2: [...]}
2. 取 current_wave（project.yaml）
3. 对 wave 内 tasks 运行 check-conflicts
4. 无硬冲突 → 并行；有硬冲突 → 串行
5. 有软冲突 → 并行但 Warning
6. Wave 全部 Reviewer PASS → 下一 wave
7. FAIL → 退回 wave 内失败 task
```

---

## 改进 5: Atomic Git Commit

### 改动 5a: orchestrator.py — init 增加 git 检测

`cmd_init` 末尾增加 ~5 行，写入 `project.yaml["is_git_repo"]`。

### 改动 5b: SKILL.md — Phase 3 增加 step 6.5

在 complete-task 和 handoff 之间（行 101 前）插入 ~10 行：

```
6.5 Atomic Commit（仅 is_git_repo == true）：
  git add {files_created} {files_modified}
  git commit -m "feat(dev-fw): {task_id} - {task_name}
  Wave {wave}/{total_waves} | Task {current}/{total}"
```

---

## 改进 6: STATE.md + resume 命令

### 改动 6a: orchestrator.py — `_update_state_md` helper（~50 行）

在 `cmd_handoff`, `cmd_next`, `cmd_complete_task`, `cmd_approve` 末尾调用。
从 project.yaml + handoff/ 聚合生成 `.plan/STATE.md`：
- Current Status（agent, phase, task, wave）
- Progress table（per task: status, wave, reviewer result）
- Decisions（from project.yaml["decisions"]）
- Cumulative files（from handoff files）

### 改动 6b: orchestrator.py — 新增 `resume` 命令（~60 行）

分析 project.yaml + STATE.md + trace.log + handoff/，检测异常：
- artifact 缺失但 agent 标 done
- handoff 链断裂（last handoff.to != current_agent）
- task 状态不一致

输出: `{"resume_action", "resume_context", "anomalies", "suggested_prompt"}`

### 改动 6c: orchestrator.py — 新增 `decision` 命令（~20 行）

记录决策: `--agent X --decision "Y" --rationale "Z"` → project.yaml["decisions"] 追加。

### 改动 6d: SKILL.md — Phase 1 会话恢复

替换行 34-41 的 `status` 调用为 `resume`。

---

## 实现顺序（Wave 分组）

### Wave 1（无依赖，可并行）
- 改进 1: Context Manifest + extract-section
- 改进 2: 结构化 Task 元数据
- 改进 6: STATE.md + resume + decision

### Wave 2（依赖 Wave 1）
- 改进 3: validate-plan（依赖改进 2 的结构化数据）
- 改进 4: Wave 执行升级（依赖改进 2 的 wave 字段）

### Wave 3（依赖 Wave 2）
- 改进 5: Atomic Git Commit（依赖改进 4 的 wave 追踪）

## 验证

| 改进 | 验证方法 |
|------|----------|
| 1 | 完整流程检查每个 Agent prompt 仅含 Manifest 项 |
| 2 | 含 `<!-- task-meta -->` 的 design.md 运行 parse-tasks 验证 YAML；删除 meta 验证 fallback |
| 3 | 缺陷 design.md（缺 section、环形 dep）运行 validate-plan 验证拦截 |
| 4 | 3-wave 5-task design 验证全路径冲突检测 + wave 递进 |
| 5 | git 项目验证每 task 一个 commit；非 git 验证静默跳过 |
| 6 | 中断后新会话 resume 验证正确恢复 |
