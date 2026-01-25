---
name: article-generator
description: Generate technical blog articles with authentic, non-AI style. Outputs Markdown format with YAML frontmatter, Obsidian callouts, code examples, and CDN images. Avoids marketing fluff and fake engagement. Supports image generation via Gemini API and automatic upload to PicGo image hosting.
---

# Article Generator

## Overview

Generate high-quality WeChat Official Account articles that follow platform best practices, maintain brand consistency, and engage target audiences. Support complete article creation, content optimization, and batch generation workflows.

## Core Capabilities

### 1. Complete Article Creation

Create full articles from scratch based on topic or keywords, including:
- Engaging headline design (15-30 characters, keyword-optimized)
- Structured body content with proper pacing and visual breaks
- Opening hook that resonates with reader pain points
- Clear value proposition and content preview
- Segmented main content with subheadings, examples, and data
- Actionable conclusion with call-to-action

**Input sources:**
- Topic/keywords only
- Existing documents or drafts
- Web research results
- Mixed sources

### 2. Content Optimization & Rewriting

Improve existing articles by:
- Refining headline impact and SEO optimization
- Restructuring content for better mobile readability
- Enhancing paragraph density (3-5 lines per paragraph)
- Adding visual elements (emoji, bold text, quotes, lists)
- Strengthening opening hooks and closing CTAs
- Improving language flow and engagement

### 3. Batch Article Generation

Generate multiple articles efficiently:
- Process topic lists in batch mode
- Maintain consistent brand voice across articles
- Apply unified style guidelines
- Optimize for different article lengths (short/medium/long)

### 4. Image Generation & Curation

Create or recommend images for articles:
- **Direct image generation** using Google Gemini API (via nanobanana MCP tool)
- **Cover image design** (900x383px, 2.35:1 ratio)
- **Section illustrations** (rhythm images every 300-500 words)
- **Data visualizations** (charts, infographics, diagrams)
- **Fallback AI prompts** for Midjourney/Stable Diffusion/文心一格
- **Stock image recommendations** with proper sourcing
- **Image optimization** (sizing, compression, mobile-friendly)

**Primary method**: Use `nanobanana` MCP tool to generate images directly with Gemini API
**Fallback method**: Provide detailed AI prompts if image generation fails

## Workflow Decision Tree

```
Start: What type of task?
│
├─ New Article Creation
│  ├─ Gather Requirements
│  │  ├─ Topic/keywords
│  │  ├─ Target audience
│  │  ├─ Article length preference
│  │  ├─ Industry/category
│  │  └─ Image generation needs
│  ├─ Apply Style Guidelines
│  │  ├─ Check brand_style_template.md if provided
│  │  └─ Use writing_guidelines.md defaults
│  ├─ Research & Structure
│  │  ├─ Conduct web search if needed
│  │  ├─ Review reference materials
│  │  └─ Plan content outline
│  ├─ Generate & Format
│  │  ├─ Write headline (15-30 chars)
│  │  ├─ Create structured body
│  │  ├─ Add visual elements
│  │  └─ Output as Markdown
│  └─ Image Planning & Generation
│     ├─ Identify image positions (cover + rhythm images)
│     ├─ Determine image types (illustration/photo/chart)
│     ├─ Generate images using nanobanana (Gemini API)
│     ├─ Save images to local directory
│     ├─ Fallback: provide AI prompts if generation fails
│     ├─ Specify image specs (size, style, format)
│     └─ Include image references in output
│
├─ Content Optimization
│  ├─ Read existing content
│  ├─ Identify improvement areas
│  │  ├─ Headline effectiveness
│  │  ├─ Paragraph density
│  │  ├─ Visual hierarchy
│  │  ├─ Engagement elements
│  │  └─ Image placement & quality
│  ├─ Apply optimization techniques
│  ├─ Suggest image improvements
│  └─ Output refined version
│
└─ Batch Generation
   ├─ Parse topic list
   ├─ For each topic:
   │  ├─ Follow "New Article Creation" workflow
   │  └─ Apply consistent style
   └─ Output multiple articles
```

## Writing Guidelines

Follow platform-specific best practices defined in `references/writing_guidelines.md`:

**Article Structure:**
- **Opening (first 3 paragraphs):** Pain point resonance → Value promise → Content preview
- **Main Body:** Segmented with subheadings, examples, data, and visual breaks
- **Conclusion:** Summary (1-3 key points) → CTA (engage/share) → Extended reading

