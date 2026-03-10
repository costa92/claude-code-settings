# 配置统一重新设计

## Context

当前 `~/.claude` 有 5 个相互独立的配置源，用户修改一处无法自动同步到其他地方，导致：
- `env.json` 有 `anthropic_base_url` 但 `settings.json` 的 `env: {}` 是空的
- `env.json` 有 `n8n_api_key` 但 `.mcp.json` 里 n8n-mcp server 未配置
- 切换 Provider 需要手动从 `settings/deepseek-settings.json` 复制内容替换 `settings.json`
- 新机器部署需要分别配置多个文件

**目标**：`env.json` 成为唯一真相源，`settings.json` 和 `.mcp.json` 完全由脚本生成。

---

## 架构

### 新配置层级

```
env.json (唯一真相源，gitignored)
    │
    ▼ config-sync.sh (生成工具)
    ├── settings.json (生成，gitignored) — Claude Code 主配置
    └── .mcp.json (生成，gitignored) — MCP 服务器配置

settings/ (provider 模板库，committed)
    └── 10 个 provider 配置（保留不变，作为生成 settings.json 的模板）
```

### env.json 新增字段

```json
{
  "provider": "anthropic",          // 新增：当前 provider（决定读取哪个模板）

  // Anthropic 直连/代理
  "anthropic_base_url": "http://127.0.0.1:5000",

  // 其他 provider keys（按需填写，空则忽略）
  "deepseek_api_key": "",
  "azure_api_key": "",
  "openrouter_api_key": "",
  "vertex_project": "",

  // 功能型 API（保留现有字段）
  "gemini_api_key": "...",
  "wechat_appid": "...",
  "wechat_secret": "...",
  "image_api_key": "...",
  "n8n_api_url": "http://localhost:5678/api/v1",
  "n8n_api_key": "...",

  // Skill 偏好（保留现有字段）
  "digest_time_range": 48,
  "digest_top_n": 15,
  "digest_language": "zh"
}
```

---

## 文件变更

### 新增文件

#### 1. `bin/config-sync.sh` — 核心同步脚本

**功能**：
- 读取 `env.json` → 生成 `settings.json` 和 `.mcp.json`
- `--provider <name>` 参数：先修改 `env.json` 中的 `provider` 字段再同步
- `--list` 参数：列出 `settings/` 中所有可用 provider
- `--dry-run` 参数：预览生成结果

**生成 settings.json 逻辑**：
1. 读取 `env.json` 中的 `provider` 字段
2. 从 `settings/{provider}-settings.json` 加载 provider 模板（model, apiUrl 等）
3. 合并稳定配置（permissions, enabledPlugins, statusLine, alwaysThinkingEnabled）
4. 注入 env 块：从 `env.json` 读取对应 provider 的 API key 填入 `env` 块
5. 输出到 `settings.json`

**生成 .mcp.json 逻辑**：
1. 基础包含 `context7` server
2. 如果 `n8n_api_key` 非空，自动添加 `n8n-mcp` server（注入 N8N_API_KEY 和 N8N_API_URL）
3. 输出到 `.mcp.json`

#### 2. `hooks/auto-config-sync.sh` — SessionStart 自动同步 hook

- 比较 `env.json` 和 `settings.json` 的修改时间
- 如果 `env.json` 更新，自动运行 `bin/config-sync.sh`
- 输出简洁提示："[config] env.json 已更新，自动同步配置..."

### 修改文件

#### 3. `env.json` + `env.example.json`

新增字段：
- `provider: "anthropic"` （默认值）
- 各 provider API keys（空字符串占位）

#### 4. `settings.json.example`

改为完整的生成模板说明，指导用户使用 `config-sync.sh` 而非手动编辑。

#### 5. `settings/README.md`

更新说明：
- settings/ 现在是模板库，不直接使用
- 切换 Provider 命令：`~/.claude/bin/config-sync.sh --provider deepseek`

#### 6. `setup.sh`（第 2 步）

将"从 settings.json.example 复制"改为：
1. 交互询问 AUTH_TOKEN（可选，代理模式不需要）
2. 交互询问 provider（列出可用列表）
3. 运行 `config-sync.sh` 生成 `settings.json` 和 `.mcp.json`

#### 7. `CLAUDE.md`

