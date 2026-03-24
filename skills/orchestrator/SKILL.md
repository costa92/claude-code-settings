---
name: article-craft
description: "Full article generation pipeline — orchestrates requirements, verification, writing, image generation, review, and publishing. Use when creating a complete technical article end-to-end."
---

# Article Craft — Orchestrator

Composes 7 skills into a complete article generation pipeline. Each skill can also
be used independently via `/article-craft:<skill-name>`.

## Workflow Modes

Three modes, selected at invocation:

| Mode | Skills Executed | Use Case |
|------|----------------|----------|
| **standard** (default) | requirements → verify → write → screenshot → images → review → publish | Full article with quality gate |
| **quick** (`--quick`) | requirements → write → screenshot → images | Fast output, skip verification and review |
| **draft** (`--draft`) | requirements → write | Content only, no images or review |
| **series** (`--series FILE`) | Read series.md → requirements (pre-filled) → standard pipeline | Write the next article in a series |

## Inputs

- **Topic** (optional): If provided as argument, skip requirements skill
- **Mode flag**: `--quick` or `--draft` (default: standard)
- **File path** (optional): If an existing article.md is provided, skip to the next unfinished stage
- **Upgrade flag**: `--upgrade` with a file path — upgrade a draft/quick article to standard
- **Series flag**: `--series SERIES_FILE` — write the next planned article in the series (reads topic, audience, depth, visual style from series.md)

## Upgrade Mode

When invoked with `--upgrade /path/to/article.md`, determine what's already done and run only the missing stages:

```
Detection logic:
  1. Has CDN image URLs?  → images already done, skip images
  2. Has <!-- IMAGE: --> placeholders?  → images NOT done, run images
  3. Has <!-- SCREENSHOT: --> placeholders?  → screenshots NOT done, run screenshots
  4. File is in 02-技术/ KB directory?  → publish already done, skip publish

Upgrade paths:
  draft → standard:  run verify → screenshot → images → review → publish
  draft → quick:     run screenshot → images
  quick → standard:  run verify → review → publish
```

Skip stages that have already been completed. Show the upgrade plan before executing:

```
Upgrading: /path/to/article.md
  verify:     will run (not done)
  screenshot: will run (2 placeholders found)
  images:     will run (3 placeholders found)
  review:     will run (not done)
  publish:    will run (not in KB)
  Proceed? [Y/n]
```

## Pipeline Execution

### Step 1: Determine Mode

Parse the invocation arguments:
- No flags → standard mode (all 7 skills)
- `--quick` → quick mode (requirements + write + screenshot + images)
- `--draft` → draft mode (requirements + write only)
- If a file path to an existing `.md` file is provided → skip requirements/verify/write,
  start from images skill

### Step 2: Initialize Status Tracker

Track each skill's status throughout the pipeline:

```
Pipeline Status:
  requirements: pending
  verify:       pending
  write:        pending
  images:       pending
  review:       pending
  publish:      pending
```

Update status as each skill runs: `pending → running → success | failed | skipped`

### Step 3: Execute Skills Sequentially

Execute each skill in order, passing context between them.

#### 3.1 Requirements (all modes)

Invoke `article-craft:requirements` skill logic:
- **Smart inference first**: Analyze the topic for writing style, depth, audience, and format signals
- If topic was provided as argument, pre-fill and skip the topic question
- Show inferred values as a single confirmation question (not 5-7 separate questions)
- Only ask individual questions when inference is genuinely ambiguous
- **Mode-aware**: In draft mode, skip image-related questions entirely
- Store gathered context in memory for downstream skills

**On failure:** Retry (user input errors are unlikely)
**Status:** Mark `success` when requirements are confirmed

#### 3.2 Verify (standard mode only)

Invoke `article-craft:verify` skill logic:
- Extract tool names and URLs from the topic/context
- Run batch verification (links, commands, feature discovery)
- Use Standard verification mode by default

**On failure:** Report failures but continue — verification is non-blocking
**Status:** Mark `success` (even with individual link/command failures)

> [!note]
> Skipped in quick and draft modes. Mark as `skipped`.

#### 3.3 Write (all modes)

