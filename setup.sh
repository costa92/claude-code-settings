#!/usr/bin/env bash
# =============================================================================
# setup.sh — 跨机器一键初始化 ~/.claude/ 插件系统
#
# 用途：git pull 后重建被 .gitignore 排除的 settings.json、marketplace、cache 等
# 幂等：重复运行安全，不会覆盖已有配置
# =============================================================================

set -eo pipefail

# ── Load common library ──
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"

MARKETPLACES_DIR="$PLUGINS_DIR/marketplaces"
CACHE_DIR="$PLUGINS_CACHE"
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

# =========================================================================
# Step 1: 环境检测
# =========================================================================
step "Step 1/9: 环境检测"

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

# Auto-install missing required tools
if [[ -n "$MISSING_TOOLS" ]]; then
  echo ""
  info "缺少必要工具:$MISSING_TOOLS，尝试自动安装..."

  if [[ "$OS" == "Darwin" ]]; then
    if command -v brew &>/dev/null; then
      info "brew install$MISSING_TOOLS"
      if brew install $MISSING_TOOLS; then
        ok "工具安装完成"
      else
        fail "brew install 失败"
        echo "    请手动运行: brew install$MISSING_TOOLS"
        exit 1
      fi
    else
      fail "Homebrew 未安装，无法自动安装依赖"
      echo "    请先安装 Homebrew: https://brew.sh"
      echo "    然后运行: brew install$MISSING_TOOLS"
      exit 1
    fi
  elif [[ "$OS" == "Linux" ]]; then
    # Detect package manager
    if command -v apt-get &>/dev/null; then
      info "sudo apt-get install -y$MISSING_TOOLS"
      if sudo apt-get update -qq && sudo apt-get install -y $MISSING_TOOLS; then
        ok "工具安装完成"
      else
        fail "apt-get install 失败"
        echo "    请手动运行: sudo apt-get install$MISSING_TOOLS"
        exit 1
      fi
    elif command -v yum &>/dev/null; then
      info "sudo yum install -y$MISSING_TOOLS"
      if sudo yum install -y $MISSING_TOOLS; then
        ok "工具安装完成"
      else
        fail "yum install 失败"
        echo "    请手动运行: sudo yum install$MISSING_TOOLS"
        exit 1
      fi
    elif command -v dnf &>/dev/null; then
      info "sudo dnf install -y$MISSING_TOOLS"
      if sudo dnf install -y $MISSING_TOOLS; then
        ok "工具安装完成"
      else
        fail "dnf install 失败"
        echo "    请手动运行: sudo dnf install$MISSING_TOOLS"
        exit 1
      fi
    elif command -v pacman &>/dev/null; then
      info "sudo pacman -S --noconfirm$MISSING_TOOLS"
      if sudo pacman -S --noconfirm $MISSING_TOOLS; then
        ok "工具安装完成"
      else
        fail "pacman install 失败"
        echo "    请手动运行: sudo pacman -S$MISSING_TOOLS"
        exit 1
      fi
    elif command -v apk &>/dev/null; then
      info "apk add$MISSING_TOOLS"
      if apk add $MISSING_TOOLS; then
        ok "工具安装完成"
      else
        fail "apk add 失败"
        echo "    请手动运行: apk add$MISSING_TOOLS"
        exit 1
      fi
    else
      fail "未识别的包管理器，无法自动安装"
      echo "    请手动安装:$MISSING_TOOLS"
      exit 1
    fi
  else
    fail "不支持的操作系统: $OS"
    echo "    请手动安装:$MISSING_TOOLS"
    exit 1
  fi

  # Verify installation succeeded
  for tool in $MISSING_TOOLS; do
    if ! command -v "$tool" &>/dev/null; then
      fail "$tool 安装后仍不可用"
      exit 1
    fi
    ok "$tool 已安装"
  done
fi

# =========================================================================
# Step 2: 初始化 env.json + 生成 settings.json
# =========================================================================
step "Step 2/9: env.json + settings.json"

ENV_JSON="$CLAUDE_DIR/env.json"
ENV_EXAMPLE="$CLAUDE_DIR/env.example.json"
CONFIG_SYNC="$CLAUDE_DIR/bin/config-sync.sh"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"

