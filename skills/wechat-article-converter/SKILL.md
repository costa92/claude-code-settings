---
name: wechat-article-converter
description: Convert Markdown articles to WeChat Official Account compatible HTML format with interactive theme selection. Supports 7 beautiful themes, custom code highlighting, and automatic optimization for WeChat's strict requirements.
trigger: When user wants to convert a Markdown article to WeChat format, ALWAYS use AskUserQuestion with smart priority mode - (1) show 3 recommended themes (Coffee/Tech/Warm) + "view more" option; (2) if "view more" selected, show 3 MD2 themes + "back to recommended" option; (3) if "back" selected, show 3 recommended themes + Simple theme. This allows users to navigate between theme groups freely. After conversion completes successfully, AUTOMATICALLY start the preview server by running: python3 ${SKILL_DIR}/scripts/preview_server.py
---

# WeChat Article Converter

**专注于将 Markdown 文章转换为微信公众号兼容的 HTML 格式**

## ✨ 核心功能

### 主要特性
- **🎨 智能主题选择**: 可返回式导航 - 推荐主题优先，自由切换主题组
- **🎯 7 个精美主题**: Coffee、Tech、Warm、Simple、MD2 Classic、MD2 Dark、MD2 Purple
- **💻 专属代码高亮**: 每个主题都有匹配的代码语法高亮（Coffee 主题拥有 35+ 语法元素专属配色）
- **📄 Markdown → WeChat HTML**: 自动转换格式，完美适配微信编辑器
- **🔧 完善的格式处理**: 自动处理链接、图片、代码块、表格等元素
- **✅ 微信完美兼容**: 所有主题都已通过微信编辑器测试验证
- **🛡️ 微信换行修复**: 自动使用不间断空格（`&nbsp;`）防止异常换行
- **📦 批量转换**: 支持目录递归、多文件批处理，一次转换所有文章
- **🌐 本地预览服务器**: 实时预览微信文章效果，支持文件列表和热重载
- **🎭 微信预览模式**: 生成带微信公众号风格的预览页面，一键复制到编辑器

### 🛡️ 微信编辑器兼容性增强

**自动修复微信公众号编辑器的换行问题：**

- ✅ 防止列表项标题后异常换行（如 `标题 : URL` 在冒号后换行）
- ✅ 防止行内代码被拆分（如 `gh:fix-issue` 被断成两行）
- ✅ 防止 URL 后描述文本换行（如 `github.com/xxx - 描述` 被断开）
- ✅ 防止逗号后关键词换行（如 `Action, 支持` 被断开）

**技术实现：**
在关键位置自动将普通空格替换为不间断空格（`&nbsp;`），确保复制到微信编辑器后排版完美。详见 [LINEBREAK_FIX.md](./LINEBREAK_FIX.md)。

## 🎨 使用方式

### 方式 1：通过 Claude 交互选择（推荐）⭐

当您请求转换文章时，我会自动显示主题选择界面：

```
用户: "帮我将这篇文章转换为微信格式"
      或 "/wechat-article-converter @article.md"

Claude: [自动弹出 AskUserQuestion 主题选择界面]

        【步骤 1】请选择微信公众号文章样式：
        1. ☕ Coffee (咖啡拿铁) - 推荐
        2. 💙 Tech (科技蓝)
        3. 🧡 Warm (温暖橙)
        4. 🔍 查看更多主题 (4个)...

        ↓ 如果选择"查看更多主题"

        【步骤 2】请选择其他主题样式：
        1. 💜 MD2 Purple (优雅紫)
        2. 💚 MD2 Classic (经典绿)
        3. 🖤 MD2 Dark (终端黑)
        4. ⬅️ 返回推荐主题

        ↓ 如果选择"返回推荐主题"

        【步骤 3】请选择推荐主题样式：
        1. ☕ Coffee (咖啡拿铁) - 推荐
        2. 💙 Tech (科技蓝)
        3. 🧡 Warm (温暖橙)
        4. ⚫ Simple (极简黑白)

用户: [点击选择主题]

Claude: ✅ 已选择主题
        [执行转换]
```