**Language Style:**
- Use first-person ("我", "我们") to build connection
- Conversational tone, avoid overly formal language
- One idea per sentence, avoid nested clauses
- Specific over abstract, use concrete examples
- Active verbs for stronger narrative

**Formatting Standards:**
- Emoji before subheadings (optional, based on brand style)
- Blank lines between paragraphs and sections
- Use `>` for important quotes or highlights
- Lists for 3+ parallel items
- Bold for key points, avoid over-highlighting

**SEO Optimization:**
- Core keyword in headline
- Keyword appears in first 100 characters
- Natural keyword integration in subheadings
- Keyword density 2-3%
- Optimal length: 1500-3000 characters
- Reading time: 3-8 minutes

**Image Integration:**
- Follow standards in `references/image_guidelines.md`
- **Use nanobanana MCP tool** to generate images with Gemini API
- Cover image: 900x383px (2.35:1 ratio) - use aspect ratio 47:20
- Rhythm images: every 300-500 words - use aspect ratio 3:2 or 1:1
- Style consistency across all images
- Proper image compression (<500KB per image)
- Alt text and attribution when needed
- Save generated images to `images/` directory with descriptive names

## Brand Customization

### Using Brand Style Guide

If the user has a specific brand voice or guidelines:

1. **Request or create** `references/brand_style_template.md` with:
   - Brand positioning and target audience
   - Language style and tone preferences
   - Prohibited words and preferred terminology
   - Visual formatting rules (emoji, spacing, emphasis)
   - Content themes and topics to avoid
   - Citation and sourcing standards

2. **Apply brand guidelines** throughout article generation:
   - Reference the brand style guide when making language choices
   - Maintain consistency across multiple articles
   - Adapt templates to match brand personality

3. **Template customization:**
   - Use `assets/article_template.md` as baseline structure
   - Modify according to brand-specific requirements
   - Adjust emoji usage, heading styles, and CTA formats

### Industry-Specific Adaptations

**Technology:**
- Explain technical terms with analogies
- Include data visualizations and charts
- Focus on trends and industry dynamics

**Finance:**
- Include risk disclaimers
- Cite data sources explicitly
- Avoid absolute statements

**Education:**
- Provide actionable methodologies
- Include examples and exercises
- Consider audience age/education level

**Lifestyle:**
- Emphasize practicality and actionability
- Rich imagery and scenario-based content
- Light, engaging language

## Output Format

Generate all articles in **Markdown format** with:

```markdown
# [Article Headline]

> Lead: 1-2 sentence summary

---

## 📌 Opening Section

[Content...]

---

## 💡 Main Point 1

[Content with examples, data, lists...]

---

## 🎯 Conclusion

**Key Takeaways:**
1. [Point 1]
2. [Point 2]
3. [Point 3]

---

## 🤝 Call to Action

[Engagement question or sharing request]
```

**Markdown advantages:**
- Easy to edit and version control
- Clean conversion to HTML
- Platform-agnostic format
- Supports all necessary formatting (bold, lists, quotes, headings)

## Resources

### references/

**writing_guidelines.md** - Comprehensive WeChat Official Account writing standards:
- Article structure templates
- Language and style guidelines
- Industry-specific adaptations
- SEO optimization techniques

Load this file when:
- Creating new articles from scratch
- User asks for "best practices" or "optimization"
- Need guidance on headline, structure, or formatting

**brand_style_template.md** - Customizable brand voice template:
- Brand information and positioning
- Language tone and prohibited terms
- Visual formatting preferences
- Content themes and sourcing standards

Load this file when:
- User mentions brand-specific requirements
- Creating multiple articles with consistent voice
- User provides their own brand guidelines to fill in

**image_guidelines.md** - Complete image strategy for WeChat articles:
- Image types and use cases (cover, rhythm, functional, emotional)
- Design principles (style unity, quality control, content relevance)
- AI image generation workflow with prompt templates
- Tool recommendations (Canva, Midjourney, stock libraries)
- Industry-specific image styles
- Image optimization and compliance checklist

Load this file when:
- User requests images or "配图"
- Generating articles that need visual enhancement
- User asks about cover image design
- Need to create AI image generation prompts
- Optimizing existing article images

