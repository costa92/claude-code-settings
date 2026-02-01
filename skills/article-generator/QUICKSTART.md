# 快速开始 (5分钟)

让你在 5 分钟内开始使用 article-generator 生成第一篇技术文章。

---

## 📋 前提条件

- Python 3.8+
- 已安装 pip
- (可选) PicGo - 用于图片上传

---

## 第一步: 安装配置 (2分钟)

### 1. 安装 Python 依赖

```bash
cd ~/.claude/skills/article-generator
pip install -r requirements.txt
```

### 2. 配置 Gemini API Key

**获取 API Key**: https://aistudio.google.com/apikey

```bash
# 方法 1: 环境变量 (推荐)
export GEMINI_API_KEY="your_api_key_here"
echo 'export GEMINI_API_KEY="your_key"' >> ~/.zshrc
source ~/.zshrc

# 方法 2: 配置文件
cat > ~/.nanobanana.env << 'EOF'
GEMINI_API_KEY=your_api_key_here
EOF
```

### 3. 验证安装

```bash
# 测试图片生成
python3 scripts/nanobanana.py \
  --prompt "test image" \
  --size 1024x1024 \
  --output /tmp/test.jpg

# 看到 "Image saved to: /tmp/test.jpg" 说明配置成功
```

---

## 第二步: 生成第一篇文章 (2分钟)

### 在 Cursor/Claude 中调用

```
@article-generator 写一篇关于 Docker 入门的技术文章
```

### 或者指定更详细的需求

```
@article-generator 写一篇 Docker 容器化实战教程
- 目标受众: 开发者
- 文章长度: 2000-3000字
- 需要配图: 封面 + 节奏图
```

### AI 会自动完成

1. ✅ 询问你的具体需求（受众、长度、配图）
2. ✅ 验证所有技术内容的准确性
3. ✅ 生成完整的 Markdown 文章
4. ✅ 生成并上传配图（如果需要）
5. ✅ 保存到当前目录

**输出文件**: `./docker-tutorial.md`

---

## 第三步: (可选) 配置图片自动上传 (1分钟)

### 安装 PicGo

```bash
# macOS
brew install picgo

# 其他系统
# 参考: https://picgo.github.io/PicGo-Core-Doc/
```

### 配置图床

```bash
picgo set uploader
```

**推荐图床**:
- GitHub (免费, 需要 token)
- SM.MS (免费, 无需配置)
- 七牛云 (需要账号)

**GitHub 配置示例**:
```bash
# 需要设置:
# - repo: username/repo-name
# - branch: main
# - token: ghp_xxxxx (需要 repo 权限)
# - path: images/
```

配置完成后，文章生成时会自动上传图片到 CDN。

---

## 🎯 你已经准备好了！

### 现在你可以

**生成不同类型的文章**:
```
# 教程型
@article-generator 写一篇 Kubernetes 部署教程

# 对比型
@article-generator 对比 Docker 和 Podman 的优劣

# 原理解析型
@article-generator 深入解析 React 渲染机制

# 工具介绍型
@article-generator 介绍 FastAPI 框架的使用
```

**自定义生成选项**:
- 指定受众: "面向初学者" / "面向开发者" / "面向架构师"
- 控制长度: "500-1000字" / "2000-3000字" / "4000+字"
- 配图选择: "需要配图" / "仅占位符" / "纯文字"

---

## 📖 进阶使用

### 手动生成图片

如果文章已经生成, 想单独生成图片:

```bash
# 1. 获取文章的绝对路径
realpath your-article.md
# 输出: /Users/you/docs/your-article.md

# 2. 生成并上传图片
python3 ~/.claude/skills/article-generator/scripts/generate_and_upload_images.py \
  --process-file /Users/you/docs/your-article.md \
  --resolution 2K
```

### 批量生成图片

创建 `images_config.json`:

```json
{
  "images": [
    {
      "name": "封面图",
      "prompt": "Modern Docker technology, container illustration, blue gradient",
      "aspect_ratio": "16:9",
      "filename": "docker_cover.jpg"
    },
    {
      "name": "架构图",
      "prompt": "Microservices architecture diagram, flat design",
      "aspect_ratio": "3:2",
      "filename": "docker_pic1.jpg"
    }
  ]
}
```

执行生成:

```bash
python3 ~/.claude/skills/article-generator/scripts/generate_and_upload_images.py \
  --config images_config.json \
  --resolution 2K
```

---

## 🔍 查看示例

查看完整的生成示例:

```bash
cd ~/.claude/skills/article-generator/examples
ls -la
```

**示例文章**:
- `docker-tutorial/` - Docker 容器化教程
- `kubernetes-guide/` - Kubernetes 部署指南
- `python-api-tutorial/` - Python API 开发

---

## ❓ 遇到问题？

### 常见问题快速解决

**1. 图片生成失败 - "Missing GEMINI_API_KEY"**

```bash
# 检查环境变量
env | grep GEMINI_API_KEY

# 如果为空, 重新设置
export GEMINI_API_KEY="your_key"
echo 'export GEMINI_API_KEY="your_key"' >> ~/.zshrc
source ~/.zshrc
```

**2. 图片生成失败 - "文件不存在"**

原因: 使用了相对路径

解决:
```bash
# 使用绝对路径
realpath article.md  # 获取绝对路径
# 然后使用绝对路径调用脚本
```

**3. PicGo 上传失败**

```bash
# 检查配置
cat ~/.picgo/config.json

# 重新配置
picgo set uploader

# 测试上传
echo "test" > test.txt
picgo upload test.txt
```

**更多问题**: 查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📚 了解更多

- **[完整功能指南](SKILL.md)** - 详细的功能说明和最佳实践
- **[详细工作流程](WORKFLOW.md)** - 内容验证机制和生成流程
- **[问题排查](TROUBLESHOOTING.md)** - 常见问题和解决方案
- **[安装配置](INSTALL.md)** - 详细的安装说明
- **[技术博客写作指南](references/technical_blog_style_guide.md)** - 写作规范

---

## 🎉 恭喜！

你已经掌握了 article-generator 的基础使用。

**下一步建议**:
1. 尝试生成不同类型的文章
2. 查看 [examples/](examples/) 了解输出效果
3. 阅读 [SKILL.md](SKILL.md) 了解高级功能

**需要帮助？**
- 查看文档: [SKILL.md](SKILL.md)
- 查看示例: [examples/](examples/)
- 问题排查: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**开始写作吧！** 🚀
