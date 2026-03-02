# Image Generation Guide

## CRITICAL: File Path Requirements

**Image generation scripts require ABSOLUTE paths, not relative paths!**

```bash
# WRONG - Will fail with "missing API key" error (misleading)
--process-file ./article.md

# CORRECT - Use absolute path
--process-file /path/to/your/article.md
```

**How to get absolute path:**
1. After saving file with Write tool, run: `Shell(command="realpath article.md")`
2. Use the returned absolute path in image generation commands

## Image Configuration File Format

### Supported Formats

**Format 1: Object with "images" key** (recommended)
```json
{
  "images": [
    {
      "name": "图片描述名称",
      "prompt": "Gemini API 图片生成提示词",
      "aspect_ratio": "16:9",
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

### Field Requirements

**Required fields:**
- `name`: Image description (e.g., "封面图")
- `prompt`: Gemini API prompt for generation
- `aspect_ratio`: Ratio string (e.g., "16:9", not "1344x768")
- `filename`: Output filename (e.g., "cover.jpg")

**Common mistakes:**
- `"size": "1344x768"` → Use `"aspect_ratio": "16:9"`
- `"output": "images/cover.jpg"` → Use `"filename": "cover.jpg"`

### Supported Aspect Ratios

| Ratio | Resolution | Usage |
|-------|-----------|-------|
| `16:9` | 1344x768 | 封面图 |
| `3:2` | 1248x832 | 节奏图（推荐） |
| `5:4` | 1152x896 | 节奏图（备选） |
| `1:1` | 1024x1024 | 方形 |
| `9:16` | 768x1344 | 竖屏 |
| `21:9` | 1536x672 | 超宽屏 |

## Shell Tool Usage

### Method 1: Batch Generation from Config File (Recommended)

```bash
python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py \
  --config images_config.json \
  --resolution 2K
```

### Method 2: Process Markdown File with Placeholders (Easiest)

```bash
# CRITICAL: Use ABSOLUTE path
python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py \
  --process-file /absolute/path/to/article_name.md \
  --resolution 2K
```

This will: parse placeholders → generate images → upload to CDN → update file with CDN URLs.

### Model Fallback Chain (MANDATORY)

图片生成前必须执行探针测试，按降级链尝试：

```bash
# 1. 默认模型探针（质量最高）
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "test" --size 1024x1024 --output /tmp/gemini_probe.jpg
# 成功 → 用默认模型

# 2. 默认失败（503/429/No data received）→ 降级到 flash
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "test" --size 1024x1024 --output /tmp/gemini_probe.jpg \
  --model gemini-2.5-flash-image
# 成功 → 所有后续命令加 --model gemini-2.5-flash-image

# 3. flash 也失败（503/429/No data received）→ 跳过 AI 图片，保留占位符
```

**降级链**：`gemini-3-pro-image-preview`（默认）→ `gemini-2.5-flash-image`（降级）→ 保留占位符

**降级后的 --process-file 命令**：
```bash
python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py \
  --process-file /absolute/path/to/article.md \
  --model gemini-2.5-flash-image \
  --resolution 2K --continue-on-error
```

### Method 3: Single Image Generation

```bash
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "Detailed image description" \
  --size 1344x768 \
  --resolution 2K \
  --output images/cover.jpg

# Then upload
picgo upload images/cover.jpg
```

## Parallel Mode (Performance Optimization)

```bash
# Basic parallel mode (2 workers, default)
python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py \
  --config images.json --parallel --resolution 2K

# With fault tolerance
python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py \
  --config images.json --parallel --continue-on-error
```

- **2 workers**: ~1.87x faster (93.5% efficiency)
- **4 workers**: ~2.5-3x faster (may trigger API rate limits)
- Recommended: 2 workers for stability

## Dry-Run Preview

```bash
python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py \
  --config images_config.json --dry-run --resolution 2K
```

## Placeholder Syntax

### AI Image Placeholders

```markdown
<!-- IMAGE: cover - 封面图 (16:9) -->
<!-- PROMPT: Modern software development workflow, minimalist illustration -->
```

### Screenshot Placeholders (shot-scraper)

```markdown
<!-- SCREENSHOT: tool-name-ui - 工具名称界面截图 -->
<!-- URL: https://example.com -->
<!-- WAIT: 3000 -->
```

Optional parameters:
```markdown
<!-- SELECTOR: .css-selector -->
<!-- JS: document.querySelector('.cookie-banner')?.remove() -->
```

**SELECTOR Rules:**
- 外部第三方网站 → **禁止 SELECTOR**，DOM 结构随时变化会导致截图失败
- 本地服务或可控系统 → 可以使用 SELECTOR
- 外部网站统一使用 `WAIT: 3000` 等待加载

## Screenshot Execution (Independent of Gemini)

截图使用 `shot-scraper` 直接执行，**不依赖 Gemini API**，不经过 `generate_and_upload_images.py`。

```bash
# 单张截图
shot-scraper https://example.com -o /tmp/screenshot.jpg --wait 3000

# 截图后上传到 CDN
picgo upload /tmp/screenshot.jpg

# 注意：generate_and_upload_images.py 没有 --screenshots-only 标志
# 截图必须用 shot-scraper 直接执行
```

**执行顺序**：先跑截图（始终可用）→ 再跑 AI 图（可能不可用）→ 分别上传 CDN

**Placement Rules:**
- SCREENSHOT 占位符**不能插入 Markdown 列表（`-` 项）之间**，必须放在整个列表块结束之后
- 参考资料区是**纯文字列表区，禁止放置任何图片**，来源截图放在正文引用段落附近

## Image Generation Workflow (MANDATORY Sequence)

1. Create directory: `mkdir -p images`
2. Generate unique prefix from article slug (e.g., `ollama_glm4_`)
3. Generate images via nanobanana.py
4. Upload to PicGo: `picgo upload images/*.jpg`
5. Embed CDN URLs in article (NOT `./images/` paths)
6. Delete local files after successful upload

**Retry on failure:**
- SSL/Network errors: Auto-retry 3 times (2-3 second delays)
- Directory errors: Auto-fix with `mkdir -p`
- Upload failures: Fail-fast to prevent broken image links