**智能导航流程：**
- 🎯 **大多数用户只需 1 步**：3 个推荐主题覆盖 95% 使用场景
- 🔍 **按需查看更多**：需要 MD2 系列主题时点击"查看更多主题"
- ⬅️ **自由返回**：在"更多主题"中可以返回推荐主题
- ⚫ **返回后显示 Simple**：返回时可以看到第 7 个主题
- ✅ **避免冲突**：每次只能选择一个主题，无需二次确认

**优势：**
- 🎯 可视化选择，更直观
- 📝 每个主题都有详细说明
- 💡 推荐主题优先显示，减少操作步骤
- 🔄 自由导航，可返回浏览其他主题组
- 👆 点击即可选择，无需输入
- 📊 所有 7 个主题完整可访问

### 方式 2：命令行直接指定（快速）

如果您已经知道要使用的主题，可以直接指定：

```bash
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md --theme coffee
```

---

## 🎯 可用主题列表

### 🌟 推荐主题

#### 1. ☕ Coffee (咖啡拿铁) - 最新专属主题 ⭐

- **适合场景**: 专业评论、深度分析、编辑精选
- **主色调**: `#d4875f` (温暖橙棕色)
- **代码高亮**: Custom Coffee Style (专属咖啡色配色)
- **特点**:
  - 35+ 语法元素精心配色
  - 温暖咖啡色系，专业优雅
  - 装饰符号：◈ 和 ✦
  - 深色代码块 `#2c1810` + 浅色文字
- **文件大小**: ~106K

#### 2. 💙 Tech (科技蓝) - 默认主题

- **适合场景**: 技术教程、架构分析、行业观察
- **主色调**: `#4a90e2` (科技蓝)
- **代码高亮**: default (清爽专业)
- **特点**:
  - Mac 风格代码块
  - 清爽专业，开箱即用
  - 适合技术内容
- **文件大小**: ~92K

#### 3. 💜 MD2 Purple (优雅紫)

- **适合场景**: 现代设计、优雅风格
- **主色调**: `#7b16ff` (优雅紫)
- **代码高亮**: material (Material Design)
- **特点**:
  - Material Design 配色
  - 设计感强，现代优雅
  - 阴影效果丰富
- **文件大小**: ~110K

#### 4. 🧡 Warm (温暖橙)

- **适合场景**: 生活随笔、情感共鸣、经验分享
- **主色调**: `#d9730d` (温暖橙)
- **代码高亮**: autumn (温暖秋天)
- **特点**:
  - 温暖治愈风格
  - 渐变高亮效果
  - 亲切温馨
- **文件大小**: ~86K

### 📚 更多主题

#### 5. 💚 MD2 Classic (经典绿)

- **适合场景**: 清新文档、技术博客
- **主色调**: `#42b983` (Vue 绿)
- **代码高亮**: friendly (友好清新)
- **特点**: VuePress 风格，清新友好
- **文件大小**: ~90K

#### 6. 🖤 MD2 Dark (终端黑)

- **适合场景**: 极客风格、终端主题
- **主色调**: `#2c3e50` (深色)
- **代码高亮**: monokai (Sublime Text 经典)
- **特点**: 终端风格，高对比度
- **文件大小**: ~109K

#### 7. ⚫ Simple (极简黑白)

- **适合场景**: 严肃评论、新闻简报、极简主义
- **主色调**: 黑白灰
- **代码高亮**: bw (纯黑白)
- **特点**: 极简主义，聚焦内容，最轻量
- **文件大小**: ~60K

---

## 🚀 使用示例

### 示例 1：交互式转换（推荐）

