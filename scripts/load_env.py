#!/usr/bin/env python3
"""Unified config loader for Claude Code skills (Python version).

Usage in Python scripts:
    from load_env import load_env
    config = load_env()                    # returns dict of all config
    config = load_env(keys=["gemini_api_key"])  # only specific keys

Usage as CLI (exports to stdout for shell eval):
    eval "$(python3 ~/.claude/scripts/load_env.py)"
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional


ENV_FILE = Path(os.environ.get("CLAUDE_ENV_FILE", Path.home() / ".claude" / "env.json"))


def load_env(keys: Optional[list] = None, set_environ: bool = True) -> dict:
    """Load config from env.json.

    Args:
        keys: If provided, only load these keys. Otherwise load all.
        set_environ: If True, also set os.environ with UPPER_SNAKE_CASE names
                     (only for keys not already set, respecting env var > env.json priority).

    Returns:
        Dict of config values (original snake_case keys).
    """
    if not ENV_FILE.exists():
        return {}

    with open(ENV_FILE) as f:
        data = json.load(f)

    result = {}
    for key, value in data.items():
        if key.startswith("_"):
            continue
        if not isinstance(value, (str, int, float, bool)):
            continue
        if keys and key not in keys:
            continue
        str_value = str(value) if not isinstance(value, str) else value
        if str_value.startswith("your-"):
            continue
        result[key] = value
        if set_environ and not os.environ.get(key.upper()):
            os.environ[key.upper()] = str_value

    return result


def main():
    """CLI mode: output export statements for shell eval."""
    config = load_env(set_environ=False)
    for key, value in config.items():
        env_name = key.upper()
        if os.environ.get(env_name):
            continue
        str_value = str(value) if not isinstance(value, str) else value
        escaped = str_value.replace("'", "'\\''")
        print(f"export {env_name}='{escaped}'")


if __name__ == "__main__":
    main()
