#!/usr/bin/env bash
# Auto-generated wrapper for ralph-wiggum Stop hook
# Plugin: ralph-wiggum@claude-code-plugins
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
PLUGIN_DIR="$CLAUDE_DIR/plugins/ralph-wiggum"

[[ ! -d "$PLUGIN_DIR" ]] && exit 0

export CLAUDE_PLUGIN_ROOT="$PLUGIN_DIR"
exec bash "$CLAUDE_PLUGIN_ROOT/hooks/stop-hook.sh"
