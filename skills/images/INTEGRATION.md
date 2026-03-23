# Heartbeat Monitoring Integration Guide

## Overview

This guide explains how to integrate the heartbeat monitoring system into the article generation pipeline to prevent incomplete articles from being published.

## Problem Statement

**Issue**: Image generation process crashes silently, leaving unprocessed `<!-- IMAGE: -->` placeholders in articles. These incomplete articles pass through review and publish gates, resulting in broken user experience.

**Root Cause**: No process health monitoring. Orchestrator can't detect if background `generate_and_upload_images.py` process hangs or crashes.

**Solution**: Three-layer GATE system with heartbeat monitoring:
1. **GATE 1** (Images): Heartbeat detection in skill itself
2. **GATE 2** (Review): Placeholder residue check blocks incomplete articles
3. **GATE 3** (Publish): Pre-publish verification rejects articles with unprocessed placeholders

## Architecture

```
generate_and_upload_images.py (background process)
    ├── Writes: {article_path}.heartbeat (timestamp every 2s)
    └── Creates: {article_path}.lock (signals process running)

Orchestrator (main process)
    └── HeartbeatWatcher thread
        ├── Checks heartbeat every 3s
        ├── Detects stale process (no update for 10s)
        ├── Kills stalled process
        └── Retries once or fails gracefully

Review Skill (GATE 2)
    └── Rule 11: IMAGE/SCREENSHOT Placeholder Residue
        ├── Grep for unprocessed placeholders
        ├── BLOCK if any found
        └── Report locations for recovery

Publish Skill (GATE 3)
    └── Step 2.5: Pre-Publish Verification
        ├── Final check for placeholders
        ├── BLOCK if any remain
        └── Suggests re-running images skill
```

## Implementation

### 1. Images Skill Integration

**File**: `~/.claude/skills/images/scripts/heartbeat.py`

In your `generate_and_upload_images.py`:

```python
#!/usr/bin/env python3
from pathlib import Path
import sys

# Add scripts dir to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from heartbeat import HeartbeatMonitor

def main(article_path: str):
    """Main image generation function."""
    monitor = HeartbeatMonitor(article_path, heartbeat_interval=2.0)

    # Start heartbeat
    monitor.start_heartbeat()

    try:
        # Do image processing work here
        print(f"🖼️  Processing images for {article_path}")
        process_images(article_path)

        print(f"✅ Image processing complete")
        return 0

    except Exception as e:
        print(f"❌ Image processing failed: {e}")
        return 1

    finally:
        # Always stop heartbeat
        monitor.stop_heartbeat()

def process_images(article_path: str):
    """Placeholder for actual image generation logic."""
    pass

if __name__ == "__main__":
    exit_code = main(sys.argv[1])
    sys.exit(exit_code)
```

**Enable heartbeat flag** in SKILL.md Step 3 (already documented):
```bash
python3 generate_and_upload_images.py \
  --process-file /ABSOLUTE/PATH/article.md \
  --enable-heartbeat  # Writes heartbeat every 2s
```

### 2. Orchestrator Integration

**File**: `~/.claude/skills/orchestrator/SKILL.md` Step 3.5 Images

Update orchestrator to use `OrchestratorMonitor`:

```python
#!/usr/bin/env python3
# In orchestrator Step 3.5: Images execution

import subprocess
import sys
from pathlib import Path

# Add images skill scripts to path
images_scripts = Path("~/.claude/skills/images/scripts").expanduser()
sys.path.insert(0, str(images_scripts))

from orchestrator_monitor import run_with_monitoring

def execute_images_skill(article_path: str) -> dict:
    """Execute images skill with heartbeat monitoring."""

    # Command to run
    command = [
        "python3",
        "~/.claude/skills/images/scripts/generate_and_upload_images.py",
        "--process-file", article_path,
        "--enable-heartbeat"
    ]

    # Run with monitoring and auto-recovery
    result = run_with_monitoring(
        command=command,
        article_path=article_path,
        timeout=300.0,  # 5 minute timeout
        heartbeat_timeout=10.0,  # Consider dead if no heartbeat for 10s
        max_retries=1  # Retry once on timeout
    )

    # Update orchestrator status
    if result.success:
        print(f"✅ Images skill: SUCCESS")
        return {
            "status": "success",
            "images_generated": "all" # Count from article
        }
    elif result.killed:
        print(f"⚠️  Images skill: TIMEOUT/STALLED")
        print(f"   Error: {result.error}")
        # Graceful degradation: keep placeholders, continue to review
        return {
            "status": "partial",
            "error": result.error,
            "note": "Process killed, some images may be incomplete"
        }
    else:
        print(f"❌ Images skill: FAILED")
        print(f"   Error: {result.error}")
        return {
            "status": "failed",
            "error": result.error
        }
```

### 3. Review Skill Integration

**File**: `~/.claude/skills/review/SKILL.md` Rule 11 (already documented)

GATE 2 catches any articles that slip through with unprocessed placeholders:

```bash
# In review skill Phase 1, after all other rules

# Rule 11: IMAGE & SCREENSHOT Placeholder Residue Check
grep -n '<!-- IMAGE:\|<!-- SCREENSHOT:' /path/to/article.md

# If ANY matches found:
# 1. BLOCK from proceeding to content-reviewer
# 2. Report error with line numbers
# 3. Suggest: Re-run /article-craft:images to generate missing content
```

