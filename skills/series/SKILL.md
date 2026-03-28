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

只传 `--series SERIES_FILE` 一个参数，orchestrator 自动从 series.md 中读取所有配置：

```
/article-craft --series /path/to/series-{slug}.md
```

Orchestrator 自动提取 topic、audience、visual prefix、writing style、save_path、series context。**不要手动拼接参数**。

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

> [!warning] 下一篇预告区块同样受红旗词规则约束
> 在 `> [!tip] 📚 下一篇预告` 中也**禁止**使用红旗词，包括：
> - `极致`、`颠覆`、`完美`、`赋能`、`一站式`
> - `链路`（即使描述技术流程）— 改用 `请求处理流程`、`调用路径`、`调用时序`
> - `综上所述`、`总而言之`、`值得注意的是`
>
> 写预告内容时用具体的技术描述，不用营销词汇。

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

### 模式 5：知识覆盖度审计 (`/article-craft:series audit`)

对已完成或进行中的系列进行知识域覆盖度分析，识别缺失主题，为续季规划提供依据。

#### Step 1: 确定审计范围

读取 series.md，提取系列主题域、目标读者等级、已有文章列表及核心内容。

#### Step 2: 构建知识图谱

用 WebSearch 查询该领域的权威知识体系：
1. 官方文档目录结构
2. 权威认证考试大纲（如 CKA/CKAD）
3. 同类优质系列/书籍目录
4. 社区高频问题和最佳实践

#### Step 3: 覆盖度映射

将已有文章映射到知识图谱节点：
- ✅ 已覆盖：有专门文章深度讲解
- 🟡 部分覆盖：在其他文章中提到但未深入
- ❌ 未覆盖：系列中完全没有涉及

覆盖率 = (已覆盖 × 1.0 + 部分覆盖 × 0.5) / 总知识点数 × 100%

#### Step 4: 生成审计报告

输出覆盖率、已覆盖/部分覆盖/未覆盖列表、重要程度评分（⭐⭐⭐/⭐⭐/⭐）、续季建议。

#### Step 5: 续季规划（可选）

如果用户确认要开新季，从未覆盖主题中筛选 P0/P1 主题，调用模式 1 创建新季 series.md。

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
  - Audit coverage — analyze knowledge gap and plan next season
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
