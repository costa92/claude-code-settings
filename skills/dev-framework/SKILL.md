---
name: dev-framework
description: 多 Agent 软件开发协作框架。多个专家 Agent 通过 Handoff 协作，覆盖需求→设计→编码→审查→测试全流程。当用户说「开发」「做一个」「实现」「修复」时使用。
---

# Dev Framework

多 Agent 软件开发协作框架。SKILL.md 是决策层，orchestrator.py 是状态层。

**关键约束：SKILL.md 不可自行决定下一个 Agent，必须通过 orchestrator.py next 获取。所有状态变更通过 orchestrator.py 完成。**

## 触发词

开发、做一个、实现、build、develop、implement、fix

## 执行流程

### Phase 1: 初始化

检查 `.plan/` 是否存在：

**不存在（首次运行）：**

1. 检测项目语言（扫描 go.mod / pyproject.toml / package.json），均不存在则询问用户
2. 运行:
   ```bash
   python3 ~/.claude/skills/dev-framework/orchestrator.py init \
     --project-dir {PWD} --language {lang} --framework {fw}
   ```
3. 进入 Phase 2

**已存在（会话恢复）：**

1. 运行:
   ```bash
   python3 ~/.claude/skills/dev-framework/orchestrator.py resume --project-dir {PWD}
   ```
2. 根据返回的 `resume_action`:
   - `completed` → 提示"流程已完成，如需重新开始请删除 .plan/ 目录"
   - `await_approval` → 进入 Phase 4（人工审批）
   - `dispatch_{agent}` → 构建该 Agent 的 prompt，继续调度循环
   - 如果 `anomalies` 非空 → 向用户展示异常项，建议修复后继续

   返回的额外字段：
   - `resume_context`: 包含 agent/phase/task/mode/wave/total_waves/completed_tasks，用于构建恢复 prompt
   - `suggested_prompt`: 建议的用户提示语，可直接展示给用户
3. 查看 `.plan/STATE.md`（由 resume 自动更新）了解完整进度

### Phase 2: Triage 路由

1. 读取 `agents/triage.md` 内容
2. 构建 prompt: triage.md 内容 + 用户输入
3. 通过 Agent tool 调度 Triage subagent
4. 提取 Agent 输出中 `---JSON---` 标记包裹的 JSON（用 orchestrator.py parse-json）
5. 调用 orchestrator.py:
   ```bash
   python3 ~/.claude/skills/dev-framework/orchestrator.py handoff --project-dir {PWD} \
     --from triage --to {route_to} --summary "{summary}" --mode {mode}
   python3 ~/.claude/skills/dev-framework/orchestrator.py next --project-dir {PWD} \
     --current-agent triage --conclusion done --route-to {route_to}
   ```
6. 进入 Phase 3

### Phase 3: Agent 调度循环

