# Plan: 集成 shot-scraper 截图工具到 article-generator

## Context

文章生成器当前只支持 AI 生成配图（Gemini API），但写技术文章时经常需要展示工具界面、代码编辑器、网页组件等**真实截图**。用户希望通过 `shot-scraper` 工具直接从 URL 截取特定元素的截图，集成到现有的 `--process-file` 图片处理流程中。

## 设计方案

### 新增占位符语法

与现有 `<!-- IMAGE -->` + `<!-- PROMPT -->` 并行，新增：

```markdown
<!-- SCREENSHOT: slug - 描述文字 -->
<!-- URL: https://example.com -->
<!-- SELECTOR: .css-selector -->
```

- `SCREENSHOT`: 标识这是截图类型（必需）
- `URL`: 要截图的网页地址（必需）
- `SELECTOR`: CSS 选择器，截取特定元素（可选，不填则截整页）

可选参数行（按需添加）：
```markdown
<!-- WAIT: 3000 -->          <!-- 等待毫秒数，等页面加载 -->
<!-- JS: document.querySelector('.cookie-banner')?.remove() -->  <!-- 截图前执行的 JS -->
```

### 修改的文件

#### 1. `scripts/generate_and_upload_images.py`（主要修改）

**新增函数：**

- `parse_markdown_screenshots(file_path)` — 解析 `<!-- SCREENSHOT -->` 占位符，返回截图配置列表
- `take_screenshot(config, output_dir)` — 调用 `shot-scraper` 执行截图，返回本地文件路径

**修改函数：**

- `main()` 中的 `--process-file` 分支 — 在解析 IMAGE 占位符之后，额外解析 SCREENSHOT 占位符，分别处理后统一上传到 CDN 并替换占位符
- `update_markdown_file()` — 确保也能处理 SCREENSHOT 类型的占位符替换

**新增数据类/配置：**

- `ScreenshotConfig` dataclass — 包含 url, selector, wait, js, slug, filename 等字段

#### 2. `SKILL.md`（文档更新）

- "Images" 章节新增 Screenshot 子节，说明占位符语法
- "Image Placeholder Syntax" 部分新增 SCREENSHOT 示例
- "Best Practices > Images" 新增截图相关建议

### 处理流程

```
--process-file article.md
  │
  ├─ parse_markdown_images()      → AI 生成图片列表
  ├─ parse_markdown_screenshots() → 截图任务列表  ← 新增
  │
  ├─ 生成 AI 图片 (Gemini API)
  ├─ 执行截图 (shot-scraper)      ← 新增
  │
  ├─ 上传所有图片到 CDN (PicGo/S3)
  └─ 替换所有占位符 (IMAGE + SCREENSHOT)
```

### shot-scraper 调用方式

```bash
# 基本截图（整页）
shot-scraper https://example.com -o output.png --width 1280 --retina

# 元素截图（CSS 选择器）
shot-scraper https://example.com -s '.main-content' -o output.png --retina --padding 20

# 带等待和 JS 预处理
shot-scraper https://example.com -s '#app' -o output.png --wait 3000 \
  --javascript "document.querySelector('.cookie-banner')?.remove()"
```

默认参数：`--width 1280 --retina --padding 10`

### 不修改的部分

- `nanobanana.py` — 不变，仍只负责 AI 图片生成
- `config.py` — 不变
- 现有 IMAGE 占位符格式 — 完全兼容，不改动

## 验证方式

1. 创建一个含 SCREENSHOT 占位符的测试 markdown 文件
2. 运行 `python3 scripts/generate_and_upload_images.py --process-file test.md --no-upload`
3. 确认截图生成成功，占位符被替换为 `![desc](local_path)`
4. 确认混合使用 IMAGE + SCREENSHOT 占位符时两者都正常工作
