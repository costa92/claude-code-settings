# PicGo 图床配置指南

## 概述

PicGo 是一个开源的图床上传工具，支持多种图床服务。本文档介绍如何配置 PicGo CLI 用于文章配图上传。

## 安装 PicGo CLI

```bash
# 使用 npm 全局安装
npm install -g picgo

# 验证安装
picgo --version
```

## 支持的图床服务

### 1. 腾讯云 COS（推荐）

**优势**：
- 稳定可靠，国内访问速度快
- 新用户有免费额度
- 价格相对便宜

**配置步骤**：

1. 访问腾讯云 COS 控制台创建存储桶
2. 获取 SecretId 和 SecretKey
3. 配置 PicGo：

```bash
picgo set uploader tcyun
```

按提示输入：
- **SecretId**: 你的腾讯云 SecretId
- **SecretKey**: 你的腾讯云 SecretKey
- **Bucket**: 存储桶名称（如 my-images-1234567890）
- **AppId**: 你的 AppId
- **Area**: 地域（如 ap-guangzhou）
- **Path**: 存储路径（如 article-images/）
- **CustomUrl**: 自定义域名（可选）

**或者直接编辑配置文件** `~/.picgo/config.json`：

```json
{
  "picBed": {
    "uploader": "tcyun",
    "tcyun": {
      "secretId": "YOUR_SECRET_ID",
      "secretKey": "YOUR_SECRET_KEY",
      "bucket": "my-images-1234567890",
      "appId": "1234567890",
      "area": "ap-guangzhou",
      "path": "article-images/",
      "customUrl": ""
    }
  },
  "picgoPlugins": {}
}
```

### 2. 阿里云 OSS

**配置步骤**：

```bash
picgo set uploader aliyun
```

输入：
- **AccessKey ID**: 阿里云 AccessKey ID
- **AccessKey Secret**: 阿里云 AccessKey Secret
- **Bucket**: 存储空间名称
- **Area**: 地域（如 oss-cn-hangzhou）
- **Path**: 存储路径
- **CustomUrl**: 自定义域名（可选）

**配置文件示例**：

```json
{
  "picBed": {
    "uploader": "aliyun",
    "aliyun": {
      "accessKeyId": "YOUR_ACCESS_KEY_ID",
      "accessKeySecret": "YOUR_ACCESS_KEY_SECRET",
      "bucket": "my-bucket",
      "area": "oss-cn-hangzhou",
      "path": "images/",
      "customUrl": ""
    }
  }
}
```

### 3. 七牛云 Kodo

**配置步骤**：

```bash
picgo set uploader qiniu
```

**配置文件示例**：

```json
{
  "picBed": {
    "uploader": "qiniu",
    "qiniu": {
      "accessKey": "YOUR_ACCESS_KEY",
      "secretKey": "YOUR_SECRET_KEY",
      "bucket": "my-bucket",
      "url": "http://cdn.example.com",
      "area": "z0",
      "path": "images/"
    }
  }
}
```

### 4. GitHub（免费方案）

**优势**：
- 完全免费
- 配置简单

**劣势**：
- 国内访问可能较慢
- 单文件限制 25MB

**配置步骤**：

1. 创建 GitHub 仓库（如 `my-image-hosting`）
2. 生成 Personal Access Token（权限选择 `repo`）
3. 配置 PicGo：

```bash
picgo set uploader github
```

输入：
- **Repo**: 用户名/仓库名（如 username/my-image-hosting）
- **Branch**: 分支名（通常为 main 或 master）
- **Token**: GitHub Personal Access Token
- **Path**: 存储路径（如 images/）
- **CustomUrl**: 自定义域名（可选，如使用 jsDelivr CDN）

**配置文件示例**：

```json
{
  "picBed": {
    "uploader": "github",
    "github": {
      "repo": "username/my-image-hosting",
      "branch": "main",
      "token": "ghp_xxxxxxxxxxxxxxxxxxxx",
      "path": "images/",
      "customUrl": "https://cdn.jsdelivr.net/gh/username/my-image-hosting"
    }
  }
}
```

**使用 jsDelivr CDN 加速**：
- CustomUrl 格式：`https://cdn.jsdelivr.net/gh/用户名/仓库名`
- 国内访问速度更快

### 5. 又拍云

**配置文件示例**：

```json
{
  "picBed": {
    "uploader": "upyun",
    "upyun": {
      "bucket": "my-bucket",
      "operator": "operator-name",
      "password": "operator-password",
      "url": "http://cdn.example.com",
      "path": "images/"
    }
  }
}
```

## 使用方法

### 1. 上传单张图片

```bash
picgo upload /path/to/image.jpg
```

### 2. 上传多张图片

```bash
picgo upload /path/to/image1.jpg /path/to/image2.jpg
```

### 3. 设置默认图床

```bash
picgo use uploader
```

然后选择默认使用的图床。

### 4. 查看配置

```bash
picgo config
```

## 与脚本集成

我们的 `generate_and_upload_images.py` 脚本会自动调用 PicGo CLI 上传图片：

```bash
# 生成并上传
python3 generate_and_upload_images.py --config images_config.json

# 只生成不上传
python3 generate_and_upload_images.py --config images_config.json --no-upload

# 指定分辨率
python3 generate_and_upload_images.py --config images_config.json --resolution 4K
```

