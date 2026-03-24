---
name: article-craft:publish
description: "Place article in knowledge base and optimize for distribution. Use after review to save the article to its final location."
---

# Publish

Place a reviewed article into the knowledge base at the correct category directory, and optionally optimize for WeChat distribution. This is the final step in the article-craft pipeline.

**Invoke**: `/article-craft:publish`

---

## Inputs

- **Article file path**: absolute path to the `.md` file to publish
- **Review score** (optional): passed from `article-craft:review` if run in pipeline

If invoked standalone (file path not provided), use AskQuestion:
```
Question: "Which article file should I publish?"
(free-form input: provide the absolute path to the .md file)
```

---

## Execution Steps

### Step 1: Knowledge Base Auto-Detect

Check if the current working directory (or a known parent) is an Obsidian knowledge base by looking for the `02-技术/` directory.

```bash
# Check from current directory upward
ls -d "02-技术" 2>/dev/null || ls -d "../02-技术" 2>/dev/null || ls -d "../../02-技术" 2>/dev/null
```

Also check for `.obsidian/` directory or numbered directories (`01-工作/`, `03-创作/`).

- **KB detected**: proceed to Step 2 (directory matching).
- **KB not detected**: save to the current working directory. Skip to Step 4.

### Step 2: Smart Directory Matching

When a knowledge base is detected, determine the best subdirectory under `02-技术/` for the article.

**Option A -- Use SmartDirectoryMatcher** (if available):

The `SmartDirectoryMatcher` class is located at `~/.claude/plugins/article-craft/scripts/utils.py`. It performs keyword matching, pattern matching, and history-based matching to find the best directory.

```bash
# Auto-match directory from CLI
python3 -c "
import sys; sys.path.insert(0, '$HOME/.claude/plugins/article-craft/scripts')
from utils import SmartDirectoryMatcher
m = SmartDirectoryMatcher(kb_root='PROJECT_ROOT')
result = m.match_directory('ARTICLE_TITLE')
print(result or 'NO_MATCH')
"
```

If match found, suggest to user. On confirmation, proceed. On rejection, ask user and call `learn_feedback(title, chosen_dir)` to improve future matches.

**Option B -- Manual keyword matching** (if SmartDirectoryMatcher is not available):

Use the directory mapping table below to determine the target directory:

| Article Topic | Target Directory | Examples |
|---------------|-----------------|----------|
| AI tools/products | `02-技术/AI-生态/工具/` | Cursor, Windsurf review |
| AI model evaluation | `02-技术/AI-生态/模型评测/` | GPT-5, Claude 4 comparison |
| AI Agent | `02-技术/AI-生态/Agent/` | Agent architecture, MCP protocol |
| Claude Code | `02-技术/AI-生态/Claude-Code/` | Claude Code tips, skills, plugins |
| Ollama | `02-技术/AI-生态/Ollama/` | Local model deployment |
| RAG | `02-技术/AI-生态/RAG/` | Retrieval-augmented generation |
| Go language | `02-技术/基础设施/Go/` | Go tutorials, source analysis |
| Cloudflare | `02-技术/基础设施/Cloudflare/` | CDN, Workers, Pages |
| Docker/K8s etc. | `02-技术/基础设施/<tool>/` | Auto-create subdirectory |
| Obsidian | `02-技术/工作流/Obsidian/` | Obsidian plugins, workflows |
| n8n | `02-技术/工作流/n8n/` | Workflow automation |
| New topic | `02-技术/<new-dir>/` | Auto-create |

Analyze the article title and frontmatter tags to determine the best match. When ambiguous, ask the user.

### Step 2.5: Pre-Publish Verification ⭐ CRITICAL GATE

**Before moving the article to the knowledge base, run final verification to ensure the article is complete and ready for publication.**

This is the final GATE (GATE 3 of 3-layer system) that prevents incomplete articles from being committed to the KB.

#### Execute Pre-Publish Verification Script

Run the integrated verification script that handles all 5 gates with proper bash error handling:

```bash
bash ~/.claude/skills/publish/scripts/pre-publish-verify.sh /path/to/article.md
```

**Exit codes:**
- `0` — PASS (all critical gates passed, warnings may exist)
- `1` — FAIL (blocking error, cannot proceed)

#### Checks Performed

**1. Placeholder Residue (BLOCKING GATE)**

Verifies no unprocessed IMAGE or SCREENSHOT placeholders remain.

```
<!-- IMAGE: name - description -->
<!-- SCREENSHOT: url -->
```

**If ANY found:**
- **BLOCKS publication** — article generation incomplete
- **Report error** with line numbers and placeholder text
- **Suggested action:** "Re-run `/article-craft:images` to generate missing content"

