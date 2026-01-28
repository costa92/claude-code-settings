---
name: wechat-article-converter
description: Convert Markdown articles to WeChat Official Account compatible HTML format with interactive theme selection. Supports 7 beautiful themes, custom code highlighting, and automatic optimization for WeChat's strict requirements.
trigger: When user wants to convert a Markdown article to WeChat format, ALWAYS use AskUserQuestion with smart priority mode - (1) show 3 recommended themes (Coffee/Tech/Warm) + "view more" option; (2) if "view more" selected, show 3 MD2 themes + "back to recommended" option; (3) if "back" selected, show 3 recommended themes + Simple theme. This allows users to navigate between theme groups freely.
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
  4. 生成 HTML 文件

输出:
  article_wechat.html
```

### 示例 2：命令行快速转换

```bash
# 使用 Coffee 主题
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md --theme coffee

# 使用 Tech 主题
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py article.md --theme tech

# 指定输出文件
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

### 场景 3: 批量转换

```bash
# 转换目录下所有 Markdown 文件
for file in *.md; do
  python3 ${SKILL_DIR}/scripts/convert_to_wechat.py "$file" --theme warm
done
```

---

## 🔧 高级选项

### 命令行参数完整列表

```bash
python3 ${SKILL_DIR}/scripts/convert_to_wechat.py [OPTIONS] INPUT_FILE

OPTIONS:
  --theme THEME           主题选择: tech, warm, simple (默认: tech)
  --output OUTPUT         输出文件路径 (默认: INPUT_FILE_wechat.html)
  --custom-css CSS_FILE   自定义 CSS 文件路径
  --no-toc                禁用目录生成
  --no-syntax-highlight   禁用代码语法高亮
  --preserve-yaml         保留 YAML frontmatter（调试用）
  --help                  显示帮助信息
```

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
