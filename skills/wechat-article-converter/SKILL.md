---
name: wechat-article-converter
description: Convert Markdown articles to WeChat Official Account compatible HTML. Supports 7 Python themes + 9 Go backend themes, batch conversion, preview server, draft box upload, AI image generation, writing assistant with creator styles, and AI trace removal (humanizer). Use when user wants to convert markdown to WeChat format, write articles, remove AI traces, generate images for WeChat, or publish to WeChat Official Account.
---

> **Trigger Behavior**: When user wants to convert a Markdown article to WeChat format, ALWAYS use AskUserQuestion with smart priority mode - (1) show 3 recommended themes (Coffee/Tech/Warm) + "view more" option; (2) if "view more" selected, show 3 MD2 themes + "back to recommended" option; (3) if "back" selected, show 3 recommended themes + Simple theme. After conversion completes successfully, AUTOMATICALLY start the preview server by running: python3 ${SKILL_DIR}/scripts/preview_server.py
>
> **Go Backend Trigger**: When user wants to generate AI images, use writing assistant, remove AI traces (humanize), or use AI/API themed conversion, use the Go backend: `bash ${SKILL_DIR}/scripts/md2wechat_backend.sh`
>
> **Draft Upload Trigger**: When user wants to upload an article to WeChat draft box, ALWAYS prefer `upload_draft.py` over manual steps. It handles conversion, image upload, cover extraction, and draft creation in one command: `python3 ${SKILL_DIR}/scripts/upload_draft.py article.md --theme coffee`
>
> **Default Author**: When generating any draft JSON for WeChat (create_draft or convert --draft), ALWAYS set `"author": "月影"` unless the user explicitly specifies a different author.

# WeChat Article Converter

**Markdown 文章转微信公众号 HTML 的一站式工具**

## 核心功能（Python 引擎）

Python 引擎负责 Markdown → WeChat HTML 转换，支持 7 个精美主题、代码高亮、微信预览模式。

### 主要特性
- **智能主题选择**: 可返回式导航，推荐主题优先，自由切换主题组
- **7 个精美主题**: Coffee、Tech、Warm、Simple、MD2 Classic、MD2 Dark、MD2 Purple
- **专属代码高亮**: 每个主题都有匹配的代码语法高亮
- **Markdown → WeChat HTML**: 自动转换，完美适配微信编辑器
- **微信换行修复**: 自动使用 `&nbsp;` 防止异常换行
- **批量转换**: 支持目录递归、多文件批处理
- **本地预览服务器**: 实时预览效果，支持文件列表
- **微信预览模式**: 带公众号风格的预览页面，一键复制

### Python CLI 命令

```bash
# 交互式转换（推荐）
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md --theme coffee

# 批量转换
python3 ${SKILL_DIR}/scripts/batch_convert.py . --theme warm

# 启动预览服务器
python3 ${SKILL_DIR}/scripts/preview_server.py

# 纯净模式（无预览框架）
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md --theme tech --no-preview-mode

# 一键上传到微信草稿箱（推荐）
python3 ${SKILL_DIR}/scripts/upload_draft.py article.md --theme coffee
```

### Python CLI 完整参数

```bash
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py [OPTIONS] INPUT_FILE

OPTIONS:
  --theme THEME           主题: tech, warm, simple, coffee, md2_classic, md2_dark, md2_purple (默认: tech)
  --output OUTPUT         输出文件路径 (默认: INPUT_FILE_wechat.html)
  --no-preview-mode       禁用微信预览模式，生成纯净 HTML
  --preview               转换后自动启动预览服务器
  --port PORT             预览服务器端口 (默认: 8000)
  --custom-css CSS_FILE   自定义 CSS 文件路径
  --no-toc                禁用目录生成
  --no-syntax-highlight   禁用代码语法高亮
  --help                  显示帮助信息
```

---

## 扩展功能（Go 后端）

Go 后端提供 Python 引擎不具备的高级功能。通过 `md2wechat_backend.sh` 调用，首次运行自动下载二进制文件。

### 草稿箱上传（一键脚本，推荐）

`upload_draft.py` 一条命令完成：Markdown 转换 → 图片上传到微信素材库 → URL 替换 → 封面提取 → 草稿创建。解决了外部 CDN 图片被微信过滤的问题。

