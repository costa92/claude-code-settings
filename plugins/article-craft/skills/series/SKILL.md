---
name: article-craft:series
description: "Plan, manage, and generate article series — shared style, auto-navigation, progress tracking. Use when creating a multi-part tutorial, deep-dive, or themed collection."
---

# Series — 系列文章管理

规划、管理和生成系列文章。自动共享视觉风格、注入上下篇导航、跟踪写作进度。

**Invoke**: `/article-craft:series`

---

## 核心概念

```
series.md (清单文件)
├── 系列元数据：名称、定位、读者、视觉风格
├── 文章列表：每篇的标题、状态、文件路径
└── 共享配置：frontmatter 字段、导航模板

每篇文章的 frontmatter 自动注入：
  series: "系列名称"
  series_order: 2
  series_total: 5
  series_prev: "上一篇标题"
  series_next: "下一篇标题"
```

---

## 工作流

### 模式 1：创建新系列 (`/article-craft:series create`)

#### Step 1: 收集系列信息

```
Question: "What's the series about?"
Options:
  - Tool tutorial series (e.g., "Go from Zero to Hero" in 5 parts)
  - Deep-dive series (e.g., "Kubernetes Internals" in 3 parts)
  - Themed collection (e.g., "AI Agent Patterns" — loosely related articles)
  - Other (free-form)
```

Then gather:
- **系列名称**: 简短标题（如 "Go 实战教程"）
- **预计篇数**: 数字
- **目标读者**: beginner / intermediate / advanced
- **系列价值**: 一句话描述读完整个系列后读者获得什么

#### Step 2: 生成文章列表

根据系列主题，自动规划每篇文章的：
- 标题（按 style-guide 公式）
- 核心内容（1-2 句话）
- 建议顺序（递进关系）
- 预计深度（overview / tutorial / deep-dive）

展示给用户确认，允许调整标题和顺序。

#### Step 3: 确定共享风格

根据系列主题自动推断（参考 requirements 的 Smart Inference）：
- **Writing style**: A-G
- **Visual style**: S1-S6
- **Visual style prefix**: 具体的 PROMPT 风格约束（色调 + 风格 + 背景）

全系列所有文章共享同一视觉风格前缀。

#### Step 4: 生成 series.md 清单文件

**系列文章使用独立子目录**，与普通文章隔离：

```
02-技术/基础设施/Go/              ← 普通 Go 文章
02-技术/基础设施/Go/go-tutorial/  ← Go 实战教程系列（自动创建）
  ├── series-go-tutorial.md       ← 系列清单
  ├── go_environment_setup.md     ← 第 1 篇
  ├── go_data_structures.md       ← 第 2 篇
  └── ...
```

目录名使用 `series_slug`（如 `go-tutorial`、`ai-agent-patterns`）。

```bash
# 自动创建系列子目录
mkdir -p "${KB_DIR}/${series_slug}"
```

series.md 和所有系列文章都保存在这个子目录下。文章间的相对链接（`./filename.md`）天然正确。

保存 series.md 到 `${KB_DIR}/${series_slug}/series-${series_slug}.md`：

```markdown
---
series_name: "Go 实战教程"
series_slug: go-tutorial
target_audience: intermediate
total_articles: 5
visual_style: S2 (Isometric)
visual_prefix: "Isometric technical illustration, soft blue and mint green palette, white background with subtle grid"
writing_style: A (教程)
created: 2026-03-22
status: in_progress
---

# 📚 系列：Go 实战教程

## 定位
- 目标读者：有其他语言基础的中级开发者
- 系列价值：读完 5 篇，能独立用 Go 写生产级 Web 服务
- 发布节奏：每周 1 篇

## 文章列表

| # | 标题 | 核心内容 | 状态 | 文件路径 |
|---|------|---------|------|---------|
| 1 | Go 环境搭建与第一个程序 | 安装、GOPATH、Hello World、模块初始化 | 💡 planned | — |
| 2 | Go 数据结构与控制流 | 类型系统、slice/map、for/switch、错误处理 | 💡 planned | — |
| 3 | Go 并发编程：goroutine 与 channel | goroutine、channel、select、WaitGroup | 💡 planned | — |
| 4 | Go Web 开发：用 Gin 写 REST API | 路由、中间件、JSON、数据库集成 | 💡 planned | — |
| 5 | Go 项目实战：部署到生产环境 | Docker 打包、CI/CD、监控、优化 | 💡 planned | — |

## 系列间引流设计
- 每篇开头：「本文是《Go 实战教程》系列第 X/Y 篇」
- 每篇结尾：预告下一篇标题和核心内容
- 合集篇：系列完结后生成一篇合集导航文章
```

---

### 模式 2：写系列中的下一篇 (`/article-craft:series next`)

#### Step 1: 读取 series.md

读取系列清单文件，找到第一个状态为 `planned` 的文章。

#### Step 2: 调用 orchestrator

自动传入以下参数给 orchestrator：
- **topic**: 从清单中读取标题和核心内容
- **audience**: 从系列元数据读取
- **depth**: 从清单中读取
- **visual prefix**: 从系列元数据读取（确保风格一致）
- **series context**: 注入系列导航信息
- **save_path**: 保存到 series.md **同目录下**（系列子目录内），不要保存到父目录

#### Step 3: 注入系列元素

写文章时自动添加：

**Frontmatter 追加字段：**
```yaml
series: "Go 实战教程"
series_order: 2
series_total: 5
```

**文章开头（在 cover 图片之后）：**
```markdown
> [!info] 📚 系列导航
> 本文是《Go 实战教程》系列第 2/5 篇。
> 上一篇：[Go 环境搭建与第一个程序](./go_environment_setup.md)
```