**gemini_image_generation.md** - Gemini API image generation guide (via nanobanana):
- nanobanana MCP tool usage and parameters
- Aspect ratio selection for different image types
- Prompt writing techniques and templates
- Batch generation workflow
- Common scenarios and prompt examples
- Error handling and fallback strategies

Load this file when:
- Need to generate images directly using Gemini
- User requests "生成配图" or "生成图片"
- Batch generating images for articles
- Need prompt examples for specific scenarios

### assets/

**article_template.md** - Markdown structure template:
- Complete article skeleton with all sections
- Placeholder guidance for each component
- Emoji and formatting examples
- Adaptable for different article types

Use this template:
- As starting point for new articles
- To ensure structural consistency
- When user requests "standard format"
- For batch generation baseline

## Usage Examples

**Example 1: Complete Article Creation**
```
User: "写一篇关于时间管理的公众号文章"

Process:
1. Clarify: target audience, article length, specific angle
2. Load: references/writing_guidelines.md
3. Research: time management techniques if needed
4. Generate: headline + structured content + CTA
5. Format: Markdown with proper visual elements
6. Output: Complete article ready for publication
```

**Example 1b: Article with Image Generation**
```
User: "写一篇关于时间管理的公众号文章，帮我生成配图"

Process:
1. Clarify: target audience, article length, image style preference
2. Load: references/writing_guidelines.md + gemini_image_generation.md
3. Generate: complete article content
4. Plan images:
   - Cover image (16:9, later crop to 900x383px)
   - 3-4 rhythm images for sections (3:2 or 1:1)
5. Use nanobanana to generate images:
   - Cover: "时间管理主题，清晨阳光办公桌，手绘插画风格，温暖色调"
   - Pic1: "四象限矩阵图表，扁平插画风格，蓝橙配色，简洁专业"
   - Pic2: "职场人士高效工作场景，温暖色调，现代办公室"
6. Save images to ./images/ directory
7. Output: Article + embedded image references + generation summary
```

**Example 2: Content Optimization**
```
User: "优化这篇文章" [provides existing draft]

Process:
1. Read: existing content
2. Analyze: headline impact, structure, paragraph density, engagement
3. Load: references/writing_guidelines.md for standards
4. Refine: headline, opening, body structure, visual elements, conclusion
5. Output: Optimized version with change notes
```

**Example 3: Batch Generation with Brand Voice**
```
User: "根据我们的品牌风格,批量生成5篇职场效率相关文章"

Process:
1. Request: brand style guide (or use template)
2. Receive: topic list or generate topic angles
3. Load: references/brand_style_template.md
4. For each article:
   - Apply brand voice consistently
   - Use writing_guidelines.md structure
   - Maintain unified formatting
5. Output: 5 articles with consistent brand tone
```

**Example 4: Industry-Specific Article**
```
User: "写一篇金融理财类的公众号文章,主题是基金定投"

Process:
1. Note: finance industry requirements (disclaimers, sourcing)
2. Load: references/writing_guidelines.md (finance section)
3. Research: recent fund investment data if needed
4. Generate: with required risk disclaimers and data citations
5. Format: include proper sourcing for all statistics
6. Output: Compliant finance article
```

**Example 5: Image-Only Request**
```
User: "帮我为这篇文章设计封面图和配图方案"

Process:
1. Read: existing article content
2. Load: references/gemini_image_generation.md
3. Analyze: article theme, tone, key sections
4. Design cover:
   - Identify article core message
   - Determine visual style (based on brand/industry)
   - Write Gemini-optimized prompt
5. Plan rhythm images:
   - Mark image positions (every 300-500 words)
   - Match image type to content (illustration/photo/chart)
   - Write prompts for each position
6. Use nanobanana to generate all images:
   - Cover (16:9): [detailed prompt]
   - Pic1 (3:2): [detailed prompt]
   - Pic2 (3:2): [detailed prompt]
   - ...
7. Save images to ./images/ directory
8. Output:
   - Generated image file paths
   - Image embedding markdown
   - Style guide for consistency
```

## Best Practices

1. **Load style guide FIRST:** Always load `references/technical_blog_style_guide.md` for complete writing rules. This file contains all style requirements - do NOT read external directories.

2. **Output to current directory:** Generate article in user's current working directory (use pwd), NOT in the skill directory. Use relative paths like `./article_name.md`

3. **YAML frontmatter required:** Every article must start with YAML metadata (title, date, tags, category, status, aliases)

