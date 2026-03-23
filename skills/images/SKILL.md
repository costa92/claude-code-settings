---
name: article-craft:images
description: "Generate and upload images for technical articles using Gemini API. Use when adding cover images, rhythm images, or screenshots to an article."
---

# Images

Generate and upload images for technical articles using Gemini API, with screenshot support via shot-scraper.

## Inputs

- **article.md file path** -- article containing image placeholders in the format:
  ```markdown
  <!-- IMAGE: name - description (ratio) -->
  <!-- PROMPT: detailed prompt for Gemini image generation -->
  ```
- **Standalone mode:** If no file path is provided as argument, use `AskQuestion` to ask the user for the article file path.

## Process

### 1. Resolve Absolute Path

```bash
realpath article.md
```

All downstream scripts require absolute paths. Relative paths cause misleading errors.

### 2. Gemini Probe Test

Run `--probe` to automatically detect the best available Gemini model. This iterates the full fallback chain with 120s subprocess timeout per model (no inner httpx timeout — avoids proxy SSL handshake issues).

```bash
python3 ~/.claude/plugins/article-craft/scripts/generate_and_upload_images.py --probe
```

Output on success (exit 0):
```
🔍 探测可用 Gemini 模型（超时 120s/模型）...
   [1/3] 测试 gemini-3-pro-image-preview... ✅

BEST_MODEL:gemini-3-pro-image-preview
```

Output on failure (exit 1):
```
❌ 所有模型均不可用
```

**Parse the result for batch processing:**
```bash
BEST_MODEL=$(python3 ~/.claude/plugins/article-craft/scripts/generate_and_upload_images.py \
  --probe 2>&1 | grep "BEST_MODEL:" | cut -d: -f2)
```

- **BEST_MODEL is set** -- proceed to batch processing with `--model $BEST_MODEL`.
- **BEST_MODEL is empty** (all models failed) -- skip AI image generation, keep placeholders, warn user.

**Full model fallback chain (tested in order):**

```
env.json:gemini_image_model (default, highest quality)
  -> gemini-3.1-flash-image-preview (mid-tier fallback)
    -> gemini-2.5-flash-image (fast, highest availability)
      -> give up, keep placeholders
```

### 2.5 Heartbeat Monitoring (Background Process Management)

When running batch processing, implement heartbeat monitoring to detect process crashes:

**Heartbeat files created by image generation script:**
- `{article_path}.heartbeat` — timestamp updated every 2 seconds (proves process is alive)
- `{article_path}.lock` — created at start, deleted at finish (proves process not stuck)

**Orchestrator monitors these files during generation** (see orchestrator Step 3.5 for details).

If process crashes:
- Heartbeat file stops updating → detected within 10 seconds
- Lock file remains → indicates incomplete processing
- Automatic recovery: kill process + retry once

### 3. Batch Process Article

After a successful probe, run the batch processor with the detected model:

```bash
python3 ~/.claude/plugins/article-craft/scripts/generate_and_upload_images.py \
  --process-file /ABSOLUTE/PATH/article.md \
  --model $BEST_MODEL --continue-on-error
```

Additional flags:
- `--continue-on-error` -- skip failed images instead of aborting
- `--resolution 2K` -- higher resolution output
- `--parallel` -- parallel generation (2 workers, ~1.87x faster)

### 3.5 Incremental Mode (skip already-uploaded images)

When re-running images on an article that already has some CDN URLs (e.g., after editing and adding new placeholders), use incremental mode to skip images that were already processed:

**How it works:** Before processing, scan the article for existing `![...](https://cdn...)` lines. Extract image names. Skip any `<!-- IMAGE: name -->` placeholder whose name matches an existing CDN image.

**Execution:**
1. Grep for existing CDN URLs in the article: `grep -o '!\[.*\](https://cdn[^)]*)'`
2. Extract placeholder names from `<!-- IMAGE: name - description -->`
3. Compare: if a name already has a CDN URL in the article, skip it
4. Only process remaining `<!-- IMAGE: -->` placeholders that have no CDN equivalent

```bash
# Manual incremental: first check what's already done
grep -c 'cdn.jsdelivr.net' /ABSOLUTE/PATH/article.md  # existing images
grep -c '<!-- IMAGE:' /ABSOLUTE/PATH/article.md        # remaining placeholders

# If remaining > 0, run batch (it only processes <!-- IMAGE: --> placeholders)
python3 ~/.claude/plugins/article-craft/scripts/generate_and_upload_images.py \
  --process-file /ABSOLUTE/PATH/article.md --continue-on-error
```

