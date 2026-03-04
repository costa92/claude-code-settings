#!/usr/bin/env bash
# superpowers-session-start.sh
# 动态定位最新 superpowers 版本，转发执行 session-start hook
# 路径通过 CLAUDE_CONFIG_DIR 环境变量或 ~/.claude 自动推断，无硬编码

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
PLUGIN_DIR="$CLAUDE_DIR/plugins/cache/superpowers-marketplace/superpowers"

LATEST=$(ls -d "$PLUGIN_DIR"/*/ 2>/dev/null | sort -V | tail -1)
if [[ -z "$LATEST" ]]; then
  exit 0
fi

export CLAUDE_PLUGIN_ROOT="${LATEST%/}"
exec bash "$CLAUDE_PLUGIN_ROOT/hooks/run-hook.cmd" session-start