**文章结尾（在 closing paragraph 之后）：**
```markdown
---

> [!tip] 📚 下一篇预告
> 《Go 并发编程：goroutine 与 channel》— 下一篇我们讲 Go 最强大的特性：
> 用 goroutine 和 channel 实现高并发，不需要锁。
```

#### Step 4: 更新 series.md

文章生成成功后，更新清单文件：
- 状态：`💡 planned` → `✅ published`
- 文件路径：填入实际保存路径
- 添加发布日期

---

### 模式 3：查看系列进度 (`/article-craft:series status`)

读取 series.md，输出进度摘要：

```
📚 系列：Go 实战教程

进度：2/5 篇 (40%)
████░░░░░░ 40%

✅ 第 1 篇：Go 环境搭建与第一个程序 (2026-03-20)
✅ 第 2 篇：Go 数据结构与控制流 (2026-03-22)
💡 第 3 篇：Go 并发编程：goroutine 与 channel
💡 第 4 篇：Go Web 开发：用 Gin 写 REST API
💡 第 5 篇：Go 项目实战：部署到生产环境

下一步：运行 /article-craft:series next 写第 3 篇
```

---

### 模式 4：生成合集导航 (`/article-craft:series collection`)

系列全部完成后，自动生成一篇合集导航文章：

- 标题：「Go 实战教程：从零到生产的完整指南（合集）」
- 内容：系列介绍 + 每篇文章的摘要和链接
- 用途：作为系列的入口页面

---

### 模式 5：批量生成 (`/article-craft:series batch`)

一次性生成多篇系列文章。适用于新建系列或补充缺失文章的场景。

#### 输入

```
Question: "Which articles to generate?"
Options:
  - All planned — generate all 💡 planned articles
  - Range — specify article numbers (e.g., #3-#5)
  - Specific — pick individual articles
```

#### 执行流程

**关键原则：不使用 Agent（避免超时），直接在主会话中逐篇生成。**

```
读取 series.md
  ↓
筛选待生成文章列表
  ↓
探测 Gemini 模型（一次探测，所有文章复用）
  ↓
For each article:
  ├── 1. 读取该文章的 topic、audience、visual_prefix
  ├── 2. 在主会话中直接调用 write skill 生成文章
  ├── 3. 运行 post-write validation（Rule 1/11/12/14）
  ├── 4. 自动修复红旗词和占位符问题
  ├── 5. 保存文件
  ├── 6. 自动生成图片（调用 generate_and_upload_images.py --process-file）
  ├── 7. 更新 series.md 状态
  ├── 8. 输出进度：✅ 第 N 篇完成 (M/Total)
  └── 9. 继续下一篇（单篇失败不阻塞）
  ↓
输出批量生成报告
```

#### 容错机制

- **单篇失败不阻塞**：记录失败文章和原因，继续生成下一篇
- **断点续传**：如果中途中断，重新运行时自动跳过已标记为 `published` 的文章
- **进度显示**：每完成一篇输出进度条

#### 完成报告

```
════════════════════════════════════════════════════════════
📚 批量生成完成：Go 实战教程
════════════════════════════════════════════════════════════

✅ 成功：5/8 篇
  ✅ #3 Go 并发编程 (456 lines)
  ✅ #4 Go Web 开发 (523 lines)
  ✅ #5 Go 项目实战 (489 lines)
  ✅ #6 Go 测试与 CI (412 lines)
  ✅ #7 Go 性能优化 (538 lines)

❌ 失败：1/8 篇
  ❌ #8 Go 微服务架构 — 错误：content too long, manual review needed

⏭️ 下一步：
  - 修复失败文章：运行 /article-craft:series next
  - 生成图片：运行 /article-craft:images 逐篇处理
  - 质量审查：运行 /review @series.md
════════════════════════════════════════════════════════════
```

#### 与 next 模式的区别

| 维度 | next 模式 | batch 模式 |
|------|----------|-----------|
| 生成数量 | 1 篇 | N 篇 |
| 执行方式 | 调用 orchestrator | 直接调用 write skill |
| 图片生成 | 包含在 orchestrator 中 | 包含（逐篇生成后自动执行） |
| review | 包含在 orchestrator 中 | 不包含（后续批量运行） |
| 适用场景 | 逐篇精细打磨 | 快速批量覆盖 |

---

## Standalone Mode

当独立调用 `/article-craft:series` 时：

```
Question: "What do you want to do?"
Options:
  - Create a new series — plan a multi-part article collection
  - Write next article — continue an existing series
  - Check status — view series progress
  - Generate collection — create a summary article for a completed series
```

如果 KB 中存在多个 series.md 文件，列出让用户选择。

---

## 与 orchestrator 的集成

orchestrator 支持 `--series SERIES_FILE` 标志：

```bash
/article-craft --series ./series-go-tutorial.md
```

等同于 `/article-craft:series next`，自动从清单中读取下一篇的配置。

---

## 与 content-planner 的关系

content-planner 已有系列规划模板（选题、排期），article-craft:series 是**执行层**：

```
content-planner   → 规划系列选题和排期（"写什么"）
article-craft:series → 执行系列生成（"怎么写"、进度跟踪、风格一致性）
```

两者互补，不重复。content-planner 的系列输出可以直接作为 article-craft:series 的输入。

---

## 关键规则

1. **风格一致性**: 系列内所有文章共享相同的 visual style prefix（从 series.md 读取）
2. **导航自动注入**: 每篇文章自动加上一篇/下一篇导航，不需要手动管理
3. **进度持久化**: series.md 是进度的单一真相源，每篇完成后自动更新
4. **渐进式**: 可以先 create 规划，随时 next 写下一篇，不需要一次写完
5. **独立可用**: 系列中的每篇文章仍然是独立的 .md 文件，可以单独阅读
