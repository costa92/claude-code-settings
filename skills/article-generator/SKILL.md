---
name: article-generator
description: Generate technical blog articles with authentic, non-AI style. Outputs Markdown format with YAML frontmatter, Obsidian callouts, code examples, and CDN images. Avoids marketing fluff and fake engagement. Supports image generation via Gemini API and automatic upload to PicGo image hosting.
---

# Article Generator

**Primary Use Case:** Technical blog articles with Markdown/Obsidian format
**Secondary Use Case:** WeChat Official Account articles (see Appendix A)

## 🚀 Initialization

**Dependency Auto-Check**: `nanobanana.py` automatically checks and installs missing dependencies on first run. When using `generate_and_upload_images.py`, dependencies are checked when it calls `nanobanana.py` as a subprocess - you may need to re-run the command after the initial auto-install.

**When to manually run setup:**
```bash
python3 ${SKILL_DIR}/scripts/setup_dependencies.py
```
- After fresh installation
- When automatic dependency check fails
- To verify PicGo and Gemini API Key configuration

---

## ⚠️ MANDATORY Pre-Writing Verification (ZERO TOLERANCE)

**CRITICAL**: Before writing ANY article, complete this verification checklist. Missing any step results in ARTICLE REJECTION.

### Step 1: Tool/Project Research (MANDATORY)
- For EVERY tool mentioned, use WebSearch or WebFetch to find official documentation
- Read README, official docs, or GitHub repo to understand actual capabilities
- NEVER rely on tool name similarity or "common sense" to infer features

### Step 2: Command/Feature Verification (MANDATORY)
- For EVERY command (bash, CLI tools, API calls), verify it exists in official docs
- If you cannot find documentation for a command, it does NOT exist - DO NOT include it
- Commands must be copy-pasted from official docs, NOT invented or assumed

### Step 3: Workflow Validation (MANDATORY)
- For multi-step workflows, verify EACH step is documented in official sources
- If any step is uncertain, mark it as "[需要验证]" and ask user to confirm
- NEVER fill gaps with "reasonable assumptions"

### Step 4: Pre-Generation Report (MANDATORY)
Before generating article, report to user:
- "✅ Verified tools: [list]"
- "✅ Verified commands: [list]"
- "❓ Unverified items: [list]" (if any - ask user for clarification)

Only proceed after user confirms unverified items or you remove them.

**Enforcement:**
- ANY fabricated command/feature → REJECT entire article
- ANY unverified claim → ASK user or OMIT section
- When in doubt → ASK, NEVER GUESS

---

## Overview

Generate **technical blog articles** with:
- Authentic, non-AI writing style (no marketing fluff)
- Markdown format with YAML frontmatter
- Obsidian callouts for better information hierarchy
- Complete, runnable code examples with type annotations
- CDN-hosted images (via Gemini API + PicGo)
- Verified technical accuracy (no hallucinated commands)

**Target Platforms:** Obsidian, GitHub Pages, Hugo, Jekyll, technical documentation sites

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

## Workflow

### Standard Article Generation Flow

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

4. Image Generation (if requested)
   ├─ Create images/ directory
   ├─ Generate unique filename prefix (e.g., article_slug_)
   ├─ Generate cover (16:9: 1344x768)
   ├─ Generate rhythm images (3:2: 1248x832)
   ├─ Upload all to PicGo/CDN
   ├─ Embed CDN URLs in article
   └─ Manually delete local files (if needed)

5. Final Review
   ├─ Verify all links are working (HTTP 200)
   ├─ Confirm all code examples are complete
   ├─ Check no AI clichés or marketing fluff
   └─ Ensure YAML frontmatter is complete
```

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

4. Add Images Later (Optional)
   ├─ Review placeholder locations
   ├─ Generate images with unique prefix
   ├─ Upload to CDN
   └─ Replace placeholders with CDN URLs
```

**Image Placeholder Syntax:**

Use this format to mark where images should go:

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

**When to use:**
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
6. **Obsidian callouts:** Use `> [!type]` syntax (abstract, info, tip, warning, note, success, quote)
7. **Single reference section:** One "参考链接" section at end, remove duplicates
8. **No redundant sections:** Avoid "互动环节", "写在最后", "下期预告"
9. **No metadata duplication:** Do NOT repeat tags/date at article end