Invoke `article-craft:write` skill logic:
- Pass requirements context from Step 3.1
- Pass verification results from Step 3.2 (if available)
- Generate article with YAML frontmatter, Obsidian callouts, image placeholders
- Apply self-check rules from `references/self-check-rules.md`
- Save article.md to disk
- **Capture the absolute file path** — this is passed to all subsequent skills

**On failure:** FATAL — pipeline stops. Report what completed so far.
**Status:** Mark `success` when article.md is saved

#### 3.4 Screenshot (standard and quick modes)

Invoke `article-craft:screenshot` skill logic:
- Pass the article.md absolute file path from Step 3.3
- Scan for `<!-- SCREENSHOT: URL -->` placeholders
- Take screenshots via `shot-scraper`
- Upload to CDN and replace placeholders in-place
- If no `<!-- SCREENSHOT: -->` placeholders found, skip silently

**On failure:** Non-fatal — keep placeholders, warn user, continue
**Status:** Mark `success` if all screenshots captured, `skipped` if no placeholders

> [!note]
> Skipped in draft mode. Mark as `skipped`.

#### 3.5 Images (standard and quick modes)

Invoke `article-craft:images` skill logic:
- Pass the article.md absolute file path from Step 3.3 (screenshot placeholders already resolved)
- Run Gemini probe test
- Batch process image placeholders with heartbeat monitoring enabled
- Update article.md in-place with CDN URLs

**CRITICAL: Heartbeat Monitoring**
- Images skill writes heartbeat file: `{article_path}.heartbeat` (updated every 2s)
- Images skill creates lock file: `{article_path}.lock` (deleted when finished)
- Orchestrator monitors these files during processing:
  ```bash
  # Check heartbeat every 3 seconds
  if no heartbeat update for 10s → skill likely crashed
    → kill process and auto-retry once
  if lock file disappears → skill finished
    → verify IMAGE placeholders are replaced
    → if any remain → log warning but continue (graceful degradation)
  ```

**On failure:** Graceful degradation — keep unresolved placeholders, log which
images failed, continue to review. Auto-retry once if process crashes.
**Status:** Mark `success` if any images generated, `failed` if all failed

> [!note]
> Skipped in draft mode. Mark as `skipped`.

#### 3.6 Review (standard mode only)

Invoke `article-craft:review` skill logic:
- Pass the article.md absolute file path
- Run self-check (10 rules from self-check-rules.md)
- Invoke `/content-reviewer` for 7-dimension scoring

**Review retry loop:**
1. If score ≥ 55/70 → PASS, continue to publish
2. If score < 55/70 and rounds ≤ 3:
   - Auto-modify the article based on reviewer feedback
   - Re-run review
   - Increment round counter
3. If score < 55/70 and rounds > 3:
   - Use AskQuestion: "Article scored {score}/70 after 3 rounds. Proceed anyway or abort?"
   - If proceed → continue to publish
   - If abort → stop pipeline, report status

**On failure (content-reviewer unavailable):** Warn user, proceed with self-check only
**Status:** Mark `success` when score ≥ 55 or user approves

> [!note]
> Skipped in quick and draft modes. Mark as `skipped`.

#### 3.7 Publish (standard mode only)

Invoke `article-craft:publish` skill logic:
- Pass the article.md absolute file path
- Auto-detect knowledge base (02-技术/ directory)
- Match subdirectory via SmartDirectoryMatcher
- Move article to final KB location
- Optionally invoke /wechat-seo-optimizer

**On failure:** Retry once, then report error with the current file path so user
can manually move it
**Status:** Mark `success` when article is in final location

> [!note]
> Skipped in quick and draft modes. Mark as `skipped`.

### Step 4: Completion Summary (HIGH VISIBILITY)

After all skills complete (or pipeline stops on fatal error), print a high-contrast summary with clear GO/NO-GO status:

**On SUCCESS (all 7 steps):**