```
首次进入或会话恢复时:
  0. python3 ~/.claude/skills/dev-framework/orchestrator.py status --project-dir {PWD}
     → 检查 resume_action:
     - "completed" → 提示"流程已完成"，不进入循环
     - "await_approval" → 直接进入 Phase 4
     - "dispatch_{agent}" → 从该 agent 继续（读取最新 handoff 文件获取上下文）

loop:
  1. python3 ~/.claude/skills/dev-framework/orchestrator.py status --project-dir {PWD}
     → 获取 current_agent, current_task, mode

  2. 如果 current_agent == "done" → Phase 5

  3. 构建 prompt — 查阅 Context Manifest 表，为 current_agent 注入 MUST 项，检查条件项，确认不包含 MUST NOT 项。
     使用 `extract-section` 命令提取指定 section（避免注入全文）：
     ```bash
     python3 ~/.claude/skills/dev-framework/orchestrator.py extract-section --project-dir {PWD} \
       --file design.md --section "Task 1"
     ```

     ### Context Manifest

     | Agent | MUST 注入 | MUST NOT 注入 | 条件注入 |
     |-------|-----------|---------------|----------|
     | pm | agents/pm.md, templates/prd.md, 最新 handoff, project.yaml(name/lang/fw) | design.md, profiles/, review-report.md, test-report.md | — |
     | ui-designer | agents/ui-designer.md, templates/ui-design.md, 最新 handoff, prd.md | design.md, profiles/, review-report.md | — |
     | architect | agents/architect.md, templates/design.md, prd.md(全文), project.yaml(全量), 最新 handoff | profiles/, review-report.md, test-report.md | ui-design.md(若存在) |
     | developer | agents/developer.md, profiles/{lang}.md, **当前 Task section**(非全文 design.md), 最新 handoff | 全文 prd.md, test-report.md, 旧 handoff | review-report.md(仅退回时) |
     | reviewer | agents/reviewer.md, profiles/{lang}.md, 当前 Task section + API 定义 section, prd.md 验收标准 section, 最新 handoff | 全文 prd.md, 全文 design.md, 旧 handoff, test-report.md | ui-design.md(need_browser_test 时) |
     | tester | agents/tester.md, profiles/{lang}.md, 测试策略 + API 定义 section, prd.md 验收标准 section, 最新 handoff | 全文 prd.md, 全文 design.md, 旧 handoff | ui-design.md 测试选择器(need_browser_test 时) |

     **额外注入规则（基于 project.yaml 标志）：**
     - `has_database` 或 `has_external_api` 为 true:
       - Developer: 提示"参考语言 Profile 中数据库/API 测试章节，确保实现可测试的接口抽象"
       - Tester: 用 extract-section 提取 design.md「测试策略」注入，提示"必须执行数据库测试和/或 API 测试"
       - Reviewer: 提示"检查存储层是否通过接口抽象、测试是否覆盖数据库/API 场景"
     - `has_api_server` 为 true:
       - Tester: 用 extract-section 提取 design.md「API 定义」注入，提示"必须启动真实服务执行端点验收测试"
     - **调度 Tester 时，必须运行前端变更检测**:
       ```bash
       python3 ~/.claude/skills/dev-framework/orchestrator.py detect-frontend-changes --project-dir {PWD}
       ```
       如果返回 `need_browser_test: true`（has_frontend 标志为 true **或** handoff 中有前端文件变更），则：
       - 注入浏览器测试指令（参考 Phase 4.6）
       - 读取 `templates/ui-design.md` 的自动化测试规范（如有 `.plan/artifacts/ui-design.md`）
       - 提示 Tester 必须执行浏览器测试，不可跳过

  4. 通过 Agent tool 调度 subagent
     → 调度前记录开始时间: start_time = 当前 UTC ISO 时间

  5. echo "{output}" | python3 ~/.claude/skills/dev-framework/orchestrator.py parse-json
     → 提取 JSON 结果
     → **如果返回 error**：重新调度同一 Agent（最多 1 次重试），提示 Agent 必须在输出末尾包含 ---JSON--- 标记

  6. python3 ~/.claude/skills/dev-framework/orchestrator.py trace --project-dir {PWD} \
       --agent {agent} --event artifact --detail {artifact} --message "{summary}" \
       --start-time "{start_time}"

  6.5 **Atomic Commit（仅 is_git_repo == true 且 agent == developer）**：
     ```bash
     git add {files_created} {files_modified}
     git commit -m "feat(dev-fw): {task_id} - {task_name}

     Wave {wave}/{total_waves} | Task {current}/{total}"
     ```
     如果 project.yaml 中 `is_git_repo` 为 false 或不存在，静默跳过此步骤。

  7. python3 ~/.claude/skills/dev-framework/orchestrator.py handoff --project-dir {PWD} \
       --from {agent} --to {handoff_to} --summary "{summary}" \
       --current-task "{task}" \
       --files-created "{files_created逗号分隔}" --files-modified "{files_modified逗号分隔}"

  7.5 **Artifact 验证（reviewer/tester 专用）**：
     如果 current_agent 是 reviewer 或 tester，在调用 next 之前验证对应 artifact 文件已创建：
     - reviewer → 检查 `.plan/artifacts/review-report.md` 存在
     - tester → 检查 `.plan/artifacts/test-report.md` 存在
     如果文件不存在，**不调用 next**，而是重新 dispatch 同一 Agent（最多 1 次重试），在 prompt 中强调必须创建 artifact 文件。
     注意：orchestrator.py next 也会做此检查（双重保险），但在 SKILL.md 层提前拦截可以避免无谓的错误输出。

  8. python3 ~/.claude/skills/dev-framework/orchestrator.py next --project-dir {PWD} \
       --current-agent {agent} --conclusion {conclusion} \
       --current-task "{task}" --total-tasks {N}
     → 获取 next_agent

  9. 如果 next.blocked == true:
     - 如果是审批 → Phase 4
     - 如果是回退超限 → 通知用户人工介入
     否则 → 回到 1
```

