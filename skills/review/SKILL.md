---
name: article-craft:review
description: "Quality gate for articles -- self-check rules plus content-reviewer scoring. Use after writing to ensure article meets quality standards."
---

# Article Review (Quality Gate)

Run self-check rules against the article, then optionally invoke the content-reviewer for scoring. This skill is the quality gate between writing and publishing.

**Invoke**: `/article-craft:review`

**Dependency**: requires the `/content-reviewer` skill for publish-mode scoring. If `/content-reviewer` is not available, the skill falls back to self-check only and warns the user.

---

## Inputs

- **Article file path**: absolute path to the `.md` file to review
- **Mode**: `publish` (default) or `draft`

If invoked standalone (file path not provided), use AskQuestion:
```
Question: "Which article file should I review?"
(free-form input: provide the absolute path to the .md file)
```

---

## Execution Steps

### Phase 1: Self-Check (all 10 rules)

Read the article file, then check each rule below. Fix violations inline using the Edit tool before proceeding. Do not leave violations for the reviewer to catch.

**Automated self-check script** (run first for quick validation):

```bash
python3 ~/.claude/plugins/article-craft/scripts/review_selfcheck.py /path/to/article.md
```

This script checks all 11 rules automatically and outputs a formatted report. If any rules fail, fix the violations using the Edit tool, then re-run until all pass. For JSON output (machine-readable): add `--json`. For gate-only check: add `--gate-only`.

Reference: `~/.claude/plugins/article-craft/references/self-check-rules.md`

#### Rule 1: Red-Flag Words

Search the article with Grep for these patterns:

```bash
grep -nE '无缝|赋能|一站式|综上所述|总而言之|值得注意的是|不难发现|深度解析|全面梳理|链路|闭环|抓手|底层逻辑|方法论|降本增效|实际上|事实上|显然|众所周知|不难看出' /path/to/article.md
```

Also flag:
- "颠覆" / "极致" / "完美解决"
- "在当今快速发展的..." / "随着...的不断发展..."
- "让我们一起探索..."
- Unverified quantitative claims like "效率提升 300%"

Every match must be rewritten. These words trigger deductions in the "AI 痕迹" scoring dimension.

#### Rule 2: Hook Length

The first paragraph (after frontmatter) must be **100 characters or fewer** (Chinese characters, excluding code blocks). It must contain:
1. Pain point or scenario
2. Solution / tool name
3. Reading value

Forbidden openers: "在当今...的时代", "随着...的发展", "你是否也有这样的困扰？", starting with a definition "XXX 是一个..."

#### Rule 3: Closing Paragraph

The article must end with a concrete next-step action or brief technical outlook (max 2 sentences).

Forbidden closings:
- "希望本文对你有帮助"
- "如果有问题欢迎留言"
- "欢迎在评论区分享"
- "点个在看" / "转发给朋友"
- "你的点赞是我最大的动力"
- "如果这篇文章对你有帮助"

Good examples:
- "装好 uv 后，在现有项目里跑一次 `uv pip install -r requirements.txt`，体感一下速度差异。"
- "uv 的 workspace 功能还在快速迭代，monorepo 支持值得关注。"

#### Rule 4: Description Field

The YAML frontmatter must include a `description` field:
- Max 120 characters (Chinese)
- Must be a meaningful abstract, not a copy of the title
- Used as the WeChat article summary

#### Rule 5: Anti-AI Structure

- **Vary paragraph length**: consecutive paragraphs must not use the same structure (e.g., "concept -> explain -> code" twice in a row). Mix: code-first with reverse explanation, Q&A style, experience-then-principle, comparison table then conclusion.
- **Personal perspective** (at least 2 per article): first-person observations such as bug/pitfall experience, choice rationale, judgement, real benchmarks.
- **Diverse paragraph openings**: never start 2 consecutive paragraphs with "此外" / "另外" / "同时" / "值得注意的是". Replace transition words with direct content.

#### Rule 6: Chapter Depth

Every technical section must contain **at least 2 commands/code snippets plus explanatory text**. A section with only 1 command and 1 sentence is too shallow.

#### Rule 7: Duplicate Image Check

Within the same section (same `##` heading), do not include two images that serve the same purpose.

#### Rule 8: External Links for WeChat

WeChat does not support clickable external links. Replace external URLs with search guidance: `搜索「关键词」` or `在 GitHub 搜索 项目名`. Internal inline links (`[Name](url)`) are fine -- the WeChat converter auto-extracts them as footnote references.

#### Rule 9: Mermaid Code Block Residue

Verify that **no Mermaid code blocks** (```` ```mermaid ... ``` ````) remain. All flowcharts/sequence diagrams/gantt charts must have been rendered to PNG and replaced with `![description](CDN_URL)`.

#### Rule 10: References Inline (No Separate Section)

All reference links must be **inlined** at first mention using `[Name](url)` format. Do NOT create a standalone "参考资料" or "参考链接" section at the end. The WeChat converter auto-generates footnotes from inline links; a manual section causes duplication.

#### Rule 11: IMAGE & SCREENSHOT Placeholder Residue ⭐ CRITICAL GATE

**Before proceeding to Phase 2 (content-reviewer), check for unprocessed placeholders:**

