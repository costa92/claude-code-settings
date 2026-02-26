# WeChat Article Converter - Installation Guide

## 依赖安装

### 自动安装（推荐）

```bash
cd ~/.claude/skills/wechat-article-converter
pip install -r requirements.txt
```

### 手动安装

```bash
pip install markdown premailer pygments beautifulsoup4 lxml cssutils
```

## 依赖说明

| 包名 | 版本 | 用途 |
|------|------|------|
| markdown | ≥3.4.0 | Markdown → HTML 转换 |
| premailer | ≥3.10.0 | CSS 内联处理（微信兼容） |
| Pygments | ≥2.15.0 | 代码语法高亮 |
| beautifulsoup4 | ≥4.12.0 | HTML 解析和处理 |
| lxml | ≥4.9.0 | XML/HTML 解析器 |
| cssutils | ≥2.6.0 | CSS 解析和处理 |

## 验证安装

```bash
python3 -c "import markdown, premailer, pygments; print('✅ 所有依赖已安装')"
```

## 故障排查

### 问题 1: pip install 失败

**解决方案**:
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题 2: lxml 编译失败

**macOS**:
```bash
brew install libxml2 libxslt
pip install lxml
```

**Ubuntu/Debian**:
```bash
sudo apt-get install libxml2-dev libxslt1-dev
pip install lxml
```

### 问题 3: 权限错误

```bash
# 使用 --user 安装到用户目录
pip install --user -r requirements.txt
```

---

## Go 后端（可选）

Go 后端提供草稿箱上传、AI 图片生成、写作助手、AI 去痕等扩展功能。

### 系统要求

- `curl` 或 `wget`（用于自动下载二进制文件）

### 安装方式

Go 后端 **无需手动安装**。首次运行 `md2wechat_backend.sh` 时会自动检测平台并下载对应的二进制文件到 `~/.cache/claude/bin/`。

```bash
# 首次运行会自动下载
bash ~/.claude/skills/wechat-article-converter/scripts/md2wechat_backend.sh --help
```

### 环境变量配置

以下环境变量用于 Go 后端的高级功能：

```bash
# 微信草稿箱上传（需要公众号开发者权限）
export WECHAT_APPID="your_appid"
export WECHAT_SECRET="your_secret"

# AI 图片生成（需要 OpenAI 兼容的图片 API）
export IMAGE_API_KEY="your_api_key"
export IMAGE_API_BASE="https://api.example.com/v1"
```

### 验证 Go 后端

```bash
bash ~/.claude/skills/wechat-article-converter/scripts/md2wechat_backend.sh --help
```

### 支持的平台

| 平台 | 架构 |
|------|------|
| macOS | Intel (amd64), Apple Silicon (arm64) |
| Linux | x64 (amd64), ARM64 |
| Windows | x64 (amd64) |

### 故障排查

**下载失败（网络问题）**
```bash
# 手动下载二进制文件
# 访问 https://github.com/geekjourneyx/md2wechat-skill/releases
# 下载对应平台的二进制文件到 ~/.cache/claude/bin/
```

**中国大陆网络问题**
脚本内置 jsDelivr CDN 镜像作为备选下载源，会自动尝试。
