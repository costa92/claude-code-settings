---
name: defuddle
description: Extract clean markdown content from web pages using Defuddle CLI, removing clutter and navigation to save tokens. Use instead of WebFetch when the user provides a URL to read or analyze, for online documentation, articles, blog posts, or any standard web page.
---

# Defuddle

Use Defuddle CLI to extract clean readable content from web pages. Prefer over WebFetch for standard web pages — it removes navigation, ads, and clutter, reducing token usage.

If not installed: `npm install -g defuddle-cli`

## Usage

Always use `--md` for markdown output:

```bash
defuddle parse <url> --md
```

Save to file:

```bash
defuddle parse <url> --md -o content.md
```

Extract specific metadata:

```bash
defuddle parse <url> -p title
defuddle parse <url> -p description
defuddle parse <url> -p domain
```

## Output formats

| Flag | Format |
|------|--------|
| `--md` | Markdown (default choice) |
| `--json` | JSON with both HTML and markdown |
| (none) | HTML |
| `-p <name>` | Specific metadata property |

## Troubleshooting

### TLS 证书错误: `unable to get local issuer certificate`

**症状**: `defuddle parse <url> --md` 报错 `unable to get local issuer certificate`

**根因**: Node.js 不使用 macOS 系统证书库，内置 CA 包可能缺少某些根证书（如 Comodo `AAA Certificate Services`）。

**修复**:

```bash
# 1. 导出 macOS 系统根证书
mkdir -p ~/.ssl
security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain > ~/.ssl/macos_system_roots.pem
security find-certificate -a -p /Library/Keychains/System.keychain >> ~/.ssl/macos_system_roots.pem

# 2. 写入 shell 配置（永久生效）
echo 'export NODE_EXTRA_CA_CERTS="$HOME/.ssl/macos_system_roots.pem"' >> ~/.zshrc
source ~/.zshrc

# 3. 验证
defuddle parse https://example.com --json
```

### 连接重置: `ECONNRESET`

**症状**: 部分网站报 `ECONNRESET`，但 `curl` 能访问

**根因**: defuddle-cli 不走 `http_proxy`/`https_proxy` 代理。被墙的网站无法直接访问。

**替代方案**: 用 `curl` 下载后本地解析，或使用 WebFetch。