```bash
# 一键上传（推荐）
python3 ${SKILL_DIR}/scripts/upload_draft.py article.md --theme coffee

# 指定作者和封面
python3 ${SKILL_DIR}/scripts/upload_draft.py article.md --theme tech --author 月影 --cover cover.jpg
```

**upload_draft.py 参数：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `file` | (必填) | Markdown 文件路径 |
| `--theme` | coffee | Python 引擎主题 |
| `--author` | 月影 | 文章作者 |
| `--cover` | (自动) | 封面图文件路径，默认使用文章中 alt 含"封面"或第一张图 |

**自动化流程：**
1. 解析 YAML frontmatter（title, description）
2. 调用 `convert_to_wechat.py` 转换 HTML（纯净模式）
3. 扫描 HTML 中所有 `<img>` 外部链接
4. 逐个上传图片到微信素材库（串行，避免竞态）
5. 替换 HTML 中的图片 URL（CDN → mmbiz.qpic.cn）
6. 提取封面图 media_id，从正文中移除封面图
7. 移除 h1 标题（避免与草稿标题重复）
8. 构建 draft JSON，调用 Go 后端 `create_draft` 上传

### 草稿箱上传（Go 后端方式）

也可以使用 Go 后端直接上传（不处理外部图片替换）：

```bash
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh convert article.md --draft --cover cover.jpg
```

### AI 图片生成
在文章中生成 AI 图片并自动上传到微信素材库。需要配置 `IMAGE_API_KEY`。

```bash
# 生成图片（默认方形）
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh generate_image "A cute cat on windowsill"

# 16:9 封面图（推荐）
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh generate_image --size 2560x1440 "prompt"

# 上传本地图片
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh upload_image photo.jpg
```

也支持自然语言：
```
"帮我在文章开头生成一张产品概念图"
"生成一张可爱的猫坐在窗台上的图片"
```

详见 [references/image_syntax.md](references/image_syntax.md)

### 写作助手
使用创作者风格（默认 Dan Koe）从零生成文章，支持自定义风格。

```bash
# 交互式写作
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh write

# 指定风格
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh write --style dan-koe

# 生成封面提示词
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh write --style dan-koe --cover-only
```

也支持自然语言：
```
"用 Dan Koe 风格写一篇关于自律的文章"
"帮我润色这篇文章，用更犀利的风格"
```

详见 [references/writing_styles.md](references/writing_styles.md)

### AI 去痕（Humanizer）
去除文本中的 AI 生成痕迹，检测 24 种 AI 写作模式，返回 5 维度质量评分。

```bash
# 基本去痕
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh humanize article.md

# 指定强度（gentle/medium/aggressive）
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh humanize article.md --intensity aggressive

# 写作 + 去痕组合
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh write --style dan-koe --humanize
```

也支持自然语言：
```
"去除这篇文章的 AI 痕迹"
"把这篇文章重写得更像人写的"
```

详见 [references/humanizer.md](references/humanizer.md)

### Go 后端 AI/API 主题转换

```bash
# API 模式（快速，秒级）
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh convert article.md --mode api

# AI 模式（精美主题）
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh convert article.md --mode ai --theme autumn-warm --preview
```

详见 [references/md2wechat_themes.md](references/md2wechat_themes.md)

---

## 主题总览

### Python 引擎主题（7 个）

| 主题 | 参数 | 主色调 | 适合场景 |
|------|------|--------|---------|
| Coffee | `--theme coffee` | #d4875f 温暖橙棕 | 专业评论、深度分析 |
| Tech | `--theme tech` | #4a90e2 科技蓝 | 技术教程、架构分析 |
| Warm | `--theme warm` | #d9730d 温暖橙 | 生活随笔、情感共鸣 |
| Simple | `--theme simple` | 黑白灰 | 严肃评论、极简主义 |
| MD2 Classic | `--theme md2_classic` | #42b983 Vue 绿 | 清新文档、技术博客 |
| MD2 Dark | `--theme md2_dark` | #2c3e50 深色 | 极客风格、终端主题 |
| MD2 Purple | `--theme md2_purple` | #7b16ff 优雅紫 | 现代设计、优雅风格 |

### Go 后端 AI 主题（3 + 自定义）

