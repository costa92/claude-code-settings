#!/usr/bin/env bash
# ralph-wiggum-stop.sh
# 动态定位 ralph-wiggum 插件目录，转发执行 stop-hook.sh
# 无硬编码路径，支持 CLAUDE_CONFIG_DIR 环境变量

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
PLUGIN_DIR="$CLAUDE_DIR/plugins/cache/claude-code-plugins/ralph-wiggum"

LATEST=$(ls -d "$PLUGIN_DIR"/*/ 2>/dev/null | sort -V | tail -1)
if [[ -z "$LATEST" ]]; then
  exit 0
fi

export CLAUDE_PLUGIN_ROOT="${LATEST%/}"
exec bash "$CLAUDE_PLUGIN_ROOT/hooks/stop-hook.sh"
