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
