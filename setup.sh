#!/usr/bin/env bash
# =============================================================================
# setup.sh — 跨机器一键初始化 ~/.claude/ 插件系统
#
# 用途：git pull 后重建被 .gitignore 排除的 settings.json、marketplace、cache 等
# 幂等：重复运行安全，不会覆盖已有配置
# =============================================================================

set -eo pipefail

CLAUDE_DIR="$HOME/.claude"
PLUGINS_DIR="$CLAUDE_DIR/plugins"
MARKETPLACES_DIR="$PLUGINS_DIR/marketplaces"
CACHE_DIR="$PLUGINS_DIR/cache"
KNOWN_MP_FILE="$PLUGINS_DIR/known_marketplaces.json"

# --- Flags ---
FORCE=false
SKIP_PYTHON=false
for arg in "$@"; do
  case "$arg" in
    --force)       FORCE=true ;;
    --skip-python) SKIP_PYTHON=true ;;
    --help|-h)
      echo "Usage: ./setup.sh [--force] [--skip-python]"
      echo "  --force        强制重建 plugin cache（即使已存在）"
      echo "  --skip-python  跳过 Python 依赖安装"
      exit 0
      ;;
    *) echo "Unknown option: $arg"; exit 1 ;;
  esac
done

# --- Color helpers ---
info()  { printf '\033[0;34m[INFO]\033[0m  %s\n' "$*"; }
ok()    { printf '\033[0;32m  ✅  \033[0m %s\n' "$*"; }
warn()  { printf '\033[0;33m  ⚠️  \033[0m %s\n' "$*"; }
fail()  { printf '\033[0;31m  ❌  \033[0m %s\n' "$*"; }
step()  { printf '\n\033[1;36m══ %s ══\033[0m\n' "$*"; }

# =========================================================================
# Step 1: 环境检测
# =========================================================================
step "Step 1/6: 环境检测"

OS="$(uname -s)"
case "$OS" in
  Darwin) info "macOS detected" ;;
  Linux)  info "Linux detected" ;;
  *)      warn "Unknown OS: $OS — 脚本可能无法完全工作" ;;
esac

MISSING_TOOLS=""
for tool in git jq; do
  if command -v "$tool" &>/dev/null; then
    ok "$tool $(command -v "$tool")"
  else
    MISSING_TOOLS="$MISSING_TOOLS $tool"
    fail "$tool not found"
  fi
done

# python3 is optional (for pip deps) but worth checking
if command -v python3 &>/dev/null; then
  ok "python3 $(python3 --version 2>&1)"
else
  warn "python3 not found — Python 依赖安装将跳过"
  SKIP_PYTHON=true
fi

if [[ -n "$MISSING_TOOLS" ]]; then
  echo ""
  fail "缺少必要工具:$MISSING_TOOLS"
  if [[ "$OS" == "Darwin" ]]; then
    echo "    brew install$MISSING_TOOLS"
  else
    echo "    sudo apt install$MISSING_TOOLS"
  fi
  exit 1
fi

# =========================================================================
# Step 2: settings.json 初始化
# =========================================================================
step "Step 2/6: settings.json"

SETTINGS_FILE="$CLAUDE_DIR/settings.json"
SETTINGS_EXAMPLE="$CLAUDE_DIR/settings.json.example"

if [[ -f "$SETTINGS_FILE" ]]; then
  ok "settings.json 已存在，跳过（不覆盖用户配置）"
else
  if [[ ! -f "$SETTINGS_EXAMPLE" ]]; then
    fail "settings.json.example 不存在，无法创建 settings.json"
    exit 1
  fi

  # Copy template
  cp "$SETTINGS_EXAMPLE" "$SETTINGS_FILE"
  info "已从 settings.json.example 复制模板"

  # Interactive: ask for env vars
  echo ""
  read -rp "  ANTHROPIC_AUTH_TOKEN (留空跳过): " AUTH_TOKEN
  read -rp "  ANTHROPIC_BASE_URL  (留空使用默认 https://api.anthropic.com): " BASE_URL

  if [[ -n "${AUTH_TOKEN:-}" ]]; then
    jq --arg token "$AUTH_TOKEN" '.env.ANTHROPIC_AUTH_TOKEN = $token' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp" \
      && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
  fi
  if [[ -n "${BASE_URL:-}" ]]; then
    jq --arg url "$BASE_URL" '.env.ANTHROPIC_BASE_URL = $url' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp" \
      && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"
  fi

  # Write enabledPlugins
  jq '.enabledPlugins = {
    "n8n-mcp-skills@n8n-mcp-skills": true,
    "superpowers@superpowers-marketplace": true,
    "ralph-wiggum@claude-code-plugins": true,
    "kiro-skill@claude-code-settings": true
  }' "$SETTINGS_FILE" > "$SETTINGS_FILE.tmp" && mv "$SETTINGS_FILE.tmp" "$SETTINGS_FILE"

  ok "settings.json 创建完成"
fi

# =========================================================================
# Step 3: Marketplace 仓库克隆 / 更新
# =========================================================================
step "Step 3/6: Marketplace 仓库"