### Phase 3.5: 任务迭代（full 模式）

当 Architect 完成后，在进入 Developer 前:

```bash
python3 ~/.claude/skills/dev-framework/orchestrator.py parse-tasks --project-dir {PWD}
→ {"tasks": [...], "total": N, "parallel_groups": [["Task 1", "Task 2"], ["Task 3"]]}
```

记住 total，在后续调用 orchestrator.py next 时传入 --total-tasks N。

#### 预执行验证

parse-tasks 完成后，验证设计质量：

```bash
python3 ~/.claude/skills/dev-framework/orchestrator.py validate-plan --project-dir {PWD}
```

根据返回的 `score` 和 `pass` 决定后续：
- `pass == false`（score < 60）→ 退回 Architect，prompt 包含 `blocking_issues`
- `score < 80` 且 `pass == true` → 在 Phase 4 审批时向用户展示 `warnings`
- `score >= 80` → 直接继续

#### Wave 执行策略

#### Wave 执行策略

`waves` 返回按依赖分组的 Wave 批次（`{1: ["Task 1", "Task 2"], 2: ["Task 3"]}`）。`current_wave` 从 project.yaml 读取（初始为 1）。

**同一 Wave 内的 Task 无依赖关系，应并行执行。**

**⚠️ 并行前必须检查文件冲突：**
```bash
python3 ~/.claude/skills/dev-framework/orchestrator.py check-conflicts --project-dir {PWD} \
  --tasks "Task 2,Task 3,Task 4"
```
- `has_conflicts: true`（硬冲突）→ 将冲突 Task 改为串行执行
- `soft_conflicts` 非空（目录级重叠）→ 可并行但 Warning，留意合并问题
- 无冲突 → 并行执行

**执行流程：**

1. 取当前 Wave（`current_wave` 对应的 tasks 列表）
2. 对 Wave 内 tasks 运行 `check-conflicts`，硬冲突 Task 拆出串行
3. 为可并行的 Task 构建 Developer prompt
4. 通过 Agent tool **在单条消息中同时调度多个 subagent**（并行执行）
5. 收集所有 Developer 输出
6. **对每个完成的 Task 调用 `complete-task` 标记完成**（必须在 handoff 之前调用，跳过会导致 handoff 和 next 报错）：
   ```bash
   python3 ~/.claude/skills/dev-framework/orchestrator.py complete-task --project-dir {PWD} \
     --task-id "Task N"
   ```
   `complete-task` 会自动追踪 Wave 进度：同 Wave 所有 Task 完成后自动推进 `current_wave`。
7. **必须 dispatch Reviewer Agent 做批量审查**（不可直接 PASS，不可跳过 Reviewer dispatch）：
   - 构建 Reviewer prompt，传入所有已完成 Task 的文件列表
   - 通过 Agent tool 调度 Reviewer subagent
   - 获取审查结论（PASS/FAIL）
8. Reviewer PASS 后，使用 `--completed-through` 一次性跳到下一 Wave：
   ```bash
   python3 ~/.claude/skills/dev-framework/orchestrator.py next --project-dir {PWD} \
     --current-agent reviewer --conclusion PASS \
     --completed-through {Wave最后一个Task编号} --total-tasks {N}
   ```
   **注意**: `--completed-through` 会校验 1-N 的所有 Task 是否已通过 `complete-task` 标记完成，未标记的会报错。
9. 如果 Reviewer FAIL，退回该 Wave 所有 Task 给 Developer 修复
10. 所有 Wave 完成后（`current_wave > total_waves`），进入下一阶段

#### 串行回退

如果并行执行中某个 Task 导致问题（如文件冲突），可回退到逐 Task 串行模式：
orchestrator.py 的 next 命令（不带 --completed-through）仍强制: Developer 完成 → 必须 Reviewer → PASS 后才能下一个 Task。

