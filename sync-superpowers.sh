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

# ── 汇总 ─────────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════"
echo "结果：${total_unchanged} 个无变化，${total_updated} 个已更新，${total_new} 个新增"

if [[ "$CHECK_ONLY" == true && $((total_updated + total_new)) -gt 0 ]]; then
  echo "（使用不带 --check 参数重新运行以应用更新）"
fi