mkdir -p "$MARKETPLACES_DIR"

# Marketplace definitions (bash 3.2 compatible — no associative arrays)
# Format: "local_name|github_owner/repo"
MARKETPLACES="
n8n-mcp-skills|czlonkowski/n8n-skills
claude-code-plugins|anthropics/claude-code
md2wechat-tools|geekjourneyx/md2wechat-skill
superpowers-marketplace|obra/superpowers-marketplace
"

echo "$MARKETPLACES" | while IFS='|' read -r mp_name repo; do
  # Skip empty lines
  [[ -z "$mp_name" ]] && continue

  target="$MARKETPLACES_DIR/$mp_name"

  if [[ -d "$target/.git" ]]; then
    info "$mp_name — git pull 更新中..."
    if git -C "$target" pull --ff-only --quiet 2>/dev/null; then
      ok "$mp_name 已更新"
    else
      warn "$mp_name git pull 失败，可能有本地修改，跳过"
    fi
  else
    info "$mp_name — 正在克隆 $repo..."
    if git clone --quiet "https://github.com/$repo.git" "$target" 2>/dev/null; then
      ok "$mp_name 克隆完成"
    else
      fail "$mp_name 克隆失败 — 请检查网络或仓库地址"
    fi
  fi
done

# Generate known_marketplaces.json
info "生成 $KNOWN_MP_FILE"
NOW="$(date -u +%Y-%m-%dT%H:%M:%S.000Z)"

jq -n \
  --arg now "$NOW" \
  '{
    "n8n-mcp-skills": {
      "source": { "source": "github", "repo": "czlonkowski/n8n-skills" },
      "installLocation": "~/.claude/plugins/marketplaces/n8n-mcp-skills",
      "lastUpdated": $now
    },
    "claude-code-plugins": {
      "source": { "source": "github", "repo": "anthropics/claude-code" },
      "installLocation": "~/.claude/plugins/marketplaces/claude-code-plugins",
      "lastUpdated": $now
    },
    "md2wechat-tools": {
      "source": { "source": "github", "repo": "geekjourneyx/md2wechat-skill" },
      "installLocation": "~/.claude/plugins/marketplaces/md2wechat-tools",
      "lastUpdated": $now
    },
    "superpowers-marketplace": {
      "source": { "source": "github", "repo": "obra/superpowers-marketplace" },
      "installLocation": "~/.claude/plugins/marketplaces/superpowers-marketplace",
      "lastUpdated": $now
    }
  }' > "$KNOWN_MP_FILE"

ok "known_marketplaces.json 已生成"

# =========================================================================
# Step 4: Plugin Cache 重建
# =========================================================================
step "Step 4/6: Plugin Cache"

mkdir -p "$CACHE_DIR"

HAS_CLAUDE_CLI=false
if command -v claude &>/dev/null; then
  HAS_CLAUDE_CLI=true
  ok "claude CLI 可用"
else
  warn "claude CLI 不可用，将使用手动方式重建 cache"
fi

# Manual install function
install_plugin_manual() {
  local marketplace="$1" plugin="$2" version="$3" source_type="$4" source_path="$5"
  local cache_target="$CACHE_DIR/$marketplace/$plugin/$version"

  if { [[ -d "$cache_target" ]] || [[ -L "$cache_target" ]]; } && [[ "$FORCE" != true ]]; then
    ok "$plugin@$marketplace cache 已存在，跳过"
    return 0
  fi

  # Remove existing if --force
  if [[ "$FORCE" == true ]]; then
    rm -rf "$cache_target"
  fi

  mkdir -p "$(dirname "$cache_target")"

  case "$source_type" in
    symlink)
      if [[ -d "$source_path" ]]; then
        ln -sfn "$source_path" "$cache_target"
        ok "$plugin → symlink 创建"
      else
        fail "$plugin symlink target 不存在: $source_path"
        return 1
      fi
      ;;
    external)
      info "$plugin — 从外部仓库克隆 $source_path"
      if git clone --quiet --depth 1 "$source_path" "$cache_target" 2>/dev/null; then
        ok "$plugin cache 克隆完成"
      else
        fail "$plugin 克隆失败: $source_path"
        return 1
      fi
      ;;
    marketplace)
      local mp_source="$MARKETPLACES_DIR/$marketplace/$source_path"
      if [[ ! -d "$mp_source" ]]; then
        fail "$plugin 源目录不存在: $mp_source"
        return 1
      fi
      cp -R "$mp_source" "$cache_target"
      ok "$plugin cache 已从 marketplace 复制"
      ;;
  esac
}

# --- Plugin definitions ---
# Format: plugin_id|marketplace|plugin_name|version|source_type|source_path
# source_type: marketplace (copy subdir), external (git clone), symlink (ln -s)
PLUGIN_DEFS="
n8n-mcp-skills@n8n-mcp-skills|n8n-mcp-skills|n8n-mcp-skills|1.0.0|marketplace|.
ralph-wiggum@claude-code-plugins|claude-code-plugins|ralph-wiggum|1.0.0|marketplace|plugins/ralph-wiggum
superpowers@superpowers-marketplace|superpowers-marketplace|superpowers|4.1.1|external|https://github.com/obra/superpowers.git
kiro-skill@claude-code-settings|claude-code-settings|kiro-skill|1.0.0|symlink|$PLUGINS_DIR/kiro-skill
"

