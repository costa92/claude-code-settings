#!/usr/bin/env bash
# common.sh — shared utilities for ~/.claude scripts
# Source this file: source "${BASH_SOURCE[0]%/*}/../lib/common.sh" or source ~/.claude/lib/common.sh

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
PLUGINS_DIR="$CLAUDE_DIR/plugins"
PLUGINS_JSON="$PLUGINS_DIR/installed_plugins.json"
PLUGINS_CACHE="$PLUGINS_DIR/cache"
SKILLS_DIR="$CLAUDE_DIR/skills"
AGENTS_DIR="$CLAUDE_DIR/agents"

# ── Cross-platform helpers ──

_mtime() {
    if stat --version &>/dev/null 2>&1; then
        stat -c '%Y' "$1" 2>/dev/null || echo 0
    else
        stat -f '%m' "$1" 2>/dev/null || echo 0
    fi
}

_sed_i() {
    if sed --version &>/dev/null 2>&1; then
        sed -i "$@"
    else
        sed -i '' "$@"
    fi
}

_require_jq() {
    if ! command -v jq &>/dev/null; then
        echo "ERROR: jq is required but not found. Install: brew install jq / apt install jq" >&2
        exit 1
    fi
}

# ── Color output (safe for piped/redirected output) ──

if [[ -t 1 ]]; then
    _C_INFO='\033[0;34m'  _C_OK='\033[0;32m'  _C_WARN='\033[0;33m'
    _C_FAIL='\033[0;31m'  _C_STEP='\033[1;36m' _C_RESET='\033[0m'
else
    _C_INFO='' _C_OK='' _C_WARN='' _C_FAIL='' _C_STEP='' _C_RESET=''
fi

info()  { printf "${_C_INFO}[INFO]${_C_RESET}  %s\n" "$*"; }
ok()    { printf "${_C_OK}  ✅  ${_C_RESET} %s\n" "$*"; }
warn()  { printf "${_C_WARN}  ⚠️  ${_C_RESET} %s\n" "$*"; }
fail()  { printf "${_C_FAIL}  ❌  ${_C_RESET} %s\n" "$*"; }
step()  { printf "\n${_C_STEP}══ %s ══${_C_RESET}\n" "$*"; }

# ── File locking (portable: mkdir-based for atomicity) ──

_lock_acquire() {
    local lockdir="$1" timeout="${2:-10}" waited=0
    while ! mkdir "$lockdir" 2>/dev/null; do
        local lock_pid=""
        [[ -f "$lockdir/pid" ]] && lock_pid=$(<"$lockdir/pid" 2>/dev/null)
        if [[ -n "$lock_pid" ]] && kill -0 "$lock_pid" 2>/dev/null; then
            if (( waited >= timeout )); then
                echo "ERROR: lock held by PID $lock_pid for >${timeout}s" >&2
                return 1
            fi
            sleep 1
            ((waited++))
        else
            # Stale lock — remove and retry
            rm -rf "$lockdir"
        fi
    done
    echo $$ > "$lockdir/pid"
}

_lock_release() {
    local lockdir="$1"
    [[ -d "$lockdir" ]] || return 0
    local lock_pid=""
    [[ -f "$lockdir/pid" ]] && lock_pid=$(<"$lockdir/pid" 2>/dev/null)
    [[ "$lock_pid" == "$$" ]] && rm -rf "$lockdir"
    return 0
}
