---
name: code-review
description: 核心代码审查中枢。当用户请求 code review、检查代码质量、提交 PR 前审查，或写完代码需要检查时使用。自动根据上下文将审查任务路由给相应的专属 Review Agent（如功能级、PR级、UI级审查）。
---

# Code Review (代码审查智能路由)

## Overview

本项目拥有精细化定义的多个 Code Review Agents。本 Skill 的作用是**审查调度器**。当你被要求进行代码审查时，不要自己强行阅读所有代码，而是应该**根据当前修改的上下文，选择并派发最合适的审查子 Agent**。

## 审查路由指南 (Review Routing)

在开始审查前，先判断当前代码修改的类型，并选择对应的 Agent 执行审查：

### 1. 局部功能审查 (Feature-Level Review)
- **适用场景**：用户刚完成一个具体功能或修复了一个 bug，在本地开发过程中要求快速审查。
- **关联 Agent**：`feature-dev` 插件下的 `code-reviewer`
- **执行方式**：使用 `Agent` 工具（选择 `superpowers:code-reviewer` 或 `general-purpose`），指示它以“功能级代码审查员”的身份，重点检查：Bug、边缘情况、代码规范和局部安全性。

### 2. PR 合并前全面审查 (PR-Level Review)
- **适用场景**：用户准备提交 Pull Request 或合并分支到 main，需要极高标准的全盘检查。
- **关联 Agent**：`pr-review-toolkit` 插件下的 `code-reviewer` (Opus)
- **执行方式**：获取 `BASE_SHA` 和 `HEAD_SHA` 的 diff，使用 `Agent` 工具，要求它基于项目中 `CLAUDE.md` 的规范，进行深度架构审查和质量把控。

### 3. UI 与前端界面审查 (UI/Frontend Review)
- **适用场景**：修改涉及到前端 UI 组件、页面布局、交互逻辑。
- **关联 Agent**：`ui-design` 插件下的 `ui-design-reviewer`
- **执行方式**：派发 Agent 或直接按以下 **五维指标** 进行严格打分和审查：
  1. 视觉一致性 (Visual Consistency)
  2. 响应式适配 (Responsiveness)
  3. 可访问性 (Accessibility)
  4. 交互完整性 (Interaction Completeness)
  5. 代码质量 (Code Quality)

### 4. 专项深度审查 (Specialized Deep-Dives - 按需选用)
如果在 Review 中发现特定风险，可补充调用以下专项审查维度：
- **`silent-failure-hunter`**：专门检测未捕获的 Promise、被吞掉的异常 (try-catch empty) 或可能导致静默失败的逻辑漏洞。
- **`type-design-analyzer`**：专注 TypeScript 类型设计，检测随意的 `any`、不合理的 interface 继承或冗余的类型映射。
- **`go-best-practices-analyzer`**：专注 Golang 规范审查，检测 goroutine 泄漏、未处理的 error、channel 死锁风险、锁的滥用 (sync.Mutex)、context 传递规范以及依赖管理规范。

## 使用方式与案例 (Usage & Examples)

你可以通过自然语言触发本 Skill 进行审查路由，以下是一些典型使用场景和触发案例：

**案例 1：快速重构后的局部审查 (触发 Feature-Level Review)**
```
用户："帮我 review 一下刚才写的 user_auth.go"
Code Review Skill 行为：
1. 识别重点为单一文件，调出 `feature-dev` 的 code-reviewer。
2. 因为是 .go 文件，额外载入 `go-best-practices-analyzer` 规范。
3. 发现 `err` 没有被 `return`，抛出 🔴 警告，并提供修复方案。
```

**案例 2：提交大型需求 PR 之前 (触发 PR-Level Review)**
```
用户："我要提 PR 了，做一下全盘代码检查吧"
Code Review Skill 行为：
1. 分析出这是合并前的请求，提取当前分支相对 main 的整体 git diff。
2. 调度 `pr-review-toolkit` 下的 Opus code-reviewer。
3. 结合项目的 CLAUDE.md 规范，全面评估架构、安全和注释质量。
```

**案例 3：前端组件开发完毕 (触发 UI/Frontend Review)**
```
用户："看看我新加的侧边栏组件 Navbar.tsx 写得怎么样"
Code Review Skill 行为：
1. 识别到前台组件变更，触发 `ui-design-reviewer` 审查逻辑。
2. 输出五维评测报告：视觉一致性、响应式适配（提醒加上 mobile viewport 断点逻辑）、无障碍支持（ARIA）等。
```

**案例 4：针对并发逻辑的问题追查 (触发专项审查)**
```
用户："帮我检查一下这里处理高并发的 Go 代码有没有可能产生死锁"
Code Review Skill 行为：
1. 捕捉到特定关键词“高并发”和“死锁”。
2. 直接拉取 `go-best-practices-analyzer` 进行专项扫描。
3. 检查通道关闭逻辑、`defer mu.Unlock()` 以及 context 管理等深层问题。
```

## 标准执行流 (Workflow)

当用户说“帮我 review 一下代码”时，严格执行以下步骤：

1. **定位变更差异**：
   使用 Bash 工具运行 `git diff` 或 `git diff <base_branch>...HEAD` 来获取本次需要 review 的确切代码内容。
   *(如果用户指定了某个文件，则直接 Read 读取该文件。)*

2. **匹配并派发 Agent**：
   通过 `Agent` tool 派发任务，在 `prompt` 中明确告知所选的审查身份和重点：
   *“请作为 [选定的 Review Agent 身份]，审查以下代码更改。重点关注...”*

3. **结构化输出报告**：
   将 Agent 返回的审查结果，整理成清晰的报告展示给用户：
   - 🔴 **高危/阻断性问题 (Critical)**：必须修复的 bug 或严重性能、安全问题。
   - 🟡 **改进建议 (Important)**：代码异味、类型优化、可复用性建议。
   - 🟢 **亮点 (Strengths)**：写得好的地方。

4. **提供一键修复**：
   在报告最后，询问用户：“是否需要我使用 Edit/Write 工具为您自动应用上述 🔴 和 🟡 的修改建议？”