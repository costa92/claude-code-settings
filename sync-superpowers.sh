#!/usr/bin/env bash
# sync-superpowers.sh — sync latest content from obra/superpowers upstream
# Usage: ./sync-superpowers.sh [--check]
#   --check  dry-run: show diffs without applying changes
set -euo pipefail

# ── Load common library ──
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"
_require_jq

UPSTREAM_BASE="https://raw.githubusercontent.com/obra/superpowers/main"
GITHUB_API="https://api.github.com/repos/obra/superpowers/contents"
CHECK_ONLY=false
[[ "${1:-}" == "--check" ]] && CHECK_ONLY=true

# Resolve superpowers plugin directory (direct path or cache path)
if [[ -d "$PLUGINS_DIR/superpowers" ]]; then
    PLUGIN_ROOT="$PLUGINS_DIR/superpowers"
elif [[ -d "$PLUGINS_CACHE/superpowers-marketplace/superpowers" ]]; then
    # Fallback: find latest version in cache
    PLUGIN_ROOT=$(ls -d "$PLUGINS_CACHE/superpowers-marketplace/superpowers"/*/ 2>/dev/null | sort -V | tail -1)
    PLUGIN_ROOT="${PLUGIN_ROOT%/}"
fi

if [[ -z "${PLUGIN_ROOT:-}" || ! -d "${PLUGIN_ROOT:-}" ]]; then
    fail "找不到 superpowers 插件目录"
    exit 1
fi
TMPFILE=$(mktemp)
trap "rm -f '$TMPFILE'" EXIT

echo "插件目录：$PLUGIN_ROOT"
echo ""

total_updated=0
total_unchanged=0
total_new=0

# ── GitHub API helper with rate limit handling ──
github_api_get() {
    local url="$1"
    local response
    response=$(curl -s -w '\n%{http_code}' "$url")
    local http_code
    http_code=$(echo "$response" | tail -1)
    local body
    body=$(echo "$response" | sed '$d')

    if [[ "$http_code" == "403" ]]; then
        if echo "$body" | jq -e '.message | test("rate limit")' &>/dev/null; then
            local reset_at
            reset_at=$(curl -sI "$url" | grep -i 'x-ratelimit-reset' | tr -d '\r' | awk '{print $2}')
            if [[ -n "$reset_at" ]]; then
                local now reset_in
                now=$(date +%s)
                reset_in=$(( reset_at - now ))
                (( reset_in < 0 )) && reset_in=0
                warn "GitHub API rate limit exceeded. Resets in ${reset_in}s."
            else
                warn "GitHub API rate limit exceeded."
            fi
            warn "Tip: set GITHUB_TOKEN env var to increase limit (5000/hr)."
            return 1
        fi
    fi

    if [[ "$http_code" != "200" ]]; then
        warn "GitHub API returned HTTP $http_code for $url"
        return 1
    fi

    echo "$body"
}

# ── Generic file sync function ──
sync_file() {
    local remote_path="$1"
    local local_file="$2"
    local executable="${3:-false}"

    curl -sf "$UPSTREAM_BASE/$remote_path" > "$TMPFILE" 2>/dev/null || {
        return 0
    }

    # Skip 404 responses
    if [[ ! -s "$TMPFILE" ]] || grep -q "^404: Not Found" "$TMPFILE" 2>/dev/null; then
        return 0
    fi

    if [[ ! -f "$local_file" ]]; then
        echo "  [NEW]     $remote_path"
        if [[ "$CHECK_ONLY" == false ]]; then
            mkdir -p "$(dirname "$local_file")"
            cp "$TMPFILE" "$local_file"
            [[ "$executable" == true ]] && chmod +x "$local_file"
        fi
        ((total_new++)) || true
        return 0
    fi

    if ! diff -q "$TMPFILE" "$local_file" > /dev/null 2>&1; then
        local gh_lines lo_lines
        gh_lines=$(wc -l < "$TMPFILE")
        lo_lines=$(wc -l < "$local_file")
        echo "  [UPDATE]  $remote_path  (本地 ${lo_lines}行 → GitHub ${gh_lines}行)"
        if [[ "$CHECK_ONLY" == false ]]; then
            cp "$TMPFILE" "$local_file"
            [[ "$executable" == true ]] && chmod +x "$local_file"
        fi
        ((total_updated++)) || true
    else
        echo "  [OK]      $remote_path"
        ((total_unchanged++)) || true
    fi
}

# ── Recursive directory listing from GitHub API ──
github_list_files() {
    local api_path="$1"
    local response
    response=$(github_api_get "$GITHUB_API/$api_path") || return 1
    echo "$response" | jq -r '.[] | "\(.type)\t\(.name)"' 2>/dev/null
}

# ── Skills: sync ALL files in each skill directory ──
echo "=== Skills ==="
SKILLS_LIST=$(github_api_get "$GITHUB_API/skills") || {
    fail "无法从 GitHub 获取 skill 列表（检查网络连接）"
    exit 1
}

SKILL_DIRS=$(echo "$SKILLS_LIST" | jq -r '.[] | select(.type=="dir") | .name' 2>/dev/null)
if [[ -z "$SKILL_DIRS" ]]; then
    fail "无法解析 skill 列表"
    exit 1
fi

for skill in $SKILL_DIRS; do
    SKILL_FILES=$(github_api_get "$GITHUB_API/skills/$skill") || continue
    FILE_LIST=$(echo "$SKILL_FILES" | jq -r '.[] | select(.type=="file") | .name' 2>/dev/null)
    for fname in $FILE_LIST; do
        sync_file "skills/$skill/$fname" "$PLUGIN_ROOT/skills/$skill/$fname"
    done
    # Handle one level of subdirectories (e.g., skills/writing-skills/examples/)
    SUB_DIRS=$(echo "$SKILL_FILES" | jq -r '.[] | select(.type=="dir") | .name' 2>/dev/null)
    for subdir in $SUB_DIRS; do
        SUB_FILES=$(github_api_get "$GITHUB_API/skills/$skill/$subdir") || continue
        SUB_FILE_LIST=$(echo "$SUB_FILES" | jq -r '.[] | select(.type=="file") | .name' 2>/dev/null)
        for sf in $SUB_FILE_LIST; do
            sync_file "skills/$skill/$subdir/$sf" "$PLUGIN_ROOT/skills/$skill/$subdir/$sf"
        done
    done
done

# ── Agents ──
echo ""
echo "=== Agents ==="
AGENTS_LIST=$(github_api_get "$GITHUB_API/agents") || { warn "无法获取 agents 列表"; AGENTS_LIST=""; }
if [[ -n "$AGENTS_LIST" ]]; then
    AGENT_FILES=$(echo "$AGENTS_LIST" | jq -r '.[] | select(.type=="file") | .name' 2>/dev/null)
    for agent in $AGENT_FILES; do
        sync_file "agents/$agent" "$PLUGIN_ROOT/agents/$agent"
    done
fi

# ── Commands ──
echo ""
echo "=== Commands ==="
COMMANDS_LIST=$(github_api_get "$GITHUB_API/commands") || { warn "无法获取 commands 列表"; COMMANDS_LIST=""; }
if [[ -n "$COMMANDS_LIST" ]]; then
    CMD_FILES=$(echo "$COMMANDS_LIST" | jq -r '.[] | select(.type=="file") | .name' 2>/dev/null)
    for cmd in $CMD_FILES; do
        sync_file "commands/$cmd" "$PLUGIN_ROOT/commands/$cmd"
    done
fi

# ── Hooks ──
echo ""
echo "=== Hooks ==="
HOOKS_LIST=$(github_api_get "$GITHUB_API/hooks") || { warn "无法获取 hooks 列表"; HOOKS_LIST=""; }
if [[ -n "$HOOKS_LIST" ]]; then
    HOOK_FILES=$(echo "$HOOKS_LIST" | jq -r '.[] | select(.type=="file") | .name' 2>/dev/null)
    for hf in $HOOK_FILES; do
        is_exec=false
        [[ "$hf" != *.json ]] && is_exec=true
        sync_file "hooks/$hf" "$PLUGIN_ROOT/hooks/$hf" "$is_exec"
    done
fi

# ── Lib ──
echo ""
echo "=== Lib ==="
LIB_LIST=$(github_api_get "$GITHUB_API/lib") || { warn "无法获取 lib 列表"; LIB_LIST=""; }
if [[ -n "$LIB_LIST" ]]; then
    LIB_FILES=$(echo "$LIB_LIST" | jq -r '.[] | select(.type=="file") | .name' 2>/dev/null)
    for lf in $LIB_FILES; do
        sync_file "lib/$lf" "$PLUGIN_ROOT/lib/$lf"
    done
fi

# ── Settings validation (using jq, no python3 injection) ──
echo ""
echo "=== Settings 验证 ==="

SETTINGS_FILE="$CLAUDE_DIR/settings.json"
PLUGIN_KEY="superpowers@superpowers-marketplace"
INSTALLED_JSON="$PLUGINS_JSON"

# Check enabledPlugins
if [[ -f "$SETTINGS_FILE" ]] && jq -e --arg k "$PLUGIN_KEY" '.enabledPlugins[$k] // false' "$SETTINGS_FILE" &>/dev/null; then
    echo "  [OK]      enabledPlugins.$PLUGIN_KEY = true"
else
    echo "  [WARN]    enabledPlugins 未包含 $PLUGIN_KEY"
    if [[ "$CHECK_ONLY" == false && -f "$SETTINGS_FILE" ]]; then
        jq --arg k "$PLUGIN_KEY" '.enabledPlugins[$k] = true' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp" \
            && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
        echo "  [FIXED]   已将 $PLUGIN_KEY 写入 enabledPlugins"
    fi
fi

# Check installed_plugins.json version consistency
ACTUAL_VERSION=$(ls -d "$PLUGIN_DIR"/*/ 2>/dev/null | sort -V | tail -1 | xargs basename)
RECORDED_VERSION=""
if [[ -f "$INSTALLED_JSON" ]]; then
    RECORDED_VERSION=$(jq -r --arg k "$PLUGIN_KEY" '.plugins[$k][-1].version // ""' "$INSTALLED_JSON")