4. **Use Obsidian callouts:** Use `> [!type]` syntax (abstract, info, tip, warning, note, success, quote) instead of regular blockquotes

5. **Code must be runnable:** Include complete, executable code examples with type annotations, docstrings, and error handling

6. **明链接 only:** Use explicit links format `**Name**: https://url` - NEVER use `[[double brackets]]` internal links

7. **Single reference section:** Keep only ONE reference/resource section, remove duplicates. Use "参考链接" with explicit URLs

8. **No AI flavor:** Eliminate all marketing fluff, fake engagement, exclamation overuse, and AI clichés. Be direct and technical.

9. **Technical comparison:** Use parameter-based comparison tables (cost, latency, memory) instead of subjective ratings

10. **Image integration:** Generate images via nanobanana (1 cover + 4-6 rhythm images for 3000-word articles), upload to PicGo/GitHub CDN, embed ALL generated images with CDN URLs in article, then delete local files

11. **Structure simplicity:** Avoid redundant sections like "互动环节", "写在最后", "下期预告" - keep it technical and focused

12. **No emoji in headings:** NEVER use emoji in article title or section headings (# ## ###). Emoji is only acceptable inside Obsidian callouts when necessary.

13. **No metadata duplication:** Do NOT repeat tags/date at article end. All metadata belongs in YAML frontmatter only.

14. **MANDATORY pre-writing verification (ZERO TOLERANCE for fabrication):**

    **CRITICAL**: Before writing ANY article, you MUST complete this verification checklist. Missing any step results in ARTICLE REJECTION:

    **Step 1: Tool/Project Research (MANDATORY)**
    - For EVERY tool mentioned in the article, use WebSearch or WebFetch to find official documentation
    - Read the README, official docs, or GitHub repo to understand actual capabilities
    - NEVER rely on tool name similarity or "common sense" to infer features

    **Step 2: Command/Feature Verification (MANDATORY)**
    - For EVERY command in the article (bash, CLI tools, API calls), verify it exists in official docs
    - If you cannot find documentation for a command, it does NOT exist - DO NOT include it
    - Commands must be copy-pasted from official docs, NOT invented or assumed

    **Step 3: Workflow Validation (MANDATORY)**
    - For multi-step workflows, verify EACH step is documented in official sources
    - If any step is uncertain, mark it as "[需要验证]" and ask user to confirm
    - NEVER fill gaps with "reasonable assumptions"

    **Step 4: Pre-Generation Report (MANDATORY)**
    - Before generating article, report to user:
      - "✅ Verified tools: [list]"
      - "✅ Verified commands: [list]"
      - "❓ Unverified items: [list]" (if any - ask user for clarification)
    - Only proceed after user confirms unverified items or you remove them

    **Enforcement**:
    - ANY fabricated command/feature → REJECT entire article
    - ANY unverified claim → ASK user or OMIT section
    - When in doubt → ASK, NEVER GUESS

17. **Project disambiguation:** When user mentions a project name (e.g., "CC-Switch"), FIRST search for it using web search or GitHub API. If multiple projects found:
    - List all candidates with: name, stars, description, URL
    - Ask user: "Found X projects named [name]. Which one do you mean?"
    - Wait for user confirmation before proceeding
    - NEVER assume which project the user means

15. **Verify all links:** Before including any URL in the article, verify it exists using curl or similar tools. If a link returns 404 or redirects to an error page, do NOT include it. Only include verified working links (HTTP 200/301 to valid pages).

16. **Image coverage:** For articles 2000+ words, generate at least 5 images total (1 cover + 4 rhythm). Place rhythm images every 400-600 words. Embed ALL generated images in the article.

18. **Image generation workflow:** MUST follow this exact sequence - NO EXCEPTIONS:
    1. Create images directory FIRST:
       ```bash
       mkdir -p images
       ```
       CRITICAL: Always create directory before generating images
    2. Generate unique prefix for this article using article slug or timestamp
       Example: article slug "ollama-glm4" → prefix "ollama_glm4_"
       Example: timestamp → prefix "20260125_183045_"
       CRITICAL: Each article MUST have unique image filenames to avoid CDN conflicts
    3. Create image config JSON with all image prompts
    4. Generate images using Bash tool to call nanobanana Python script:
       ```bash
       python3 ${SKILL_DIR}/scripts/nanobanana.py \
         --prompt "your prompt here" \
         --size {valid_size} \
         --output images/{unique_prefix}cover.jpg
       ```
       CRITICAL: --size parameter MUST be one of these EXACT values (Gemini API限制):
       - 1344x768 (16:9, landscape) - Cover images, banners, WeChat covers (crop to 900x383)
       - 1248x832 (3:2, landscape) - Rhythm images, screenshots
       - 1152x896 (5:4, landscape) - Architecture diagrams
       - 1024x1024 (1:1, square) - Icons, logos
       - 768x1344 (9:16, portrait) - Mobile screenshots
       - 832x1248 (2:3, portrait) - Tall infographics
       - 1536x672 (21:9, ultrawide) - Wide diagrams
       NOTE: Gemini API does NOT support 900x383 (2.35:1) directly
       For WeChat Official Account covers: Generate 1344x768, then crop to 900x383 after upload
       DO NOT use any other sizes (e.g., 1344x896 is INVALID)
       DO NOT use generic names like "cover.jpg" or "pic1.jpg"
       MUST use unique prefix for each article (e.g., "ollama_cover.jpg", "unsloth_cover.jpg")
       DO NOT try to use MCP tool or assume nanobanana is unavailable
       MUST use Bash tool to execute Python script directly
    5. If image generation fails with SSL/network error:
       - Wait 2-3 seconds
       - Retry the same command up to 3 times
       - If still fails after 3 retries, ask user whether to:
         (a) Continue retrying
         (b) Skip that image and continue
         (c) Abort article generation
    3. Verify all images were created (ls images/*.jpg)
    4. Upload ALL images to PicGo/GitHub CDN using Bash:
       ```bash
       picgo upload images/*.jpg
       ```
    5. Embed ALL CDN URLs in article markdown (NOT local paths like ./images/)
    6. Delete local image files
    7. If ANY step fails, STOP and report error to user - DO NOT generate article without images

19. **Image generation is mandatory:** Articles MUST include images. If nanobanana fails:
    - For directory errors: Create images/ directory with mkdir -p
    - For SSL/network errors: Retry 3 times with 2-3 second delays
    - Report the exact error to user after retries exhausted
    - Ask user: "Image generation failed after retries. Should I: (1) Retry (2) Generate article without images (3) Abort"
    - DO NOT decide to skip images on your own
    - DO NOT use local paths like ./images/pic.jpg - always use CDN URLs

23. **Error recovery and retry:** When encountering errors during image generation:
    - SSL/Network errors: Retry 3 times with 2-3 second delays between attempts
    - Directory errors: Auto-fix with mkdir -p images and retry
    - API rate limits: Wait 5 seconds and retry
    - Other errors: Report to user and ask for decision
    - Track retry count and report to user if exhausted

20. **Sources validation:** When using WebSearch and presenting sources to user:
    - Remove duplicate URLs (same URL appearing multiple times)
    - Remove incomplete URLs (e.g., "https://github.com/" without repo path)
    - Each source must be a complete, specific URL (e.g., "https://github.com/user/repo")
    - If a source is invalid/incomplete, omit it rather than include broken links
    - Format: `- [Project Name](https://complete-url)` or `- https://complete-url`

21. **Image filename uniqueness:** CRITICAL - Each article MUST have unique image filenames:
    - Generate prefix from article title slug (e.g., "ollama-glm4" → "ollama_glm4_")
    - Apply prefix to ALL image files: {prefix}cover.jpg, {prefix}pic1.jpg, etc.
    - Example filenames: ollama_glm4_cover.jpg, unsloth_finetune_pic1.jpg
    - NEVER reuse generic names (cover.jpg, pic1.jpg) across different articles
    - This prevents CDN conflicts when generating multiple articles

22. **Image size validation:** MUST use ONLY these exact nanobanana-supported sizes:
    - Cover images: 1344x768 (16:9 landscape) - Also for WeChat, crop to 900x383 later
    - Rhythm images: 1248x832 (3:2 landscape) or 1152x896 (5:4 landscape)
    - Square images: 1024x1024 (1:1)
    - Portrait: 768x1344 (9:16) or 832x1248 (2:3)
    - Ultrawide: 1536x672 (21:9)
    CRITICAL: Gemini API does NOT support 900x383 or 2.35:1 aspect ratio
    For WeChat covers (900x383): Generate 1344x768 first, then manually crop
    NEVER use unsupported sizes like 900x383, 1344x896, 1920x1080, or custom dimensions