#### 禁止事项

- **禁止跳过 Reviewer dispatch**：不可直接调用 `next --conclusion PASS` 而不实际 dispatch Reviewer Agent
- **禁止跳过 complete-task**：每个 Task 完成后必须调用 `complete-task` 标记
- **禁止 completed-through 超过实际完成数**：orchestrator 会拒绝未标记完成的 Task
- **禁止跨 Wave 执行**：必须当前 Wave 全部 PASS 后才能进入下一 Wave

### Phase 4.5: 集成验证（全栈项目）

当项目同时包含前端和后端（`has_frontend: true` + 后端语言非空）时，所有 Task 完成后、进入 Tester 前，执行集成验证：

```bash
python3 ~/.claude/skills/dev-framework/orchestrator.py validate-build --project-dir {PWD}
```

此命令自动根据 project.yaml 的 language/has_frontend 运行对应构建命令：
- Go: `go build ./...`
- Python: `python3 -m compileall -q {pkg}`
- TypeScript: `npx tsc --noEmit`
- 前端: 自动查找 web/frontend/client 子目录运行 `npm run build`

**构建失败则阻塞**：命令返回 exit(1)，不可进入 Tester。修复后重新运行直到通过。
通过后写 trace：
```bash
python3 ~/.claude/skills/dev-framework/orchestrator.py trace --project-dir {PWD} \
  --agent system --event build-ok --message "集成构建验证通过"
```

### Phase 4.6: 浏览器测试（涉及前端代码时）

当 `has_frontend: true`，**或开发过程中涉及前端文件变更**时，**Tester Agent 必须执行浏览器测试**，不可跳过。

#### 判断是否需要浏览器测试

在构建 Tester prompt 前，运行：
```bash
python3 ~/.claude/skills/dev-framework/orchestrator.py detect-frontend-changes --project-dir {PWD}
```
返回 `need_browser_test: true` 时，注入浏览器测试指令。该命令检测两个条件：
1. `has_frontend: true`（project.yaml 标志）
2. handoff 文件中有前端文件变更（.html/.css/.jsx/.tsx/.vue/.svelte 等）

任一条件满足即触发。

#### 调度 Tester 时的额外注入

在构建 Tester prompt 时，除标准内容外，必须注入：

1. **`templates/ui-design.md` 中的「自动化测试规范」**（如存在 `.plan/artifacts/ui-design.md`）
2. **浏览器测试指令**：提示 Tester 使用 Playwright 执行以下验证：
   - 启动 dev server（参考语言 Profile 中的 `dev_server` 命令）
   - 截图（桌面 1280x720 + 移动端 375x667）
   - DOM 结构验证（对照 ui-design.md 的选择器规范）
   - 交互测试（表单提交、按钮点击、导航跳转）
   - Console 错误捕获（有 JS error 则 FAIL）
   - 响应式布局检查（对照 ui-design.md 断点定义）
3. **webapp-testing 工具路径**：`~/.claude/skills/webapp-testing/scripts/with_server.py`

#### 浏览器测试 artifact

截图保存至 `.plan/artifacts/screenshots/`：
- `desktop.png` — 桌面视口截图
- `mobile.png` — 移动端视口截图
- 其他交互状态截图（按需）

录制保存至 `.plan/artifacts/recordings/`：
- `trace.zip` — Playwright Trace（含操作日志 + DOM 快照 + 逐步截图 + 网络请求），回放命令：`npx playwright show-trace .plan/artifacts/recordings/trace.zip`
- `*.webm` — 浏览器操作视频（自动生成）

#### Reviewer 浏览器截图与录制审查（可选增强）

当 `has_frontend: true` 且存在 `.plan/artifacts/ui-design.md` 时，Reviewer Agent 可在审查时额外执行浏览器截图，对比实际渲染结果与设计规范。此步骤为可选增强——Reviewer 读取截图文件（png），肉眼比对 ui-design.md 中的 ASCII 线框图和组件规范。如果 Tester 已生成 Trace 录制（`.plan/artifacts/recordings/trace.zip`），Reviewer 可回放 Trace 逐步审查交互流程和网络请求。

### Phase 4: 人工审批（🔒 节点）

当 orchestrator.py next 返回 `blocked: true`（Architect → Developer 转交）:

1. 向用户展示 PRD、UI 设计（如有）和技术设计方案摘要
2. 提示: 此时可直接编辑 .plan/artifacts/prd.md、ui-design.md 或 design.md
3. 使用 AskUserQuestion 三个选项:
   - 「确认，进入编码」→ `python3 ~/.claude/skills/dev-framework/orchestrator.py approve --project-dir {PWD}`
   - 「我修改了 PRD」→ 回退到 Architect（或 UI Designer，如有前端）
   - 「我修改了设计文档」→ 直接继续编码
4. 回到 Phase 3

### 前端项目特殊流程

当 project.yaml 中 `has_frontend: true` 时，PM 完成后自动插入 UI Designer 环节：

```
PM → UI Designer → Architect → [人工审批] → Developer → Reviewer → ...
```

UI Designer 产出 `.plan/artifacts/ui-design.md`，Architect 和 Developer 必须参考此文件。
Reviewer 在审查前端代码时需对照 ui-design.md 检查 UI 实现一致性。

### Phase 5: 完成

当 orchestrator.py next 返回 `next_agent: done`:

1. **完成前验证（full 模式必须）**：检查 `.plan/artifacts/review-report.md` 和 `.plan/artifacts/test-report.md` 是否存在。
   - 如果缺失，不可写 trace done。回退到对应阶段：
     - 缺 review-report.md → 回退到 reviewer（重新 dispatch Reviewer Agent）
     - 缺 test-report.md → 回退到 tester（重新 dispatch Tester Agent）
2. python3 ~/.claude/skills/dev-framework/orchestrator.py trace --project-dir {PWD} --agent system --event done --message "交付完成"
3. 向用户输出完成摘要:
   - 创建/修改的文件列表
   - 测试结果概要
   - 所有 artifacts 路径

## Agent Prompt 构建模板

```
[agents/{agent}.md 内容]

---

## Context Packet

[最新 .plan/handoff/NNN-xxx.md 内容]

## 语言 Profile（如适用）

[profiles/{language}.md 内容]

## 模板（如适用）

[templates/{template}.md 内容]

## 项目信息

[.plan/project.yaml 内容]
```

## orchestrator.py 路径

所有 orchestrator.py 调用使用绝对路径:
```
python3 ~/.claude/skills/dev-framework/orchestrator.py {command} --project-dir {PWD}
```

## 辅助命令

### decision — 记录架构决策

Architect 完成设计后可选调用，将重要的架构/技术决策持久化到 project.yaml：

```bash
python3 ~/.claude/skills/dev-framework/orchestrator.py decision --project-dir {PWD} \
  --agent architect --decision "使用 PostgreSQL 而非 SQLite" --rationale "需要并发写入支持"
```

决策记录会写入 project.yaml 的 `decisions` 列表并同步到 STATE.md，方便后续 Agent 和会话恢复时参考。

### diagnose — 诊断项目状态

当项目状态异常（如 STATE.md 与 project.yaml 不一致、artifact 缺失等）时使用：

```bash
python3 ~/.claude/skills/dev-framework/orchestrator.py diagnose --project-dir {PWD}
```

返回 `issues`（阻塞性问题）、`warnings`（非阻塞警告）和 `suggestions`（建议），以及检测到的语言/框架信息。根据 `status` 字段判断：
- `ok` → 项目状态正常
- `warning` → 有非阻塞问题，建议修复
- `error` → 有阻塞性问题，必须修复后才能继续

## 上下文管理

长流程（full 模式 + 多 Task）容易耗尽上下文窗口。遵循以下规则：

1. **Agent prompt 精简**：构建 prompt 时只注入必要内容，不要把整个 PRD + design + 所有 handoff 历史都塞进去
2. **优先并行执行**：并行 Agent 消耗的是各自 subagent 的上下文，不增加主会话负担
3. **Agent 输出限制**：在 Agent prompt 中明确要求「输出控制在 200 行以内，只输出关键信息和 JSON 结果」
4. **中间结果落盘**：Agent 产出的报告/代码写入文件而非在对话中传递。后续 Agent 通过读取文件获取上下文
5. **handoff 文件摘要化**：handoff 只记录摘要和文件列表，不复制完整内容