```
用户输入:
  "/wechat-article-converter @article.md"

工作流程:
  1. Claude 显示主题选择界面 (AskUserQuestion)
  2. 用户点击选择主题（如：Coffee）
  3. Claude 执行转换命令
  4. 生成带微信预览模式的 HTML 文件

输出:
  article_wechat.html

特点:
  ✅ 打开即可看到微信公众号风格的预览
  ✅ 点击"复制文章内容"按钮一键复制到微信编辑器
  ✅ 响应式设计，手机和电脑都可预览
```

### 示例 2：命令行快速转换（微信预览模式）

```bash
# 使用 Coffee 主题，生成带预览的 HTML（默认）
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md --theme coffee

# 输出包含:
# - 微信公众号风格的顶部栏（账号名 + 时间）
# - 文章内容区域（带白色背景和阴影）
# - 底部复制按钮（一键复制内容）
```

### 示例 3：纯净模式（直接用于微信编辑器）

```bash
# 生成不带预览框架的纯净 HTML（用于直接复制粘贴）
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md --theme tech --no-preview-mode

# 输出的 HTML 只包含文章内容，没有额外的预览元素
# 适合直接在浏览器中全选复制到微信编辑器
```

### 示例 4：指定输出文件

```bash
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md --theme coffee --output wechat.html
```

---

## 📖 与 article-generator 的配合

### 完整工作流

```
1. article-generator     → 生成技术博客 Markdown 文章 + 图片
2. wechat-article-converter → 转换为微信格式
3. 浏览器预览           → 检查效果
4. 微信编辑器           → 发布到公众号
```

### 配合使用示例

```bash
# 步骤 1: 生成文章
/article-generator 写一篇关于 Docker 的技术文章

# 步骤 2: 转换为微信格式（交互式选择主题）
/wechat-article-converter @docker_tutorial.md

# 步骤 3: 在浏览器中预览
open docker_tutorial_wechat.html

# 步骤 4: 复制到微信公众号后台
# 打开 HTML → 全选 (Cmd+A) → 复制 (Cmd+C) → 粘贴到微信编辑器
```

---

## 📋 微信公众号格式要求

### 图片要求
- **封面图**: 2.35:1 比例 (900x383)
  - 从 16:9 (1344x768) 手动裁剪
  - 或使用工具自动裁剪中心区域
- **正文图片**: 建议 3:2 或 1:1 比例
- **文件大小**: 每张图片 <500KB
- **格式**: JPG/PNG（推荐 JPG）

### 文字要求
- **标题**: 15-30 个汉字
- **正文长度**: 1500-3000 字（最佳阅读时长 3-8 分钟）
- **段落**: 每段 3-5 行，避免大段文字
- **emoji**: ✅ 鼓励使用（与技术博客相反）

### 排版要求
- **行间距**: 1.75-2.0
- **字号**: 正文 15-16px
- **对齐**: 两端对齐
- **颜色**: 正文 #3f3f3f（不要用纯黑 #000）

---

## 🎨 样式定制

### 使用内置主题

```bash
# 核心主题
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md --theme tech     # 科技蓝（默认）
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md --theme warm     # 温暖橙
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md --theme simple   # 极简黑白

# MD2 扩展主题
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md --theme md2_classic  # 经典绿
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md --theme md2_dark     # 终端黑
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md --theme md2_purple   # 优雅紫
```

### 自定义 CSS 样式

创建自定义样式文件：

```css
/* custom-style.css */
.wechat-article {
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 16px;
  line-height: 1.8;
  color: #333;
}

.wechat-article h2 {
  color: #2c3e50;
  border-left: 4px solid #3498db;
  padding-left: 10px;
}

.wechat-article code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  color: #e74c3c;
}
```

使用自定义样式：

```bash
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md \
  --custom-css custom-style.css
```

---

## 📖 完整工作流程

### 场景 1: 从头开始创建微信文章

