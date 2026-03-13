#!/usr/bin/env bash
# sync-superpowers.sh — sync latest content from obra/superpowers upstream (ZIP version)
set -euo pipefail

# ── Load common library ──
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"
_require_jq

UPSTREAM_ZIP="https://github.com/obra/superpowers/archive/refs/heads/main.zip"
CHECK_ONLY=false
[[ "${1:-}" == "--check" ]] && CHECK_ONLY=true

# Resolve superpowers plugin directory
if [[ -d "$PLUGINS_DIR/superpowers" ]]; then
    PLUGIN_ROOT="$PLUGINS_DIR/superpowers"
elif [[ -d "$PLUGINS_CACHE/superpowers-marketplace/superpowers" ]]; then
    PLUGIN_ROOT=$(ls -d "$PLUGINS_CACHE/superpowers-marketplace/superpowers"/*/ 2>/dev/null | sort -V | tail -1)
    PLUGIN_ROOT="${PLUGIN_ROOT%/}"
fi

if [[ -z "${PLUGIN_ROOT:-}" || ! -d "${PLUGIN_ROOT:-}" ]]; then
    fail "找不到 superpowers 插件目录"
    exit 1
fi

TMP_DIR=$(mktemp -d)
trap "rm -rf '$TMP_DIR'" EXIT

echo "插件目录：$PLUGIN_ROOT"
echo "正在从 GitHub 下载最新版本..."

if ! curl -sL "$UPSTREAM_ZIP" -o "$TMP_DIR/main.zip"; then
    fail "下载失败，请检查网络连接"
    exit 1
fi

unzip -q "$TMP_DIR/main.zip" -d "$TMP_DIR"
# Find the actual directory created by unzip (usually the only directory there)
SRC_DIR=$(find "$TMP_DIR" -maxdepth 1 -type d -not -path "$TMP_DIR" | head -n 1)

if [[ -z "$SRC_DIR" || ! -d "$SRC_DIR" ]]; then
    fail "解压失败或未找到源目录"
    exit 1
fi

total_updated=0
total_unchanged=0
total_new=0

sync_dir() {
    local sub_dir="$1"
    local src="$SRC_DIR/$sub_dir"
    local dest="$PLUGIN_ROOT/$sub_dir"

    [[ ! -d "$src" ]] && return 0
    mkdir -p "$dest"

    while read -r src_file; do
        local rel_path="${src_file#$src/}"
        local dest_file="$dest/$rel_path"
        
        if [[ ! -f "$dest_file" ]]; then
            echo "  [NEW]     $sub_dir/$rel_path"
            if [[ "$CHECK_ONLY" == false ]]; then
                mkdir -p "$(dirname "$dest_file")"
                cp "$src_file" "$dest_file"
                # Keep executable bit for hooks
                [[ "$sub_dir" == "hooks" ]] && [[ "$rel_path" != *.json ]] && chmod +x "$dest_file"
            fi
            total_new=$((total_new + 1))
        elif ! diff -q "$src_file" "$dest_file" >/dev/null 2>&1; then
            echo "  [UPDATE]  $sub_dir/$rel_path"
            if [[ "$CHECK_ONLY" == false ]]; then
                cp "$src_file" "$dest_file"
                [[ "$sub_dir" == "hooks" ]] && [[ "$rel_path" != *.json ]] && chmod +x "$dest_file"
            fi
            total_updated=$((total_updated + 1))
        else
            total_unchanged=$((total_unchanged + 1))
        fi
    done < <(find "$src" -type f)
}

echo "=== 同步目录 ==="
for d in skills agents commands hooks .claude-plugin; do
    sync_dir "$d"
done

# ── Settings validation ──
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

# Check version consistency
ACTUAL_VERSION=""
[[ -f "$PLUGIN_ROOT/.claude-plugin/plugin.json" ]] && ACTUAL_VERSION=$(jq -r '.version // ""' "$PLUGIN_ROOT/.claude-plugin/plugin.json" 2>/dev/null)
[[ -z "$ACTUAL_VERSION" || "$ACTUAL_VERSION" == "null" ]] && ACTUAL_VERSION=$(basename "$PLUGIN_ROOT")

if [[ -f "$INSTALLED_JSON" ]]; then
    RECORDED_VERSION=$(jq -r --arg k "$PLUGIN_KEY" '.plugins[$k][-1].version // ""' "$INSTALLED_JSON")
    if [[ "$ACTUAL_VERSION" != "$RECORDED_VERSION" ]]; then
        echo "  [WARN]    版本不一致：json=$RECORDED_VERSION, 实际=$ACTUAL_VERSION"
        if [[ "$CHECK_ONLY" == false ]]; then
            NOW_UTC=$(date -u +%Y-%m-%dT%H:%M:%S.000Z)
            # Use the actual PLUGIN_ROOT (resolved to absolute path, with ~ replaced by $HOME)
            ABS_PLUGIN_ROOT="${PLUGIN_ROOT/#\~/$HOME}"
            jq --arg k "$PLUGIN_KEY" --arg ver "$ACTUAL_VERSION" --arg ts "$NOW_UTC" --arg path "$PLUGIN_ROOT" '
                .plugins[$k][-1].version = $ver |
                .plugins[$k][-1].installPath = $path |
                .plugins[$k][-1].lastUpdated = $ts
            ' "$INSTALLED_JSON" > "$INSTALLED_JSON.tmp" && mv "$INSTALLED_JSON.tmp" "$INSTALLED_JSON"
            echo "  [FIXED]   版本和路径已同步为 $ACTUAL_VERSION ($PLUGIN_ROOT)"
        fi
    else
        echo "  [OK]      版本一致 ($ACTUAL_VERSION)"
    fi
fi

# Check SessionStart hook
if [[ -f "$SETTINGS_FILE" ]] && jq -e '.hooks.SessionStart // [] | [.[].hooks[]?.command // ""] | any(test("superpowers-session-start"))' "$SETTINGS_FILE" &>/dev/null; then
    echo "  [OK]      SessionStart hook 已配置"
else
    echo "  [WARN]    SessionStart hook 未注册"
    if [[ "$CHECK_ONLY" == false && -f "$SETTINGS_FILE" ]]; then
        WRAPPER_REF="~/.claude/hooks/superpowers-session-start.sh"
        jq --arg cmd "$WRAPPER_REF" '.hooks.SessionStart = (.hooks.SessionStart // []) + [{"hooks": [{"type": "command", "command": $cmd, "async": false}]}]' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
        echo "  [FIXED]   已写入 SessionStart hook"
    fi
fi

echo ""
echo "════════════════════════════════"
echo "结果：${total_unchanged} 个无变化，${total_updated} 个已更新，${total_new} 个新增"

# Trigger sync to Cursor IDE
SYNC_SCRIPT="$CLAUDE_DIR/bin/sync-plugin-skills.sh"
if [[ "$CHECK_ONLY" == false && $((total_updated + total_new)) -gt 0 && -x "$SYNC_SCRIPT" ]]; then
    echo ""
    echo "=== 同步到 ~/.claude/skills/ (Cursor IDE) ==="
    "$SYNC_SCRIPT" --force
fi