### Code & Links
10. **Code must be runnable:** Include complete, executable code with type annotations, docstrings, error handling
11. **Explicit links only:** Use `**Name**: https://url` - NEVER `[[double brackets]]`
12. **Verify all links:** Use curl/WebFetch to confirm URLs return HTTP 200 before including
13. **Technical comparisons:** Use parameter tables (cost, latency, memory) not subjective ratings

### Images
14. **Image integration:** Generate via nanobanana (1 cover + 4-6 rhythm for 3000-word articles)
15. **Upload to CDN:** Use PicGo to upload, embed CDN URLs, delete local files
16. **Unique filenames:** Each article must have unique image prefix (e.g., `ollama_cover.jpg` vs `unsloth_cover.jpg`)
17. **Supported sizes:**
    - Cover: 1344x768 (16:9)
    - Rhythm: 1248x832 (3:2) or 1152x896 (5:4)
    - Square: 1024x1024 (1:1)
    - Portrait: 768x1344 (9:16)
    - Ultrawide: 1536x672 (21:9)
    - **NOT supported:** 900x383 (crop from 1344x768 manually)

### Article-Only Mode
18. **Placeholder format:** Use HTML comments for future image locations:
    ```markdown
    <!-- IMAGE: cover - 封面图 (16:9) -->
    <!-- PROMPT: your image generation prompt here -->
    ```
19. **Placeholder placement:** Cover after title, rhythm images every 400-600 words
20. **Preserve prompts:** Always include PROMPT comment for later batch generation
21. **Replace workflow:** Use find-replace to swap placeholders with CDN URLs when images ready

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

19. **Retry on failure:**
    - SSL/Network errors: Auto-retry 3 times (2-3 second delays)
    - Directory errors: Auto-fix with `mkdir -p`
    - Upload failures: **Fail-fast** - Any upload error stops the entire workflow to prevent generating articles with broken image links
    - Other errors: Report to user, ask for decision

20. **Progress tracking:**
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
22. **Use relative paths:** `./article_name.md` not absolute paths

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
```

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
   - Generate new token: https://github.com/settings/tokens
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
         }
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

**PicGo Documentation:** https://picgo.github.io/PicGo-Core-Doc/

---

### Image generation SSL/Network error
→ Automatic retry (3 attempts). If persists, check network and Gemini API Key

### Gemini API Key not found
→ Create `~/.nanobanana.env` with:
```
GEMINI_API_KEY=your_api_key_here
```

---

## Appendix A: WeChat Official Account Articles (Secondary Use Case)

**Note:** This skill primarily targets technical blogs. For WeChat Official Account articles, follow these adjusted guidelines:

### WeChat-Specific Requirements

**Headline:**
- 15-30 Chinese characters
- Include core keyword
- Emotional hook or curiosity gap

**Structure:**
- Opening hook (3 paragraphs): Pain point → Value promise → Content preview
- Main body: Segmented with emoji subheadings
- Conclusion: Summary + CTA + Extended reading

**Language Style:**
- First-person (我, 我们) to build connection
- Conversational tone
- One idea per sentence
- Specific over abstract

**Formatting:**
- Emoji before subheadings (✅ allowed for WeChat)
- Blank lines between paragraphs
- Use `>` for important quotes
- Lists for 3+ parallel items
- Bold for key points

**SEO:**
- Core keyword in headline
- Keyword in first 100 characters
- Keyword density 2-3%
- Optimal length: 1500-3000 characters
- Reading time: 3-8 minutes

**Images:**
- Cover: Generate 1344x768 (16:9), crop to 900x383 manually
- Rhythm images: Every 300-500 words, 3:2 or 1:1 ratio
- Style consistency across all images
- Compression: <500KB per image

### WeChat vs Technical Blog Comparison

| Feature | Technical Blog | WeChat Official Account |
|---------|---------------|-------------------------|
| Emoji in headings | ❌ NEVER | ✅ Encouraged |
| Format | Markdown + YAML | Plain Markdown |
| Tone | Technical, formal | Conversational, engaging |
| Length | 2000-3000 words | 1500-3000 characters (Chinese) |
| Code examples | Required, runnable | Optional, simplified |
| References | Explicit URLs | In-text links |
| Cover image | 16:9 (1344x768) | 2.35:1 (900x383, crop from 16:9) |

---

**Version:** 2.0 (Restructured 2026-01-27)
**Changes:** Clarified primary use case (technical blogs), moved WeChat content to appendix, relocated verification checklist to top, removed redundant content