更新配置中心说明，突出 config-sync 工具的使用方式。

### 保持不变

- `settings/` 目录下 10 个 provider 配置文件（作为模板库，继续使用）
- `.mcp.json.example`（保留参考）
- 各 skill 的 `SKILL.md`（读取 env.json 的方式不变）
- `lib/common.sh`, `bin/sync-plugin-skills.sh`（无关）

---

## Provider 映射表

脚本需要知道：每个 provider 对应哪个模板文件，以及 env 块需要注入哪些 key：

| Provider | 模板文件 | env 注入 |
|----------|---------|---------|
| `anthropic` | （无模板，直连/代理模式）| `ANTHROPIC_BASE_URL` = `anthropic_base_url` |
| `deepseek` | `settings/deepseek-settings.json` | `ANTHROPIC_AUTH_TOKEN` = `deepseek_api_key` |
| `azure` | `settings/azure-settings.json` | `ANTHROPIC_AUTH_TOKEN` = `azure_api_key` |
| `openrouter` | `settings/openrouter-settings.json` | `ANTHROPIC_AUTH_TOKEN` = `openrouter_api_key` |
| `vertex` | `settings/vertex-settings.json` | `CLOUDSDK_CORE_PROJECT` = `vertex_project` |
| `litellm` | `settings/litellm-settings.json` | 无 key |
| `copilot` | `settings/copilot-settings.json` | 无 key |
| `qwen` | `settings/qwen-settings.json` | `ANTHROPIC_AUTH_TOKEN` = `qwen_api_key` |
| `siliconflow` | `settings/siliconflow-settings.json` | `ANTHROPIC_AUTH_TOKEN` = `siliconflow_api_key` |
| `minimax` | `settings/minimax.json` | `ANTHROPIC_AUTH_TOKEN` = `minimax_api_key` |

---

## 实现细节

### config-sync.sh 结构

```bash
#!/usr/bin/env bash
# 依赖: jq

CLAUDE_DIR="$HOME/.claude"
ENV_JSON="$CLAUDE_DIR/env.json"
SETTINGS_JSON="$CLAUDE_DIR/settings.json"
MCP_JSON="$CLAUDE_DIR/.mcp.json"

# 读取 env.json 字段
get_env() { jq -r "${1} // empty" "$ENV_JSON"; }

# 生成 settings.json
generate_settings() { ... }

# 生成 .mcp.json
generate_mcp() { ... }

# 主入口
case "$1" in
  --provider) update_provider "$2"; sync_all ;;
  --list)     list_providers ;;
  --dry-run)  DRY_RUN=1; sync_all ;;
  *)          sync_all ;;
esac
```

### auto-config-sync.sh（hook）

```bash
#!/usr/bin/env bash
ENV_JSON="$HOME/.claude/env.json"
SETTINGS_JSON="$HOME/.claude/settings.json"

# 只有 env.json 比 settings.json 新才同步
if [ "$ENV_JSON" -nt "$SETTINGS_JSON" ]; then
  echo "[config] env.json changed, syncing..."
  "$HOME/.claude/bin/config-sync.sh"
fi
```

---

## 执行顺序

1. 更新 `env.json` + `env.example.json`（新增 provider 字段）
2. 创建 `bin/config-sync.sh`（核心逻辑）
3. 创建 `hooks/auto-config-sync.sh`
4. 将 hook 注册到 `settings.json` 的 hooks 块
5. 更新 `setup.sh` 第 2 步
6. 更新 `settings/README.md`
7. 更新 `CLAUDE.md`
8. 运行 `config-sync.sh` 验证生成结果

---

## 验证

1. 运行 `bin/config-sync.sh --list` — 应列出所有可用 provider
2. 运行 `bin/config-sync.sh --dry-run` — 预览生成的 settings.json 和 .mcp.json
3. 运行 `bin/config-sync.sh` — 实际生成文件，对比原始 settings.json 确认配置正确
4. 修改 `env.json`（例如改 anthropic_base_url），下次启动 Claude 自动同步（hook 验证）
5. 运行 `bin/config-sync.sh --provider deepseek` — 确认切换后 settings.json 中的 apiUrl 正确
6. 验证 `.mcp.json` 包含 n8n-mcp server（当 n8n_api_key 非空时）