# 2a. 初始化 env.json（新机器首次）
if [[ -f "$ENV_JSON" ]]; then
  ok "env.json 已存在，跳过"
else
  if [[ ! -f "$ENV_EXAMPLE" ]]; then
    fail "env.example.json 不存在"
    exit 1
  fi
  cp "$ENV_EXAMPLE" "$ENV_JSON"
  info "已从 env.example.json 复制模板"

  # 交互式收集 provider 和 API key
  echo ""
  echo "  可用 provider: pro | anthropic | deepseek | openrouter | qwen | siliconflow | minimax | azure | vertex | litellm | copilot | azure-foundry"
  read -rp "  选择 provider（留空默认 pro）: " PROVIDER
  PROVIDER="${PROVIDER:-pro}"
  jq --arg p "$PROVIDER" '.provider = $p' "$ENV_JSON" > "$ENV_JSON.tmp" && mv "$ENV_JSON.tmp" "$ENV_JSON"

  if [[ "$PROVIDER" == "anthropic" ]]; then
    read -rp "  ANTHROPIC_API_KEY（留空跳过）: " API_KEY
    read -rp "  ANTHROPIC_BASE_URL（留空使用官方地址）: " BASE_URL
    [[ -n "$API_KEY" ]] && jq --arg v "$API_KEY" '.anthropic_api_key = $v' "$ENV_JSON" > "$ENV_JSON.tmp" && mv "$ENV_JSON.tmp" "$ENV_JSON"
    [[ -n "$BASE_URL" ]] && jq --arg v "$BASE_URL" '.anthropic_base_url = $v' "$ENV_JSON" > "$ENV_JSON.tmp" && mv "$ENV_JSON.tmp" "$ENV_JSON"
  elif [[ "$PROVIDER" != "pro" && "$PROVIDER" != "litellm" && "$PROVIDER" != "copilot" && "$PROVIDER" != "vertex" ]]; then
    read -rp "  ${PROVIDER}_api_key（留空跳过）: " API_KEY
    [[ -n "$API_KEY" ]] && jq --arg v "$API_KEY" ".${PROVIDER}_api_key = \$v" "$ENV_JSON" > "$ENV_JSON.tmp" && mv "$ENV_JSON.tmp" "$ENV_JSON"
  fi

  ok "env.json 初始化完成"
fi

# 2b. 生成 settings.json（通过 config-sync.sh）
if [[ -f "$SETTINGS_FILE" ]]; then
  ok "settings.json 已存在，跳过（如需重新生成：bin/config-sync.sh）"
else
  if [[ ! -x "$CONFIG_SYNC" ]]; then
    fail "bin/config-sync.sh 不存在或不可执行"
    exit 1
  fi
  "$CONFIG_SYNC"
  ok "settings.json 生成完成"
fi

# =========================================================================
# Step 3: Marketplace 仓库克隆 / 更新
# =========================================================================
step "Step 3/9: Marketplace 仓库"

mkdir -p "$MARKETPLACES_DIR"

# Marketplace definitions (bash 3.2 compatible — no associative arrays)
# Format: "local_name|github_owner/repo"
MARKETPLACES="
n8n-mcp-skills|czlonkowski/n8n-skills
claude-code-plugins|anthropics/claude-code
superpowers-marketplace|obra/superpowers-marketplace
"

while IFS='|' read -r mp_name repo; do
  # Skip empty lines
  [[ -z "$mp_name" ]] && continue

  target="$MARKETPLACES_DIR/$mp_name"

  if [[ -d "$target/.git" ]]; then
    info "$mp_name — git pull 更新中..."
    if git -C "$target" pull --ff-only --quiet </dev/null 2>/dev/null; then
      ok "$mp_name 已更新"
    else
      warn "$mp_name git pull 失败，可能有本地修改，跳过"
    fi
  else
    info "$mp_name — 正在克隆 $repo..."
    if git clone --quiet "https://github.com/$repo.git" "$target" </dev/null 2>/dev/null; then
      ok "$mp_name 克隆完成"
    else
      fail "$mp_name 克隆失败 — 请检查网络或仓库地址"
    fi
  fi
