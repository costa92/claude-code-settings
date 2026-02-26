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
# 输出: /path/to/your/my_article.md

# Step 2: 使用绝对路径调用脚本
python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py \
  --process-file /path/to/your/my_article.md \
  --resolution 2K
```

**常见错误：**

```bash
# ❌ 错误 - 相对路径
--process-file ./article.md
--process-file article.md

# ✅ 正确 - 绝对路径
--process-file /path/to/your/article.md
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
cd ${SKILL_DIR}/scripts
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
python3 ${SKILL_DIR}/scripts/generate_and_upload_images.py --check
echo ""

# 3. S3 检查 (可选)
if python3 -c "import boto3" 2>/dev/null; then
    echo "3. S3 支持: ✅ boto3 已安装"
else
    echo "3. S3 支持: ⚪ boto3 未安装 (仅支持 PicGo)"
fi
echo ""

# 4. 测试图片生成
echo "4. 测试图片生成:"
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "test" --size 1024x1024 --output /tmp/test_diagnosis.jpg
echo ""

echo "=== 诊断完成 ==="
```

---

## 并行模式 `--parallel` 崩溃问题

### 问题症状

使用 `--parallel` 标志批量生成图片时，图片生成和上传成功后脚本崩溃：

```
NameError: name 'args' is not defined
```

错误出现在 `generate_and_upload_parallel()` 函数内部，上传完成后尝试删除本地文件时。

---

### 根本原因

`generate_and_upload_parallel()` 函数内部使用了 `args.keep_files`（全局 argparse 变量），但该函数作为独立函数不应依赖全局变量。

**Bug 位置：**
- 函数签名（约第 885 行）：缺少 `keep_files` 参数
- 函数内部（约第 1122 行）：引用 `args.keep_files` 而非本地参数
- 调用处（约第 1655 行）：未传递 `keep_files` 参数

---

### 解决方案

**已在 2026-02-26 修复。** 如果你使用的是修复前的版本：

#### 临时解决方案（不修改代码）

当并行模式崩溃但图片已生成时，手动上传：

```bash
# 检查已生成的本地图片
ls -la images/*.jpg

# 手动上传到 CDN
picgo upload images/*.jpg

# 手动删除本地文件
rm images/*.jpg
```

#### 永久修复

修改 `generate_and_upload_images.py` 三处：

1. **函数签名**（约第 885 行）— 添加 `keep_files` 参数：
```python
def generate_and_upload_parallel(configs: List[ImageConfig],
                                   upload: bool = True,
                                   resolution: str = "2K",
                                   max_workers: int = 2,
                                   fail_fast: bool = True,
                                   model: str = "gemini-3-pro-image-preview",
                                   keep_files: bool = False) -> Dict:
```

2. **函数内部**（约第 1122 行）— 使用本地参数：
```python
# 之前: if not args.keep_files:
if not keep_files:
```

3. **调用处**（约第 1655 行）— 传递参数：
```python
results = generate_and_upload_parallel(
    configs=configs,
    upload=not args.no_upload,
    resolution=args.resolution,
    max_workers=args.max_workers,
    fail_fast=not args.continue_on_error,
    model=args.model,
    keep_files=args.keep_files  # 新增
)
```

---

## S3 上传问题

### `RuntimeError: boto3 is not installed`

**原因**: 启用了 S3 但未安装 Python SDK。

**解决**:
```bash
pip install boto3
```

### `S3 upload failed: An error occurred (403)`

**原因**: Access Key 或 Secret Key 错误，或权限不足。

**解决**:
1. 检查 `~/.article-generator.conf` 中的密钥配置。
2. 确认 Bucket 名称正确。
3. 确认 IAM 用户有 `PutObject` 权限。

---

*最后更新: 2026-01-31*
