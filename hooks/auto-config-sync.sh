#!/usr/bin/env bash
# =============================================================================
# auto-config-sync.sh — SessionStart hook
#
# 逻辑：
#   1. 检测 OAuth token 是否有效（存在且未过期且有 subscriptionType）
#   2. 有效 → 自动切换到 pro 模式
#   3. 失效 → 回退到 fallback_provider，并提示用户重新登录
# =============================================================================

CLAUDE_DIR="$HOME/.claude"
CREDS="$CLAUDE_DIR/.credentials.json"
ENV_JSON="$CLAUDE_DIR/env.json"
CONFIG_SYNC="$CLAUDE_DIR/bin/config-sync.sh"

get_env() {
  jq -r ".${1} // empty" "$ENV_JSON" 2>/dev/null || echo ""
}

# ── 检测 OAuth 是否有效 ──
is_oauth_valid() {
  [[ -f "$CREDS" ]] || return 1

  local expires_at sub_type now_ms buffer_ms
  expires_at=$(jq -r '.claudeAiOauth.expiresAt // 0' "$CREDS" 2>/dev/null)
  sub_type=$(jq -r '.claudeAiOauth.subscriptionType // ""' "$CREDS" 2>/dev/null)
  now_ms=$(date +%s%3N)
  buffer_ms=$((3600 * 1000))  # 1 小时缓冲

  [[ -n "$sub_type" ]] && [[ "$expires_at" -gt "$((now_ms + buffer_ms))" ]]
}

# ── 判断 token 是否存在但已过期 ──
is_oauth_expired() {
  [[ -f "$CREDS" ]] || return 1
  local sub_type
  sub_type=$(jq -r '.claudeAiOauth.subscriptionType // ""' "$CREDS" 2>/dev/null)
  [[ -n "$sub_type" ]]  # 曾经登录过（有 subscriptionType），但 is_oauth_valid 返回 false
}

# ── 主逻辑 ──
current_provider=$(get_env "provider")

if is_oauth_valid; then
  if [[ "$current_provider" != "pro" ]]; then
    echo "[config] OAuth 有效，自动切换到 pro 模式" >&2
    "$CONFIG_SYNC" --provider pro 2>&1 | sed 's/^/[config] /' >&2
  fi
else
  fallback=$(get_env "fallback_provider")
  [[ -z "$fallback" || "$fallback" == "pro" ]] && fallback="anthropic"

  if [[ "$current_provider" == "pro" ]]; then
    if is_oauth_expired; then
      echo "" >&2
      echo "╔══════════════════════════════════════════════╗" >&2
      echo "║  Pro OAuth token 已过期，已回退到 $fallback 模式  ║" >&2
      echo "║  运行 claude login 重新登录以恢复 Pro 模式   ║" >&2
      echo "╚══════════════════════════════════════════════╝" >&2
      echo "" >&2
    else
      echo "" >&2
      echo "╔══════════════════════════════════════════════╗" >&2
      echo "║  未检测到 Pro OAuth 登录，已回退到 $fallback 模式  ║" >&2
      echo "║  运行 claude login 登录以启用 Pro 模式       ║" >&2
      echo "╚══════════════════════════════════════════════╝" >&2
      echo "" >&2
    fi
    "$CONFIG_SYNC" --provider "$fallback" 2>&1 | sed 's/^/[config] /' >&2
  fi
fi
