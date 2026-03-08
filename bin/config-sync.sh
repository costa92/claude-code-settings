#!/usr/bin/env bash
# =============================================================================
# config-sync.sh — 配置统一生成工具
#
# 用途：从 env.json 生成 settings.json 和 .mcp.json
# 参数：
#   --provider <name>   切换 provider 并同步配置
#   --list              列出所有可用 provider
#   --dry-run           预览生成结果，不写入文件
#
# 依赖：jq
# 兼容：bash 3.2+（macOS 默认）、bash 4/5、zsh
# =============================================================================

set -eo pipefail

CLAUDE_DIR="$HOME/.claude"
source "$CLAUDE_DIR/lib/common.sh"
_require_jq

ENV_JSON="$CLAUDE_DIR/env.json"
SETTINGS_JSON="$CLAUDE_DIR/settings.json"
MCP_JSON="$CLAUDE_DIR/.mcp.json"
SETTINGS_TEMPLATE_DIR="$CLAUDE_DIR/settings"
LOCKDIR="$CLAUDE_DIR/.config-sync.lock"

DRY_RUN=false

# ── File locking (reuse common.sh _lock_acquire/_lock_release) ──
acquire_lock() {
  _lock_acquire "$LOCKDIR" 10 || error "Could not acquire lock"
  trap release_lock EXIT INT TERM
}

release_lock() {
  _lock_release "$LOCKDIR"
}

# ── Provider 配置映射表 ──
# 使用函数代替 declare -A，兼容 bash 3.2
# "pro" 和 "anthropic" 不需要模板文件，在代码中特殊处理
get_provider_template() {
  case "$1" in
    deepseek)      echo "$SETTINGS_TEMPLATE_DIR/deepseek-settings.json" ;;
    azure)         echo "$SETTINGS_TEMPLATE_DIR/azure-settings.json" ;;
    openrouter)    echo "$SETTINGS_TEMPLATE_DIR/openrouter-settings.json" ;;
    vertex)        echo "$SETTINGS_TEMPLATE_DIR/vertex-settings.json" ;;
    litellm)       echo "$SETTINGS_TEMPLATE_DIR/litellm-settings.json" ;;
    copilot)       echo "$SETTINGS_TEMPLATE_DIR/copilot-settings.json" ;;
    qwen)          echo "$SETTINGS_TEMPLATE_DIR/qwen-settings.json" ;;
    siliconflow)   echo "$SETTINGS_TEMPLATE_DIR/siliconflow-settings.json" ;;
    minimax)       echo "$SETTINGS_TEMPLATE_DIR/minimax.json" ;;
    azure-foundry) echo "$SETTINGS_TEMPLATE_DIR/azure-foundry-settings.json" ;;
    *)             echo "" ;;
  esac
}

get_provider_env_keys() {
  case "$1" in
    deepseek)      echo "deepseek_api_key:ANTHROPIC_AUTH_TOKEN" ;;
    azure)         echo "azure_api_key:ANTHROPIC_API_KEY" ;;
    openrouter)    echo "openrouter_api_key:ANTHROPIC_AUTH_TOKEN" ;;
    vertex)        echo "vertex_project:CLOUDSDK_CORE_PROJECT" ;;
    litellm)       echo "" ;;
    copilot)       echo "" ;;
    qwen)          echo "qwen_api_key:ANTHROPIC_AUTH_TOKEN" ;;
    siliconflow)   echo "siliconflow_api_key:ANTHROPIC_AUTH_TOKEN" ;;
    minimax)       echo "minimax_api_key:ANTHROPIC_AUTH_TOKEN" ;;
    azure-foundry) echo "azure_api_key:ANTHROPIC_API_KEY" ;;
    *)             echo "" ;;
  esac
}

is_known_provider() {
  case "$1" in
    pro|anthropic|deepseek|azure|openrouter|vertex|litellm|copilot|qwen|siliconflow|minimax|azure-foundry) return 0 ;;
    *) return 1 ;;
  esac
}

ALL_TEMPLATE_PROVIDERS="azure azure-foundry copilot deepseek litellm minimax openrouter qwen siliconflow vertex"

# ── Helper functions ──
error() {
  echo "[ERROR] $*" >&2
  exit 1
}

warn() {
  echo "[WARN] $*" >&2
}

info() {
  echo "[INFO] $*"
}

# Read a field from env.json
get_env() {
  jq -r ".${1} // empty" "$ENV_JSON" 2>/dev/null || echo ""
}

# Write to env.json
set_env() {
  local key="$1"
  local value="$2"
  jq --arg val "$value" ".${key} = \$val" "$ENV_JSON" > "$ENV_JSON.tmp"
  mv "$ENV_JSON.tmp" "$ENV_JSON"
}