| 主题 | 参数 | 风格 | 适合场景 |
|------|------|------|---------|
| 秋日暖光 | `--theme autumn-warm` | 温暖治愈，橙色调 | 情感故事、生活随笔 |
| 春日清新 | `--theme spring-fresh` | 清新自然，绿色调 | 旅行日记、自然主题 |
| 深海静谧 | `--theme ocean-calm` | 深邃冷静，蓝色调 | 技术文章、商业分析 |
| 自定义 | `--theme custom` | 自定义提示词 | 特殊需求 |

### Go 后端 API 主题（6 个）

| 主题 | 参数 | 风格 | 适合场景 |
|------|------|------|---------|
| default | `--mode api` | 简洁专业 | 通用内容 |
| bytedance | `--theme bytedance` | 字节跳动 | 科技资讯 |
| apple | `--theme apple` | Apple 极简 | 产品评测 |
| sports | `--theme sports` | 运动活力 | 体育内容 |
| chinese | `--theme chinese` | 中国传统 | 文化文章 |
| cyber | `--theme cyber` | 赛博朋克 | 前沿科技 |

---

## 使用方式

### 方式 1：Claude 交互选择主题（推荐）

```
用户: "帮我将这篇文章转换为微信格式"
      或 "/wechat-article-converter @article.md"

Claude: [弹出 AskUserQuestion 主题选择界面]
        1. Coffee (咖啡拿铁) - 推荐
        2. Tech (科技蓝)
        3. Warm (温暖橙)
        4. 查看更多主题...
```

### 方式 2：命令行直接指定

```bash
# Python 引擎
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md --theme coffee

# Go 后端（API 模式）
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh convert article.md --preview

# Go 后端（AI 主题）
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh convert article.md --mode ai --theme autumn-warm
```

### 方式 3：自然语言

```
"转换 article.md 为微信格式，用 Coffee 主题"
"用秋日暖光主题转换这篇文章"
"用 Dan Koe 风格写一篇关于 AI 的文章，然后转微信格式"
"去除这篇文章的 AI 痕迹"
"生成一张封面图"
```

---

## 工作流示例

### 场景 1：从头创建微信文章（完整流程）

```
1. /article-generator 写一篇关于 Docker 的技术文章
2. /wechat-article-converter @docker_tutorial.md
3. 浏览器预览 → 微信编辑器 → 发布
```

### 场景 2：一键上传到微信草稿箱（推荐）

```bash
# 自动处理图片 + 封面 + 上传（解决外部图片被微信过滤的问题）
python3 ${SKILL_DIR}/scripts/upload_draft.py article.md --theme coffee
```

### 场景 3：写作 + 去痕 + 上传（完整 AI 流水线）

```bash
# 1. AI 写作
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh write --style dan-koe

# 2. 去 AI 痕迹
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh humanize article.md

# 3. 一键上传到草稿箱（含图片上传）
python3 ${SKILL_DIR}/scripts/upload_draft.py article.md --theme coffee
```

### 场景 4：批量转换

```bash
python3 ${SKILL_DIR}/scripts/batch_convert.py ./articles -r --theme tech --output ./wechat_output
```

### 场景 5：本地预览服务器

```bash
python3 ${SKILL_DIR}/scripts/preview_server.py --port 8080 --dir ./articles
```

---

## 配置

### Python 引擎依赖

```bash
pip install markdown premailer pygments beautifulsoup4 lxml cssutils
```

详见 [INSTALL.md](./INSTALL.md)

### Go 后端环境变量

| 变量 | 说明 | 必需 |
|------|------|------|
| `WECHAT_APPID` | 微信公众号 AppID | 草稿上传 |
| `WECHAT_SECRET` | 微信 API Secret | 草稿上传 |
| `IMAGE_API_KEY` | 图片生成 API Key | AI 图片 |
| `IMAGE_API_BASE` | 图片 API Base URL | AI 图片 |

Go 后端通过 `md2wechat_backend.sh` 自动下载二进制，需要 `curl` 或 `wget`。

---

## Go 后端 CLI 命令参考

```bash
# 帮助
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh --help

# 转换
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh convert article.md --preview
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh convert article.md --mode ai --theme autumn-warm
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh convert article.md --draft --cover cover.jpg

# 图片
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh upload_image photo.jpg
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh download_and_upload https://example.com/image.jpg
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh generate_image "prompt"
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh generate_image --size 2560x1440 "prompt"

# 写作
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh write
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh write --style dan-koe
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh write --style dan-koe --cover-only

# AI 去痕
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh humanize article.md
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh humanize article.md --intensity aggressive

# 配置
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh config init
bash ${SKILL_DIR}/scripts/md2wechat_backend.sh config show
```

