#!/usr/bin/env python3
"""
Thin wrapper — delegates to the canonical implementation in article-craft plugin.

The canonical script lives at:
  ~/.claude/plugins/article-craft/scripts/nanobanana.py

This wrapper only exists so the plugin can be invoked standalone
with a different default size (9:16 portrait vs 16:9 landscape).
"""
import sys
import os

CANONICAL_DIR = os.path.expanduser("~/.claude/plugins/article-craft/scripts")
sys.path.insert(0, CANONICAL_DIR)

from nanobanana import run  # noqa: E402

if __name__ == "__main__":
    run(default_size="768x1344")