fi

if [[ "$ACTUAL_VERSION" == "$RECORDED_VERSION" ]]; then
    echo "  [OK]      installed_plugins.json 版本 = $ACTUAL_VERSION"
elif [[ -n "$ACTUAL_VERSION" && -n "$RECORDED_VERSION" ]]; then
    echo "  [WARN]    版本不一致：installed_plugins.json=$RECORDED_VERSION，实际目录=$ACTUAL_VERSION"
    if [[ "$CHECK_ONLY" == false && -f "$INSTALLED_JSON" ]]; then
        NOW_UTC=$(date -u +%Y-%m-%dT%H:%M:%S.000Z)
        jq --arg k "$PLUGIN_KEY" --arg ver "$ACTUAL_VERSION" --arg ts "$NOW_UTC" '
            .plugins[$k][-1].version = $ver |
            .plugins[$k][-1].installPath = (.plugins[$k][-1].installPath | split("/")[:-1] | join("/")) + "/" + $ver |
            .plugins[$k][-1].lastUpdated = $ts
        ' "$INSTALLED_JSON" > "$INSTALLED_JSON.tmp" && mv "$INSTALLED_JSON.tmp" "$INSTALLED_JSON"
        echo "  [FIXED]   版本已更新为 $ACTUAL_VERSION"
    fi