# Generate settings.json
generate_settings() {
  local provider="$1"
  local template_file
  template_file=$(get_provider_template "$provider")

  # Load base settings from current settings.json if it exists and has stable configs
  local base_settings=""
  if [[ -f "$SETTINGS_JSON" ]]; then
    # Preserve existing fields, only remove .env (will be regenerated)
    base_settings=$(jq 'del(.env)' "$SETTINGS_JSON")
  else
    base_settings=$(jq -n '{}')
  fi

  # Ensure required fields exist (use //= to fill only if missing, never overwrite)
  base_settings=$(jq '
    .includeCoAuthoredBy //= false |
    .permissions //= {"allow": [], "deny": [], "ask": []} |
    .statusLine //= {"type": "command", "command": "~/.claude/status-line.sh"} |
    .enabledPlugins //= {} |
    .alwaysThinkingEnabled //= true |
    .skipDangerousModePermissionPrompt //= true
  ' <<< "$base_settings")

  # Auto-populate enabledPlugins from installed_plugins.json if empty
  local installed_json="$CLAUDE_DIR/plugins/installed_plugins.json"
  if [[ -f "$installed_json" ]]; then
    local current_enabled
    current_enabled=$(jq '.enabledPlugins | length' <<< "$base_settings")
    if [[ "$current_enabled" == "0" ]]; then
      # Extract all plugin keys and enable them
      local plugin_keys
      plugin_keys=$(jq -r '.plugins | keys[]' "$installed_json" 2>/dev/null)
      if [[ -n "$plugin_keys" ]]; then
        local enable_obj="{}"
        while IFS= read -r key; do
          enable_obj=$(jq --arg k "$key" '.[$k] = true' <<< "$enable_obj")
        done <<< "$plugin_keys"
        base_settings=$(jq --argjson ep "$enable_obj" '.enabledPlugins = $ep' <<< "$base_settings")
        info "Auto-enabled plugins: $(echo "$plugin_keys" | tr '\n' ' ')"
      fi
    fi
  fi

  # Load and merge provider template
  if [[ "$provider" == "pro" ]]; then
    # Pro 会员模式：OAuth 登录，不需要任何 API key/URL
    # 不禁用 telemetry（Pro 订阅已包含）
    base_settings=$(jq '.env = {}' <<< "$base_settings")
  elif [[ "$provider" == "anthropic" ]]; then
    # API key 模式：通过 ANTHROPIC_BASE_URL 配置代理
    base_settings=$(jq '.env = {}' <<< "$base_settings")
  else
    if [[ ! -f "$template_file" ]]; then
      error "Provider template not found: $template_file"
    fi
    # Merge template env config into base settings
    local template_env=$(jq '.env' "$template_file")
    base_settings=$(jq --argjson env "$template_env" '.env = $env' <<< "$base_settings")
  fi

  # Inject env vars based on provider
  local env_config=$(jq '.env // {}' <<< "$base_settings")

  if [[ "$provider" == "pro" ]]; then
    # Pro 模式：清除所有 API 相关变量，确保使用 OAuth
    env_config=$(jq 'del(.ANTHROPIC_BASE_URL, .ANTHROPIC_API_KEY, .ANTHROPIC_AUTH_TOKEN)' <<< "$env_config")
  elif [[ "$provider" == "anthropic" ]]; then
    # API key 模式：注入 base_url + api_key 或 auth_token
    local base_url=$(get_env "anthropic_base_url")
    if [[ -n "$base_url" ]]; then
      env_config=$(jq --arg url "$base_url" '.ANTHROPIC_BASE_URL = $url' <<< "$env_config")
    fi
    # 优先使用 auth_token（适合代理服务如 anyrouter、openrouter-compatible）
    local auth_token=$(get_env "anthropic_auth_token")
    if [[ -n "$auth_token" ]]; then
      env_config=$(jq --arg tok "$auth_token" '.ANTHROPIC_AUTH_TOKEN = $tok' <<< "$env_config")
    else
      local api_key=$(get_env "anthropic_api_key")
      if [[ -n "$api_key" ]]; then
        env_config=$(jq --arg key "$api_key" '.ANTHROPIC_API_KEY = $key' <<< "$env_config")
      fi
    fi
    # 注入模型覆盖（可选）
    local model_opus=$(get_env "anthropic_default_opus_model")
    local model_sonnet=$(get_env "anthropic_default_sonnet_model")
    local model_haiku=$(get_env "anthropic_default_haiku_model")
    local model_default=$(get_env "anthropic_model")
    [[ -n "$model_opus" ]]   && env_config=$(jq --arg m "$model_opus"   '.ANTHROPIC_DEFAULT_OPUS_MODEL = $m'   <<< "$env_config")
    [[ -n "$model_sonnet" ]] && env_config=$(jq --arg m "$model_sonnet" '.ANTHROPIC_DEFAULT_SONNET_MODEL = $m' <<< "$env_config")
    [[ -n "$model_haiku" ]]  && env_config=$(jq --arg m "$model_haiku"  '.ANTHROPIC_DEFAULT_HAIKU_MODEL = $m'  <<< "$env_config")
    [[ -n "$model_default" ]] && env_config=$(jq --arg m "$model_default" '.ANTHROPIC_MODEL = $m' <<< "$env_config")
  else
    # For other providers, inject API keys
    local env_key_mapping
    env_key_mapping=$(get_provider_env_keys "$provider")
    if [[ -n "$env_key_mapping" ]]; then
      IFS=':' read -r env_field env_var <<< "$env_key_mapping"
      local env_value=$(get_env "$env_field")
      if [[ -n "$env_value" ]]; then
        env_config=$(jq --arg var "$env_var" --arg val "$env_value" '.[$var] = $val' <<< "$env_config")
      fi
    fi
  fi

  # NOTE: N8N_* 不再注入 settings.json.env
  # - MCP server 从 .mcp.json 的 env 字段获取
  # - Skills 通过 load_env.sh/load_env.py 直接读取 env.json
  # - 避免 env.json ↔ settings.json 重复存储

  # Merge env config back
  local result=$(jq --argjson env "$env_config" '.env = $env' <<< "$base_settings")

  # Ensure stable fields
  result=$(jq '.alwaysThinkingEnabled = true' <<< "$result")
  result=$(jq '.skipDangerousModePermissionPrompt = true' <<< "$result")

  if [[ "$DRY_RUN" == true ]]; then
    echo "=== Generated settings.json (preview) ==="
    echo "$result" | jq .
  else
    echo "$result" > "$SETTINGS_JSON"
    info "Generated $SETTINGS_JSON"
  fi
}

# Generate .mcp.json
generate_mcp() {
  local mcp_config=$(jq -n '{
    "mcpServers": {
      "context7": {
        "command": "npx",
        "args": ["-y", "@upstash/context7-mcp"],
        "type": "stdio"
      }
    }
  }')

  # Add n8n-mcp if n8n_api_key is set
  local n8n_api_key=$(get_env "n8n_api_key")
  local n8n_api_url=$(get_env "n8n_api_url")

  if [[ -n "$n8n_api_key" && "$n8n_api_key" != "your-n8n-api-key" ]] && \
     [[ -n "$n8n_api_url" && "$n8n_api_url" != "your-n8n-api-url" ]]; then
    mcp_config=$(jq --arg url "$n8n_api_url" --arg key "$n8n_api_key" '
      .mcpServers["n8n-mcp"] = {
        "command": "npx",
        "args": ["-y", "@n8n-official/n8n-mcp"],
        "type": "stdio",
        "env": {
          "N8N_API_URL": $url,
          "N8N_API_KEY": $key
        }
      }
    ' <<< "$mcp_config")
  fi

  if [[ "$DRY_RUN" == true ]]; then
    echo "=== Generated .mcp.json (preview) ==="
    echo "$mcp_config" | jq .
  else
    echo "$mcp_config" > "$MCP_JSON"
    info "Generated $MCP_JSON"
  fi
}

# List available providers
list_providers() {
  echo "Available providers:"
  echo "  pro             Pro/Max subscription (OAuth login, no API key needed)"
  echo "  anthropic       API key mode (uses anthropic_base_url + anthropic_api_key)"
  for provider in $ALL_TEMPLATE_PROVIDERS; do
    echo "  $provider"
  done
}

# Update provider in env.json
update_provider() {
  local new_provider="$1"

  # Validate provider exists
  if ! is_known_provider "$new_provider"; then
    error "Unknown provider: $new_provider. Use --list to see available providers"
  fi

  # Update provider field
  set_env "provider" "$new_provider"
  info "Updated provider to: $new_provider"
}

# Main sync function
sync_all() {
  if [[ ! -f "$ENV_JSON" ]]; then
    error "env.json not found at $ENV_JSON"
  fi

  # Acquire lock to prevent concurrent writes
  if [[ "$DRY_RUN" == false ]]; then
    acquire_lock
  fi

  # Read current provider
  local provider=$(get_env "provider")
  if [[ -z "$provider" ]]; then
    provider="anthropic"
    warn "provider field not found in env.json, using default: anthropic"
  fi

  info "Syncing configuration for provider: $provider"
  generate_settings "$provider"
  generate_mcp

  if [[ "$DRY_RUN" == false ]]; then
    info "Configuration sync completed successfully"
  fi
}

# ── Main entry point ──
case "${1:-}" in
  --provider)
    if [[ -z "${2:-}" ]]; then
      error "--provider requires an argument"
    fi
    update_provider "$2"
    sync_all
    ;;
  --list)
    list_providers
    ;;
  --dry-run)
    DRY_RUN=true
    sync_all
    ;;
  --help|-h)
    cat <<EOF
Usage: config-sync.sh [OPTION]

  --provider <name>   Switch provider and sync configuration
  --list              List available providers
  --dry-run           Preview generated files without writing
  --help              Show this help message

Examples:
  config-sync.sh                    # Sync using current provider from env.json
  config-sync.sh --provider qwen    # Switch to qwen and sync
  config-sync.sh --list             # List all available providers
  config-sync.sh --dry-run          # Preview without writing files

EOF
    ;;
  *)
    sync_all
    ;;
esac