**Why this gate matters:**
- Placeholders in published KB = broken links and poor user experience
- Indicates image generation process crashed but wasn't fully detected
- Heartbeat monitoring catches hangs, but this gate catches partial failures
- **Non-negotiable**: Never publish with unprocessed placeholders

**2. Frontmatter Validation (WARNING)**

Checks required YAML frontmatter fields are present:
- `title` — article headline
- `date` — publication date (YYYY-MM-DD)
- `tags` — at least 1 tag
- `category` — content category
- `status` — draft or published
- `description` — WeChat article summary (≤ 120 Chinese characters)

**If missing:**
- **Non-blocking warning** — article can publish but with reduced metadata
- **Recommendation**: fix before publishing for better discoverability

**3. External Links (WARNING)**

Verifies all URLs are in proper Markdown format for WeChat compatibility.

**Good format:**
```
[Link text](https://example.com)
```

**Bad format (bare URLs in body text):**
```
Check https://example.com for details
```

**Fix:** Convert to search guidance `搜索「keyword」` for body text.

**4. Mermaid Code Blocks (WARNING)**

Checks no Mermaid diagram code blocks remain.

Mermaid blocks must be replaced with `<!-- IMAGE -->` placeholders for proper rendering.

**Fix:** Use `/article-craft:images` to generate diagram images.

**5. Standalone Reference Section (WARNING)**

Checks no manual reference section at article end.

**Bad:**
```markdown
## 参考资料
- [Link 1](url)
- [Link 2](url)
```

**Good:**
```markdown
See the [official documentation](url) for details.
```

WeChat converter auto-generates footnotes from inline links; manual sections cause duplication.

#### Gate Violation Response

**BLOCK (stop pipeline):**
```
ERROR: Article contains unprocessed placeholders. Cannot publish.

Found 2 unprocessed IMAGE placeholders:
- Line 45: <!-- IMAGE: service-startup-flow - ... -->
- Line 123: <!-- IMAGE: sidecar-architecture - ... -->

Action: Re-run /article-craft:images to generate missing content.
Verify with: grep -c '<!-- IMAGE:' {article_path}
(Must return 0 to proceed)
```

**WARNING (non-blocking, log and proceed):**
```
⚠️ Pre-Publish Verification found issues:

1. Missing 'description' field in frontmatter
   → Add description field (max 120 chars) for WeChat article summary

2. Found 3 bare URLs in body text
   → Consider converting to: 搜索「关键词」

3. Found 1 Mermaid code block at line 78
   → Convert to <!-- IMAGE --> placeholder for rendering

Proceed anyway? [Y/n]
```

### Step 3: Create Directory and Move Article

```bash
# Set the target directory
ARTICLE_DIR="${PROJECT_ROOT}/02-技术/<matched-subdirectory>"

# Create if not exists
mkdir -p "${ARTICLE_DIR}"

# Move the article to its final location
# Use cp if the original should be preserved, mv if it should be relocated
cp /path/to/article.md "${ARTICLE_DIR}/"
```

Rules:
- **Never hardcode paths.** Derive `PROJECT_ROOT` from the user's working directory or explicit input.
- **Use `mkdir -p`** to create any missing intermediate directories.
- **Collision handling:** Before copying, check if the target file already exists:
  - If exists and content is identical → skip (already published)
  - If exists and content differs → rename new file with timestamp suffix (e.g., `article_20260322.md`) and warn user
  - Never silently overwrite an existing file

### Step 4: WeChat Distribution (optional)

If the user wants to publish to WeChat, invoke `/wechat-seo-optimizer` for title and abstract optimization.

```
Question: "Optimize for WeChat distribution?"
Options:
  - Yes -- run SEO optimizer for title and abstract, then convert to WeChat format
  - No -- keep as Markdown only
```

If yes:
1. Invoke `/wechat-seo-optimizer` on the published article.
2. The WeChat converter will save the HTML to `03-创作/已发布/<YYYY-MM>/` (e.g., `03-创作/已发布/2026-03/`).

### Step 4.5: Verification Status

After pre-publish verification (Step 2.5), update the completion summary with results:

```markdown
### Pre-Publish Verification

| Check | Status | Notes |
|-------|--------|-------|
| Placeholder Residue | ✅ PASS | No IMAGE or SCREENSHOT placeholders found |
| Frontmatter | ✅ PASS | All required fields present and valid |
| External Links | ⚠️ WARNING | 2 bare URLs in body (not critical) |
| Mermaid Blocks | ✅ PASS | No Mermaid code blocks found |
| Reference Section | ✅ PASS | No standalone reference section |
```

