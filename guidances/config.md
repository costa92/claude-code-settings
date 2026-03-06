# Claude Code 配置说明

## 概览

配置中心为 `~/.claude/env.json`（受 .gitignore 保护，不提交）。
所有 skill、agent、MCP 配置均从此文件读取。
模板文件为 `~/.claude/env.example.json`（可提交，所有值为空占位符）。

切换 provider 后，运行 `config-sync.sh` 自动生成 `settings.json` 和 `.mcp.json`。

---

## 自动切换逻辑

每次启动 Claude Code 时，SessionStart hook 自动执行以下检测：

```
启动
 ↓
检测 OAuth token（~/.claude/.credentials.json）
 ├─ 有效（subscriptionType 非空 + 到期 > 1小时）
 │   └─ 自动切换到 pro 模式
 └─ 失效 / 未登录
     ├─ 当前 provider 为 pro → 提示重新登录，回退到 fallback_provider
     └─ 当前已是其他 provider → 不做操作
```

相关字段：
- `provider` — 当前生效的认证模式
- `fallback_provider` — OAuth 失效时的回退 provider（默认 `anthropic`）

---

## 认证模式

### 模式一：Pro/Max 订阅（pro）

Anthropic 官方订阅，OAuth 登录，无需 API key。

```bash
# 1. 登录（浏览器授权）
claude login

# 2. 切换到 pro 模式（首次手动切换，之后自动维持）
~/.claude/bin/config-sync.sh --provider pro
```

env.json 最小配置：
```json
{
  "provider": "pro",
  "fallback_provider": "anthropic"
}
```

生成的 `settings.json` 中 `env` 字段不包含任何认证变量，由 Claude Code 内部使用 OAuth token。

---

### 模式二：API Key / 代理（anthropic）

使用 Anthropic 官方 API key，或对接第三方兼容代理（anyrouter、自建 litellm 等）。

```bash
~/.claude/bin/config-sync.sh --provider anthropic
```

env.json 配置示例：
```json
{
  "provider": "anthropic",
  "anthropic_base_url": "https://anyrouter.top",
  "anthropic_auth_token": "sk-xxx"
}
```

**认证字段规则（二选一，`anthropic_auth_token` 优先）：**

| env.json 字段 | 注入为环境变量 | 适用场景 |
|--------------|--------------|---------|
| `anthropic_auth_token` | `ANTHROPIC_AUTH_TOKEN` | 代理服务（anyrouter、openrouter-compatible）|
| `anthropic_api_key` | `ANTHROPIC_API_KEY` | Anthropic 官方直连 |

**模型覆盖字段（可选，留空不注入）：**

