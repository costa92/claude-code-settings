#!/usr/bin/env bash
# sync-superpowers.sh - 从 obra/superpowers 上游同步最新内容
# 用法: ./sync-superpowers.sh [--check]
#   --check  只检查差异，不更新文件

set -euo pipefail

UPSTREAM_BASE="https://raw.githubusercontent.com/obra/superpowers/main"
CHECK_ONLY=false

# 动态检测 Claude 配置目录（优先 CLAUDE_CONFIG_DIR 环境变量，回退到 ~/.claude）
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
PLUGIN_DIR="$CLAUDE_DIR/plugins/cache/superpowers-marketplace/superpowers"

[[ "${1:-}" == "--check" ]] && CHECK_ONLY=true

# 自动检测已安装的版本目录
VERSION_DIR=$(ls -d "$PLUGIN_DIR"/*/ 2>/dev/null | sort -V | tail -1)
if [[ -z "$VERSION_DIR" ]]; then
  echo "错误：找不到 superpowers 插件目录" >&2
  exit 1
fi

PLUGIN_ROOT="${VERSION_DIR%/}"
TMPFILE=$(mktemp)
trap "rm -f $TMPFILE" EXIT

echo "插件目录：$PLUGIN_ROOT"
echo ""

total_updated=0
total_unchanged=0
total_new=0

# ── 通用文件同步函数 ─────────────────────────────────────────────────────────
sync_file() {
  local remote_path="$1"   # 相对于 GitHub 仓库根的路径
  local local_file="$2"    # 本地完整路径
  local executable="${3:-false}"

  curl -s "$UPSTREAM_BASE/$remote_path" > "$TMPFILE"

  # 跳过 404 响应（GitHub 返回 "404: Not Found"）
  if grep -q "^404: Not Found" "$TMPFILE" 2>/dev/null; then
    return
  fi

  if [[ ! -f "$local_file" ]]; then
    echo "  [NEW]     $remote_path"
    if [[ "$CHECK_ONLY" == false ]]; then
      mkdir -p "$(dirname "$local_file")"
      cp "$TMPFILE" "$local_file"
      [[ "$executable" == true ]] && chmod +x "$local_file"
    fi
    ((total_new++)) || true
    return
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

# ── Skills ───────────────────────────────────────────────────────────────────
echo "=== Skills ==="
SKILLS=$(curl -s "https://api.github.com/repos/obra/superpowers/contents/skills" \
  | python3 -c "import sys,json; [print(d['name']) for d in json.load(sys.stdin) if d['type']=='dir']" 2>/dev/null)

if [[ -z "$SKILLS" ]]; then
  echo "错误：无法从 GitHub 获取 skill 列表（检查网络连接）" >&2
  exit 1
fi

for skill in $SKILLS; do
  sync_file "skills/$skill/SKILL.md" "$PLUGIN_ROOT/skills/$skill/SKILL.md"
done

# ── Agents ───────────────────────────────────────────────────────────────────
echo ""
echo "=== Agents ==="
AGENTS=$(curl -s "https://api.github.com/repos/obra/superpowers/contents/agents" \
  | python3 -c "import sys,json; [print(d['name']) for d in json.load(sys.stdin) if d['type']=='file']" 2>/dev/null)

for agent in $AGENTS; do
  sync_file "agents/$agent" "$PLUGIN_ROOT/agents/$agent"
done

# ── Commands ─────────────────────────────────────────────────────────────────
echo ""
echo "=== Commands ==="
COMMANDS=$(curl -s "https://api.github.com/repos/obra/superpowers/contents/commands" \
  | python3 -c "import sys,json; [print(d['name']) for d in json.load(sys.stdin) if d['type']=='file']" 2>/dev/null)

for cmd in $COMMANDS; do
  sync_file "commands/$cmd" "$PLUGIN_ROOT/commands/$cmd"
done

# ── Hooks ────────────────────────────────────────────────────────────────────
echo ""
echo "=== Hooks ==="
HOOK_FILES=$(curl -s "https://api.github.com/repos/obra/superpowers/contents/hooks" \
  | python3 -c "import sys,json; [print(d['name']) for d in json.load(sys.stdin) if d['type']=='file']" 2>/dev/null)

for hf in $HOOK_FILES; do
  # 判断是否需要可执行权限（非 .json 文件）
  is_exec=false
  [[ "$hf" != *.json ]] && is_exec=true
  sync_file "hooks/$hf" "$PLUGIN_ROOT/hooks/$hf" "$is_exec"
done

# ── Lib ──────────────────────────────────────────────────────────────────────
echo ""
echo "=== Lib ==="
LIB_FILES=$(curl -s "https://api.github.com/repos/obra/superpowers/contents/lib" \
  | python3 -c "import sys,json; [print(d['name']) for d in json.load(sys.stdin) if d['type']=='file']" 2>/dev/null)

for lf in $LIB_FILES; do
  sync_file "lib/$lf" "$PLUGIN_ROOT/lib/$lf"
done

# ── 设置验证 ──────────────────────────────────────────────────────────────────
echo ""
echo "=== Settings 验证 ==="

SETTINGS_FILE="$CLAUDE_DIR/settings.json"
PLUGIN_KEY="superpowers@superpowers-marketplace"
INSTALLED_JSON="$CLAUDE_DIR/plugins/installed_plugins.json"

# 检查 enabledPlugins 是否包含 superpowers
if python3 -c "
import json, sys
with open('$SETTINGS_FILE') as f: s = json.load(f)
enabled = s.get('enabledPlugins', {})
sys.exit(0 if enabled.get('$PLUGIN_KEY') else 1)
" 2>/dev/null; then
  echo "  [OK]      enabledPlugins.$PLUGIN_KEY = true"
else
  echo "  [WARN]    enabledPlugins 未包含 $PLUGIN_KEY"
  if [[ "$CHECK_ONLY" == false ]]; then
    python3 - "$SETTINGS_FILE" "$PLUGIN_KEY" <<'PYEOF'
import json, sys
path, key = sys.argv[1], sys.argv[2]
with open(path) as f: s = json.load(f)
s.setdefault("enabledPlugins", {})[key] = True
with open(path, "w") as f: json.dump(s, f, indent=2, ensure_ascii=False)
print(f"  [FIXED]   已将 {key} 写入 enabledPlugins")
PYEOF
  fi
fi

# 检查 installed_plugins.json 版本是否与实际目录一致
ACTUAL_VERSION=$(ls -d "$PLUGIN_DIR"/*/ 2>/dev/null | sort -V | tail -1 | xargs basename)
RECORDED_VERSION=$(python3 -c "
import json
with open('$INSTALLED_JSON') as f: p = json.load(f)
entries = p.get('plugins', {}).get('$PLUGIN_KEY', [])
print(entries[0]['version'] if entries else '')
" 2>/dev/null)

if [[ "$ACTUAL_VERSION" == "$RECORDED_VERSION" ]]; then
  echo "  [OK]      installed_plugins.json 版本 = $ACTUAL_VERSION"
else
  echo "  [WARN]    版本不一致：installed_plugins.json=$RECORDED_VERSION，实际目录=$ACTUAL_VERSION"
  if [[ "$CHECK_ONLY" == false ]]; then
    python3 - "$INSTALLED_JSON" "$PLUGIN_KEY" "$ACTUAL_VERSION" <<'PYEOF'
import json, sys
path, key, ver = sys.argv[1], sys.argv[2], sys.argv[3]
with open(path) as f: p = json.load(f)
entries = p.get("plugins", {}).get(key, [])
if entries:
    entries[0]["version"] = ver
    entries[0]["installPath"] = entries[0]["installPath"].rsplit("/", 1)[0] + "/" + ver
    from datetime import datetime, timezone
    entries[0]["lastUpdated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
with open(path, "w") as f: json.dump(p, f, indent=2, ensure_ascii=False)
print(f"  [FIXED]   版本已更新为 {ver}")
PYEOF
  fi
fi

# 检查 SessionStart hook 是否注册（指向 wrapper 脚本）
WRAPPER_SCRIPT="$CLAUDE_DIR/hooks/superpowers-session-start.sh"
WRAPPER_REF="~/.claude/hooks/superpowers-session-start.sh"

if python3 -c "
import json, sys
with open('$SETTINGS_FILE') as f: s = json.load(f)
hooks = s.get('hooks', {}).get('SessionStart', [])
cmds = [h.get('command','') for g in hooks for h in g.get('hooks',[])]
sys.exit(0 if any('superpowers-session-start' in c for c in cmds) else 1)
" 2>/dev/null; then
  echo "  [OK]      SessionStart hook → wrapper 脚本"
else
  echo "  [WARN]    settings.json 未注册 SessionStart hook"
  if [[ "$CHECK_ONLY" == false ]]; then
    python3 - "$SETTINGS_FILE" "$WRAPPER_REF" <<'PYEOF'
import json, sys
path, wrapper = sys.argv[1], sys.argv[2]
with open(path) as f: s = json.load(f)
# 移除旧的硬编码 hook（如有）
for group in s.get("hooks", {}).get("SessionStart", []):
    group["hooks"] = [h for h in group.get("hooks", []) if "run-hook.cmd" not in h.get("command", "")]
hook_entry = {"hooks": [{"type": "command", "command": wrapper, "async": False}]}
s.setdefault("hooks", {}).setdefault("SessionStart", [])
cmds = [h.get("command","") for g in s["hooks"]["SessionStart"] for h in g.get("hooks",[])]
if not any("superpowers-session-start" in c for c in cmds):
    s["hooks"]["SessionStart"].append(hook_entry)
with open(path, "w") as f: json.dump(s, f, indent=2, ensure_ascii=False)
print(f"  [FIXED]   已写入 SessionStart hook → {wrapper}")
PYEOF
  fi
fi

# 确保 wrapper 脚本存在且可执行
if [[ -f "$WRAPPER_SCRIPT" ]]; then
  echo "  [OK]      wrapper 脚本存在: $WRAPPER_SCRIPT"
else
  echo "  [WARN]    wrapper 脚本不存在，将创建"
  if [[ "$CHECK_ONLY" == false ]]; then
    mkdir -p "$(dirname "$WRAPPER_SCRIPT")"
    cat > "$WRAPPER_SCRIPT" <<'WRAPPER'
#!/usr/bin/env bash
# 动态定位最新 superpowers 版本并转发 session-start hook
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
PLUGIN_DIR="$CLAUDE_DIR/plugins/cache/superpowers-marketplace/superpowers"
LATEST=$(ls -d "$PLUGIN_DIR"/*/ 2>/dev/null | sort -V | tail -1)
[[ -z "$LATEST" ]] && exit 0
export CLAUDE_PLUGIN_ROOT="${LATEST%/}"
exec bash "$CLAUDE_PLUGIN_ROOT/hooks/run-hook.cmd" session-start
WRAPPER
    chmod +x "$WRAPPER_SCRIPT"
    echo "  [FIXED]   wrapper 脚本已创建"
  fi
fi

# ── 汇总 ─────────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════"
echo "结果：${total_unchanged} 个无变化，${total_updated} 个已更新，${total_new} 个新增"

if [[ "$CHECK_ONLY" == true && $((total_updated + total_new)) -gt 0 ]]; then
  echo "（使用不带 --check 参数重新运行以应用更新）"
fi
