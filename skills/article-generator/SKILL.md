---
name: article-generator
description: Generate technical blog articles with authentic, non-AI style. Outputs Markdown format with YAML frontmatter, Obsidian callouts, code examples, and CDN images. Avoids marketing fluff and fake engagement. Supports image generation via Gemini API and automatic upload to PicGo image hosting.
---

# Article Generator

**专注于生成技术博客文章（Markdown/Obsidian 格式）**

> **🚀 新手？** 查看 [快速开始指南 (5分钟)](QUICKSTART.md) | [完整示例](examples/)

---

## 🚨 EXECUTION CHECKLIST (Read This FIRST)

**Before you finish ANY article generation task, verify ALL items below are completed:**

### ⚠️ CRITICAL: File Path Requirements

**Image generation scripts require ABSOLUTE paths, not relative paths!**

```bash
# ❌ WRONG - Will fail with "missing API key" error (misleading)
--process-file ./article.md
--process-file article.md

# ✅ CORRECT - Use absolute path
--process-file /home/hellotalk/onedrive/docs/article.md
```

**How to get absolute path:**


1. After saving file with Write tool, run: `Shell(command="realpath article.md")`
2. Use the returned absolute path in image generation commands

### ✅ Mandatory Actions (Cannot Skip)

1. **[ ] Save article to file**
   - ❌ WRONG: Display article content in chat only
   - ✅ CORRECT: Use `Write` tool to save content to `.md` file
   - Example: `Write(path="./kimi-k25-review.md", contents="...")`

2. **[ ] Generate images (if user requested)**
   - ❌ WRONG: Use relative path like `--process-file ./article.md`
   - ❌ WRONG: Mention image generation without executing scripts
   - ✅ CORRECT: Get absolute path first with `realpath`, then use Shell tool

   - Example:

     ```bash
     # Step 1: Get absolute path
     realpath article.md  # Returns: /home/hellotalk/onedrive/docs/article.md

     # Step 2: Use absolute path in image generation
     python3 /home/hellotalk/.claude/skills/article-generator/scripts/generate_and_upload_images.py \
       --process-file /home/hellotalk/onedrive/docs/article.md \
       --resolution 2K
     ```

3. **[ ] Update article with image URLs**
   - ❌ WRONG: Leave placeholder comments in saved file
   - ✅ CORRECT: Replace placeholders with actual CDN URLs after upload

4. **[ ] Verify Content Depth**
   - ✅ CORRECT: "Includes Real-world Case Study section"
   - ✅ CORRECT: "Word count > 2000 words (unless 'quick start')"
   - ❌ WRONG: Superficial tutorial without performance analysis

5. **[ ] Confirm completion to user**
   - ✅ CORRECT: "✅ 文章已保存到: ./article-name.md"
   - ✅ CORRECT: "✅ 图片已生成并上传，CDN 链接已更新"

### ⚠️ Common Mistakes to Avoid

- **Mistake 1:** Generate article content but never call `Write` tool
  - **Impact:** User has nothing to work with - task incomplete

- **Mistake 2:** Say "images will be generated" but never execute shell commands
  - **Impact:** No images created - task incomplete

- **Mistake 3:** Save article with placeholder comments but don't process them
  - **Impact:** Article has broken image placeholders - task incomplete

**IF ANY CHECKBOX ABOVE IS UNCHECKED, THE TASK IS INCOMPLETE.**

---

## 🚀 快速配置 (2 分钟)

**如果你只想快速开始，无需深入了解所有配置细节：**

### 最简配置三步走

#### 第 1 步: 安装 Python 依赖 (30 秒)

```bash
pip install -r requirements.txt
```

#### 第 2 步: 设置 API Key (1 分钟)

```bash
# 获取 API Key: https://aistudio.google.com/apikey
export GEMINI_API_KEY="your_api_key_here"

# 永久保存 (可选但推荐)
echo 'export GEMINI_API_KEY="your_key"' >> ~/.zshrc
source ~/.zshrc
```

#### 第 3 步: 开始使用 (30 秒)

```
# 在 Cursor/Claude 中调用
@article-generator 写一篇关于 Docker 的技术文章
```

**就这么简单！** 🎉

---

### 图片自动处理说明

**无需手动配置图片生成！**

- ✅ AI 会自动使用绝对路径
- ✅ 自动选择正确的图片尺寸
- ✅ 自动生成图片配置
- ✅ 如果配置了 PicGo，自动上传 CDN