Include any **warnings** so the user is aware of non-critical issues, but do not block publication for warnings.

### Step 5: Completion Summary (HIGH VISIBILITY)

Display a high-contrast completion summary with clear GO/NO-GO status:

**If publish SUCCEEDED:**

```
╔════════════════════════════════════════════════════════════╗
║          ✅ ARTICLE PUBLISHED SUCCESSFULLY                 ║
╚════════════════════════════════════════════════════════════╝

📄 Article Details:
   • Title: [article title]
   • File path: /absolute/path/to/02-技术/.../article.md
   • KB directory: 02-技术/<matched-subdirectory>/
   • Status: ✅ published

✨ Quality Verification:
   ✅ Pre-publish verification: PASS (all gates cleared)
   ✅ Placeholder residue: NONE
   ✅ Frontmatter: complete
   ✅ Review score: X/70 (≥55 published)
   ✅ Images: N/M successfully uploaded

📦 Distribution:
   • WeChat: [optimized / skipped]
   • Knowledge base: ready

🎯 Next Steps:
   1. Convert to WeChat format: /wechat-article-converter
   2. Multi-platform distribution: /content-repurposer
   3. SEO optimization: /wechat-seo-optimizer

╚════════════════════════════════════════════════════════════╝
```

**Always include the absolute file path** so other sessions can locate the article.

---

**If publish BLOCKED (pre-publish verification FAILED):**

```
╔════════════════════════════════════════════════════════════╗
║          ❌ PUBLISH BLOCKED - VERIFICATION FAILED           ║
╚════════════════════════════════════════════════════════════╝

⚠️ Blocking Issues:
   ❌ Found N unprocessed IMAGE placeholders at:
      • Line X: <!-- IMAGE: name1 - description -->
      • Line Y: <!-- IMAGE: name2 - description -->

🔧 Required Actions:
   1. Re-run /article-craft:images to generate missing content
   2. Verify: grep -c '<!-- IMAGE:' {article_path}
   3. Must return 0 (zero placeholders) to proceed

📁 File path: /absolute/path/to/article.md

⏱️  Status: BLOCKED - Cannot publish until images are generated

╚════════════════════════════════════════════════════════════╝
```

---

**If publish SUCCEEDED but with WARNINGS:**

```
╔════════════════════════════════════════════════════════════╗
║          ✅ ARTICLE PUBLISHED (WITH WARNINGS)              ║
╚════════════════════════════════════════════════════════════╝

📄 Article Published: /absolute/path/article.md

⚠️ Non-blocking Issues Found:
   ⚠️ Missing 'description' in frontmatter
      → Will auto-generate from first paragraph

   ⚠️ Found 2 bare URLs in body text
      → Recommend converting to: 搜索「keyword」

📋 Quality Checklist:
   ✅ Placeholder residue: NONE (GATE PASSED)
   ✅ Frontmatter validation: PASS (with warnings)
   ✅ External links: properly formatted
   ✅ Mermaid blocks: none found
   ✅ Reference section: inline (no duplication)

✨ Status: PUBLISHED (review warnings before distribution)

╚════════════════════════════════════════════════════════════╝
```

### Key Features of This Summary:

1. **High Contrast**: Uses `╔════╗` boxes for visual separation
2. **Clear Status**: ✅ vs ❌ at the top (GO/NO-GO decision)
3. **Grouped Information**: Details organized by category
4. **Action Items**: Clear next steps displayed
5. **File Path**: Always included for session continuity
6. **No Scrolling Needed**: All critical info visible above the fold

---

## Standalone Mode

When invoked directly (not as part of the orchestrator pipeline):

1. AskQuestion for the article file path if not provided.
2. Read the article to extract title and tags for directory matching.
3. Execute all steps (1, 2, 2.5, 3, 4, 4.5, 5) above:
   - Step 2.5 (Pre-Publish Verification) is **mandatory** — blocks on placeholder residue or frontmatter errors
   - Other verification checks (links, Mermaid blocks) are warnings only
4. If review score is not available (article was not reviewed), note it in the summary:
   ```
   | **Review score** | not reviewed (run `/article-craft:review` first) |
   ```
5. Always show the pre-publish verification results in the completion summary so the user knows what was checked

---

## Reference

- Knowledge base directory rules: `~/.claude/plugins/article-craft/references/knowledge-base-rules.md`
- SmartDirectoryMatcher source: `~/.claude/plugins/article-craft/scripts/utils.py`
- WeChat HTML output location: `03-创作/已发布/<YYYY-MM>/`
