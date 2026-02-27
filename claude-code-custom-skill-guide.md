---
title: "别只会用 /help —— Claude Code 自定义 Skill 入门指南"
date: 2026-02-27
tags: [Claude Code, AI 工具, 开发效率, Skill]
category: AI 工具链
status: draft
aliases: [claude-code-skill-guide, 自定义skill教程]
abstract: "Claude Code 的自定义 Skill 功能，让你把重复的工作流固化为可复用的指令。本文从零开始，用三分钟带你创建第一个 Skill，并详解参数传递、动态注入等进阶用法。"
---

我用 Claude Code 写了三个月代码，直到有一天同事甩给我一个 `/deploy` 命令——输入一行，自动跑测试、构建、推到生产环境。我才意识到，我一直在用的只是 Claude Code 的基础功能，而他已经把 Claude 调教成了专属助手。

区别在哪？**自定义 Skill。**

![Claude Code Skills 官方文档页面](https://cdn.jsdelivr.net/gh/costa92/article-images/images/claude-code-custom-skill-guide_claude-code-skills-docs.jpg)

## Skill 是什么，不是什么

Skill 就是一个 `SKILL.md` 文件，放在特定目录下，Claude Code 启动时会自动发现它。你在 SKILL.md 里写好指令，Claude 就会在合适的时候加载这些指令来增强自己的能力。

它**不是**插件系统，不需要写 JavaScript/Python 代码（虽然可以配合脚本）。它的本质是**结构化的提示词**——用 YAML 元数据告诉 Claude "我是谁、什么时候用我"，用 Markdown 正文告诉 Claude "该怎么做"。

一个最简单的 Skill 长这样：

```yaml
---
name: explain-code
description: 用类比和 ASCII 图解释代码。当用户问"这段代码怎么工作的"时使用。
---

解释代码时，遵循以下步骤：

1. 先用一个日常生活的类比来描述
2. 画一个 ASCII 流程图展示结构
3. 逐步走读关键代码
4. 指出一个常见的误解或坑
```

两个 `---` 之间是 YAML frontmatter，下面是 Markdown 指令。就这么简单。

## 三分钟创建你的第一个 Skill

### 第 1 步：建目录

```bash
mkdir -p ~/.claude/skills/commit-helper
```

Skill 放在 `~/.claude/skills/` 下就是**个人级**的，所有项目都能用。如果放在项目的 `.claude/skills/` 下，只对当前项目生效。

| 位置 | 路径 | 生效范围 |
|------|------|---------|
| 个人 | `~/.claude/skills/<名称>/SKILL.md` | 你的所有项目 |
| 项目 | `.claude/skills/<名称>/SKILL.md` | 仅当前项目 |
| 插件 | `<插件>/skills/<名称>/SKILL.md` | 启用了该插件的项目 |

### 第 2 步：写 SKILL.md

创建 `~/.claude/skills/commit-helper/SKILL.md`：

```yaml
---
name: commit-helper
description: 生成规范的 Git commit message。当用户说"提交"、"commit"、"写个提交信息"时使用。
---

根据 staged changes 生成 commit message，遵循以下规范：

## 格式
type(scope): 简短描述

## type 可选值
- feat: 新功能
- fix: 修复 bug
- refactor: 重构
- docs: 文档
- chore: 杂项

## 规则
- 描述用中文，type 和 scope 用英文
- 描述不超过 50 字
- 如果改动复杂，加上 body 说明"为什么改"
```

### 第 3 步：测试

两种触发方式：

```
# 方式 1：直接用斜杠命令
/commit-helper

# 方式 2：自然语言触发（Claude 根据 description 自动匹配）
帮我写个提交信息
```

没有编译、没有安装步骤。保存文件后新会话即可使用，编辑中的会话也可能自动检测到变更。

## Frontmatter 字段详解

description 是唯一"推荐填"的字段，但掌握其他字段能让 Skill 更可控。

```yaml
---
name: deploy
description: 部署应用到生产环境
disable-model-invocation: true
allowed-tools: Bash(npm *), Bash(docker *)
context: fork
---
```

核心字段一览：

| 字段 | 作用 | 默认值 |
|------|------|--------|
| `name` | Skill 名称，即 `/` 命令名 | 目录名 |
| `description` | 告诉 Claude 什么时候用这个 Skill | 正文第一段 |
| `disable-model-invocation` | 设为 `true` 禁止 Claude 自动触发 | `false` |
| `user-invocable` | 设为 `false` 从 `/` 菜单隐藏 | `true` |
| `allowed-tools` | 该 Skill 激活时允许的工具 | 无限制 |
| `context` | 设为 `fork` 在子 Agent 中运行 | 主会话 |
| `model` | 指定运行模型 | 继承当前 |

两个控制触发的字段容易混淆，画个表就清楚了：

| 设置 | 用户能 `/触发` | Claude 自动触发 | 适用场景 |
|------|--------------|----------------|---------|
| 默认 | 能 | 能 | 一般用途 |
| `disable-model-invocation: true` | 能 | 不能 | 部署、发消息等有副作用的操作 |
| `user-invocable: false` | 不能 | 能 | 背景知识、项目约定等 |

> [!tip]
> 有副作用的操作（部署、发消息、删数据）一定要加 `disable-model-invocation: true`。你不会想让 Claude 因为"代码看起来准备好了"就自动部署。

## 参数传递

Skill 支持接收参数。用 `$ARGUMENTS` 占位符：

```yaml
---
name: fix-issue
description: 修复 GitHub Issue
disable-model-invocation: true
---

修复 GitHub Issue $ARGUMENTS，遵循项目编码规范。

1. 读取 Issue 描述
2. 理解需求
3. 实现修复
4. 写测试
5. 创建 commit
```

运行 `/fix-issue 123` 时，`$ARGUMENTS` 会被替换成 `123`。

需要多个参数？用索引访问：

```yaml
---
name: migrate
description: 迁移组件框架
---

将 $0 组件从 $1 迁移到 $2，保留所有现有行为和测试。
```

`/migrate SearchBar React Vue` → `$0=SearchBar`, `$1=React`, `$2=Vue`。

## 配套文件：让 Skill 更强大

Skill 不只是一个 SKILL.md。你可以在目录里放入脚本、模板、参考文档：

```
my-skill/
├── SKILL.md           # 主指令（必须）
├── template.md        # 输出模板
├── examples/
│   └── sample.md      # 示例输出
├── references/
│   └── api-docs.md    # 参考文档
└── scripts/
    └── validate.sh    # 可执行脚本
```

在 SKILL.md 里引用它们，Claude 会在需要时加载：

```markdown
## 参考资源

- 完整 API 文档见 [references/api-docs.md](references/api-docs.md)
- 输出格式参考 [examples/sample.md](examples/sample.md)
```

> [!warning]
> SKILL.md 建议控制在 **500 行以内**。详细的参考资料放到单独文件中，Claude 会按需加载，不会每次都塞进上下文。

## 动态注入：让 Skill 读取实时数据

前面的 Skill 都是写好就固定的。但有时候你需要实时数据——比如当前的 PR diff、最新的测试结果。

用 `` !`command` `` 语法可以在 Skill 加载前执行 Shell 命令，把输出注入到提示词中：

```yaml
---
name: pr-summary
description: 总结 PR 变更
context: fork
---

## PR 上下文
- Diff: !`gh pr diff`
- 评论: !`gh pr view --comments`
- 变更文件: !`gh pr diff --name-only`

## 任务
基于以上信息总结这个 PR...
```

`` !`gh pr diff` `` 会在 Claude 看到提示词之前执行，结果直接替换占位符。Claude 收到的是填好数据的完整提示词。

## 实战案例：代码审查 Skill

把前面学到的都用上，做一个实用的代码审查 Skill：

```yaml
---
name: review
description: 审查当前改动的代码质量。当用户说"帮我看看代码"、"review"时使用。
allowed-tools: Read, Grep, Glob, Bash(git diff *)
---

审查 `git diff` 中的改动，关注以下维度：

## 审查清单
1. **Bug 检测**：逻辑错误、空指针、竞态条件
2. **安全性**：注入漏洞、敏感信息泄露、权限问题
3. **代码规范**：命名、格式、项目约定
4. **性能**：N+1 查询、不必要的循环、内存泄漏

## 输出格式
按严重程度分组（Critical / Important / Suggestion），每个问题包含：
- 文件路径和行号
- 问题描述
- 修复建议

只报告有把握的问题，不确定的标注 [需确认]。
```

保存到 `~/.claude/skills/review/SKILL.md`，以后在任何项目里说"帮我 review 一下"，Claude 就知道该怎么做了。

## 常见问题

**Skill 没有被触发？**
- 检查 description 是否包含了用户会自然说出的关键词
- 试试直接 `/skill-name` 调用
- 在对话中问 Claude "你有哪些可用的 skill？"确认它能看到

**Skill 触发太频繁？**
- 把 description 写得更具体
- 加 `disable-model-invocation: true` 改为仅手动触发

**Skill 太多导致一些不显示？**
- Skill 描述会占用上下文预算（约上下文窗口的 2%，fallback 为 16,000 字符）
- 运行 `/context` 查看是否有 Skill 被排除的警告
- 可设置环境变量 `SLASH_COMMAND_TOOL_CHAR_BUDGET` 调整上限

## 从这里开始

1. 先做一个最简 Skill（5 行就够），验证流程跑通
2. 把你经常对 Claude 重复说的话提炼成 Skill
3. 有副作用的操作加上 `disable-model-invocation: true`
4. 复杂 Skill 拆分成 SKILL.md + 配套文件

Anthropic 维护了一个官方 Skill 仓库，可以直接拿来用或参考：https://github.com/anthropics/skills

![Anthropic 官方 Skills 仓库](https://cdn.jsdelivr.net/gh/costa92/article-images/images/claude-code-custom-skill-guide_anthropic-skills-repo.jpg)

自定义 Skill 的本质是把你的工作流固化下来。每次你发现自己在重复教 Claude 同一件事，那就是一个 Skill 的种子。

---

**参考链接**（以下链接请在浏览器中打开）

- **Claude Code Skills 官方文档**: https://code.claude.com/docs/en/skills
- **Anthropic Skills 仓库**: https://github.com/anthropics/skills
- **如何创建自定义 Skills（帮助中心）**: https://support.claude.com/en/articles/12512198-how-to-create-custom-skills
- **Agent Skills 开放标准**: https://agentskills.io

![帮助中心：如何创建自定义 Skills](https://cdn.jsdelivr.net/gh/costa92/article-images/images/claude-code-custom-skill-guide_claude-support-skills.jpg)

![Agent Skills 开放标准网站](https://cdn.jsdelivr.net/gh/costa92/article-images/images/claude-code-custom-skill-guide_agentskills-io.jpg)