done <<< "$MARKETPLACES"

# Generate known_marketplaces.json
info "生成 $KNOWN_MP_FILE"
NOW="$(date -u +%Y-%m-%dT%H:%M:%S.000Z)"

jq -n \
  --arg now "$NOW" \
  --arg mp_root "$MARKETPLACES_DIR" \
  '{
    "n8n-mcp-skills": {
      "source": { "source": "github", "repo": "czlonkowski/n8n-skills" },
      "installLocation": ($mp_root + "/n8n-mcp-skills"),
      "lastUpdated": $now
    },
    "claude-code-plugins": {
      "source": { "source": "github", "repo": "anthropics/claude-code" },
      "installLocation": ($mp_root + "/claude-code-plugins"),
      "lastUpdated": $now
    },
    "superpowers-marketplace": {
      "source": { "source": "github", "repo": "obra/superpowers-marketplace" },
      "installLocation": ($mp_root + "/superpowers-marketplace"),
      "lastUpdated": $now
    }
  }' > "$KNOWN_MP_FILE"

ok "known_marketplaces.json 已生成"

# =========================================================================
# Step 4: Plugin Cache 重建
# =========================================================================
step "Step 4/9: Plugin Cache"

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
# version: use "latest" to auto-detect from git tags, or a fixed version string

