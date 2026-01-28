# WeChat Official Account Article Guidelines

**Note:** The article-generator skill primarily targets technical blogs. This guide provides adjusted guidelines for WeChat Official Account articles.

## WeChat-Specific Requirements

### Headline
- 15-30 Chinese characters
- Include core keyword
- Emotional hook or curiosity gap

### Structure
- Opening hook (3 paragraphs): Pain point → Value promise → Content preview
- Main body: Segmented with emoji subheadings
- Conclusion: Summary + CTA + Extended reading

### Language Style
- First-person (我, 我们) to build connection
- Conversational tone
- One idea per sentence
- Specific over abstract

### Formatting
- Emoji before subheadings (✅ allowed for WeChat)
- Blank lines between paragraphs
- Use `>` for important quotes
- Lists for 3+ parallel items
- Bold for key points

### SEO
- Core keyword in headline
- Keyword in first 100 characters
- Keyword density 2-3%
- Optimal length: 1500-3000 characters
- Reading time: 3-8 minutes

### Images
- Cover: Generate 1344x768 (16:9), crop to 900x383 manually
- Rhythm images: Every 300-500 words, 3:2 or 1:1 ratio
- Style consistency across all images
- Compression: <500KB per image

## WeChat vs Technical Blog Comparison

| Feature | Technical Blog | WeChat Official Account |
|---------|---------------|-------------------------|
| Emoji in headings | ❌ NEVER | ✅ Encouraged |
| Format | Markdown + YAML | Plain Markdown |
| Tone | Technical, formal | Conversational, engaging |
| Length | 2000-3000 words | 1500-3000 characters (Chinese) |
| Code examples | Required, runnable | Optional, simplified |
| References | Explicit URLs | In-text links |
| Cover image | 16:9 (1344x768) | 2.35:1 (900x383, crop from 16:9) |

## Converting to WeChat Format

Use the `--wechat` flag with `generate_and_upload_images.py`:

```bash
python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py \
  --process-file article.md \
  --wechat \
  --theme tech  # Options: tech, warm, simple
```

This will automatically:
1. Generate images from placeholders
2. Upload to CDN
3. Convert Markdown to WeChat-compatible HTML
4. Apply theme styling

---

**See Also:**
- Main documentation: [SKILL.md](../SKILL.md)
- WeChat conversion script: [convert_to_wechat.py](../scripts/convert_to_wechat.py)
- Writing guidelines: [writing_guidelines.md](writing_guidelines.md)