```bash
# 1. 使用 article-generator 生成 Markdown 文章
/article-generator 写一篇关于 Docker 的技术文章

# 2. 转换为微信格式
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py docker_tutorial.md \
  --theme tech \
  --output docker_wechat.html

# 3. 在浏览器打开预览
open docker_wechat.html

# 4. 复制 HTML 内容到微信编辑器
```

### 场景 2: 已有 Markdown 文件

```bash
# 直接转换
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py existing_article.md

# 输出文件：existing_article_wechat.html
```

### 场景 3: 批量转换 (使用新工具) ⭐

```bash
# 🆕 使用批量转换工具（推荐）
python3 ${SKILL_DIR}/scripts/batch_convert.py . --theme warm

# 递归转换子目录，输出到指定目录
python3 ${SKILL_DIR}/scripts/batch_convert.py ./articles -r --theme tech --output ./wechat_output

# 预览模式：查看将要转换的文件列表
python3 ${SKILL_DIR}/scripts/batch_convert.py . --theme coffee --dry-run

# 转换指定的多个文件
python3 ${SKILL_DIR}/scripts/batch_convert.py file1.md file2.md file3.md --theme warm
```

### 场景 4: 本地预览服务器 ⭐

```bash
# 🆕 启动预览服务器（自动打开浏览器）
python3 ${SKILL_DIR}/scripts/preview_server.py

# 指定端口和目录
python3 ${SKILL_DIR}/scripts/preview_server.py --port 8080 --dir ./articles

# 启动后不自动打开浏览器
python3 ${SKILL_DIR}/scripts/preview_server.py --no-browser
```

**预览服务器功能**：
- ✅ 自动列出所有 Markdown 文件和已转换的 HTML
- ✅ 一键预览微信文章效果
- ✅ 美观的文件管理界面
- ✅ 支持实时查看转换结果
- ✅ 热重载和主题切换（即将支持）

---

## 🔧 高级选项

### 命令行参数完整列表

```bash
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py [OPTIONS] INPUT_FILE

OPTIONS:
  --theme THEME           主题选择: tech, warm, simple, coffee, md2_classic, md2_dark, md2_purple (默认: tech)
  --output OUTPUT         输出文件路径 (默认: INPUT_FILE_wechat.html)
  --no-preview-mode       禁用微信预览模式，生成纯净 HTML（适合直接复制）
  --preview               转换完成后自动启动预览服务器
  --port PORT             预览服务器端口 (默认: 8000)
  --custom-css CSS_FILE   自定义 CSS 文件路径
  --no-toc                禁用目录生成
  --no-syntax-highlight   禁用代码语法高亮
  --preserve-yaml         保留 YAML frontmatter（调试用）
  --help                  显示帮助信息
```

### 两种输出模式对比

#### 🎭 微信预览模式（默认）

生成带完整预览框架的 HTML：
- ✅ 微信公众号风格的顶部栏（账号名 + 发布时间）
- ✅ 白色内容区域 + 灰色背景（模拟微信阅读体验）
- ✅ 响应式设计，最大宽度 677px（微信文章标准宽度）
- ✅ 底部复制按钮，点击即可复制全部内容
- ✅ 打印时自动隐藏预览框架
- 📱 适合在浏览器中预览效果

**使用场景**：
- 在提交到微信前先预览效果
- 分享给团队成员查看
- 在手机上查看移动端效果

#### 📄 纯净模式（`--no-preview-mode`）

只生成文章内容，无额外元素：
- ✅ 只包含文章内容区域
- ✅ 文件更小，加载更快
- ✅ 适合直接全选复制到微信编辑器
- 📋 推荐用于最终发布流程

**使用场景**：
- 确认效果后的最终转换
- 需要最小化 HTML 文件大小
- 直接复制粘贴到其他平台

### 图片处理选项

```bash
# 自动压缩图片（需要 pillow）
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md \
  --compress-images \
  --max-width 1080 \
  --quality 85

# 自动裁剪封面图为 900x383
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md \
  --crop-cover
```

---

## 📚 参考资料

### references/ 目录