echo "$PLUGIN_DEFS" | while IFS='|' read -r plugin_id marketplace plugin version source_type source_path; do
  # Skip empty lines
  [[ -z "$plugin_id" ]] && continue

  cache_target="$CACHE_DIR/$marketplace/$plugin/$version"

  # Skip if already exists and not forcing
  if { [[ -d "$cache_target" ]] || [[ -L "$cache_target" ]]; } && [[ "$FORCE" != true ]]; then
    ok "$plugin_id cache 已存在"
    continue
  fi

  # Try claude CLI first (skip for symlink type)
  if [[ "$HAS_CLAUDE_CLI" == true ]] && [[ "$source_type" != "symlink" ]]; then
    info "$plugin_id — 尝试 claude plugin install..."
    if claude plugin install "$plugin_id" 2>/dev/null; then
      ok "$plugin_id 安装成功 (via CLI)"
      continue
    else
      warn "$plugin_id CLI 安装失败，回退到手动方式"
    fi
  fi

  # Fallback: manual install
  install_plugin_manual "$marketplace" "$plugin" "$version" "$source_type" "$source_path"
done

# =========================================================================
# Step 5: 权限修复
# =========================================================================
step "Step 5/6: 权限修复"

# status-line.sh
if [[ -f "$CLAUDE_DIR/status-line.sh" ]]; then
  chmod +x "$CLAUDE_DIR/status-line.sh"
  ok "status-line.sh +x"
fi

# All shell scripts under skills/ and plugins/ (excluding marketplaces/cache)
SCRIPT_COUNT=0
while IFS= read -r script; do
  [[ -z "$script" ]] && continue
  chmod +x "$script"
  SCRIPT_COUNT=$((SCRIPT_COUNT + 1))
done <<< "$(find "$CLAUDE_DIR/skills" "$CLAUDE_DIR/plugins" \
  -path "*/scripts/*.sh" \
  -not -path "*/marketplaces/*" \
  -not -path "*/cache/*" \
  2>/dev/null)"

if [[ $SCRIPT_COUNT -gt 0 ]]; then
  ok "$SCRIPT_COUNT 个 skill 脚本已设置 +x"
else
  warn "未找到 skill 脚本"
fi

# =========================================================================
# Step 6: Python 依赖（可选）
# =========================================================================
step "Step 6/6: Python 依赖"

if [[ "$SKIP_PYTHON" == true ]]; then
  info "跳过 Python 依赖安装 (--skip-python)"
else
  REQ_FILES=""
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    REQ_FILES="$REQ_FILES
$f"
  done <<< "$(find "$CLAUDE_DIR/skills" "$CLAUDE_DIR/plugins" \
    -name "requirements.txt" \
    -not -path "*/marketplaces/*" \
    -not -path "*/cache/*" \
    -not -path "*/.git/*" \
    -not -path "*/node_modules/*" \
    2>/dev/null)"

  # Trim leading newline
  REQ_FILES="$(echo "$REQ_FILES" | sed '/^$/d')"

  if [[ -z "$REQ_FILES" ]]; then
    info "未找到 requirements.txt"
  else
    REQ_COUNT=$(echo "$REQ_FILES" | wc -l | tr -d ' ')
    echo ""
    info "发现 $REQ_COUNT 个 requirements.txt:"
    echo "$REQ_FILES" | while read -r f; do
      echo "    - ${f#$CLAUDE_DIR/}"
    done
    echo ""
    read -rp "  是否安装 Python 依赖？[y/N] " answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
      echo "$REQ_FILES" | while read -r f; do
        info "pip install -r ${f#$CLAUDE_DIR/}"
        python3 -m pip install -r "$f" --quiet 2>/dev/null && ok "完成" || warn "安装失败: $f"
      done
    else
      info "跳过"
    fi
  fi
fi

# =========================================================================
# Summary
# =========================================================================
echo ""
step "初始化完成"
echo ""
info "检查清单:"
[[ -f "$SETTINGS_FILE" ]] && ok "settings.json" || fail "settings.json"
[[ -d "$MARKETPLACES_DIR" ]] && ok "plugins/marketplaces/ ($(ls "$MARKETPLACES_DIR" | wc -l | tr -d ' ') repos)" || fail "plugins/marketplaces/"
[[ -f "$KNOWN_MP_FILE" ]] && ok "plugins/known_marketplaces.json" || fail "plugins/known_marketplaces.json"
[[ -d "$CACHE_DIR" ]] && ok "plugins/cache/ ($(ls "$CACHE_DIR" | wc -l | tr -d ' ') plugins)" || fail "plugins/cache/"
echo ""
info "如果插件仍无法加载，请运行: claude plugin list"
