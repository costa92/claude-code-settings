# 🔧 故障排查指南

## 图片生成失败问题

### 问题症状

运行 article-generator 技能时，出现以下错误信息：

```
⚠️ 图片生成失败
图片生成过程中遇到错误，原因是未配置 Gemini API Key 或配置无效
```

但实际上环境变量中已经设置了 `GEMINI_API_KEY`。

---

### 根本原因

**环境变量作用域问题 + 文件路径问题**

最常见的原因是**使用了相对路径而非绝对路径**，导致脚本找不到文件。

---

### 解决方案

#### 方案 A: 使用绝对路径（必须）⭐

图片生成脚本**必须使用绝对路径**：

**对于文章文件：**

```bash
# Step 1: 获取绝对路径
realpath my_article.md
# 输出: /home/hellotalk/onedrive/docs/my_article.md

# Step 2: 使用绝对路径调用脚本
python3 /home/hellotalk/.claude/skills/article-generator/scripts/generate_and_upload_images.py \
  --process-file /home/hellotalk/onedrive/docs/my_article.md \
  --resolution 2K
```

**常见错误：**

```bash
# ❌ 错误 - 相对路径
--process-file ./article.md
--process-file article.md

# ✅ 正确 - 绝对路径
--process-file /home/hellotalk/onedrive/docs/article.md
```

---

#### 方案 B: 配置环境变量（如果确实缺失）

如果 `GEMINI_API_KEY` 确实未配置：

**检查当前值：**

```bash
env | grep GEMINI_API_KEY
```

**如果为空，设置环境变量：**

```bash
# 添加到 ~/.zshrc (Zsh 用户)
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc

# 或添加到 ~/.bashrc (Bash 用户)
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

**获取 API Key：**

1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 创建新的 API Key
3. 按照上述命令添加到配置文件

---

### 验证配置

#### 1. 验证环境变量

```bash
# 检查环境变量是否设置
env | grep GEMINI_API_KEY
```

期望输出：

```
GEMINI_API_KEY=AIzaSyBUMY8bn1wxtHieDwWqAiM7wc356cJ9GD0
```

#### 2. 验证文件路径

```bash
# 检查文件是否存在
ls -la /path/to/your/article.md

# 如果找不到，使用 realpath 获取正确路径
realpath article.md
```

#### 3. 测试图片生成

```bash
# 测试单张图片生成
cd /home/hellotalk/.claude/skills/article-generator/scripts
python3 nanobanana.py \
  --prompt "test image" \
  --size 1024x1024 \
  --output /tmp/test.jpg
```

期望输出：

```
Generating image (size: 1024x1024) with prompt: test image
Image saved to: /tmp/test.jpg
```

---

### 常见错误

#### 错误 1: `ValueError: Missing GEMINI_API_KEY`

**原因：** 未设置 API Key

**解决：**

```bash
# 创建配置
echo 'export GEMINI_API_KEY="your_key_here"' >> ~/.zshrc
source ~/.zshrc
```

---

#### 错误 2: `❌ 文件不存在: ./article.md`

**原因：** 使用了相对路径，脚本找不到文件

**解决：**

```bash
# 获取绝对路径
realpath article.md

# 使用绝对路径
python3 generate_and_upload_images.py \
  --process-file /absolute/path/to/article.md
```

---

#### 错误 3: `API Key 无效 (401 Unauthorized)`

**原因：** API Key 错误或已过期

**解决：**

1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 重新生成 API Key
3. 更新环境变量

---

#### 错误 4: `quota exceeded (429 Too Many Requests)`

**原因：** API 配额用尽或请求频率过高

**解决：**

1. 检查 API 配额：[Google Cloud Console](https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas)
2. 等待配额重置（通常每分钟/每天重置）
3. 考虑升级到付费计划

---

### 配置优先级

脚本按以下顺序查找 API Key（优先级从高到低）：

```
1. 环境变量 GEMINI_API_KEY (推荐) ⭐
   ↓ (如果不存在)
2. ~/.nanobanana.env 文件 (备用)
   ↓ (如果不存在)
3. 报错: "Missing GEMINI_API_KEY"
```

**推荐做法：** 使用环境变量方式（添加到 `~/.zshrc` 或 `~/.bashrc`），这是标准做法。

---

### 安全建议

1. **保护 API Key 隐私：**

   ```bash
   # 确保 shell 配置文件权限正确
   chmod 600 ~/.zshrc  # 或 ~/.bashrc

   # 不要将 API Key 提交到 Git 仓库
   # 确保 ~/.zshrc 不在版本控制中
   ```

2. **使用环境变量的最佳实践：**

   ```bash
   # ✅ 推荐: 添加到 shell 配置文件
   echo 'export GEMINI_API_KEY="your_key"' >> ~/.zshrc
   source ~/.zshrc

   # ❌ 不推荐: 临时设置（重启终端失效）
   export GEMINI_API_KEY="AIza..."
   ```

3. **定期轮换 API Key：**
   - 每 90 天轮换一次 API Key
   - 发现泄露后立即撤销并重新生成

---

### 相关文档

- [Google Gemini API 文档](https://ai.google.dev/docs)
- [API Key 管理](https://aistudio.google.com/app/apikey)
- [定价和配额](https://ai.google.dev/pricing)

---

### 仍然有问题？

如果按照上述步骤仍然无法解决问题，请检查：

1. **网络连接：** 确保能访问 `generativelanguage.googleapis.com`
2. **Python 依赖：** 运行 `pip install -r requirements.txt`
3. **日志输出：** 查看完整的错误堆栈信息
4. **API 状态：** 访问 [Google Cloud Status](https://status.cloud.google.com/)
5. **文件路径：** 使用 `realpath` 确认文件的绝对路径

---

### 快速诊断命令

运行以下命令进行快速诊断：

```bash
#!/bin/bash
echo "=== 快速诊断 ==="
echo ""

# 1. 检查环境变量
echo "1. GEMINI_API_KEY:"
if [ -n "$GEMINI_API_KEY" ]; then
  echo "   ✅ 已设置"
else
  echo "   ❌ 未设置"
fi
echo ""

# 2. 检查依赖
echo "2. 脚本依赖:"
python3 /home/hellotalk/.claude/skills/article-generator/scripts/generate_and_upload_images.py --check
echo ""

# 3. 测试图片生成
echo "3. 测试图片生成:"
python3 /home/hellotalk/.claude/skills/article-generator/scripts/nanobanana.py \
  --prompt "test" --size 1024x1024 --output /tmp/test_diagnosis.jpg
echo ""

echo "=== 诊断完成 ==="
```

---

*最后更新: 2026-01-31*
