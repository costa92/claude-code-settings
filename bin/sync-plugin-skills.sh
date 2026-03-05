#!/usr/bin/env bash
# sync-plugin-skills.sh — sync skills/agents from plugins to ~/.claude/skills/ for Cursor IDE
# Usage:
#   --check   quick mtime check, fork background sync if needed (for .zshrc)
#   --force   full re-sync regardless of timestamps
#   (no args) sync only if installed_plugins.json is newer than manifest
set -euo pipefail

# ── Load common library ──
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"
_require_jq

MANIFEST="$PLUGINS_DIR/.sync-manifest.json"
LOG_FILE="$PLUGINS_DIR/.sync.log"
LOCKFILE="$PLUGINS_DIR/.sync.lock"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }

needs_sync() {
    [[ ! -f "$PLUGINS_JSON" ]] && return 1
    [[ ! -f "$MANIFEST" ]] && return 0
    local src_mtime manifest_mtime
    src_mtime=$(_mtime "$PLUGINS_JSON")
    manifest_mtime=$(_mtime "$MANIFEST")
    [[ "$src_mtime" -gt "$manifest_mtime" ]]
}

# ── --check mode: fork background sync if needed ──
if [[ "${1:-}" == "--check" ]]; then
    if needs_sync; then
        "$0" &
    fi
    exit 0
fi

# ── Normal mode: skip if up-to-date ──
if [[ "${1:-}" != "--force" ]] && ! needs_sync; then
    exit 0
fi

# ── Acquire lock ──
if ! _lock_acquire "$LOCKFILE" 10; then
    log "SKIP: another sync process is running"
    exit 0
fi
trap '_lock_release "$LOCKFILE"' EXIT

# ── Validate inputs ──
if [[ ! -f "$PLUGINS_JSON" ]]; then
    log "ERROR: $PLUGINS_JSON not found"
    exit 1
fi

mkdir -p "$SKILLS_DIR" "$AGENTS_DIR"

# ── Load old manifest (jq, no python3) ──
if [[ -f "$MANIFEST" ]]; then
    OLD_MANIFEST="$MANIFEST"
else
    OLD_MANIFEST="/dev/null"
fi

# ── Collect plugin install paths (jq, bash 3.2 compatible — no associative arrays) ──
PLUGIN_NAMES=()
PLUGIN_INSTALL_PATHS=()

while IFS=$'\t' read -r pname ppath; do
    local_path="${ppath/#\~/$HOME}"
    if [[ -d "$local_path" ]]; then
        PLUGIN_NAMES+=("$pname")
        PLUGIN_INSTALL_PATHS+=("$local_path")
    fi