```bash
# Check for any remaining placeholders
placeholder_count=$(grep -c '<!-- IMAGE:\|<!-- SCREENSHOT:' /path/to/article.md)

if [ "$placeholder_count" -eq 0 ]; then
  echo "✅ GATE PASSED: No placeholder residue"
  exit 0
else
  echo "❌ GATE BLOCKED: Found $placeholder_count unprocessed placeholders"
  grep -n '<!-- IMAGE:\|<!-- SCREENSHOT:' /path/to/article.md
  exit 1
fi
```

**If ANY placeholders found:**
1. **This is a GATE violation** — article generation incomplete
2. **BLOCK** from proceeding to content-reviewer
3. **Report error with locations:**
   ```
   ════════════════════════════════════════════════════════════
   ❌ REVIEW BLOCKED: Placeholder Residue Detected
   ════════════════════════════════════════════════════════════

   Found N unprocessed placeholders at:
   - Line X: <!-- IMAGE: name1 - description -->
   - Line Y: <!-- SCREENSHOT: url -->

   Action required:
   → Re-run /article-craft:images to generate missing content
   → Verify with: grep -c '<!-- IMAGE:' {article_path}
   → Must return 0 to proceed

   ════════════════════════════════════════════════════════════
   ```

**Why GATE?**
- Placeholders = generation process incomplete/crashed
- Publishing with placeholders = broken links + poor UX
- This gate prevents incomplete articles from reaching review
- Clear error message prevents user confusion

### Phase 1 Completion Summary (NEW)

After all 11 rules pass, display a high-visibility completion summary:

```
════════════════════════════════════════════════════════════
✅ PHASE 1 SELF-CHECK COMPLETE
════════════════════════════════════════════════════════════

📋 Self-Check Results (11 Rules):
   ✅ Rule 1: Red-flag words — no violations
   ✅ Rule 2: Hook length — 52 chars (≤100)
   ✅ Rule 3: Closing paragraph — concrete action
   ✅ Rule 4: Description field — 120 chars summary
   ✅ Rule 5: Anti-AI structure — varied & personal
   ✅ Rule 6: Chapter depth — sufficient examples
   ✅ Rule 7: Duplicate images — none found
   ✅ Rule 8: WeChat links — all inline format
   ✅ Rule 9: Mermaid residue — none found
   ✅ Rule 10: References inline — no separate section
   ✅ Rule 11: Placeholder residue — GATE PASSED ✨

✨ Status: READY FOR CONTENT-REVIEWER SCORING
════════════════════════════════════════════════════════════
```

This summary:
- Uses high-contrast formatting (═══ boxes)
- Shows all 11 rules at a glance
- Clearly indicates GATE PASSED status
- Signals readiness for Phase 2

### Phase 2: Content-Reviewer Scoring (publish mode only)

**If mode is `draft`**: skip this phase. Report self-check results only.

**If mode is `publish`**:

1. Invoke `/content-reviewer` on the article file.
2. Check the score against the **55/70 threshold**.
3. **If score >= 55/70**: pass. Proceed to output.
4. **If score < 55/70**: auto-modify the article, then re-run `/content-reviewer`. Repeat for up to **3 rounds**.

   **Auto-modify strategy** (applied in order):
   1. **Rule-based fixes** — Apply self-check rules: grep for red-flag words and rewrite them; fix hook length if over 100 chars; fix forbidden closings
   2. **Dimension-targeted rewrites** — Read the reviewer's per-dimension scores. For any dimension scoring below 7/10, use the Edit tool to rewrite the weakest sections:
      - "AI 痕迹" low → diversify paragraph structure, add personal perspective, vary openings
      - "标题与 Hook" low → rewrite title per style-guide formula, shorten hook
      - "内容深度" low → add code examples, expand thin sections
      - "结构可读" low → split long paragraphs, add callouts, improve transitions
      - "代码质量" low → add error handling, comments, type hints to code blocks
      - "结尾行动力" low → replace generic closing with concrete next-step command
   3. **Never regenerate the entire article** — only edit specific sections identified by the reviewer
5. **After 3 failed rounds**: ask the user:
   ```
   Question: "The article scored [X]/70 after 3 revision rounds (threshold: 55/70). How to proceed?"
   Options:
     - Continue revising -- attempt another round of fixes
     - Publish anyway -- accept the current score and proceed
     - Abort -- stop the pipeline, return to manual editing
   ```

---

## Output: Score + Feedback Report

```markdown
## Review Results

### Self-Check
- Rule 1 (Red-Flag Words): PASS / FIXED (N violations rewritten)
- Rule 2 (Hook Length): PASS / FIXED
- Rule 3 (Closing): PASS / FIXED
- Rule 4 (Description): PASS / FIXED
- Rule 5 (Anti-AI Structure): PASS / FIXED
- Rule 6 (Chapter Depth): PASS / WARNING (section X is thin)
- Rule 7 (Duplicate Images): PASS
- Rule 8 (WeChat Links): PASS / FIXED
- Rule 9 (Mermaid Residue): PASS
- Rule 10 (References Inline): PASS / FIXED

### Content-Reviewer Score (publish mode)
- Score: [X]/70
- Status: PASS (>= 55) / FAIL (< 55, round N/3)
- Key feedback: [reviewer's main points]
```

---

## Standalone Mode

When invoked directly (not as part of the orchestrator pipeline):

1. AskQuestion for the article file path if not provided.
2. AskQuestion for the mode:
   ```
   Question: "Review mode?"
   Options:
     - Publish -- full review with content-reviewer scoring (>= 55/70 required)
     - Draft -- self-check only, skip content-reviewer
   ```
3. Execute the review steps above.
4. Output the report.