## 配置文件示例

创建 `images_config.json`：

```json
{
  "images": [
    {
      "name": "封面图",
      "prompt": "清晨阳光透过窗户洒进房间，一个人在窗边伸展身体迎接新的一天，温暖的金色光线，充满希望和活力，手绘插画风格，温暖色调，侧面视角，治愈系氛围",
      "aspect_ratio": "16:9",
      "filename": "cover.jpg"
    },
    {
      "name": "配图1-清晨桌面",
      "prompt": "清晨第一缕阳光洒在桌面上，咖啡杯冒着热气，旁边是打开的笔记本，窗外是渐亮的天空，温暖治愈的氛围，手绘插画风格，暖色调，俯视45度角，宁静美好",
      "aspect_ratio": "3:2",
      "filename": "pic1.jpg"
    },
    {
      "name": "配图2-高效工作",
      "prompt": "年轻人在整洁明亮的书桌前专注工作，电脑屏幕发出柔和光线，桌面有绿植和笔记本，充满活力和专注的氛围，扁平插画风格，蓝色和橙色配色，侧面视角，简洁现代",
      "aspect_ratio": "3:2",
      "filename": "pic2.jpg"
    }
  ]
}
```

## 环境变量配置

确保设置了必要的环境变量：

```bash
# Gemini API Key
export GEMINI_API_KEY="your-gemini-api-key"

# 可选：PicGo 配置路径
export PICGO_CONFIG_PATH="~/.picgo/config.json"
```

建议将这些环境变量添加到 `~/.zshrc` 或 `~/.bashrc`：

```bash
# 编辑配置文件
vim ~/.zshrc

# 添加以下内容
export GEMINI_API_KEY="your-gemini-api-key"

# 重新加载配置
source ~/.zshrc
```

## 故障排查

### 1. PicGo 上传失败

**问题**：上传返回错误

**解决方案**：
- 检查配置文件 `~/.picgo/config.json` 是否正确
- 验证图床服务的 API Key/Token 是否有效
- 确认网络连接正常
- 查看 PicGo 日志：`picgo log`

### 2. 图片生成失败

**问题**：Gemini API 调用失败

**解决方案**：
- 检查 `GEMINI_API_KEY` 环境变量是否设置
- 验证 API Key 是否有效
- 检查提示词是否包含敏感内容
- 简化提示词重试

### 3. 配置文件位置

PicGo 配置文件默认位置：
- macOS/Linux: `~/.picgo/config.json`
- Windows: `C:\Users\用户名\.picgo\config.json`

### 4. 权限问题

```bash
# 给脚本添加执行权限
chmod +x ~/.claude/skills/article-generator/scripts/generate_and_upload_images.py
```

## 最佳实践

### 1. 图床选择建议

**公众号文章推荐**：
- 首选：腾讯云 COS（国内稳定，速度快）
- 备选：阿里云 OSS
- 免费方案：GitHub + jsDelivr CDN

**个人博客推荐**：
- GitHub（免费且够用）
- 七牛云（有免费额度）

### 2. 目录规划

建议在图床中创建清晰的目录结构：

```
article-images/
├── 2024/
│   ├── 01/
│   │   ├── article-1/
│   │   │   ├── cover.jpg
│   │   │   ├── pic1.jpg
│   │   │   └── pic2.jpg
│   │   └── article-2/
│   └── 02/
└── templates/
```

在配置中设置 path：
```json
{
  "path": "article-images/2024/01/article-1/"
}
```

### 3. 命名规范

- 使用有意义的文件名：`cover.jpg`, `section1.jpg`
- 避免中文文件名（可能导致URL编码问题）
- 使用小写字母和连字符：`early-morning-sunrise.jpg`

### 4. 图片优化

上传前优化图片：
- 压缩图片减小文件大小（使用 TinyPNG 等工具）
- 调整尺寸到合适大小（封面 900x383px，配图宽度 900px）
- 保持清晰度的同时控制文件大小（建议 < 500KB）

### 5. CDN 加速

- 腾讯云/阿里云：配置 CDN 加速域名
- GitHub：使用 jsDelivr 或其他 CDN 服务
- 自定义域名：配置 CNAME 指向图床

## 完整工作流程

```bash
# 1. 安装 PicGo CLI
npm install -g picgo

# 2. 配置图床（以腾讯云为例）
picgo set uploader tcyun

# 3. 设置环境变量
export GEMINI_API_KEY="your-api-key"

# 4. 准备配置文件
cat > images_config.json << 'EOF'
{
  "images": [
    {
      "name": "封面图",
      "prompt": "清晨阳光...",
      "aspect_ratio": "16:9",
      "filename": "cover.jpg"
    }
  ]
}
EOF

# 5. 运行脚本生成并上传
python3 ~/.claude/skills/article-generator/scripts/generate_and_upload_images.py \
  --config images_config.json \
  --resolution 2K \
  --output image_urls.md

# 6. 查看结果
cat image_urls.md
```

## 参考资源

- [PicGo 官方文档](https://picgo.github.io/PicGo-Doc/)
- [腾讯云 COS 文档](https://cloud.tencent.com/document/product/436)
- [阿里云 OSS 文档](https://help.aliyun.com/product/31815.html)
- [GitHub Token 创建指南](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
