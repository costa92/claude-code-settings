#!/usr/bin/env bash
# load_env.sh - Unified config loader for Claude Code skills
#
# Reads ~/.claude/env.json and exports values as environment variables.
# Key naming: JSON snake_case → ENV UPPER_SNAKE_CASE
#   e.g. gemini_api_key → GEMINI_API_KEY
#
# Priority: existing env var > env.json (won't overwrite already-set vars)
#
# Usage:
#   source ~/.claude/scripts/load_env.sh           # export all
#   source ~/.claude/scripts/load_env.sh gemini     # export only keys matching "gemini"
#   eval "$(~/.claude/scripts/load_env.sh)"         # alternative usage

ENV_FILE="${CLAUDE_ENV_FILE:-$HOME/.claude/env.json}"

if [ ! -f "$ENV_FILE" ]; then
  echo "warn: $ENV_FILE not found. Copy env.example.json and fill in your values." >&2
  return 0 2>/dev/null || exit 0
fi

FILTER="${1:-}"

# Parse JSON and export as environment variables
# - Skips keys starting with _ (e.g. _comment)
# - Skips placeholder values (your-*)
# - Skips keys already set in environment (respects env var > env.json priority)
# - Uses single quotes to prevent $, `, ! expansion
_load_env_exports="$(python3 -c "
import json, sys, os

env_file, filter_key = sys.argv[1], sys.argv[2].lower()

with open(env_file) as f:
    data = json.load(f)

for key, value in data.items():
    if key.startswith('_'):
        continue
    if filter_key and filter_key not in key.lower():
        continue
    if not isinstance(value, (str, int, float, bool)):
        continue
    env_name = key.upper()
    if os.environ.get(env_name):
        continue
    str_value = str(value) if not isinstance(value, str) else value
    if str_value.startswith('your-'):
        continue
    escaped = str_value.replace(\"'\", \"'\\\\''\" )
    print(f\"export {env_name}='{escaped}'\")
" "$ENV_FILE" "$FILTER" 2>&1)" || {
  echo "warn: failed to parse $ENV_FILE" >&2
  unset _load_env_exports
  return 1 2>/dev/null || exit 1
}

eval "$_load_env_exports"
unset _load_env_exports