### 4. Publish Skill Integration

**File**: `~/.claude/skills/publish/SKILL.md` Step 2.5 (already documented)

GATE 3 is final safety net before KB commit:

```bash
# In publish skill Step 2.5: Pre-Publish Verification

# Check for unprocessed IMAGE placeholders
grep -n '<!-- IMAGE:' /path/to/article.md

# If ANY matches found:
# 1. BLOCK publication
# 2. Report: "Found N unprocessed IMAGE placeholders at lines X, Y, Z"
# 3. Suggest: Re-run /article-craft:images to generate missing content
# 4. Verify with: grep -c '<!-- IMAGE:' {article_path}  # Must return 0
```

## Usage Examples

### Example 1: Normal Execution

```bash
# Orchestrator runs images skill with monitoring
$ python3 orchestrator_monitor.py \
    --article-path /home/user/docs/article.md \
    --timeout 300 \
    --heartbeat-timeout 10

# ✅ Heartbeat file created: article.md.heartbeat
# Heartbeat updates: [timestamp updated every 2s]
# ✅ Process completed successfully
# Heartbeat file removed: article.md.lock
```

### Example 2: Process Timeout (Auto-Recovery)

```bash
# Process hangs after 10 seconds (no heartbeat)
$ python3 orchestrator_monitor.py \
    --article-path /home/user/docs/article.md

# ⚠️ Process stalled (no heartbeat for 10s)
# 🔄 Auto-retry attempt 1/1
# ⚠️ Process stalled again
# ❌ Failed after 1 retry

# Result: 64 images generated, 1 incomplete
# GATE 2 (Review): Detects placeholder at line 245
# GATE 3 (Publish): Would block if it reached here
```

### Example 3: Review Gate Catches Incomplete Article

```bash
# Review skill executes Rule 11
$ grep -n '<!-- IMAGE:' /path/to/article.md

# OUTPUT:
# 245:<!-- IMAGE: missing-diagram - Architecture flow -->

# ❌ ERROR: Found 1 unprocessed IMAGE placeholder
# Cannot proceed to content-reviewer
# Action: Re-run /article-craft:images

# User runs:
$ /article-craft:images /path/to/article.md

# Generates remaining image, review proceeds
```

## Testing

### Unit Tests

```bash
# Test HeartbeatMonitor
python3 /home/hellotalk/.claude/skills/images/scripts/heartbeat.py

# OUTPUT:
# Testing HeartbeatMonitor...
# ✓ Test 1: Start/stop heartbeat
#   Heartbeat file created: True
#   Lock file removed: True
# ✓ Test 2: Staleness detection
#   Should be alive with 1s timeout: True
#   Should be stale after 1.5s: True
# ✅ All tests passed!
```

```bash
# Test OrchestratorMonitor
python3 /home/hellotalk/.claude/skills/images/scripts/orchestrator_monitor.py

# OUTPUT:
# Testing OrchestratorMonitor...
# ✓ Test 1: Monitor successful process
#   Success: True, Exit code: 0
# ✓ Test 2: Monitor failed process
#   Success: False, Exit code: 1
# ✅ All orchestrator tests passed!
```

### Integration Test

```bash
# Test full pipeline with monitoring
/article-craft --series /path/to/series.md 2>&1 | grep -E "(heartbeat|GATE|ERROR|SUCCESS)"

# Expected output shows heartbeat checks passing each GATE
```

## Monitoring Files Created

During processing, three files are created:

```
article.md              # Original article
article.md.heartbeat    # Timestamp of last heartbeat (removed on success)
article.md.lock         # Signals process is running (removed on completion)
```

**Cleanup behavior**:
- On success: Both `.heartbeat` and `.lock` removed
- On timeout: Both files removed, process killed
- On crash: Files remain (diagnostic aid), manual cleanup may be needed

## Troubleshooting

### "Process stalled (no heartbeat for 10s)"

**Cause**: Image generation process hung or crashed

**Solution**:
1. Check Gemini API status (may be rate-limited)
2. Check disk space (CDN upload writes temp files)
3. Check network connectivity
4. Run `/article-craft:images` again to retry

### "Found N unprocessed IMAGE placeholders"

**Cause**: Images skill failed to generate or upload images

**Solution**:
1. Check `--enable-heartbeat` flag is being used
2. Verify absolute paths (not relative)
3. Check PicGo/S3 credentials
4. Review image generation logs

### Heartbeat file stuck

**Cause**: Process killed externally, cleanup not ran

**Solution**:
```bash
# Manual cleanup
rm /path/to/article.md.heartbeat
rm /path/to/article.md.lock
```

## Performance Impact

**Overhead**: < 1% CPU (one heartbeat write every 2 seconds)

- Heartbeat thread: Sleeps 2s between writes
- Watcher thread: Checks every 3s
- File I/O: Write timestamp string (~30 bytes) to disk

No measurable impact on image generation speed.

## Future Enhancements

- [ ] Heartbeat metrics: Track staleness patterns over time
- [ ] Adaptive timeout: Adjust based on cluster size
- [ ] Progress reporting: Heartbeat includes current state (e.g., "Image 4/10")
- [ ] Alert system: Notify on repeated timeouts