_resolve_superpowers_version() {
  local existing
  existing=$(ls -d "$CACHE_DIR/superpowers-marketplace/superpowers"/*/ 2>/dev/null | sort -V | tail -1 | xargs basename 2>/dev/null)
  if [[ -n "$existing" ]]; then
    echo "$existing"
    return
  fi
  local tag
  tag=$(git ls-remote --tags --sort=-v:refname "https://github.com/obra/superpowers.git" 2>/dev/null \
    | head -1 | sed 's|.*refs/tags/v\?||' | tr -d ' ')
  if [[ -n "$tag" ]]; then
    echo "$tag"
  else
    echo "latest"
  fi
}

SUPERPOWERS_VERSION=$(_resolve_superpowers_version)
info "superpowers version: $SUPERPOWERS_VERSION"

PLUGIN_DEFS="
n8n-mcp-skills@n8n-mcp-skills|n8n-mcp-skills|n8n-mcp-skills|1.0.0|marketplace|.
ralph-wiggum@claude-code-plugins|claude-code-plugins|ralph-wiggum|1.0.0|marketplace|plugins/ralph-wiggum
superpowers@superpowers-marketplace|superpowers-marketplace|superpowers|${SUPERPOWERS_VERSION}|external|https://github.com/obra/superpowers.git
kiro-skill@claude-code-settings|claude-code-settings|kiro-skill|1.0.0|symlink|$PLUGINS_DIR/kiro-skill
autonomous-skill@claude-code-settings|claude-code-settings|autonomous-skill|1.0.0|symlink|$PLUGINS_DIR/autonomous-skill
codex-skill@claude-code-settings|claude-code-settings|codex-skill|1.0.0|symlink|$PLUGINS_DIR/codex-skill
nanobanana-skill@claude-code-settings|claude-code-settings|nanobanana-skill|1.0.0|symlink|$PLUGINS_DIR/nanobanana-skill
spec-kit-skill@claude-code-settings|claude-code-settings|spec-kit-skill|1.0.0|symlink|$PLUGINS_DIR/spec-kit-skill
youtube-transcribe-skill@claude-code-settings|claude-code-settings|youtube-transcribe-skill|1.0.0|symlink|$PLUGINS_DIR/youtube-transcribe-skill
"

while IFS='|' read -r plugin_id marketplace plugin version source_type source_path; do
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
done <<< "$PLUGIN_DEFS"

# ── Create direct symlinks from $PLUGINS_DIR/<name> → cache target ──
# installed_plugins.json references plugins/<name>, but cache installs to plugins/cache/<marketplace>/<plugin>/<version>
# Symlinks bridge this gap so both paths work
info "确保插件直接路径可用..."
while IFS='|' read -r plugin_id marketplace plugin version source_type source_path; do
  [[ -z "$plugin_id" ]] && continue
  [[ "$source_type" == "symlink" ]] && continue  # local plugins already at direct path

  direct_path="$PLUGINS_DIR/$plugin"
  cache_target="$CACHE_DIR/$marketplace/$plugin/$version"

  # Skip if direct path already exists (real dir or working symlink)
  if [[ -d "$direct_path" ]]; then
    continue
  fi

  # Remove broken symlink if present
  [[ -L "$direct_path" ]] && rm -f "$direct_path"

  # Create symlink if cache target exists
  if [[ -d "$cache_target" ]]; then
    ln -sfn "$cache_target" "$direct_path"
    ok "$plugin → symlink 创建 ($direct_path → $cache_target)"
  fi
done <<< "$PLUGIN_DEFS"

# =========================================================================
INSTALLED_PLUGINS="$PLUGINS_DIR/installed_plugins.json"
if [[ -f "$INSTALLED_PLUGINS" ]]; then
  # Replace absolute $HOME paths with ~/ in installPath fields
  if grep -q "\"installPath\": \"$HOME" "$INSTALLED_PLUGINS" 2>/dev/null; then
    _sed_i "s|\"installPath\": \"$HOME/|\"installPath\": \"~/|g" "$INSTALLED_PLUGINS"
    ok "installed_plugins.json 路径已修正（$HOME → ~）"
  else
    ok "installed_plugins.json 路径格式正常"
  fi

  # Verify and fix cache paths: update installPath to point to actual cache location
  info "验证 installed_plugins.json 中的路径..."
  PATHS_FIXED=0
  python3 - "$INSTALLED_PLUGINS" "$PLUGINS_DIR" "$CACHE_DIR" <<'PYEOF' && PATHS_FIXED=1 || warn "installed_plugins.json 路径验证脚本执行失败（python3 错误）"
import json, os, sys
from pathlib import Path

installed_path, plugins_dir, cache_dir = sys.argv[1:]
home = str(Path.home())

with open(installed_path) as f:
    data = json.load(f)

changed = False
for plugin_key, entries in data.get("plugins", {}).items():
    for entry in entries:
        ip = entry["installPath"].replace("~", home)
        if os.path.isdir(ip):
            continue
        # Try to find the plugin in cache or direct plugin dir
        plugin_name = plugin_key.split("@")[0]
        # Check cache (rebuilt by setup.sh)
        cache_path = os.path.join(cache_dir, *ip.split("/cache/", 1)[1:]) if "/cache/" in ip else ""
        if cache_path and os.path.isdir(cache_path):
            entry["installPath"] = cache_path.replace(home, "~")
            changed = True
            print(f"  fixed: {plugin_key} → cache")
            continue
        # Check direct plugin dir
        direct_path = os.path.join(plugins_dir, plugin_name)
        if os.path.isdir(direct_path):
            entry["installPath"] = direct_path.replace(home, "~")
            changed = True
            print(f"  fixed: {plugin_key} → direct")
            continue
        print(f"  warn: {plugin_key} — 路径不存在，无法自动修复")

if changed:
    with open(installed_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("  installed_plugins.json 路径已更新")
PYEOF
  if [[ "$PATHS_FIXED" == "1" ]]; then
    ok "installed_plugins.json 路径已验证/修复"
  fi
else
  info "installed_plugins.json 不存在，跳过路径修正"
fi

# =========================================================================
# Step 5: 权限修复
# =========================================================================
step "Step 5/9: 权限修复"

# status-line.sh
if [[ -f "$CLAUDE_DIR/status-line.sh" ]]; then
  chmod +x "$CLAUDE_DIR/status-line.sh"
  ok "status-line.sh +x"
fi

# bin/ scripts
if [[ -d "$CLAUDE_DIR/bin" ]]; then
  find "$CLAUDE_DIR/bin" -name "*.sh" -exec chmod +x {} +
  ok "bin/*.sh +x"
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
step "Step 6/9: Python 依赖"

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

      # shot-scraper needs a post-install step to download Playwright browser
      if command -v shot-scraper &>/dev/null; then
        info "shot-scraper install (下载 Playwright 浏览器)..."
        shot-scraper install --quiet 2>/dev/null && ok "shot-scraper 浏览器就绪" || warn "shot-scraper install 失败，可稍后手动运行: shot-scraper install"
      fi
    else
      info "跳过"
    fi
  fi

  # --- Playwright (webapp-testing skill, no requirements.txt) ---
  if [[ -d "$CLAUDE_DIR/skills/webapp-testing" ]]; then
    echo ""
    info "检测到 webapp-testing skill，需要 Playwright"
    if python3 -c "import playwright" &>/dev/null; then
      ok "playwright 已安装"
    else
      read -rp "  是否安装 playwright？[y/N] " answer
      if [[ "$answer" =~ ^[Yy]$ ]]; then
        python3 -m pip install playwright --quiet && ok "playwright 安装完成" || { warn "playwright 安装失败"; }
      else
        info "跳过 playwright 安装"
      fi
    fi

    # Install Chromium browser binaries (needed even if already pip-installed)
    if python3 -c "import playwright" &>/dev/null; then
      if python3 -m playwright install chromium --quiet 2>/dev/null; then
        ok "Playwright Chromium 浏览器就绪"
      else
        warn "Playwright 浏览器安装失败，可稍后手动运行: playwright install chromium"
      fi
    fi
  fi
fi

# =========================================================================
# Step 7: 系统软件包（LibreOffice、Poppler）
# =========================================================================
step "Step 7/9: 系统软件包"

# Skills that need these: pptx, docx, pdf, xlsx
NEED_SOFFICE=false
NEED_POPPLER=false
for skill in pptx docx pdf xlsx; do
  [[ -d "$CLAUDE_DIR/skills/$skill" ]] && NEED_SOFFICE=true && NEED_POPPLER=true
done

if [[ "$NEED_SOFFICE" == false ]] && [[ "$NEED_POPPLER" == false ]]; then
  info "无需系统软件包（相关 skill 未安装）"
else
  # Helper: install a system package if missing
  _install_sys_pkg() {
    local pkg_name="$1" brew_pkg="${2:-$1}" apt_pkg="${3:-$1}"
    if [[ "$OS" == "Darwin" ]]; then
      command -v brew &>/dev/null && brew install "$brew_pkg" && return 0
    elif [[ "$OS" == "Linux" ]]; then
      if command -v apt-get &>/dev/null; then
        sudo apt-get install -y "$apt_pkg" && return 0
      elif command -v yum &>/dev/null; then
        sudo yum install -y "$apt_pkg" && return 0
      elif command -v dnf &>/dev/null; then
        sudo dnf install -y "$apt_pkg" && return 0
      elif command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm "$apt_pkg" && return 0
      elif command -v apk &>/dev/null; then
        apk add "$apt_pkg" && return 0
      fi
    fi
    return 1
  }

  # LibreOffice (soffice)
  if command -v soffice &>/dev/null; then
    ok "LibreOffice $(soffice --version 2>/dev/null | head -1)"
  else
    warn "LibreOffice 未安装 — pptx/docx/pdf/xlsx skill 需要"
    info "尝试自动安装 LibreOffice..."
    if _install_sys_pkg libreoffice libreoffice libreoffice; then
      ok "LibreOffice 安装完成"
    else
      warn "LibreOffice 自动安装失败"
      if [[ "$OS" == "Darwin" ]]; then
        echo "    brew install libreoffice"
      else
        echo "    sudo apt install libreoffice"
      fi
    fi
  fi

  # Poppler (pdftoppm)
  if command -v pdftoppm &>/dev/null; then
    ok "Poppler pdftoppm $(pdftoppm -v 2>&1 | head -1)"
  else
    warn "Poppler 未安装 — pptx/docx/pdf skill 需要 pdftoppm"
    info "尝试自动安装 Poppler..."
    if _install_sys_pkg poppler poppler poppler-utils; then
      ok "Poppler 安装完成"
    else
      warn "Poppler 自动安装失败"
      if [[ "$OS" == "Darwin" ]]; then
        echo "    brew install poppler"
      else
        echo "    sudo apt install poppler-utils"
      fi
    fi
  fi
fi

# =========================================================================
# Step 8: npm 全局工具
# =========================================================================
step "Step 8/9: npm 全局工具"

if ! command -v npm &>/dev/null; then
  warn "npm 未安装，跳过 npm 全局工具安装"
  if [[ "$OS" == "Darwin" ]]; then
    echo "    brew install node"
  else
    echo "    sudo apt install nodejs npm"
  fi
else
  ok "npm $(npm --version)"

  # Format: "tool_name|npm_package|skill_dir|description|check_type"
  # check_type: cli = command -v, lib = npm list -g
  NPM_TOOLS="
defuddle|defuddle-cli|defuddle|网页内容提取（defuddle skill）|cli
pptxgenjs|pptxgenjs|pptx|PowerPoint 生成（pptx skill）|lib
decktape|decktape|revealjs|Reveal.js 导出 PDF（revealjs skill）|cli
"

  npm_tool_installed() {
    local tool="$1" check_type="$2"
    if [[ "$check_type" == "lib" ]]; then
      npm list -g --depth=0 "$tool" 2>/dev/null | grep -q "$tool"
    else
      command -v "$tool" &>/dev/null
    fi
  }

  while IFS='|' read -r tool pkg skill desc check_type; do
    [[ -z "$tool" ]] && continue
    # Only check if the skill is installed
    [[ ! -d "$CLAUDE_DIR/skills/$skill" ]] && continue

    if npm_tool_installed "$tool" "$check_type"; then
      ok "$tool 已安装 — $desc"
    else
      echo ""
      info "$tool 未安装 — $desc"
      read -rp "  是否安装 $pkg？[y/N] " answer
      if [[ "$answer" =~ ^[Yy]$ ]]; then
        npm install -g "$pkg" --quiet && ok "$tool 安装完成" || warn "$tool 安装失败，可手动运行: npm install -g $pkg"
      else
        info "跳过 — 可稍后运行: npm install -g $pkg"
      fi
    fi
  done <<< "$NPM_TOOLS"
fi

# =========================================================================
# Step 9: 同步插件 Skills/Agents 到 ~/.claude/skills/ (供 Cursor IDE 使用)
# =========================================================================
step "Step 9/9: 同步插件 Skills 到 Cursor"

SYNC_SCRIPT="$CLAUDE_DIR/bin/sync-plugin-skills.sh"
if [[ -x "$SYNC_SCRIPT" ]]; then
  info "运行 sync-plugin-skills.sh --force ..."
  if "$SYNC_SCRIPT" --force; then
    ok "插件 skills/agents 已同步到 ~/.claude/skills/ 和 ~/.claude/agents/"
  else
    warn "sync-plugin-skills.sh 执行失败，可稍后手动运行"
  fi
else
  warn "sync-plugin-skills.sh 不存在或不可执行，跳过"
  info "如需在 Cursor 中使用插件 skills，请运行: chmod +x $SYNC_SCRIPT"
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
command -v soffice &>/dev/null && ok "LibreOffice" || warn "LibreOffice 未安装（pptx/docx/pdf/xlsx skill 需要）"
command -v pdftoppm &>/dev/null && ok "Poppler (pdftoppm)" || warn "Poppler 未安装（pptx/docx/pdf skill 需要）"
command -v defuddle &>/dev/null && ok "defuddle" || warn "defuddle 未安装（defuddle skill 需要: npm install -g defuddle-cli）"
npm list -g --depth=0 pptxgenjs 2>/dev/null | grep -q pptxgenjs && ok "pptxgenjs" || warn "pptxgenjs 未安装（pptx skill 需要: npm install -g pptxgenjs）"
python3 -c "import playwright" &>/dev/null && ok "playwright (Python)" || warn "playwright 未安装（webapp-testing skill 需要）"
[[ -f "$CLAUDE_DIR/plugins/.sync-manifest.json" ]] && ok "plugin→skills 同步 ($(python3 -c "import json; d=json.load(open('$CLAUDE_DIR/plugins/.sync-manifest.json')); print(len(d.get('skills',{})))" 2>/dev/null || echo '?') skills)" || warn "plugin→skills 未同步"
echo ""
info "如果插件仍无法加载，请运行: claude plugin list"
