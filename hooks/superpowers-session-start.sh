#!/usr/bin/env bash
# Auto-generated wrapper for superpowers SessionStart hook
# Plugin: superpowers@superpowers-marketplace
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
PLUGIN_DIR="$CLAUDE_DIR/plugins/superpowers"

[[ ! -d "$PLUGIN_DIR" ]] && exit 0

export CLAUDE_PLUGIN_ROOT="$PLUGIN_DIR"
exec bash "$CLAUDE_PLUGIN_ROOT/hooks/run-hook.cmd" session-start
