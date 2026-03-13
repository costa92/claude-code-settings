---
name: dev-framework
description: 多 Agent 软件开发协作框架。多个专家 Agent 通过 Handoff 协作，覆盖需求→设计→编码→审查→测试全流程。当用户说「开发」「做一个」「实现」「修复」时使用。
---

# Dev Framework

多 Agent 软件开发协作框架，基于 OpenAI 多 Agent 设计哲学。

## 触发词

开发、做一个、实现、build、develop、implement、fix

## 执行流程

### Phase 1: 初始化

检查项目根目录下 `.plan/` 是否存在：

**不存在（首次运行）：**

1. 创建目录结构：
   ```
   .plan/
   ├── project.yaml
   ├── trace.log
   ├── handoff/
   └── artifacts/
   ```
2. 检测项目语言（按优先级扫描）：
   - `go.mod` → language: go
   - `pyproject.toml` / `setup.py` / `requirements.txt` → language: python
   - `package.json`（含 react 依赖）→ language: react
   - `tsconfig.json` / `package.json`（无 react）→ language: typescript
   - 均不存在 → 询问用户
3. 初始化 `project.yaml`（使用 templates/project.yaml 模板）
4. 向 `.gitignore` 追加 `.plan/`（如果不存在）
5. 写入 trace.log 首条记录

**已存在（会话恢复）：**

1. 读取 `.plan/project.yaml` 获取 `current_agent` 和 `current_phase`
2. 读取 `.plan/trace.log` 最后一条记录：
   - `handoff` → 启动目标 Agent
   - `start` 或 `artifact` → 恢复该 Agent（重新调度）
   - `blocked` → 提示用户审批
   - `done` → 提示"流程已完成，如需重新开始请删除 .plan/ 目录"
3. 告知用户恢复状态，继续流程

### Phase 2: Triage 路由

将用户输入传给 Triage Agent：

1. 读取 `agents/triage.md` 作为 Agent prompt
2. 将用户输入作为任务描述
3. 通过 Agent tool 调度 Triage subagent
4. 解析返回的 JSON（route_to, mode, summary）
5. 更新 project.yaml（mode, current_agent, current_phase）
6. 写入 handoff 文件：`.plan/handoff/001-triage-to-{target}.md`
7. 写入 trace.log

### Phase 3: Agent 调度循环

根据 Triage 路由结果（或恢复点），进入调度循环：

```
while current_agent != "done":
    1. 读取 agents/{current_agent}.md
    2. 读取对应语言 Profile（如需要）
    3. 读取对应模板文件
    4. 构建 Context Packet（注入 profile + template + 前序 artifacts）
       - 如果是 Reviewer 退回 Developer：注入 review-report.md
       - 如果是 full 模式：注入当前 Task 信息
    5. 通过 Agent tool 调度 subagent
    6. 解析返回 JSON
    7. 处理结果：
       - status: done
         → 写入 handoff 文件
         → 写入 trace.log
         → 如果 requires_approval: true → 暂停，请求人工审批（🔒）
         → 更新 current_agent = handoff_to
       - status: rollback
         → 写入 trace.log（rollback 事件）
         → 更新 current_agent = handoff_to
         → 写入 handoff 文件（附带 reason）
    8. 如果 handoff_to == "done" → 退出循环
```

### Phase 3.5: 任务迭代（full 模式）

当 Architect 产出含 Task List 的 design.md 后，按任务驱动迭代：

```
解析 design.md 中的 Task List → tasks = [Task1, Task2, ...]

for task in tasks:
    1. current_task = task
    2. 调度 Developer（注入当前 task 描述）
    3. Developer 完成 → 调度 Reviewer
    4. Reviewer PASS → 进入下一个 task
       Reviewer FAIL → 回退 Developer（注入 review-report.md），重复直到 PASS
    5. 写入 trace.log 记录每个 task 的完成

所有 tasks 完成 → 调度 Tester（整体测试）
```

快速模式下无 Task List，直接走 Developer → Reviewer → Tester。

### Phase 4: 人工审批（🔒 节点）

当 Architect Agent 返回 `requires_approval: true` 时：

1. 写入 trace.log：`blocked` 事件
2. 向用户展示：
   - PRD 摘要（来自 .plan/artifacts/prd.md）
   - 设计方案摘要（来自 .plan/artifacts/design.md）
3. 提示用户：此时可直接编辑 `.plan/artifacts/prd.md` 或 `design.md`
4. 使用 AskUserQuestion 请求审批，三个选项：
   - 「确认，进入编码」→ 写入 trace.log：`approved`，继续调度 Developer
   - 「我修改了 PRD」→ 回退到 Architect，基于修改后的 PRD 重新设计
   - 「我修改了设计文档」→ 直接继续编码，Developer 读取最新 design.md

### Phase 5: 完成

当 Tester 返回 `handoff_to: done` 时：

1. 写入 trace.log：`done` 事件
2. 更新 project.yaml：`current_phase: done`
3. 向用户输出完成摘要：
   - 创建/修改的文件列表
   - 测试结果概要
   - 所有 artifacts 的路径

## Agent 调度时的 Prompt 构建

调度每个 Agent 时，构建的完整 prompt 包含：

```
[Agent 定义文件内容]

---

## Context Packet

[最新 handoff 文件内容]

## 语言 Profile（如适用）

[profiles/{language}.md 内容]

## 模板（如适用）

[对应 template 文件内容]

## 项目信息

[project.yaml 内容]
```

## Trace 日志写入

每个关键事件写入 `.plan/trace.log`，格式：

```
[{ISO timestamp}] {AGENT} | {event_type} | {detail} | {message}
```

Agent 名缩写映射：
- triage → TRIAGE
- pm → PM
- architect → ARCH
- developer → DEV
- reviewer → REVIEW
- tester → TESTER
- 系统事件 → SYSTEM

## 错误处理

- Agent 调度失败（tool 超时等）→ 写入 trace.log error 事件，通知用户
- 回退超过 2 次 → 暂停循环，写入 trace.log，请求人工介入
- 护栏重试超过 3 次 → 写入 trace.log，转交给下一步处理或通知用户
