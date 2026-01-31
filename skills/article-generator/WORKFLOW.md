# Article Generator - 详细工作流程

本文档详细说明了 article-generator 的完整工作流程，包括标准流程、快速模式和各种使用场景。

> **提示**: 这是详细流程文档。如需快速了解，请查看 [SKILL.md](./SKILL.md)

---

## 📋 目录

- [标准文章生成流程](#标准文章生成流程)
- [快速模式（仅文章）](#快速模式仅文章)
- [预写作验证清单](#预写作验证清单)
- [用户交互指南](#用户交互指南)
- [图片生成工作流](#图片生成工作流)
- [最佳实践](#最佳实践)
- [常见场景示例](#常见场景示例)

---

## 标准文章生成流程

**⚠️ CRITICAL: 你必须执行实际的工具调用（Write、Shell）来完成每个步骤。仅在聊天中显示内容是不够的。**

### 流程图

```
1. 明确需求
   ├─ 主题和范围
   ├─ 目标受众（初学者/开发者/架构师）
   ├─ 文章长度（~2000-3000 字推荐）
   └─ 图片需求（封面 + 节奏图）

2. 研究 & 验证（强制性）
   ├─ WebSearch 查找官方文档
   ├─ 验证所有工具/命令存在
   ├─ 在沙箱中测试命令（如果可能）
   └─ 向用户报告已验证/未验证项目

3. 内容生成
   ├─ YAML frontmatter
   ├─ 文章结构和标题
   ├─ 代码示例（可运行、完整）
   ├─ Obsidian callouts 用于关键信息
   └─ 明确的参考链接

4. 💾 保存文章到文件（强制性 - 不可跳过）
   ├─ 从文章标题生成文件名（如 "kimi-k25-claude-code.md"）
   ├─ 使用 Write 工具保存内容到文件
   ├─ 向用户确认文件路径（如 "./kimi-k25-claude-code.md"）
   └─ 绝不只在聊天中显示内容而不保存文件

5. 🎨 图片生成（如果请求）
   ├─ 重要：使用 Shell(command="realpath filename.md") 获取绝对路径
   ├─ 创建 images/ 目录：mkdir -p images
   ├─ 生成唯一的文件名前缀（如 article_slug_）
   ├─ 使用 Shell 工具调用 generate_and_upload_images.py（使用绝对路径）
   ├─ 示例：python3 /home/hellotalk/.claude/skills/article-generator/scripts/generate_and_upload_images.py --process-file /absolute/path/to/article.md
   ├─ 生成封面（16:9: 1344x768）
   ├─ 生成节奏图（3:2: 1248x832）
   ├─ 上传所有图片到 PicGo/CDN
   ├─ 使用 CDN URLs 更新文章文件
   └─ 成功上传后自动删除本地文件

6. 最终审查
   ├─ 验证所有链接正常（HTTP 200）
   ├─ 确认所有代码示例完整
   ├─ 检查没有 AI 陈词滥调或营销废话
   └─ 确保 YAML frontmatter 完整
```

### 执行要求

- **步骤 4（保存到文件）是不可协商的** - 你必须调用 Write 工具
- **步骤 5（图片生成）需要实际的 Shell 命令执行**
- **如果你只显示内容而不保存文件，任务就是不完整的**

---

## 快速模式（仅文章）

适用于想要**先写文章，稍后添加图片**的用户。

### 流程图

```
1. 明确需求
   ├─ 主题和范围
   ├─ 目标受众
   ├─ 文章长度
   └─ 确认："暂时跳过图片"

2. 研究 & 验证（强制性）
   ├─ 与标准流程相同
   └─ 报告已验证/未验证项目

3. 内容生成（仅文章）
   ├─ YAML frontmatter
   ├─ 文章结构和标题
   ├─ 代码示例（可运行、完整）
   ├─ Obsidian callouts
   ├─ 图片占位符（见下文）
   └─ 明确的参考链接

4. 💾 保存文章到文件（强制性）
   ├─ 从标题生成文件名
   ├─ 使用 Write 工具保存到文件
   ├─ 向用户确认文件路径
   └─ 在保存的文件中包含图片占位符

5. 稍后添加图片（可选）
   ├─ 使用 generate_and_upload_images.py --process-file
   ├─ 脚本将解析占位符并生成图片
   ├─ 自动上传到 CDN
   └─ 脚本将使用 CDN URLs 更新文件
```

### 图片占位符语法

在文章中使用此格式标记图片位置：

```markdown
<!-- IMAGE: cover - 封面图 (16:9) -->
<!-- PROMPT: Modern software development workflow, minimalist illustration -->

<!-- IMAGE: pic1 - 架构示意图 (3:2) -->
<!-- PROMPT: Microservices architecture diagram, flat design, technical illustration -->
```

### 快速模式的优点

- ✅ 更快的初稿（无需等待图片生成）
- ✅ 首先关注内容质量
- ✅ 稍后轻松定位和替换占位符
- ✅ 保留提示词用于未来生成

### 何时使用快速模式

- 紧迫的截止日期（发布无图片的草稿）
- 对图片风格/需求不确定
- 在移动设备/有限带宽上写作
- 稍后为多篇文章批量生成图片

---

## 预写作验证清单

**关键**: 在写任何文章之前，完成此验证清单。缺少任何步骤会导致文章被拒绝。

### 受信任工具白名单（跳过验证）

以下广泛使用的工具是**预先验证的** - 无需 WebSearch：

**开发工具:**
- Docker, Kubernetes, Git, npm, yarn, pnpm, pip, cargo, Maven, Gradle
- Node.js, Python, Go, Rust, Java, TypeScript, Ruby

**操作系统 & 包管理器:**
- apt, yum, dnf, brew, pacman, apk, snap

**常见 CLI 工具:**
- curl, wget, ssh, scp, rsync, grep, sed, awk, tar, gzip

**为什么需要白名单？** 这些工具有稳定的 API 和广泛的官方文档。可以信任它们的基本命令。

**何时仍需验证：**
- 小众标志或选项（如 `docker run --gpus` 需要验证）
- 版本特定功能（如 "Docker 24.0+ only"）
- 已弃用的命令

### 验证步骤

#### 步骤 1: 工具/项目研究（对于非白名单工具是强制性的）
- 对于不在白名单中的工具，使用 WebSearch 或 WebFetch 查找官方文档
- 阅读 README、官方文档或 GitHub 仓库以了解实际功能
- 绝不依赖工具名称相似性或"常识"来推断功能

#### 步骤 2: 命令/功能验证（强制性）
- 对于每个命令（bash、CLI 工具、API 调用），验证它存在于官方文档中
- **例外**: 白名单工具的基本命令可以信任
- 如果你无法找到命令的文档，它就不存在 - 不要包含它
- 命令必须从官方文档复制粘贴，而不是发明或假设

#### 步骤 3: 工作流验证（强制性）
- 对于多步骤工作流，验证每一步都有官方来源记录
- 如果任何步骤不确定，标记为 "[需要验证]" 并要求用户确认
- 绝不用"合理假设"填补空白

#### 步骤 4: 预生成报告（强制性）
生成文章前，向用户报告：
- "✅ 已验证工具: [列表]"
- "✅ 受信任（白名单）: [列表]"
- "❓ 未验证项目: [列表]"（如果有 - 请求用户澄清）

只有在用户确认未验证项目或你删除它们后才继续。

**执行：**
- 任何虚构的命令/功能 → 拒绝整篇文章
- 任何未验证的声明 → 询问用户或省略部分
- 有疑问时 → 询问，绝不猜测

---

## 用户交互指南

### 强制性：对所有用户决策使用 AskQuestion 工具

生成文章时，你必须使用 `AskQuestion` 工具收集用户需求和偏好。这提供了清晰、结构化的交互体验。

**核心原则：渐进式交互**
- ✅ 一次问一个问题
- ✅ 在继续之前等待用户响应
- ✅ 每个问题应该有 2-4 个带描述的清晰选项
- ✅ 根据先前的答案调整后续问题
- ❌ 绝不在单条文本消息中问所有问题

### 何时使用 AskQuestion

#### 场景 1: 初始需求收集
文章生成开始时，收集：
1. 主题和范围
2. 目标受众
3. 文章长度/深度
4. 图片需求

#### 场景 2: 模糊的内容决策
当你遇到：
- 多个有效的实现方法
- 不确定的技术细节
- 用户请求中缺少的信息
- 需要在写作风格之间选择

#### 场景 3: 图片生成工作流
生成图片前，确认：
- 图片风格和格式
- 需要的图片数量
- 是立即生成还是使用占位符

#### 场景 4: 错误处理和重试
当问题发生时：
- 图片生成超时/失败
- PicGo 上传错误
- 验证失败

### 问题模板示例

#### 示例 1: 目标受众选择
```javascript
AskQuestion({
  questions: [{
    id: "audience",
    prompt: "这篇文章的目标读者是？",
    options: [
      {
        id: "beginner",
        label: "初学者 - 需要详细的基础知识和步骤说明"
      },
      {
        id: "developer",
        label: "开发者 - 需要代码示例和最佳实践"
      },
      {
        id: "architect",
        label: "架构师 - 需要设计思路和性能分析"
      }
    ]
  }]
})
```

#### 示例 2: 文章长度
```javascript
AskQuestion({
  questions: [{
    id: "length",
    prompt: "期望的文章篇幅？",
    options: [
      {
        id: "quick",
        label: "快速入门（500-1000字）- 15分钟阅读，核心概念介绍"
      },
      {
        id: "tutorial",
        label: "实战教程（2000-3000字）- 完整代码示例和实践步骤"
      },
      {
        id: "deep",
        label: "深度解析（4000+字）- 原理剖析、性能优化、最佳实践"
      }
    ]
  }]
})
```

#### 示例 3: 图片生成决策
```javascript
AskQuestion({
  questions: [{
    id: "images",
    prompt: "如何处理文章配图？",
    options: [
      {
        id: "generate",
        label: "立即生成（封面 + 节奏图）- 自动生成并上传到CDN，一步完成"
      },
      {
        id: "placeholder",
        label: "仅占位符（稍后添加）- 文章中使用HTML注释占位，可后续批量生成"
      },
      {
        id: "none",
        label: "纯文字文章 - 不需要配图"
      }
    ]
  }]
})
```

---

## 图片生成工作流

### 方法 1: 从配置文件批量生成（推荐）

#### 步骤 1: 创建图片配置 JSON

```json
{
  "images": [
    {
      "name": "封面图",
      "prompt": "Modern AI technology, neural network visualization, blue and purple gradient, professional tech style",
      "size": "1344x768",
      "aspect_ratio": "16:9",
      "filename": "ai_article_cover.jpg"
    },
    {
      "name": "架构图",
      "prompt": "System architecture diagram, microservices, containers, cloud infrastructure, technical illustration",
      "size": "1248x832",
      "aspect_ratio": "3:2",
      "filename": "ai_article_pic1.jpg"
    }
  ]
}
```

#### 步骤 2: 执行批量生成

```bash
python3 /home/hellotalk/.claude/skills/article-generator/scripts/generate_and_upload_images.py \
  --config images_config.json \
  --output-dir ./images \
  --resolution 2K
```

### 方法 2: 从 Markdown 文件自动处理（推荐用于已有文章）

**重要：必须使用绝对路径！**

#### 步骤 1: 获取文件的绝对路径

```bash
# 错误方式（相对路径）
--process-file ./article.md  # ❌ 将失败

# 正确方式（绝对路径）
realpath article.md  # 返回: /home/hellotalk/onedrive/docs/article.md
```

#### 步骤 2: 使用绝对路径执行

```bash
python3 /home/hellotalk/.claude/skills/article-generator/scripts/generate_and_upload_images.py \
  --process-file /home/hellotalk/onedrive/docs/article.md \
  --resolution 2K
```

### 图片规格

**支持的尺寸：**
- 封面：1344x768 (16:9)
- 节奏图：1248x832 (3:2) 或 1152x896 (5:4)
- 方形：1024x1024 (1:1)
- 竖版：768x1344 (9:16)
- 超宽：1536x672 (21:9)
- **不支持**: 900x383（需要从 1344x768 手动裁剪）

### 重试和错误处理

- **SSL/网络错误**: 自动重试 3 次（2-3 秒延迟）
- **目录错误**: 自动修复 `mkdir -p`
- **上传失败**: 快速失败 - 任何上传错误都会停止整个工作流，以防止生成带有损坏图片链接的文章
- **其他错误**: 报告给用户，询问决定

### 进度跟踪

- 批量生成使用 tqdm 显示进度条（自动安装）
- 显示：当前图片名称、进度百分比、时间估计
- 示例：`📸 处理 2/5: 封面图 |████░░░░| 40% [00:15<00:22]`
- 如果 tqdm 不可用，回退到简单计数器

---

## 最佳实践

### 写作风格

1. **无 AI 味道**: 消除营销废话、虚假互动、过度使用感叹号和 AI 陈词滥调
2. **直接和技术性**: 关注技术准确性而非可读性
3. **标题中无 emoji**: 绝不在文章标题或章节标题（# ## ###）中使用 emoji
4. **emoji 仅在 callouts 中**: 必要时在 Obsidian callouts 内可接受

### 结构

5. **需要 YAML frontmatter**: 每篇文章必须以元数据开头（title、date、tags、category、status、aliases）
6. **Obsidian callouts**: 使用 `> [!type]` 语法（abstract、info、tip、warning、note、success、quote）
7. **单个参考部分**: 末尾一个"参考链接"部分，删除重复
8. **无冗余部分**: 避免"互动环节"、"写在最后"、"下期预告"
9. **无元数据重复**: 不要在文章末尾重复 tags/date

### 代码 & 链接

10. **代码必须可运行**: 包含完整的、可执行的代码，带有类型注释、文档字符串、错误处理
11. **仅明确链接**: 使用 `**名称**: https://url` - 绝不使用 `[[双括号]]`
12. **验证所有链接**: 在包含之前使用 curl/WebFetch 确认 URLs 返回 HTTP 200
13. **技术比较**: 使用参数表（成本、延迟、内存），而不是主观评分

### 图片

14. **图片集成**: 通过 nanobanana 生成（3000 字文章 1 个封面 + 4-6 个节奏图）
15. **上传到 CDN**: 使用 PicGo 上传，嵌入 CDN URLs，删除本地文件
16. **唯一文件名**: 每篇文章必须有唯一的图片前缀（如 `ollama_cover.jpg` vs `unsloth_cover.jpg`）

### 仅文章模式

17. **占位符格式**: 使用 HTML 注释标记未来图片位置
    ```markdown
    <!-- IMAGE: cover - 封面图 (16:9) -->
    <!-- PROMPT: your image generation prompt here -->
    ```
18. **占位符位置**: 标题后封面，每 400-600 字一个节奏图
19. **保留提示词**: 始终包含 PROMPT 注释用于稍后批量生成
20. **替换工作流**: 图片准备好时使用查找-替换将占位符换成 CDN URLs

### 项目消歧

21. **当用户提到项目时**:
    - 首先使用 WebSearch 或 GitHub API 搜索
    - 如果找到多个项目：
      - 列出所有候选项目：名称、星标、描述、URL
      - 询问用户："找到 X 个名为 [name] 的项目。你指的是哪一个？"
    - 绝不假设用户指的是哪个项目

### 输出

22. **输出到当前目录**: 在用户的 pwd 中生成，而不是 skill 目录
23. **响应中的文件路径**: 显示给用户时使用相对路径（如 `./article_name.md`），但调用图片生成脚本时使用绝对路径

---

## 常见场景示例

### 场景 1: 标准技术博客（带图片）

**用户请求**: "写一篇关于 Docker 容器化的实战教程"

**工作流**:
1. ✅ 使用 AskQuestion 明确受众（开发者）
2. ✅ 使用 AskQuestion 确认长度（2000-3000字）
3. ✅ 使用 AskQuestion 确认图片（封面 + 节奏图）
4. ✅ 验证：Docker 在白名单中，基本命令可信任
5. ✅ 生成文章内容（YAML + 结构 + 代码 + callouts）
6. ✅ 使用 Write 工具保存到 `docker-containerization-guide.md`
7. ✅ 获取绝对路径：`realpath docker-containerization-guide.md`
8. ✅ 生成图片：`python3 ... --process-file /absolute/path/docker-containerization-guide.md`
9. ✅ 最终审查并向用户确认

### 场景 2: 快速草稿（无图片）

**用户请求**: "快速写一篇 Kubernetes 入门，先不要图片"

**工作流**:
1. ✅ 使用 AskQuestion 明确受众（初学者）
2. ✅ 使用 AskQuestion 确认长度（500-1000字）
3. ✅ 确认：跳过图片，使用占位符
4. ✅ 验证：Kubernetes 在白名单中
5. ✅ 生成文章内容（包含图片占位符）
6. ✅ 使用 Write 工具保存到 `kubernetes-quickstart.md`
7. ✅ 向用户确认文件路径
8. ✅ 告知用户稍后可以运行图片生成

### 场景 3: 翻译和本地化

**用户请求**: "将这个英文博客翻译成中文技术文章"

**工作流**:
1. ✅ 使用 WebFetch 获取原始内容
2. ✅ 使用 AskQuestion 明确受众和风格
3. ✅ 翻译内容，保持技术准确性
4. ✅ 调整为符合中文技术博客风格
5. ✅ 使用 Write 工具保存翻译后的文章
6. ✅ （可选）生成适合中文读者的本地化图片

### 场景 4: 批量图片生成

**用户请求**: "为 3 篇已有的文章生成图片"

**工作流**:
1. ✅ 列出 3 篇文章的路径
2. ✅ 对每篇文章：
   - 获取绝对路径：`realpath article.md`
   - 运行：`python3 ... --process-file /absolute/path/article.md`
3. ✅ 验证所有图片上传成功
4. ✅ 向用户确认完成

---

## 相关文档

- **[SKILL.md](./SKILL.md)** - 核心指南和快速参考
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - 问题排查指南
- **[INSTALL.md](./INSTALL.md)** - 安装和配置
- **[references/](./references/)** - 详细的写作和图片指南

---

**最后更新**: 2026-01-31
**版本**: 1.0.0