| env.json 字段 | 注入为环境变量 | 说明 |
|--------------|--------------|------|
| `anthropic_model` | `ANTHROPIC_MODEL` | 默认模型 |
| `anthropic_default_opus_model` | `ANTHROPIC_DEFAULT_OPUS_MODEL` | Opus 别名映射 |
| `anthropic_default_sonnet_model` | `ANTHROPIC_DEFAULT_SONNET_MODEL` | Sonnet 别名映射 |
| `anthropic_default_haiku_model` | `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Haiku 别名映射 |

---

### 模式三：第三方 Provider

```bash
~/.claude/bin/config-sync.sh --provider deepseek
```

| Provider | env.json 字段 | 模板文件 |
|----------|--------------|---------|
| `deepseek` | `deepseek_api_key` | settings/deepseek-settings.json |
| `azure` | `azure_api_key` | settings/azure-settings.json |
| `azure-foundry` | `azure_api_key` | settings/azure-foundry-settings.json |
| `openrouter` | `openrouter_api_key` | settings/openrouter-settings.json |
| `vertex` | `vertex_project` | settings/vertex-settings.json |
| `copilot` | —（本地代理，无需 key）| settings/copilot-settings.json |
| `litellm` | —（本地网关）| settings/litellm-settings.json |
| `qwen` | `qwen_api_key` | settings/qwen-settings.json |
| `siliconflow` | `siliconflow_api_key` | settings/siliconflow-settings.json |
| `minimax` | `minimax_api_key` | settings/minimax.json |

---

## env.json 字段全览

> 所有字段留空（`""`）表示不生效，不会注入对应环境变量。

```jsonc
{
  // ── 认证模式控制 ────────────────────────────────────────────────
  // provider: 当前使用的认证模式
  //   "pro"        → OAuth 登录，无需 key，启动时自动检测并切换
  //   "anthropic"  → API key 或代理模式
  //   其他值       → 对应第三方 provider（见第三方模式表格）
  "provider": "pro",

  // fallback_provider: OAuth 失效时自动回退的 provider
  //   建议设为 "anthropic"，确保有 token 时可用
  "fallback_provider": "anthropic",

  // ── Anthropic 认证（anthropic 模式使用）─────────────────────────
  // anthropic_auth_token: 代理服务 token，注入为 ANTHROPIC_AUTH_TOKEN
  //   优先级高于 anthropic_api_key
  //   适用：anyrouter.top、openrouter-compatible 等代理
  "anthropic_auth_token": "",

  // anthropic_api_key: 官方直连 API key，注入为 ANTHROPIC_API_KEY
  //   仅当 anthropic_auth_token 为空时生效
  //   适用：直连 api.anthropic.com
  "anthropic_api_key": "",

  // anthropic_base_url: API 请求地址，留空则直连官方
  //   示例："https://anyrouter.top"、"http://127.0.0.1:5000"
  "anthropic_base_url": "",

  // ── 模型覆盖（anthropic 模式，留空不注入）──────────────────────
  // 用于将 Claude Code 内置的 opus/sonnet/haiku 别名映射到具体模型
  "anthropic_model": "",                  // 注入为 ANTHROPIC_MODEL
  "anthropic_default_opus_model": "",     // 注入为 ANTHROPIC_DEFAULT_OPUS_MODEL
  "anthropic_default_sonnet_model": "",   // 注入为 ANTHROPIC_DEFAULT_SONNET_MODEL
  "anthropic_default_haiku_model": "",    // 注入为 ANTHROPIC_DEFAULT_HAIKU_MODEL

  // ── 第三方 Provider API Keys（对应 provider 时生效）─────────────
  "deepseek_api_key": "",
  "azure_api_key": "",
  "openrouter_api_key": "",
  "vertex_project": "",       // Vertex AI: GCP 项目 ID
  "litellm_api_key": "",
  "copilot_api_key": "",
  "qwen_api_key": "",
  "siliconflow_api_key": "",
  "minimax_api_key": "",

  // ── Skill 通用配置 ──────────────────────────────────────────────
  // gemini_api_key: nanobanana 图片生成（Gemini API）
  "gemini_api_key": "",

  // openai_*: OpenAI 兼容接口，供各 skill 直接调用（非 Claude Code 主模型）
  "openai_api_key": "",
  "openai_api_base": "",      // 示例："https://api.deepseek.com/v1"
  "openai_model": "",         // 示例："deepseek-chat"

  // image_*: 图片生成备用接口
  "image_api_key": "",
  "image_api_base": "",

  // ── 微信公众号（wechat-article-converter skill）─────────────────
  "wechat_appid": "",
  "wechat_secret": "",

  // ── n8n 自动化（n8n-mcp skill 及 MCP server）───────────────────
  // n8n_api_url 同时注入 settings.json env 和 .mcp.json
  "n8n_api_url": "http://localhost:5678/api/v1",
  "n8n_api_key": "",

  // ── ai-daily-digest skill 偏好 ──────────────────────────────────
  "digest_time_range": 48,    // 抓取时间范围（小时）
  "digest_top_n": 15,         // 保留条目数
  "digest_language": "zh"     // 输出语言：zh / en
}
```

---

## config-sync.sh 用法

```bash
# 查看所有可用 provider
~/.claude/bin/config-sync.sh --list

# 切换 provider 并立即同步
~/.claude/bin/config-sync.sh --provider pro
~/.claude/bin/config-sync.sh --provider anthropic
~/.claude/bin/config-sync.sh --provider deepseek

# 仅同步（不切换，重新生成 settings.json 和 .mcp.json）
~/.claude/bin/config-sync.sh

# 预览生成结果，不写入文件
~/.claude/bin/config-sync.sh --dry-run
```

同步后生成：
- `~/.claude/settings.json` — Claude Code 主配置（认证、模型、权限、插件）
- `~/.claude/.mcp.json` — MCP 服务器配置（context7、n8n-mcp）

---

## 快速操作

```bash
# 首次配置：复制模板并填写
cp ~/.claude/env.example.json ~/.claude/env.json

# Pro 会员：登录后自动生效
claude login

# 切换到代理模式（anyrouter 等）
# 先在 env.json 填写 anthropic_auth_token 和 anthropic_base_url
~/.claude/bin/config-sync.sh --provider anthropic

# 临时使用 deepseek（先填 deepseek_api_key）
~/.claude/bin/config-sync.sh --provider deepseek

# OAuth 失效时手动恢复
claude login && ~/.claude/bin/config-sync.sh --provider pro
```
