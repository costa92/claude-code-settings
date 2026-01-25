# article-generator skill 安装指南

## 前置要求
- Python 3.8+
- pip
- PicGo（用于图片上传）

## 安装步骤

### 1. 安装 Python 依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
创建 `~/.nanobanana.env` 文件：
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

获取 Gemini API Key：https://aistudio.google.com/app/apikey

### 3. 测试图片生成
```bash
python3 scripts/nanobanana.py \
  --prompt "测试图片：现代办公场景" \
  --size 1344x768 \
  --output test.jpg
```

如果看到 `Image saved to: test.jpg`，说明配置成功。

### 4. 配置 PicGo（可选）
如果需要自动上传图片到 CDN，请安装并配置 PicGo：
- macOS: `brew install picgo`
- 配置 GitHub 图床或其他图床

## 使用
```bash
/article-generator 生成文章主题
```

## 故障排查

### 图片生成失败
1. 检查 GEMINI_API_KEY 是否正确
2. 检查网络连接
3. 运行测试命令验证

### 依赖安装失败
```bash
# 升级 pip
pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```