fi

# Check SessionStart hook
if [[ -f "$SETTINGS_FILE" ]] && jq -e '
    .hooks.SessionStart // [] | [.[].hooks[]?.command // ""] |
    any(test("superpowers-session-start"))
' "$SETTINGS_FILE" &>/dev/null; then
    echo "  [OK]      SessionStart hook → wrapper 脚本"
else
    echo "  [WARN]    settings.json 未注册 SessionStart hook"
    if [[ "$CHECK_ONLY" == false && -f "$SETTINGS_FILE" ]]; then
        WRAPPER_REF="~/.claude/hooks/superpowers-session-start.sh"
        jq --arg cmd "$WRAPPER_REF" '
            .hooks.SessionStart = (.hooks.SessionStart // []) +
            [{"hooks": [{"type": "command", "command": $cmd, "async": false}]}]
        ' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
        echo "  [FIXED]   已写入 SessionStart hook → $WRAPPER_REF"
    fi
fi

# Ensure wrapper script exists
WRAPPER_SCRIPT="$CLAUDE_DIR/hooks/superpowers-session-start.sh"
if [[ -f "$WRAPPER_SCRIPT" ]]; then
    echo "  [OK]      wrapper 脚本存在: $WRAPPER_SCRIPT"
else
    echo "  [WARN]    wrapper 脚本不存在，将创建"
    if [[ "$CHECK_ONLY" == false ]]; then
        mkdir -p "$(dirname "$WRAPPER_SCRIPT")"
        cat > "$WRAPPER_SCRIPT" <<'WRAPPER'
#!/usr/bin/env bash
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
PLUGIN_DIR="$CLAUDE_DIR/plugins/superpowers"
[[ ! -d "$PLUGIN_DIR" ]] && exit 0
export CLAUDE_PLUGIN_ROOT="$PLUGIN_DIR"
exec bash "$CLAUDE_PLUGIN_ROOT/hooks/run-hook.cmd" session-start
WRAPPER
        chmod +x "$WRAPPER_SCRIPT"
        echo "  [FIXED]   wrapper 脚本已创建"
    fi
fi

# ── Summary ──
echo ""
echo "════════════════════════════════"
echo "结果：${total_unchanged} 个无变化，${total_updated} 个已更新，${total_new} 个新增"

if [[ "$CHECK_ONLY" == true && $((total_updated + total_new)) -gt 0 ]]; then
    echo "（使用不带 --check 参数重新运行以应用更新）"
fi

# ── Trigger plugin→skills sync for Cursor IDE ──
SYNC_SCRIPT="$CLAUDE_DIR/bin/sync-plugin-skills.sh"
if [[ "$CHECK_ONLY" == false && $((total_updated + total_new)) -gt 0 && -x "$SYNC_SCRIPT" ]]; then
    echo ""
    echo "=== 同步到 ~/.claude/skills/ (Cursor IDE) ==="
    "$SYNC_SCRIPT" --force
fi