done < <(jq -r '
    .plugins // {} | to_entries[] |
    select(.value | length > 0) |
    (.key | split("@")[0]) as $name |
    (.value[-1].installPath // "") as $path |
    select($path != "") |
    "\($name)\t\($path)"
' "$PLUGINS_JSON")

ADDED_SKILLS=()
UPDATED_SKILLS=()
ADDED_AGENTS=()
UPDATED_AGENTS=()
SKIPPED_SKILLS=()

# ── Build new manifest as a temp file (single jq call at the end) ──
NEW_SKILLS_JSON="{}"
NEW_AGENTS_JSON="{}"

manifest_has_skill() {
    jq -e --arg k "$1" '.skills[$k] // empty' "$OLD_MANIFEST" &>/dev/null
}

manifest_has_agent() {
    jq -e --arg k "$1" '.agents[$k] // empty' "$OLD_MANIFEST" &>/dev/null
}

sync_skill() {
    local src_dir="$1" skill_name="$2" plugin_name="$3"
    local dest="$SKILLS_DIR/$skill_name"

    if [[ -d "$dest" ]]; then
        if ! manifest_has_skill "$skill_name"; then
            SKIPPED_SKILLS+=("$skill_name")
            return
        fi
        if ! diff -rq "$src_dir" "$dest" &>/dev/null; then
            rm -rf "$dest"
            cp -r "$src_dir" "$dest"
            UPDATED_SKILLS+=("$skill_name")
            log "  UPDATED: skill/$skill_name <- $plugin_name"
        fi
    else
        cp -r "$src_dir" "$dest"
        ADDED_SKILLS+=("$skill_name")
        log "  ADDED: skill/$skill_name <- $plugin_name"
    fi
    NEW_SKILLS_JSON=$(echo "$NEW_SKILLS_JSON" | jq --arg k "$skill_name" --arg p "$plugin_name" --arg s "$src_dir" \
        '.[$k] = {plugin: $p, source: $s}')
}

sync_agent() {
    local src_file="$1" agent_name="$2" plugin_name="$3"
    local dest="$AGENTS_DIR/$agent_name"
    local key="${agent_name%.md}"

    if [[ -f "$dest" ]]; then
        if ! manifest_has_agent "$key"; then
            log "  SKIPPED: agent/$agent_name (user-owned)"
            return
        fi
        if ! diff -q "$src_file" "$dest" &>/dev/null; then
            cp "$src_file" "$dest"
            UPDATED_AGENTS+=("$agent_name")
            log "  UPDATED: agent/$agent_name <- $plugin_name"
        fi
    else
        cp "$src_file" "$dest"
        ADDED_AGENTS+=("$agent_name")
        log "  ADDED: agent/$agent_name <- $plugin_name"
    fi
    NEW_AGENTS_JSON=$(echo "$NEW_AGENTS_JSON" | jq --arg k "$key" --arg p "$plugin_name" --arg s "$src_file" \
        '.[$k] = {plugin: $p, source: $s}')
}

# ── Main sync loop ──
log "=== Plugin Skills Sync Started ==="
log "Detected ${#PLUGIN_NAMES[@]} plugin(s)"

for i in "${!PLUGIN_NAMES[@]}"; do
    plugin_name="${PLUGIN_NAMES[$i]}"
    install_path="${PLUGIN_INSTALL_PATHS[$i]}"
    log "Processing plugin: $plugin_name ($install_path)"

    if [[ -d "$install_path/skills" ]]; then
        for skill_dir in "$install_path/skills"/*/; do
            [[ -d "$skill_dir" ]] || continue
            sync_skill "$skill_dir" "$(basename "$skill_dir")" "$plugin_name"
        done
    fi

    if [[ -d "$install_path/agents" ]]; then
        for agent_file in "$install_path/agents"/*.md; do
            [[ -f "$agent_file" ]] || continue
            sync_agent "$agent_file" "$(basename "$agent_file")" "$plugin_name"
        done
    fi
done

# ── Clean up plugin-sourced skills that no longer exist ──
if [[ -f "$OLD_MANIFEST" && "$OLD_MANIFEST" != "/dev/null" ]]; then
    while IFS= read -r old_skill; do
        [[ -z "$old_skill" ]] && continue
        if ! echo "$NEW_SKILLS_JSON" | jq -e --arg k "$old_skill" '.[$k] // empty' &>/dev/null; then
            if [[ -d "$SKILLS_DIR/$old_skill" ]]; then
                log "  REMOVED: skill/$old_skill (no longer in any plugin)"
                rm -rf "$SKILLS_DIR/$old_skill"
            fi
        fi
    done < <(jq -r '.skills // {} | keys[]' "$OLD_MANIFEST" 2>/dev/null || true)
fi

# ── Write new manifest (single jq call) ──
jq -n --arg ts "$(date -Iseconds)" \
    --argjson skills "$NEW_SKILLS_JSON" \
    --argjson agents "$NEW_AGENTS_JSON" \
    '{synced_at: $ts, skills: $skills, agents: $agents}' > "$MANIFEST"

log "=== Sync Complete ==="
log "Added: ${#ADDED_SKILLS[@]} skills, ${#ADDED_AGENTS[@]} agents | Updated: ${#UPDATED_SKILLS[@]} skills, ${#UPDATED_AGENTS[@]} agents | Skipped: ${#SKIPPED_SKILLS[@]}"

if [[ $(( ${#ADDED_SKILLS[@]} + ${#UPDATED_SKILLS[@]} + ${#ADDED_AGENTS[@]} + ${#UPDATED_AGENTS[@]} )) -gt 0 ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Plugin skills synced: +${#ADDED_SKILLS[@]} ~${#UPDATED_SKILLS[@]} skills, +${#ADDED_AGENTS[@]} ~${#UPDATED_AGENTS[@]} agents" | tee -a "$LOG_FILE"
fi