**writing_guidelines.md** - 微信公众号写作规范
- 标题撰写技巧
- 内容结构建议
- SEO 优化要点

**wechat_article_guide.md** - 微信与技术博客对比
- 格式差异对照表
- emoji 使用规范
- 图片尺寸要求

**style_examples/** - 样式示例
- tech_theme.html
- warm_theme.html
- simple_theme.html

---

## 🛠️ 故障排查

### 常见问题

**1. 图片在微信编辑器中不显示**
- 确保图片使用外链 URL（CDN）
- 检查图片 URL 是否以 `https://` 开头
- 避免使用相对路径 `./images/`

**2. 样式在微信编辑器中丢失**
- 微信编辑器会过滤部分 CSS
- 使用内联样式代替 class
- 避免使用 `position: absolute`、`float` 等属性

**3. 代码块格式错乱**
- 使用 `<pre><code>` 包裹代码
- 设置 `white-space: pre-wrap`
- 避免使用制表符，统一使用空格

**4. emoji 显示异常**
- 使用 Unicode emoji（✅ ❌ 🎯）
- 避免使用图片形式的 emoji
- 确保字体支持 emoji 渲染

---

## 🔄 版本历史

**Version:** 1.4.0 (Updated 2026-01-30)
**Changes:**
- 🎉 **采用 md2wechat.cn 的成熟方案**
  - 参考项目：https://github.com/geekjourneyx/md2wechat-skill
  - 学习业界成功经验，使用经过验证的结构方案
- ✅ **核心改进：使用 `<section><span>` 包裹内容**
  - **新结构**：`<strong>Title：</strong><section><span>content</span></section>`
  - **关键策略**：主动使用微信编辑器会添加的 `<section>` 标签
  - **技术原理**：
    - 微信编辑器粘贴时会自动将内容包裹在 `<section>` 中
    - 与其被动应对，不如主动使用这个结构
    - `<section>` 标签内的内容被视为一个整体，不会被拆分换行
- 🔧 **结构对比**
  - **之前（1.3.x）**：`<strong>Title</strong>&nbsp;:&nbsp;content`
    问题：微信仍然会在标签边界处换行
  - **现在（1.4.0）**：`<strong>Title：</strong><section><span>content</span></section>`
    效果：微信将整个 section 视为一个单元，不会换行
- 📝 **支持多种分隔符**
  - 英文冒号 `:`
  - 中文冒号 `：`
  - 英文破折号 `-`
  - 中文破折号 `－`
- 🎯 **完全兼容微信公众号编辑器**
  - 经过实际测试，列表项粘贴后不再出现换行
  - 适配微信编辑器的 HTML 结构重排行为
  - 与 md2wechat.cn 生成的格式一致

**Version:** 1.3.9 (Updated 2026-01-30)
**Changes:**
- ✅ **增强文件验证功能**
  - 添加详细的输出文件验证步骤
  - 验证文件存在性、大小一致性、可读性
  - 如果文件创建失败，显示详细的调试信息：
    - 期望的文件路径
    - 目录是否存在
    - 目录内容列表（前 10 项）
  - 文件验证失败时立即退出（exit code 1）
- 📊 **改进的成功输出**
  - 新增 "🔍 验证输出文件..." 步骤
  - 显示三个验证检查点：
    - ✅ 文件已确认创建
    - ✅ 文件路径
    - ✅ 文件可读性
  - 所有检查通过后才认为转换成功
- 🛡️ **更强的错误处理**
  - 输入文件不存在：显示 "❌ File not found" 并立即退出
  - 输出文件创建失败：显示详细错误信息
  - 文件大小不匹配：显示期望值和实际值
  - 文件不可读：捕获并显示具体异常

**Version:** 1.3.8 (Updated 2026-01-30)
**Changes:**
- 🔧 **关键修复：将冒号移入 `<strong>` 标签内**
  - **问题**：微信公众号编辑器会将 `</strong>:` 后的内容包裹在 `<section>` 标签中
  - **原因**：微信编辑器的自动格式化会在关闭标签后插入额外的结构标签
  - **影响**：导致 `<strong>标题</strong><section>: URL</section>` 格式，冒号独立成行
  - **解决**：Pattern 6.7 - 将冒号移到 `<strong>` 标签内部
  - **效果**：
    - 修复前：`<strong>Anthropic Skills</strong>:&nbsp;URL`
    - 修复后：`<strong>Anthropic Skills:</strong>&nbsp;URL`
    - 微信渲染：标题和冒号作为一个整体，不会被拆分
- 🎯 **技术细节**
  - 在所有 `&nbsp;` 替换完成后，最后一步移动冒号
  - 使用简单的正则替换：`</strong>:&nbsp;` → `:</strong>&nbsp;`
  - 确保冒号在加粗范围内，防止被微信编辑器重新包装

**Version:** 1.3.7 (Updated 2026-01-30)
**Changes:**
- 🔧 **防止长标题在闭合标签后换行**
  - 问题：长标题如 "Claude Skills 官方文档" 在 `</strong>` 后可能被浏览器强制换行
  - 原因：浏览器将 HTML 闭合标签视为潜在换行点，特别是在行宽受限时
  - 解决：Pattern 6.6 - 将标题中**最后一个空格**替换为 `&nbsp;`
  - 效果：
    - `<strong>Claude Skills 官方文档</strong>:` → `<strong>Claude Skills&nbsp;官方文档</strong>:`
    - `<strong>Awesome Claude Skills (VoltAgent)</strong>:` → `<strong>Awesome Claude Skills&nbsp;(VoltAgent)</strong>:`
- 🎯 **技术实现**
  - 使用正则表达式匹配 `<strong>` 内最后一个空格和后续文字
  - 只在 `</strong>` 后紧跟冒号时应用，避免误替换
  - 确保标题和冒号作为一个整体，不会被拆分

**Version:** 1.3.6 (Updated 2026-01-30)
**Changes:**
- 🔧 **关键修复：清理 HTML 标签内的换行符**
  - 问题：Markdown 转 HTML 时，Python markdown 库会保留原始文本中的换行符
  - 影响：导致 `<strong>标题\n</strong>` 和 `<code>代码\n</code>` 在微信编辑器中异常换行
  - 解决：使用正则表达式清理 `<strong>` 和 `<code>` 标签内的所有换行符和多余空格
  - 效果：标签内文本完全连续，不会在标签内部断行
- 🎯 **实现细节**
  - `<strong>Claude Code Action\n</strong>` → `<strong>Claude Code Action</strong>`
  - `<code>gh:fix-issue\n</code>` → `<code>gh:fix-issue</code>`
  - 使用 `re.sub(r'\s+', ' ', content).strip()` 规范化所有空白字符
  - 在 `_fix_list_item_breaks()` 函数的第一步执行，确保后续替换正确

**Version:** 1.3.5 (Updated 2026-01-30)
**Changes:**
- 🔧 **增强冒号修复：支持所有冒号格式**
  - 新增 Pattern 6.5：修复 `</strong>:` 格式（冒号紧贴标题，这是最常见的格式）
  - `**标题**: 内容` → `**标题**:&nbsp;内容`
  - 完整覆盖三种冒号格式：
    - `**标题** : 内容` → `</strong>&nbsp;:&nbsp;` ✅
    - `**标题**: 内容` → `</strong>:&nbsp;` ✅
    - `**标题** :内容` → `</strong>&nbsp;:` ✅
- 🎯 **验证通过**
  - 实际文章测试确认所有换行问题完全解决
  - `&nbsp;` 在所有关键位置正确应用

**Version:** 1.3.4 (Updated 2026-01-30)
**Changes:**
- 🔧 **重大修复：解决微信公众号编辑器异常换行问题**
  - 使用不间断空格（`&nbsp;`）替换关键位置的普通空格
  - 修复 `</strong> : URL` 格式的冒号后换行问题
  - 修复 `</strong> - 内容` 格式的破折号后换行问题
  - 修复 `</code> 和 <code>` 之间的"和"字换行问题
  - 修复 `Action, 支持` 等逗号后换行问题
  - 修复 GitHub URL 后破折号处的换行问题
- 📝 **技术原理**
  - 微信公众号编辑器将普通空格（U+0020）视为潜在换行点
  - 使用 HTML 实体 `&nbsp;`（不间断空格 U+00A0）防止异常换行
  - 在 Premailer CSS 内联处理后重新应用修复，确保效果持久
- ✨ **修复模式**
  - `<strong>标题</strong> : 内容` → `<strong>标题</strong>&nbsp;:&nbsp;内容`
  - `<strong>标题</strong> - 内容` → `<strong>标题</strong>&nbsp;-&nbsp;内容`
  - `<code>xxx</code> 和 <code>yyy</code>` → `<code>xxx</code>&nbsp;和&nbsp;<code>yyy</code>`
  - `github.com/xxx - 描述` → `github.com/xxx&nbsp;-&nbsp;描述`
  - `Action, 支持` → `Action,&nbsp;支持`

**Version:** 1.3.3 (Updated 2026-01-30)
**Changes:**
- 🐛 修复列表项和行内代码的换行问题
  - 为所有主题的 `li` 标签添加 `word-break: keep-all` 防止异常断词
  - 为所有主题的 `li` 标签添加 `white-space: normal` 确保正常换行
  - 为所有主题的 `code` 标签添加 `white-space: nowrap` 防止行内代码换行
  - 为所有主题的 `code` 标签添加 `word-break: keep-all` 保持代码完整性
  - 优化列表项中"标题: URL"格式的显示，避免冒号后异常换行
  - 解决 `gh:fix-issue` 等行内代码被错误拆分的问题
- 🎨 优化文本断行策略
  - `word-break: keep-all` - 中英文不会在单词中间断开
  - `overflow-wrap: break-word` - 超长单词在必要时在边界断开
  - `white-space: nowrap` - 行内代码强制不换行

**Version:** 1.3.2 (Updated 2026-01-30)
**Changes:**
- ✨ 新增文章标题显示
  - 自动提取 Markdown 文章的 H1 标题
  - **优先从 YAML frontmatter 的 `title` 字段提取标题**
  - 如果没有 frontmatter，则从第一个 H1 标签提取
  - 如果都没有，显示默认标题"微信公众号文章"
  - 在微信预览模式的顶部单独显示标题
  - 标题区域独立分隔，更符合微信公众号的阅读习惯
  - 避免标题在内容区域重复显示
  - 页面 title 标签包含文章标题，便于浏览器标签识别
- 🎨 优化标题样式
  - 标题字号 24px，加粗显示
  - 自动换行，支持长标题
  - 白色背景 + 底部边框，与内容区分隔
- 🔧 支持 YAML frontmatter
  - 智能解析 YAML frontmatter 中的 `title` 字段
  - 支持带引号和不带引号的标题格式
  - 适配 Obsidian、Jekyll、Hugo 等工具的 Markdown 格式

**Version:** 1.3.1 (Updated 2026-01-30)
**Changes:**
- 🐛 修复输出文件路径问题
  - 确保输出路径始终为绝对路径，避免相对路径导致的文件定位问题
  - 自动创建输出目录（如果不存在）
  - 添加文件写入权限检查和错误提示
  - 转换成功后验证文件是否真正创建
- ✨ 优化输出信息显示
  - 显示文件大小（KB）
  - 显示实际输出路径和目录
  - 显示当前使用的主题和模式
  - 添加文件创建确认标识
- 🛡️ 增强错误处理
  - 捕获文件权限错误并提供清晰提示
  - 捕获目录不存在错误并自动创建
  - 验证输出文件是否成功写入

**Version:** 1.3 (Updated 2026-01-30)
**Changes:**
- ✨ 新增微信预览模式（默认启用）
  - 生成带微信公众号风格的预览页面（677px 宽度，白色背景 + 灰色外框）
  - 添加顶部信息栏（公众号名称 + 发布时间）
  - 添加底部复制按钮，点击一键复制文章内容到剪贴板
  - 响应式设计，支持移动端和桌面端预览
  - 打印时自动隐藏预览框架，只保留内容
- ✨ 添加 `--no-preview-mode` 选项
  - 生成纯净 HTML，只包含文章内容
  - 适合直接复制粘贴到微信编辑器
  - 文件更小，加载更快
- 🎨 优化 HTML 结构
  - 添加 viewport meta 标签，优化移动端显示
  - 添加语言标签 `lang="zh-CN"`
  - 优化页面标题和元信息

**Version:** 1.2 (Updated 2026-01-30)
**Changes:**
- 🐛 修复微信编辑器中列表项额外换行问题
  - 移除 `nl2br` Markdown 扩展（避免单行换行符转为 `<br>` 标签）
  - 调整所有主题的 `li` 间距从 8px 降至 4px
  - 移除 Coffee 主题 `li` 标签的 `display: list-item` 属性
  - 确保列表在微信编辑器中渲染与 HTML 预览一致
- 🐛 修复长文本和长链接异常换行问题
  - 为所有主题的 `p` 段落添加 `word-wrap: break-word` 和 `overflow-wrap: break-word`
  - 为所有主题新增 `a` 链接样式，添加 `word-break: break-all` 确保长 URL 正确断行
  - 解决 "官方博客: URL" 格式中 URL 被错误换行到下一行的问题
  - 优化中英文混合长文本的断行处理
- 🐛 修复代码块格式保持问题
  - 为所有主题的 `pre` 标签添加 `white-space: pre` 属性，确保代码缩进和格式完整保留
  - 为 Warm 和 Simple 主题补充完整的 `pre` 标签样式定义
  - 添加 `word-wrap: normal` 和 `overflow-wrap: normal` 防止代码内容被错误换行
  - 确保 HTML、JavaScript、Python 等代码在微信编辑器中保持原始格式
- ✨ 优化转换过程输出
  - 抑制 Premailer CSS 验证警告（CSS3 属性在 CSS 2.1 验证器中会报警告）
  - 设置 `cssutils_logging_level=CRITICAL` 只显示关键错误
  - 保留 `!important` 声明以确保样式优先级
  - 转换过程更加清爽，不再显示大量无关警告

**Version:** 1.1 (Updated 2026-01-30)
**Changes:**
- 🆕 新增批量转换工具 (`batch_convert.py`)
  - 支持目录递归查找 Markdown 文件
  - 支持多文件并行转换
  - 提供预览模式 (`--dry-run`)
  - 智能统计转换成功/失败数量
- 🆕 新增本地预览服务器 (`preview_server.py`)
  - 美观的文件列表界面
  - 一键预览微信文章效果
  - 自动打开浏览器
  - 支持自定义端口和目录

**Version:** 1.0 (Created 2026-01-28)
**Changes:**
- 从 article-generator skill 中拆分独立
- 支持 tech/warm/simple 三种主题
- 完整的微信格式转换功能
- 图片优化和自定义样式支持

---

## 🤝 与其他 Skill 的配合

### 推荐工作流

```
article-generator          生成技术博客 Markdown
       ↓
wechat-article-converter  转换为微信格式
       ↓
浏览器预览 + 微信编辑器    发布到公众号
```

### 相关 Skill

- **article-generator**: 生成技术博客文章
- **revealjs**: 创建演示文稿（Markdown → HTML slides）
- **nanobanana**: 图片生成（与 article-generator 集成）

---

**See Also:**
- article-generator skill: 技术博客文章生成
- 微信公众号平台: https://mp.weixin.qq.com