```
╔════════════════════════════════════════════════════════════╗
║          ✅ ARTICLE CRAFT PIPELINE COMPLETE                ║
╚════════════════════════════════════════════════════════════╝

📊 Pipeline Execution Summary:

│ Step  │ Skill          │ Status   │ Key Metrics              │
├───────┼────────────────┼──────────┼──────────────────────────┤
│ 3.1   │ requirements   │ ✅ PASS  │ Topic inferred correctly │
│ 3.2   │ verify         │ ✅ PASS  │ 5/5 links verified       │
│ 3.3   │ write          │ ✅ PASS  │ 4,700+ words generated   │
│ 3.4   │ screenshot     │ ⊘ skip   │ no SCREENSHOT tags       │
│ 3.5   │ images         │ ✅ PASS  │ 5/5 images CDN uploaded  │
│ 3.6   │ review         │ ✅ PASS  │ 62/70 (≥55 threshold)    │
│ 3.7   │ publish        │ ✅ PASS  │ KB published             │

════════════════════════════════════════════════════════════

🎯 Final Status: ✨ READY FOR DISTRIBUTION

📁 File: /absolute/path/to/02-技术/.../article.md
✅ All GATES passed (3-layer verification)
✅ All images uploaded and verified
✅ Quality threshold met (62/70)
✅ Knowledge base published

🚀 Next Actions (Optional):
   1. /wechat-article-converter  — Convert to WeChat HTML
   2. /wechat-seo-optimizer      — Optimize title & SEO
   3. /content-repurposer        — Multi-platform distribution
   4. /content-analytics        — Track performance metrics

════════════════════════════════════════════════════════════
```

**On FAILURE (with specific step blocked):**

```
╔════════════════════════════════════════════════════════════╗
║          ⚠️  ARTICLE CRAFT PIPELINE STOPPED                ║
╚════════════════════════════════════════════════════════════╝

📊 Pipeline Execution Status:

│ Step  │ Skill          │ Status   │ Notes                    │
├───────┼────────────────┼──────────┼──────────────────────────┤
│ 3.1   │ requirements   │ ✅ PASS  │ Confirmed by user        │
│ 3.2   │ verify         │ ✅ PASS  │ 5/5 links OK             │
│ 3.3   │ write          │ ✅ PASS  │ Article generated        │
│ 3.4   │ screenshot     │ ⊘ skip   │ no SCREENSHOT tags       │
│ 3.5   │ images         │ ❌ FAIL  │ 2/5 images failed        │
│ 3.6   │ review         │ ⏸ blocked│ waiting for images       │
│ 3.7   │ publish        │ ⏸ blocked│ waiting for review       │

════════════════════════════════════════════════════════════

🔴 Blocked At: Step 3.5 (Images)

❌ Failure Details:
   • 2 out of 5 images failed to upload
   • Failed images: cover, architecture-diagram
   • Error: CDN connection timeout

🔧 Recovery Action Required:
   1. Check network connection
   2. Re-run: /article-craft:images {file_path}
   3. Verify: grep -c '<!-- IMAGE:' {file_path}
   4. Should return 0 (zero placeholders)

📁 Current File: /absolute/path/to/article.md
⏱️  Partial Progress: 3.4/7 steps completed

════════════════════════════════════════════════════════════
```

**Key Improvements:**

1. ✅ **Unified box formatting** — Both success/failure use `╔════╝` boxes for visual consistency
2. ✅ **Clear status indicators** — ✅ PASS / ❌ FAIL / ⊘ skip / ⏸ blocked
3. ✅ **Quick scanning** — Key metrics on same line as step status
4. ✅ **Error context** — Explains what went wrong and how to fix it
5. ✅ **No scrolling** — All critical info visible (mobile/small screens friendly)
6. ✅ **File path included** — Always shows article location for session continuity

## Standalone Skill Usage

Each skill can be used independently without the orchestrator:

```
/article-craft:requirements   # Just gather requirements
/article-craft:verify         # Just verify links/commands
/article-craft:write          # Just write an article
/article-craft:screenshot     # Just take screenshots / generate share cards
/article-craft:images         # Just generate images for existing article
/article-craft:review         # Just review an existing article
/article-craft:publish        # Just publish to knowledge base
```

When used standalone, each skill handles its own input gathering via AskQuestion
if no arguments are provided.

## Integration

- **content-pipeline agent**: Already updated to use `article-craft` as the writing skill
- **content-reviewer**: Delegated to by the review skill (dependency declared in plugin.json)
- **wechat-seo-optimizer**: Called by publish skill for WeChat optimization