> [!tip] The batch processor already skips replaced placeholders
> `generate_and_upload_images.py --process-file` only matches `<!-- IMAGE: -->` comments.
> Already-replaced images (now `![...](url)`) are not matched. So re-running the
> batch processor on a partially-processed article is inherently incremental.
```

This script performs the full pipeline:
1. Parses `<!-- IMAGE: ... -->` and `<!-- PROMPT: ... -->` placeholders from the article
2. Generates images via Gemini API
3. Uploads to CDN (PicGo or S3)
4. Replaces placeholders with CDN URLs in the article file (in-place)

Additional flags:
- `--resolution 2K` -- higher resolution output
- `--parallel` -- parallel generation (2 workers, ~1.87x faster)
- `--continue-on-error` -- skip failed images instead of aborting

### 4. Verify No Placeholder Residue

```bash
grep -n '<!-- IMAGE:' /ABSOLUTE/PATH/article.md
```

- No matches -- all images processed successfully.
- Matches found -- some images failed; list them in the completion summary.

### 5. Screenshots (Independent of Gemini)

Screenshots use `shot-scraper` and always work regardless of Gemini API status.

When using `--process-file`, screenshots (`<!-- SCREENSHOT: ... -->`) are handled automatically. For standalone screenshots:

```bash
shot-scraper https://example.com -o /tmp/screenshot.jpg --wait 3000
picgo upload /tmp/screenshot.jpg
```

Screenshot placeholder format:
```markdown
<!-- SCREENSHOT: tool-name-ui - Tool Name Interface -->
<!-- URL: https://example.com -->
<!-- WAIT: 3000 -->
```

Optional parameters:
```markdown
<!-- SELECTOR: .css-selector -->
<!-- JS: document.querySelector('.cookie-banner')?.remove() -->
```

**SELECTOR rules:**
- External third-party sites -- **never use SELECTOR** (DOM changes break screenshots)
- Local services or controlled systems -- SELECTOR is fine
- External sites -- use `WAIT: 3000` for load delay

## CRITICAL Rules

### Absolute Paths Only

**ALWAYS use absolute paths, never relative.** Relative paths cause misleading "missing API key" errors.

```bash
# WRONG
--process-file ./article.md

# CORRECT
--process-file /Users/you/articles/article.md
```

### Image Placeholder Format

Two consecutive HTML comments:

```markdown
<!-- IMAGE: name - description (ratio) -->
<!-- PROMPT: detailed prompt for Gemini image generation -->
```

### Supported Aspect Ratios

| Ratio | Resolution | Usage |
|-------|-----------|-------|
| `16:9` | 1344x768 | Cover image |
| `3:2` | 1248x832 | Rhythm image (recommended) |
| `5:4` | 1152x896 | Architecture / flow diagrams |
| `1:1` | 1024x1024 | Square |
| `9:16` | 768x1344 | Vertical / mobile |
| `21:9` | 1536x672 | Ultra-wide / panorama |

### Image Placement Rules

- **Cover image:** 16:9 (1344x768), placed at the top of the article
- **Rhythm images:** 3:2 (1248x832), one every 400-600 words
- **Typical count:** 1 cover + 4-6 rhythm images per 3000-word article
- **No duplicate images** in the same section (e.g., two versions of the same diagram)
- **SCREENSHOT placeholders must NOT be inserted between Markdown list items** -- place after the list block

### Script Distinction

- `nanobanana.py` -- single-image generation, used for **probes only** (does NOT auto-create output directories; run `mkdir -p` first)
- `generate_and_upload_images.py` -- batch processor with `--process-file`, used for **all production image generation**

## Error Handling

Graceful degradation:

1. **Gemini probe fails on all models** -- keep `<!-- IMAGE: ... -->` placeholders in the article. Log which images were not generated. Screenshots still execute.
2. **Individual image fails during batch** -- with `--continue-on-error`, skip that image and continue. Failed placeholders remain in the article.
3. **Upload fails** -- fail-fast to prevent broken image links in the article.
4. **Network/SSL errors** -- auto-retry 3 times with 2-3 second delays.
5. **Directory errors** -- auto-fix with `mkdir -p`.

Always report in the completion summary:
- Total images: X generated / Y total
- Failed images: list names and placeholder locations
- Executable command for re-trying failed images

## Outputs

- `article.md` updated in-place with CDN URLs replacing image placeholders
- Any remaining `<!-- IMAGE: ... -->` placeholders indicate failed generations

## Hand-off

Next skill: **article-craft:review**

## Standalone Mode

This skill operates in **dual-mode**:

1. **Pipeline mode:** Receives the article file path as an argument from the orchestrator or a previous skill.
2. **Standalone mode:** If invoked directly without a file path, uses `AskQuestion` to prompt the user for the article file path.

Reference: [image-guide.md](./image-guide.md) for detailed placeholder syntax, prompt patterns, and aspect ratio details.