**可选**: 如需手动上传图片，参见 [图片生成章节](#image-generation-examples)

---

### (可选) 配置 PicGo 图床

只有当你需要自动上传图片到 CDN 时才需要配置：

```bash
# macOS 安装
brew install picgo

# 配置图床 (选择 GitHub、SM.MS、七牛云等)
picgo set uploader

# 测试上传
echo "test" > test.txt
picgo upload test.txt
```

**S3 支持 (替代 PicGo)**:
如果不想安装 PicGo，可以直接配置 S3 (AWS/OSS/R2)。在 `~/.article-generator.conf` 中添加 S3 配置：
```json
{
  "s3": {
    "enabled": true,
    "endpoint_url": "https://<accountid>.r2.cloudflarestorage.com",
    "access_key_id": "your_access_key",
    "secret_access_key": "your_secret_key",
    "bucket_name": "your-bucket",
    "public_url_prefix": "https://pub-domain.com"
  }
}
```

**不配置也可以**：图片会保存在本地，你可以手动上传。

---

## 🔧 完整配置 (进阶)

**如果你需要自定义配置或遇到问题，查看以下详细说明：**

### 1. Install Dependencies

**Dependency Auto-Check**: `nanobanana.py` automatically checks and installs missing dependencies on first run. When using `generate_and_upload_images.py`, dependencies are checked when it calls `nanobanana.py` as a subprocess - you may need to re-run the command after the initial auto-install.


**When to manually run setup:**


```bash
python3 ${SKILL_DIR}/scripts/setup_dependencies.py
```

- After fresh installation
- When automatic dependency check fails
- To verify PicGo configuration

---

### 2. Configure Gemini API Key

**Priority: Environment Variable > Config File**


The image generation script prioritizes environment variables to avoid configuration inconsistency issues.

**Method 1: Environment Variable (Recommended)**

```bash
# Set for current session
export GEMINI_API_KEY=your_api_key_here

# Make permanent (choose your shell)
echo 'export GEMINI_API_KEY=your_api_key_here' >> ~/.bashrc   # Bash

echo 'export GEMINI_API_KEY=your_api_key_here' >> ~/.zshrc    # Zsh
source ~/.bashrc  # or ~/.zshrc
```

**Method 2: Config File (Fallback)**

```bash<https://aistudio.google.com/apikey>
cat > ~/.nanobanana.env << 'EOF'
GEMINI_API_KEY=your_api_key_here

EOF
```

**Get API Key:** <https://aistudio.google.com/apikey>

**Verification:**

```bash
# Check environment variable
echo $GEMINI_API_KEY

# Test image generation
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "Test image" \
  --size 1024x1024 \
  --output test.jpg
```

---

### 3. Optional: Custom Configuration

Create `~/.article-generator.conf` to customize timeouts and defaults:


```bash
cp ${SKILL_DIR}/.article-generator.conf.example ~/.article-generator.conf
# Edit with your preferences
```


**Supported settings:**

- `timeouts.image_generation`: Image generation timeout (default: 120s)
- `timeouts.upload`: Upload timeout (default: 60s)
- `image_defaults.resolution`: Default resolution (1K/2K/4K, default: 2K)
- `image_defaults.model`: Gemini model (default: gemini-3-pro-image-preview)

**Example:**

```json
{
  "timeouts": {
    "image_generation": 180,
    "upload": 90
  }
}
```

---


## ⚠️ MANDATORY Pre-Writing Verification (ZERO TOLERANCE)

**CRITICAL**: Before writing ANY article, complete this verification checklist. Missing any step results in ARTICLE REJECTION.

### Verification Philosophy

**核心原则：验证先行，绝不编造**

- ✅ 验证过的内容 → 可以写入文章
- ❓ 无法验证的内容 → 标记 "[需要验证]" 或询问用户
- ❌ 编造的内容 → 立即拒绝整篇文章

**所有技术内容必须经过以下验证流程之一：**

1. **官方文档验证**（最可靠）
2. **受信任工具白名单**（预验证）
3. **用户提供的信息**（需确认可靠性）

---

### Trusted Tools Whitelist (Skip Verification)

The following widely-used tools are **pre-verified** - no WebSearch needed:


**Development Tools:**

- Docker, Kubernetes, Git, npm, yarn, pnpm, pip, cargo, Maven, Gradle
- Node.js, Python, Go, Rust, Java, TypeScript, Ruby


**Operating Systems & Package Managers:**

- apt, yum, dnf, brew, pacman, apk, snap

**Common CLI Tools:**


- curl, wget, ssh, scp, rsync, grep, sed, awk, tar, gzip

**Why whitelist?** These tools have stable APIs and widespread official documentation. Trust their basic commands from your knowledge base.

**When to verify anyway:**


- Niche flags or options (e.g., `docker run --gpus` requires verification)
- Version-specific features (e.g., "Docker 24.0+ only")
- Deprecated commands
- Any command you're unsure about

---


### Step 1: Tool/Project Research (MANDATORY for non-whitelisted tools)

**对于不在白名单中的工具，必须先验证存在性和准确性：**

1. **使用 WebSearch 查找官方文档**
   ```
   WebSearch(search_term="[tool_name] official documentation")
   WebSearch(search_term="[tool_name] GitHub repository")
   ```

2. **验证工具真实存在**
   - 检查官方网站
   - 确认 GitHub 仓库（星标数、维护状态）
   - 阅读 README 和官方文档

3. **理解实际功能**
   - 不要根据工具名称推测功能
   - 不要根据"常识"假设用法
   - 必须从官方文档确认功能

**示例验证流程：**

```
用户请求："写一篇关于 XYZ 工具的文章"

❌ 错误做法：直接开始写，根据名称猜测功能
✅ 正确做法：
  1. WebSearch("XYZ tool official documentation")
  2. WebFetch(找到的官方文档 URL)
  3. 确认工具存在、功能、安装方法
  4. 如果找不到可靠信息 → 询问用户或拒绝任务
```

---

### Step 2: Command/Feature Verification (MANDATORY)

**对于文章中的每个命令、API 调用、配置项，必须验证：**

1. **命令存在性验证**
   - ✅ 在官方文档中找到该命令
   - ✅ 参数、选项与官方文档一致
   - ❌ 无法找到文档 → 该命令不存在，不要包含

2. **代码示例验证**
   - ✅ 代码是完整可运行的
   - ✅ API 用法与官方示例一致
   - ✅ 依赖版本明确标注
   - ❌ 编造的代码 → 拒绝

3. **配置文件验证**
   - ✅ 配置项在官方文档中存在
   - ✅ 值的格式正确
   - ❌ 猜测的配置 → 拒绝

**Exception**: Whitelisted tools' basic commands can be trusted

**验证要求：**

- **每个命令都必须能在官方文档中找到对应说明**
- **如果无法找到文档，命令就是不存在的 → 不要包含**
- **命令必须从官方文档复制，不能发明或假设**

**示例：**

```markdown
❌ 错误（编造的命令）：
docker magic-deploy --auto-scale

✅ 正确（验证过的命令）：
docker run -d --name myapp nginx
# 来源：https://docs.docker.com/engine/reference/run/
```

---

### Step 3: Workflow Validation (MANDATORY)

**对于多步骤教程，验证每一步：**

1. **步骤完整性**
   - 每一步都有官方文档支持
   - 没有"应该能工作"的假设步骤
   - 步骤顺序经过验证

2. **依赖关系验证**
   - 前置条件明确列出
   - 版本兼容性已确认
   - 环境要求已说明

3. **潜在问题标记**
   - 如果某步不确定 → 标记 "[需要验证]"
   - 询问用户确认或提供补充信息
   - 绝不用"合理假设"填补空白

**示例：**

```markdown
❌ 错误（假设的步骤）：
1. 安装工具
2. 运行 `tool magic-command`  # 编造的命令
3. 应该就能工作了  # 模糊不清

✅ 正确（验证过的步骤）：
1. 安装 Docker (v20.10+)：apt install docker.io
2. 验证安装：docker --version
3. 拉取镜像：docker pull nginx:latest
4. 运行容器：docker run -d -p 80:80 nginx
# 每一步都有官方文档来源
```

---

### Step 4: Link Verification (MANDATORY)

**所有引用链接必须验证可用性：**

1. **使用 WebFetch 验证链接**
   ```
   WebFetch(url="https://example.com/docs")
   # 确认返回 200 状态码，内容存在
   ```

2. **链接类型要求**
   - ✅ 官方文档链接（优先）
   - ✅ GitHub 官方仓库
   - ✅ 经验证的技术博客
   - ❌ 404 错误链接 → 移除或替换
   - ❌ 编造的 URL → 拒绝文章

3. **链接格式**
   - 使用明确格式：`**名称**: https://url`
   - 不使用 `[[Obsidian links]]`（除非用户明确要求）

---

### Step 5: Pre-Generation Report (MANDATORY)

**生成文章前，必须向用户报告验证结果：**

```markdown
## 📋 内容验证报告

### ✅ 已验证工具
- Docker (官方文档: https://docs.docker.com/)
- nginx (官方文档: https://nginx.org/en/docs/)

### ✅ 受信任工具（白名单）
- Git, npm, curl

### ❓ 需要验证的内容
- [工具X] 的高级配置选项 - 未找到官方文档
- [步骤Y] 的兼容性 - 需要确认版本要求

### 📝 处理建议
- 已验证内容将包含在文章中
- 未验证内容已标记或省略
- 是否继续生成文章？
```

**只有在以下情况才继续生成：**

1. ✅ 用户确认未验证项目
2. ✅ 或者已移除所有未验证内容

---

### Enforcement Rules

**严格执行：**

| 情况 | 处理方式 |
|------|---------|
| ❌ 编造的命令/功能 | **拒绝整篇文章** |
| ❌ 未验证的声明 | **询问用户或省略该部分** |
| ❌ 无法验证的工作流 | **标记或移除** |
| ❌ 404 链接 | **移除或替换** |
| ❓ 有疑问的内容 | **询问用户，绝不猜测** |

**验证失败示例：**

```
用户："写一篇关于 SuperTool 的文章"

验证步骤：
1. WebSearch("SuperTool official documentation") → 无结果
2. WebSearch("SuperTool GitHub") → 找到 3 个不同的项目

处理方式：
❌ 错误：随便选一个开始写
✅ 正确：
   "找到 3 个名为 SuperTool 的项目：
   1. owner1/supertool (1.2k stars) - CLI 工具
   2. owner2/SuperTool (500 stars) - Web 框架  
   3. owner3/super-tool (50 stars) - Python 库
   
   您指的是哪一个？"
```

---

### Quick Reference Checklist

**生成文章前，确保：**

- [ ] 所有非白名单工具已通过 WebSearch/WebFetch 验证
- [ ] 所有命令在官方文档中存在
- [ ] 所有代码示例完整可运行
- [ ] 所有链接已验证可访问（HTTP 200）
- [ ] 多步骤教程每一步都有文档支持
- [ ] 已向用户报告验证结果
- [ ] 用户确认继续或已移除未验证内容

**如果任何一项未完成 → 不要生成文章**

---



## 🎯 User Interaction Guidelines

### **MANDATORY: Use AskUserQuestion for All User Decisions**

When generating articles, you MUST use the `AskUserQuestion` tool to collect user requirements and preferences. This provides a clean, structured interaction experience.


**Core Principle: Gradual Progressive Interaction**


- ✅ Ask ONE question at a time
- ✅ Wait for user response before proceeding
- ✅ Each question should have 2-4 clear options with descriptions
- ✅ Adjust follow-up questions based on previous answers
- ❌ NEVER ask all questions in a single text message



---

### **When to Use AskUserQuestion**

#### **Scenario 1: Initial Requirements Gathering**



At the start of article generation, collect:

1. Topic and scope
2. Target audience
3. Article length/depth
4. Image requirements

#### **Scenario 2: Ambiguous Content Decisions**


When you encounter:

- Multiple valid implementation approaches
- Uncertain technical details
- Missing information from user's request
- Need to choose between writing styles

#### **Scenario 3: Image Generation Workflow**

Before generating images, confirm:

- Image style and format
- Number of images needed
- Whether to generate now or use placeholders

#### **Scenario 4: Error Handling and Retries**

When issues occur:

- Image generation timeout/failure
- PicGo upload errors
- Verification failures

---


### **Question Template Examples**

#### **Example 1: Target Audience Selection**

```javascript
AskUserQuestion({
  questions: [{
    header: "受众定位",  // Max 12 characters
    question: "这篇文章的目标读者是？",
    options: [
      {
        label: "初学者",
        description: "需要详细的基础知识和步骤说明"
      },
      {
        label: "开发者",
        description: "需要代码示例和最佳实践"
      },
      {
        label: "架构师",
        description: "需要设计思路和性能分析"
      }
    ],
    multiSelect: false
  }]

})
```

#### **Example 2: Article Length**

```javascript
AskUserQuestion({
  questions: [{
    header: "文章长度",
    question: "期望的文章篇幅？",
    options: [
      {
        label: "快速入门（500-1000字）",
        description: "15分钟阅读，核心概念介绍"
      },
      {
        label: "实战教程（2000-3000字）",
        description: "完整代码示例和实践步骤"
      },
      {
        label: "深度解析（4000+字）",
        description: "原理剖析、性能优化、最佳实践"
      }
    ],
    multiSelect: false

  }]
})
```

#### **Example 3: Image Generation Decision**

```javascript
AskUserQuestion({
  questions: [{
    header: "配图方式",
    question: "如何处理文章配图？",
    options: [
      {
        label: "立即生成（封面 + 节奏图）",
        description: "自动生成并上传到CDN，一步完成"
      },
      {
        label: "仅占位符（稍后添加）",
        description: "文章中使用HTML注释占位，可后续批量生成"
      },
      {
        label: "纯文字文章",
        description: "不需要配图"
      }
    ],
    multiSelect: false
  }]
})
```


#### **Example 4: Error Recovery**

```javascript
AskUserQuestion({
  questions: [{
    header: "失败处理",
    question: "图片生成超时，如何处理？",
    options: [
      {

        label: "使用现有图片",
        description: "跳过失败的图片，使用已有资源"
      },
      {
        label: "重试生成",
        description: "调整超时时间或更换提示词后重试"
      },
      {
        label: "容错模式",

        description: "继续生成其他图片，忽略单个失败"
      }
    ],
    multiSelect: false
  }]
})
```

---


### **Progressive Interaction Flow**

**Step 1: Topic Clarification**

```
Question: "您想写什么主题的技术文章？"
Options:
  - 工具使用教程（如：Docker入门、Git进阶）

  - 技术原理解析（如：React渲染机制、HTTP/3协议）
  - 实战项目分享（如：构建博客系统、API设计）
  - 其他（自定义输入）
```

**Step 2: Audience Selection** (after Step 1)

```
Question: "目标读者是？"
Options:
  - 初学者（需要详细步骤）
  - 开发者（需要代码示例）
  - 架构师（需要设计思路）
```

**Step 3: Content Depth** (adjusted based on Step 2)

```
Question: "期望的文章深度？"
Options:
  - 快速入门（500-1000字）
  - 实战教程（2000-3000字，推荐）
  - 深度解析（4000+字）
```

**Step 4: Image Requirements** (after Step 3)

```
Question: "是否需要生成配图？"
Options:
  - 是 - 封面 + 节奏图（推荐）
  - 仅占位符（稍后添加）
  - 纯文字文章
```

**Step 5: Additional Information** (optional, based on topic complexity)

```
Question: "您可以提供以下哪些补充信息？"
Options:
  - 官方文档链接
  - 真实配置文件示例
  - 个人使用经验
  - 无额外信息（仅基于公开资料）

multiSelect: true  // Allow multiple selections
```

---

### **Best Practices**

1. **Clear Option Labels**
   - ✅ "快速入门（500-1000字）"
   - ❌ "短文章"

2. **Helpful Descriptions**
   - ✅ "完整代码示例和实践步骤"
   - ❌ "包含代码"

3. **Reasonable Option Count**
   - ✅ 2-4 options per question
   - ❌ 5+ options (overwhelming)

4. **Short Headers**
   - ✅ "受众定位" (4 characters)
   - ❌ "请选择目标受众群体" (too long)

5. **Contextual Follow-ups**
   - Adjust next question based on previous answer
   - Example: If user chooses "初学者" → next question should include beginner-friendly options

6. **Avoid Information Overload**
   - ONE question at a time
   - Each question focuses on ONE decision point
   - Never combine multiple concerns in one question

---

## Overview

Generate **technical blog articles** with:

- Authentic, non-AI writing style (no marketing fluff)
- Markdown format with YAML frontmatter
- Obsidian callouts for better information hierarchy
- Complete, runnable code examples with type annotations
- CDN-hosted images (via Gemini API + PicGo)
- Verified technical accuracy (no hallucinated commands)

**Primary Target Platforms:** Obsidian, GitHub Pages, Hugo, Jekyll, Hexo, technical documentation sites

**Secondary Use Case:** Can be converted to WeChat Official Account format using wechat-article-converter skill

**Not a Primary Use Case:** Direct WeChat Official Account article generation (use wechat-article-converter for that)

---

## 📚 文档导航


本 skill 遵循 **Claude Skills 官方最佳实践**，采用"信息渐进式披露"（Progressive Disclosure）架构。

### 核心文档

- **[SKILL.md](./SKILL.md)** (当前文档) - 核心指南和快速参考
- **[WORKFLOW.md](./WORKFLOW.md)** ⭐ - 详细工作流程、用户交互指南、场景示例
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - 问题排查和常见错误解决
- **[INSTALL.md](./INSTALL.md)** - 安装和配置说明

### 详细参考

- **[references/](./references/)** - 写作规范、图片指南、API 文档
- **[scripts/](./scripts/)** - Python 脚本（图片生成、上传等）

- **[assets/](./assets/)** - 模板文件

> **提示**: 如需了解详细的工作流程、用户交互模式和场景示例，请查看 [WORKFLOW.md](./WORKFLOW.md)

---

## Core Capabilities

### 1. Technical Article Creation

- Research-backed content with verified commands and tools
- YAML frontmatter (title, date, tags, category, status, aliases)
- Obsidian callouts (`> [!info]`, `> [!warning]`, `> [!tip]`, etc.)
- Code blocks with syntax highlighting and explanations

- Parameter-based comparison tables (cost, latency, memory)
- Explicit reference links with working URLs

### 2. Image Generation & Integration

- **Cover images:** 16:9 (1344x768) using Gemini API
- **Rhythm images:** 3:2 (1248x832) every 400-600 words
- Auto-upload to PicGo/GitHub CDN
- Embed CDN URLs (not local paths)
- Unique filenames per article (e.g., `ollama_glm4_cover.jpg`)

### 3. Content Optimization

- Refine existing articles for clarity and accuracy
- Verify all commands and tools mentioned
- Replace broken links with working alternatives

- Add missing code examples or explanations

---

## 📋 Image Configuration File Format


### **Supported Formats (Flexible)**

The script now supports **two configuration formats** - use whichever is more convenient:


**Format 1: Object with "images" key** (recommended for consistency)

```json
{
  "images": [
    {
      "name": "图片描述名称",
      "prompt": "Gemini API 图片生成提示词",
      "aspect_ratio": "宽高比（16:9, 3:2, 1:1 等）",
      "filename": "输出文件名.jpg"
    }
  ]
}
```

**Format 2: Direct array** (auto-converted internally)

```json
[
  {
    "name": "图片描述名称",
    "prompt": "Gemini API 图片生成提示词",
    "aspect_ratio": "16:9",
    "filename": "输出文件名.jpg"
  }
]
```

---

### **Field Requirements**

**Required fields:**

- ✅ `name`: Image description (e.g., "封面图")
- ✅ `prompt`: Gemini API prompt for generation
- ✅ `aspect_ratio`: Ratio string (e.g., "16:9", not "1344x768")
- ✅ `filename`: Output filename (e.g., "cover.jpg")

**Common mistakes:**

- ❌ `"size": "1344x768"` → ✅ Use `"aspect_ratio": "16:9"`
- ❌ `"output": "images/cover.jpg"` → ✅ Use `"filename": "cover.jpg"`

**Supported aspect ratios:**

- `16:9` → 1344x768 (封面图)
- `3:2` → 1248x832 (节奏图，推荐)
- `1:1` → 1024x1024 (方形)
- `9:16` → 768x1344 (竖屏)
- `21:9` → 1536x672 (超宽屏)
- See full list in Best Practices section

---

### **Example Configuration**

```json
{
  "images": [
    {
      "name": "封面图",
      "prompt": "Modern AI assistant robot working on computer with digital interface, minimalist illustration, tech blue and purple gradient, clean professional design",
      "aspect_ratio": "16:9",
      "filename": "article_cover.jpg"
    },
    {
      "name": "架构示意图",
      "prompt": "System architecture diagram showing components and data flow, flat design, technical illustration, clean lines",
      "aspect_ratio": "3:2",
      "filename": "article_pic1.jpg"
    }
  ]
}
```

---

## Workflow

> **📖 详细工作流程**: 本节提供简化概览。完整的流程说明、用户交互指南和场景示例，请查看 **[WORKFLOW.md](./WORKFLOW.md)**

### Standard Article Generation Flow

**⚠️ CRITICAL: You MUST execute actual tool calls (Write, Shell) to complete each step. Simply displaying content in chat is NOT sufficient.**


```
1. Clarify Requirements
   ├─ Topic and scope
   ├─ Target audience (beginner/intermediate/advanced)
   ├─ Article length (~2000-3000 words recommended)
   └─ Image requirements (cover + rhythm images)

2. Research & Verification (MANDATORY)
   ├─ WebSearch for official documentation
   ├─ Verify all tools/commands exist
   ├─ Test commands in sandbox if possible
   └─ Report verified/unverified items to user

3. Content Generation
   ├─ YAML frontmatter
   ├─ Article structure with headings
   ├─ Code examples (runnable, complete)
   ├─ Obsidian callouts for key information
   └─ Explicit reference links

4. 💾 SAVE ARTICLE TO FILE (MANDATORY - DO NOT SKIP)
   ├─ Generate filename from article title (e.g., "kimi-k25-claude-code.md")
   ├─ Use Write tool to save content to file
   ├─ Confirm file path to user (e.g., "./kimi-k25-claude-code.md")
   └─ NEVER just display content in chat without saving to file

5. 🎨 Image Generation (if requested)
   ├─ IMPORTANT: Get absolute path of saved file using Shell(command="pwd")
   ├─ Create images/ directory: mkdir -p images
   ├─ Generate unique filename prefix (e.g., article_slug_)
   ├─ Use Shell tool to call generate_and_upload_images.py with ABSOLUTE path
   ├─ Example: python3 /home/hellotalk/.claude/skills/article-generator/scripts/generate_and_upload_images.py --process-file /absolute/path/to/article.md
   ├─ Generate cover (16:9: 1344x768)
   ├─ Generate rhythm images (3:2: 1248x832)
   ├─ Upload all to PicGo/CDN
   ├─ Update article file with CDN URLs
   └─ **Automatically delete local files after successful upload**

6. Final Review
   ├─ Verify all links are working (HTTP 200)
   ├─ Confirm all code examples are complete

   ├─ Check no AI clichés or marketing fluff
   └─ Ensure YAML frontmatter is complete
```

**ENFORCEMENT:**

- Step 4 (Save to file) is **NON-NEGOTIABLE** - you MUST call the Write tool
- Step 5 (Image generation) requires **actual Shell command execution**
- If you only display content without saving files, the task is **INCOMPLETE**

### Article-Only Workflow (Fast Track)

For users who want to **write first, add images later**:

```
1. Clarify Requirements
   ├─ Topic and scope

   ├─ Target audience
   ├─ Article length
   └─ Confirm: "Skip images for now"

2. Research & Verification (MANDATORY)
   ├─ Same as standard workflow

   └─ Report verified/unverified items

3. Content Generation (Article Only)
   ├─ YAML frontmatter
   ├─ Article structure with headings
   ├─ Code examples (runnable, complete)
   ├─ Obsidian callouts
   ├─ Image placeholders (see below)
   └─ Explicit reference links


4. 💾 SAVE ARTICLE TO FILE (MANDATORY)
   ├─ Generate filename from title
   ├─ Use Write tool to save to file
   ├─ Confirm file path to user
   └─ Include image placeholders in saved file


5. Add Images Later (Optional)
2  ├─ Use generate_and_upload_images.py --process-file
3  ├─ Script will parse placeholders and generate images
4  ├─ Upload to CDN automatically
5  └─ Script will update file with CDN URLs
```


**CRITICAL REMINDER:**
2
3**ALWAYS save to file using Write tool** - displaying in chat is insufficient
4Even without images, the article file MUST be created
- Image placeholders should be included in the saved file for later processing


**Image Placeholder Syntax:**
2
3e this format to mark where images should go:
4
```markdown
<!-- IMAGE: cover - 封面图 (16:9) -->
<!-- PROMPT: Modern software development workflow, minimalist illustration -->

<!-- IMAGE: pic1 - 架构示意图 (3:2) -->
<!-- PROMPT: Microservices architecture diagram, flat design, technical illustration -->
```


**Benefits:**


- ✅ Faster initial draft (no waiting for image generation)
- ✅ Focus on content quality first
- ✅ Easy to locate and replace placeholders later

- ✅ Prompts are preserved for future generation
3
4When to use:**

- Tight deadlines (publish draft without images)

- Uncertain about image style/requirements

- Writing on mobile/limited bandwidth
- Batch image generation later for multiple articles

---

## Best Practices

### Writing Style

1. **No AI flavor:** Eliminate marketing fluff, fake engagement, exclamation overuse, and AI clichés
2. **Direct and technical:** Focus on technical accuracy over readability
3. **No emoji in headings:** NEVER use emoji in article title or section headings (# ## ###)
4. **Emoji only in callouts:** Acceptable inside Obsidian callouts when necessary

### Structure

5. **YAML frontmatter required:** Every article must start with metadata (title, date, tags, category, status, aliases)
2. **Obsidian callouts:** Use `> [!type]` syntax (abstract, info, tip, warning, note, success, quote)
3. **Single reference section:** One "参考链接" section at end, remove duplicates
4. **No redundant sections:** Avoid "互动环节", "写在最后", "下期预告"
2 **No metadata duplication:** Do NOT repeat tags/date at article end

### Code & Links

10. **Code must be runnable:** Include complete, executable code with type annotations, docstrings, error handling
2. **Explicit links only:** Use `**Name**: https://url` - NEVER `[[double brackets]]`
3 **Verify all links:** Use curl/WebFetch to confirm URLs return HTTP 200 before including
4. **Technical comparisons:** Use parameter tables (cost, latency, memory) not subjective ratings

### Images

14. **Image integration:** Generate via nanobanana (1 cover + 4-6 rhythm for 3000-word articles)
2. **Upload to CDN:** Use PicGo to upload, embed CDN URLs, delete local files

3. **Unique filenames:** Each article must have unique image prefix (e.g., `ollama_cover.jpg` vs `unsloth_cover.jpg`)
4. **Supported sizes:**
    - Cover: 1344x768 (16:9)
    - Rhythm: 1248x832 (3:2) or 1152x896 (5:4)
    - Square: 1024x1024 (1:1)
    - Portrait: 768x1344 (9:16)
    - Ultrawide: 1536x672 (21:9)
    - **NOT supported:** 900x383 (crop from 1344x768 manually)


2# Article-Only Mode

18. **Placeholder format:** Use HTML comments for future image locations:

    ```markdown
    <!-- IMAGE: cover - 封面图 (16:9) -->
    <!-- PROMPT: your image generation prompt here -->
    ```

19. **Placeholder placement:** Cover after title, rhythm images every 400-600 words
3. **Preserve prompts:** Always include PROMPT comment for later batch generation
4. **Replace workflow:** Use find-replace to swap placeholders with CDN URLs when images ready

### Image Generation Workflow (MANDATORY Sequence)


18. **Step-by-step process:**

    ```bash
    # 1. Create directory
    mkdir -p images

    # 2. Generate unique prefix from article slug
    # Example: "ollama-glm4" → prefix "ollama_glm4_"

    # 3. Generate images
    python3 ${SKILL_DIR}/scripts/nanobanana.py \
      --prompt "your prompt" \
      --size 1344x768 \
      --output images/ollama_glm4_cover.jpg

    # 4. Upload to PicGo
    picgo upload images/*.jpg

    # 5. Embed CDN URLs in article (NOT ./images/ paths)
    # 6. Delete local files

    ```

2. **Retry on failure:**
    - SSL/Network errors: Auto-retry 3 times (2-3 second delays)
    - Directory errors: Auto-fix with `mkdir -p`
    - Upload failures: **Fail-fast** - Any upload error stops the entire workflow to prevent generating articles with broken image links
    - Other errors: Report to user, ask for decision

3. **Progress tracking:**
    - Batch generation displays progress bar with tqdm (auto-installed)
    - Shows: current image name, progress percentage, time estimate
    - Example: `📸 处理 2/5: 封面图 |████░░░░| 40% [00:15<00:22]`
    - Fallback to simple counter if tqdm not available

### Project Disambiguation

20. **When user mentions a project:**
    - FIRST search using WebSearch or GitHub API
    - If multiple projects found:
      - List all candidates with: name, stars, description, URL

      - Ask user: "Found X projects named [name]. Which one do you mean?"
    - NEVER assume which project the user means

### Output

21. **Output to current directory:** Generate in user's pwd, NOT skill directory
2. **File paths in responses:** Use relative paths when displaying to user (e.g., `./article_name.md`), but use absolute paths when calling image generation scripts


---

## Resources

### references/ Directory

**technical_blog_style_guide.md** - Complete writing rules for technical blogs (load this FIRST)

**writing_guidelines.md** - WeChat Official Account writing standards (for secondary use case)

**image_guidelines.md** - Complete image strategy and design principles


**gemini_image_generation.md** - Gemini API image generation guide via nanobanana

- Aspect ratio selection
- Prompt writing techniques
- Batch generation workflow
- Error handling strategies


**brand_style_template.md** - Customizable brand voice template (optional)

### assets/ Directory

**article_template.md** - Markdown structure template

---

## 🛠️ How to Execute Image Generation (Shell Tool Usage)

**IMPORTANT:** When user requests image generation, you MUST use the Shell tool to call these scripts. DO NOT just describe what should be done.


### Method 1: Batch Generation from Config File (Recommended)

**Step 1: Create image configuration JSON**

```json
{

  "images": [
    {
      "name": "封面图",
      "prompt": "Your detailed image prompt here",
      "aspect_ratio": "16:9",
      "filename": "article_slug_cover.jpg"
    },
    {

      "name": "节奏图1",
      "prompt": "Another image prompt",
      "aspect_ratio": "3:2",
      "filename": "article_slug_pic1.jpg"
    }
  ]
}
```


**Step 2: Execute Shell command**

```bash
# Replace ${SKILL_DIR} with actual path: /home/hellotalk/.claude/skills/article-generator
python3 /home/hellotalk/.claude/skills/article-generator/scripts/generate_and_upload_images.py \
  --config images_config.json \
  --resolution 2K
```

**Example Shell tool call:**

```
Shell(
  command="python3 /home/hellotalk/.claude/skills/article-generator/scripts/generate_and_upload_images.py --config images_config.json --resolution 2K",
  description="Generate images from config and upload to CDN"
)
```

---

### Method 2: Process Markdown File with Placeholders (Easiest)

**If article has placeholders like:**

```markdown
<!-- IMAGE: cover - 封面图 (16:9) -->
<!-- PROMPT: Your image prompt -->
```

**Execute Shell command:**

```bash
# CRITICAL: Use ABSOLUTE path for --process-file, NOT relative path

python3 /home/hellotalk/.claude/skills/article-generator/scripts/generate_and_upload_images.py \
  --process-file /absolute/path/to/article_name.md \
  --resolution 2K


# To get absolute path, use:
# realpath article_name.md
# OR
# pwd  # then combine with filename

```

**This will:**

1. Parse placeholders

2. Generate all images
3. Upload to CDN
4. Update file with CDN URLs automatically

**IMPORTANT:**

- ❌ WRONG: `--process-file ./article.md` (relative path)
- ✅ CORRECT: `--process-file /home/hellotalk/onedrive/docs/article.md` (absolute path)


---

### Method 3: Single Image Generation

**For one-off images:**

```bash
python3 /home/hellotalk/.claude/skills/article-generator/scripts/nanobanana.py \
  --prompt "Detailed image description" \
  --size 1344x768 \
  --resolution 2K \
  --output images/cover.jpg
```


**Then upload:**

```bash
picgo upload images/cover.jpg
```

---

## Image Generation Examples

### Parallel Mode (Performance Optimization)

**Parallel generation mode** enables concurrent image generation for significant speed improvements.
```bash
# Basic parallel mode (2 workers, default)
python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py \
  --config images.json \
  --parallel \
  --resolution 2K

# High-speed parallel (4 workers, use with caution)
python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py \
  --config images.json \
  --parallel \
  --max-workers 4


# Parallel with fault tolerance
python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py \
  --config images.json \
  --parallel \
  --continue-on-error

```

**Performance:**

- **2 workers**: ~1.87x faster (93.5% efficiency)
- **4 workers**: ~2.5-3x faster (may trigger API rate limits)

**Modes:**


- **Fail-Fast (default)**: Stops immediately on any error
- **Fault-Tolerant (--continue-on-error)**: Logs errors but continues processing

**When to use:**

- Batch generation (5+ images)
- Time-critical workflows
- Offline generation (--no-upload)

**Caution:**

- May trigger Gemini API rate limits with 4+ workers
- Recommended: 2 workers for stability



---

## Image Generation Examples (Single Image)

### Dry-Run Preview (Cost & Time Estimation)


```bash
# Preview before generating - shows cost estimate and time
python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py \
  --config images_config.json \

  --dry-run \
  --resolution 2K \
  --model gemini-3-pro-image-preview

# Example output:
# 📊 总览: 5 images, 2K resolution
# 💰 成本估算: $0.20/image, total $1.00
# ⏱️  时间估算: ~27s/image, total ~2.3分钟
```<https://github.com/settings/tokens>

### Batch Generation with Configuration File

```bash
# Generate multiple images from JSON config
python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py \

  --config images_config.json \
  --resolution 2K

# Without upload (local generation only)
python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py \
  --config images_config.json \
  --no-upload \
  --resolution 4K
```

### Process Existing Markdown File (Automated)

Scans an existing Markdown file for `<!-- IMAGE -->` placeholders, generates the images, uploads them to CDN, and automatically replaces the placeholders with the final image links.

```bash
# Process a file, generate images, and update content in-place

python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py \
  --process-file my_article.md \
  --resolution 2K
```

**Required Placeholder Format:**

```markdown
<!-- IMAGE: unique_slug - Short Description (16:9) -->
<!-- PROMPT: Detailed promp<https://picgo.github.io/PicGo-Core-Doc/>
```

### Cover Image (16:9 - 1344x768)

```bash
python3 ${SKILL_DIR}/scripts/nanobanana.py \

  --prompt "Modern software development workflow, minimalist illustration, clean lines, tech blue and orange color scheme, professional" \
  --size 1344x768 \
  --resolution 2K \
  --output images/article_slug_cover.jpg
```

### Rhythm Image (3:2 - 1248x832)



```bash
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "Architecture diagram showing microservices communication, flat design, technical illustration, clean and simple" \
  --size 1248x832 \
  --resolution 2K \
  --output images/article_slug_pic1.jpg

```

---

## Troubleshooting

### ImportError: No module named 'google.genai'

→ Dependencies will auto-install on first run. If fails, run:

```bash
python3 ${SKILL_DIR}/scripts/setup_dependencies.py
```


### PicGo upload fails

→ Run `picgo set uploader` to configure image hosting service

**Common PicGo configuration issues:**

1. **No uploader configured**

   ```bash

   # Configure uploader (choose: github, smms, qiniu, etc.)
   picgo set uploader
   ```

2. **GitHub uploader - Token permissions**
   - ❌ Error: `Resource not accessible by personal access token (403)`
   - ✅ Solution: GitHub Token must have **`repo` permission**
   - Generate new token: <https://github.com/settings/tokens>
   - Required scope: Select **`repo`** (Full control of private repositories)


3. **Configuration file mismatch**
   - Check config: `cat ~/.picgo/config.json`
   - Ensure `picBed.uploader` matches `picBed.current`
   - Example:

     ```json

     {
       "picBed": {
         "uploader": "github",
         "current": "github",
         "github": {
           "repo": "username/repo-name",
           "branch": "main",
           "token": "ghp_xxxxx",
           "path": "images/"
         }<https://aistudio.google.com/apikey>
       }
     }
     ```

4. **Verify configuration**

   ```bash
   # Test upload
   echo "test" > test.txt
   picgo upload test.txt

   # Should return CDN URL
   # If error, reconfigure: picgo set uploader
   ```


### PicGo Documentation:** <https://picgo.github.io/PicGo-Core-Doc/>

---

### Web Reader MCP "Insufficient balance" Error


**Error message:**

```
MCP error -429: {"error":{"code":"1113","message":"Insufficient balance or no resource package. Please recharge."}}
```

**Cause:** Web Reader MCP tool has reached quota limit or requires payment.

**Solutions:**


1. **Use WebSearch + WebFetch instead:**

   ```
   WebSearch(search_term="article title author name")
   # Then manually extract key information
   ```

2. **Use WebFetch directly (if you have full URL):**

   ```
   WebFetch(url="https://example.com/article")
   ```

3. **Ask user to provide article content:**
   - User can copy-paste article text
   - User can provide summary or key points
   - User can share article in accessible format (PDF, local file)

**Recommendation:** Always have fallback plan when using paid MCP tools. Prefer free alternatives (WebSearch, WebFetch) for article research.

---

### Image generation SSL/Network error

→ Automatic retry<https://aistudio.google.com/apikey>network and Gemini API Key

### Gemini API Key not found

**Priority: Environment Variable > Config File**

The script prioritizes environment variables to avoid configuration inconsistency.

**Method 1: Set Environment Variable (Recommended)**

```bash
export GEMINI_API_KEY=your_api_key_here


# Add to shell profile for persistence
echo 'export GEMINI_API_KEY=your_api_key_here' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc  # or ~/.zshrc
```

**Method 2: Create Config File (Fallback)**

```bash

cat > ~/.nanobanana.env << 'EOF'
GEMINI_API_KEY=your_api_key_here
EOF
```

**Verification:**

```bash
# Check environment variable
echo $GEMINI_API_KEY

# Test image generation
python3 /home/hellotalk/.claude/skills/article-generator/scripts/nanobanana.py \
  --prompt "Test" --size 1024x1024 --output test.jpg
```

**Get API Key:** <https://aistudio.google.com/apikey>

---

## 🔧 Troubleshooting Image Generation

### Common Error: "未配置 GEMINI_API_KEY"

**Symptom:** Script reports missing API key, but `env | grep GEMINI_API_KEY` shows it exists.

**Root Cause:** File path issue, not API key issue. The error message is misleading.

**Debug Steps:**

1. **Check if file exists:**

   ```bash
   ls -la ./your_article.md
   # If shows "No such file", the path is wrong
   ```

2. **Get absolute path:**

   ```bash
   # Method 1: realpath
   realpath your_article.md

   # Method 2: pwd + filename
   pwd  # e.g., /home/hellotalk/onedrive/docs
   # Then use: /home/hellotalk/onedrive/docs/your_article.md
   ```

3. **Use absolute path:**

   ```bash
   # ❌ WRONG
   python3 generate_and_upload_images.py --process-file ./article.md

   # ✅ CORRECT
   python3 /home/hellotalk/.claude/skills/article-generator/scripts/generate_and_upload_images.py \
     --process-file /home/hellotalk/onedrive/docs/article.md
   ```

### Actual GEMINI_API_KEY Issues

If environment variable is truly missing:

```bash
# Check current value
env | grep GEMINI_API_KEY

# If empty, set it
export GEMINI_API_KEY="your_key_here"

# Make permanent (add to ~/.zshrc or ~/.bashrc)
echo 'export GEMINI_API_KEY="your_key_here"' >> ~/.zshrc
source ~/.zshrc
```

**Get API Key:** <https://aistudio.google.com/apikey>

**For more details:** See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

---

## Appendix A: WeChat Official Account Articles

**Note:** This skill primarily targets **technical blogs**. For WeChat Official Account articles, please refer to:

📄 **[WeChat Article Guidelines](references/wechat_article_guide.md)**

Key differences:

- ✅ Emoji in headings (encouraged for WeChat)
- Conversational tone vs technical formal
- Use `--wechat` flag for automatic conversion

---

**Version:** 2.1 (Optimized 2026-01-28)
**Changes:**

- Removed dead code (CheckpointManager, ThreadStatusTracker)
- Simplified config format validation (auto-converts arrays)
- Added `--keep-files` parameter for file retention control
- Moved WeChat content to separate reference guide
