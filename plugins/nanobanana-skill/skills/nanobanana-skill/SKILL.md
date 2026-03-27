---
name: nanobanana-skill
description: 'Generate or edit images using Google Gemini API via nanobanana. Triggers: nanobanana, generate image, create image, edit image, AI drawing, 图片生成, AI绘图, 图片编辑, 生成图片.'
allowed-tools: Read, Write, Glob, Grep, Task, Bash(cat:*), Bash(ls:*), Bash(tree:*), Bash(python3:*)
---

# Nanobanana Image Generation Skill

Generate or edit images using Google Gemini API through the nanobanana tool.

## Architecture

This plugin is a **thin wrapper** that delegates to the canonical implementation:

- **Canonical script**: `~/.claude/plugins/article-craft/scripts/nanobanana.py`
- **This wrapper**: `${CLAUDE_PLUGIN_ROOT}/skills/nanobanana-skill/nanobanana.py`

The wrapper only changes the default size (9:16 portrait vs 16:9 landscape in article-generator).
All features — retry, model degradation, enhance — are in the canonical script.

## Requirements

1. **GEMINI_API_KEY**（必需）: 优先从 `~/.claude/env.json` 的 `gemini_api_key` 字段读取。
   如未配置，尝试环境变量 `GEMINI_API_KEY`，或遗留路径 `~/.nanobanana.env`。
2. **Python3 及依赖**: `google-genai`、`Pillow`、`python-dotenv`
   （首次运行自动安装）

**注意**: 必须使用绝对路径调用脚本。

## Instructions

### For image generation

1. Ask the user for:
   - What they want to create (the prompt)
   - Desired aspect ratio/size (optional, defaults to 9:16 portrait)
   - Output filename (optional, auto-generates UUID if not specified)
   - Model preference (optional, defaults to gemini-3-pro-image-preview)
   - Resolution (optional, defaults to 1K)

2. Run the nanobanana script:

   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/nanobanana-skill/nanobanana.py --prompt "description of image" --output "filename.png"
   ```

3. Show the user the saved image path when complete

### For image editing

1. Ask the user for:
   - Input image file(s) to edit
   - What changes they want (the prompt)
   - Output filename (optional)

2. Run with input images:

   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/nanobanana-skill/nanobanana.py --prompt "editing instructions" --input image1.png image2.png --output "edited.png"
   ```

## Available Options

### Aspect Ratios (--size)

- `1024x1024` (1:1) - Square
- `832x1248` (2:3) - Portrait
- `1248x832` (3:2) - Landscape
- `864x1184` (3:4) - Portrait
- `1184x864` (4:3) - Landscape
- `896x1152` (4:5) - Portrait
- `1152x896` (5:4) - Landscape
- `768x1344` (9:16) - Portrait (default)
- `1344x768` (16:9) - Landscape
- `1536x672` (21:9) - Ultra-wide

### Models (--model)

- `gemini-3-pro-image-preview` (default) - Higher quality
- `gemini-2.5-flash-image` - Faster generation
- `gemini-3.1-flash-image-preview` - Good balance of quality and availability

**Model degradation**: On 503/overloaded errors, automatically falls back:
`pro → 3.1-flash → 2.5-flash`. Use `--no-fallback` to disable.

### Resolution (--resolution)

- `1K` (default)
- `2K`
- `4K`

### Prompt Enhancement (--enhance)

Add `--enhance` to automatically rewrite the prompt using Gemini for better image quality.

## Examples

### Generate a simple image

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/nanobanana-skill/nanobanana.py --prompt "A serene mountain landscape at sunset with a lake"
```

### Generate with specific size and output

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/nanobanana-skill/nanobanana.py \
  --prompt "Modern minimalist logo for a tech startup" \
  --size 1024x1024 \
  --output "logo.png"
```

### Generate with prompt enhancement

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/nanobanana-skill/nanobanana.py \
  --prompt "Futuristic cityscape" \
  --size 1344x768 \
  --enhance \
  --output "cityscape.png"
```

### Edit existing images

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/nanobanana-skill/nanobanana.py \
  --prompt "Add a rainbow in the sky" \
  --input photo.png \
  --output "photo-with-rainbow.png"
```

## Error Handling

- **503/Overloaded**: Automatic model degradation (pro → 3.1-flash → 2.5-flash)
- **Network errors**: Automatic retry with exponential backoff (4 attempts)
- **Missing API key**: Check `~/.claude/env.json` → env var → `~/.nanobanana.env`
- **No image generated**: Try a more specific prompt

## Best Practices

1. Be descriptive in prompts - include style, mood, colors, composition
2. For logos/graphics, use square aspect ratio (1024x1024)
3. For social media posts, use 9:16 for stories or 1:1 for posts
4. For wallpapers, use 16:9 or 21:9
5. Start with 1K resolution for testing, upgrade to 2K/4K for final output
6. Use `--enhance` for blog article images to get better quality prompts