---

## 参考文档列表

### 原有参考文档
- [writing_guidelines.md](references/writing_guidelines.md) - 微信公众号写作规范
- [wechat_article_guide.md](references/wechat_article_guide.md) - 微信与技术博客对比
- [theme_code_highlighting.md](references/theme_code_highlighting.md) - 主题代码高亮配置

### Go 后端参考文档
- [md2wechat_themes.md](references/md2wechat_themes.md) - AI/API 主题风格指南
- [wechat_api.md](references/wechat_api.md) - 微信公众号 API 参考
- [image_syntax.md](references/image_syntax.md) - 图片语法与 AI 图片生成
- [humanizer.md](references/humanizer.md) - AI 写作去痕
- [writing_styles.md](references/writing_styles.md) - 写作功能与创作者风格
- [wechat_html_spec.md](references/wechat_html_spec.md) - 微信 HTML 规范

---

## 故障排查

### Python 引擎

**图片在微信编辑器中不显示**
- 确保图片使用外链 URL（CDN），以 `https://` 开头
- 避免使用相对路径 `./images/`

**样式在微信编辑器中丢失**
- 微信编辑器会过滤部分 CSS
- 使用内联样式代替 class
- 避免使用 `position: absolute`、`float` 等

**代码块格式错乱**
- 使用 `<pre><code>` 包裹，设置 `white-space: pre-wrap`

### Go 后端

**"command not found" 或下载失败**
- `md2wechat_backend.sh` 首次运行会自动下载二进制
- 确保有 `curl` 或 `wget`
- 网络问题可手动下载：https://github.com/geekjourneyx/md2wechat-skill/releases

**"IP not in whitelist" 错误**
- 获取公网 IP：`curl ifconfig.me`
- 在微信开发者平台添加 IP 白名单

**"AppID not configured" 错误**
- 设置环境变量 `WECHAT_APPID` 和 `WECHAT_SECRET`
- 或运行 `bash ${SKILL_DIR}/scripts/md2wechat_backend.sh config init`

**AI 图片生成失败**
- 检查 `IMAGE_API_KEY` 是否已设置
- 检查 `IMAGE_API_BASE` 是否正确

---

## 微信公众号格式要求

### 图片
- **封面图**: 2.35:1 比例 (900x383)，或 16:9 (2560x1440) 使用 AI 生成
- **正文图片**: 建议 3:2 或 1:1，每张 <500KB，JPG/PNG

### 文字
- **标题**: 15-30 个汉字
- **正文**: 1500-3000 字（最佳 3-8 分钟阅读）
- **段落**: 每段 3-5 行

### 排版
- **行间距**: 1.75-2.0
- **字号**: 正文 15-16px
- **颜色**: 正文 #3f3f3f（非纯黑）

---

## 与其他 Skill 的配合

```
article-generator          生成技术博客 Markdown
       ↓
wechat-article-converter  转换为微信格式（Python 或 Go）
       ↓
浏览器预览 + 微信编辑器    发布到公众号
```

### 相关 Skill
- **article-generator**: 生成技术博客文章
- **content-repurposer**: 多平台内容分发
- **content-analytics**: 文章数据分析
- **wechat-seo-optimizer**: 标题和摘要优化
- **nanobanana-skill**: 图片生成

---

**Version:** 2.1.0 (Updated 2026-02-28)
**Changes:**
- 新增 `upload_draft.py`：一键上传 Markdown 到微信草稿箱，自动处理外部图片上传替换
- 修复外部 CDN 图片（如 cdn.jsdelivr.net）被微信过滤的问题
- 更新触发行为：草稿上传优先使用 `upload_draft.py`

**Version:** 2.0.0 (Updated 2026-02-26)
**Changes:**
- 合并 md2wechat 技能，统一为一个 Skill
- 新增 Go 后端扩展功能：草稿箱上传、AI 图片生成、写作助手、AI 去痕
- 新增 9 个 Go 后端主题（3 AI + 6 API）
- 新增 6 个参考文档
- 统一所有微信相关功能入口
