# Fix: Image Generation Probe Timeout Issue

## Context

When the images skill runs, it first probes the Gemini API with a test image to verify availability. The probe calls `nanobanana.py` directly, but this call has **no timeout protection**. When the default model (`gemini-3-pro-image-preview`) is slow/overloaded, the probe hangs indefinitely, requiring manual kill + retry.

In contrast, `generate_and_upload_images.py` (batch mode) has a proper 120s subprocess timeout AND automatic 3-level model fallback. The probe workflow relies on Claude to manually detect timeout and switch models — fragile and slow.

## Changes

### 1. `nanobanana.py` — Add `--timeout` CLI parameter

**File**: `~/.claude/plugins/article-craft/scripts/nanobanana.py`

- Add `--timeout` argument (default: 30 seconds) at line ~296 (after `--no-fallback`)
- Apply timeout to `client.models.generate_content()` call via `httpx` timeout config at line 121:
  ```python
  client = genai.Client(api_key=api_key, http_options={"timeout": timeout_value})
  ```
- Since `client` is initialized at module level (line 121) before CLI args are parsed, refactor: move client initialization into `run()` function, or create client lazily on first use
- Pass timeout through `_generate_single_model()` → update function signature

### 2. `generate_and_upload_images.py` — Add `--probe` flag

**File**: `~/.claude/plugins/article-craft/scripts/generate_and_upload_images.py`

- Add `--probe` CLI argument at line ~1785 (after `--enhance`)
- When `--probe` is passed, run a lightweight probe that:
  1. Iterates through `MODEL_FALLBACK_CHAIN`
  2. For each model, calls `nanobanana.py --prompt "test" --size 1024x1024 --timeout 30 --output /tmp/gemini_probe.jpg --no-fallback`
  3. If subprocess succeeds within 30s → print model name and exit 0
  4. If fails → try next model
  5. All fail → print error and exit 1
- Insert probe logic after dependency check (line ~1940), before batch processing (line ~1998)
- When `--probe` flag is used alone (without `--process-file`), just print the best available model and exit

### 3. `SKILL.md` — Simplify probe workflow

**File**: `~/.claude/skills/images/SKILL.md`

Replace the manual 2-step probe (lines 29-59) with a single command:

```bash
# Auto-detect best available model
BEST_MODEL=$(python3 ~/.claude/plugins/article-craft/scripts/generate_and_upload_images.py --probe 2>&1 | grep "BEST_MODEL:" | cut -d: -f2)
```

Then pass `--model $BEST_MODEL` to batch processing. This eliminates the manual probe-kill-retry loop entirely.

## File Summary

| File | Change | Lines |
|------|--------|-------|
| `nanobanana.py` | Add `--timeout` arg, apply to Gemini client | ~121, ~180-215, ~296 |
| `generate_and_upload_images.py` | Add `--probe` flag with auto model detection | ~1785, ~1790-1800 |
| `SKILL.md` | Replace manual probe with `--probe` command | ~29-90 |

## Verification

1. Test `nanobanana.py --timeout 5 --prompt "test" --size 1024x1024 --output /tmp/test.jpg` with intentionally short timeout → should fail fast
2. Test `generate_and_upload_images.py --probe` → should output the best available model
3. Test full pipeline: `generate_and_upload_images.py --probe` then `--process-file` with returned model
