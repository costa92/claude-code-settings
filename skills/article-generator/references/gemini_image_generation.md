# Gemini 图片生成指南（通过 nanobanana Python 脚本）

## 概述

使用 Google Gemini API 通过 nanobanana Python 脚本直接生成文章配图，无需手动使用第三方AI绘图工具。

## nanobanana Python 脚本

### 脚本位置
```bash
${SKILL_DIR}/scripts/nanobanana.py
# 或绝对路径
~/.claude/skills/article-generator/scripts/nanobanana.py
```

### 功能
通过 Google Gemini API 生成图片并保存到本地

### 命令格式

```bash
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "图片描述提示词" \
  --size 1344x768 \
  --output images/filename.jpg
```

### 参数说明

| 参数 | 必需 | 说明 | 默认值 |
|------|------|------|--------|
| `--prompt` | ✅ | 图片描述提示词（中英文均可） | - |
| `--size` | ❌ | 图片尺寸（见下表支持的尺寸） | 768x1344 |
| `--output` | ❌ | 输出文件路径 | nanobanana-<UUID>.png |
| `--model` | ❌ | Gemini 模型 | gemini-3-pro-image-preview |
| `--resolution` | ❌ | 分辨率质量（1K/2K/4K） | 1K |

### 支持的尺寸（size 参数）

**CRITICAL**: 只能使用以下精确尺寸，Gemini API 不支持其他尺寸！

| 尺寸 | 宽高比 | 用途 |
|------|--------|------|
| `1344x768` | 16:9 | **封面图**（推荐，可后期裁剪为 900x383） |
| `1248x832` | 3:2 | **正文横图**（适合大多数场景） |
| `1152x896` | 5:4 | 架构图、流程图 |
| `1024x1024` | 1:1 | 正文方图、产品图 |
| `832x1248` | 2:3 | 正文竖图、手机截图 |
| `768x1344` | 9:16 | 移动端竖屏 |
| `1536x672` | 21:9 | 超宽图、全景图 |
| `896x1152` | 4:5 | - |
| `1184x864` | 4:3 | - |
| `864x1184` | 3:4 | - |

**注意**：
- ❌ 不支持 `900x383` (2.35:1) - 微信公众号封面比例
- ✅ 使用 `1344x768` (16:9) 生成后手动裁剪为 900x383

## 使用流程

### Step 1: 创建图片目录

**CRITICAL**: 必须在生成图片前创建目录！

```bash
mkdir -p images
```

### Step 2: 分析文章配图需求

根据文章内容确定：
- 封面图：1张（1344x768，后期裁剪为 900x383）
- 正文配图：每 300-500 字一张（1248x832 或 1024x1024）
- 配图类型：场景图、情绪图、概念图

### Step 3: 编写图片提示词

**提示词结构**：
```
[主体内容] + [风格描述] + [色调] + [氛围] + [视角/构图]
```

**示例**：
```
清晨阳光透过窗户洒进房间，一个人在窗边伸展身体，
温暖的金色光线，充满希望和活力，手绘插画风格，
温暖色调，侧面视角，治愈系氛围
```

### Step 4: 生成图片（使用 Bash 工具）

**CRITICAL**: 必须使用 Bash 工具调用 Python 脚本，不是 MCP 工具！

#### 示例 1：生成封面图

```bash
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "清晨阳光透过窗户洒进房间，一个人在窗边伸展身体迎接新一天，温暖的金色光线，充满希望和活力，手绘插画风格，温暖色调，侧面视角，治愈系氛围" \
  --size 1344x768 \
  --output images/cover.jpg
```

#### 示例 2：生成正文配图

```bash
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "整洁明亮的书桌，电脑屏幕发出柔和光线，桌上有笔记本和咖啡，窗外是城市景观，专注高效的氛围，扁平插画风格，蓝色和橙色配色" \
  --size 1248x832 \
  --output images/pic1.jpg
```

#### 示例 3：批量生成

```bash
# 封面图
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "..." \
  --size 1344x768 \
  --output images/cover.jpg

# 正文图 1
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "..." \
  --size 1248x832 \
  --output images/pic1.jpg

# 正文图 2
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "..." \
  --size 1248x832 \
  --output images/pic2.jpg
```

### Step 5: 验证图片生成

```bash
ls -lh images/
# 应显示所有生成的图片文件
```

### Step 6: 上传到 CDN

```bash
# 使用 picgo 上传所有图片
picgo upload images/*.jpg

# picgo 会返回 CDN URL，复制这些 URL
```

### Step 7: 在文章中引用

```markdown
![封面图](https://cdn.jsdelivr.net/gh/username/repo/images/cover.jpg)

...

![配图1](https://cdn.jsdelivr.net/gh/username/repo/images/pic1.jpg)
```

### Step 8: 清理本地文件

```bash
rm -rf images/
```

## 配图风格指南

### 生活方式类（如"早起的力量"）

**整体风格**: 手绘插画风格、温暖治愈

**提示词模板**:
```
[场景描述]，手绘插画风格，温暖色调（金黄色、橙色、米色），
[情绪描述]，柔和光线，治愈系氛围
```

**色调关键词**:
- 温暖色调: warm tones, golden yellow, orange, beige
- 清新色调: fresh colors, light blue, mint green
- 莫兰迪色: Morandi colors, muted tones, pastel

**风格关键词**:
- 手绘插画: hand-drawn illustration, illustrated style
- 扁平插画: flat illustration, flat design
- 极简风格: minimalist style, simple and clean
- 水彩风格: watercolor style, soft and dreamy

### 科技类

**整体风格**: 极简现代、科技感

**提示词模板**:
```
[科技元素]，极简风格，蓝色和白色配色，现代科技感，
简洁构图，专业商务
```

**关键词**:
- 几何图形: geometric shapes
- 科技线条: technology lines, circuit patterns
- 数据可视化: data visualization, infographic

### 金融类

**整体风格**: 专业稳重、可信

**提示词模板**:
```
[金融场景]，专业摄影风格，深蓝和金色配色，稳重可信，
商务氛围，高端质感
```

### 教育类

**整体风格**: 温馨活泼、启发性

**提示词模板**:
```
[教育场景]，温馨插画风格，多彩但不花哨，活泼友好，
学习氛围，鼓励成长
```

## 常见配图场景提示词

### 封面图（1344x768，16:9）

#### 场景1: 清晨阳光
```
清晨阳光透过窗户洒进房间，一个人在窗边伸展身体迎接新一天，
温暖的金色光线，充满希望和活力，手绘插画风格，
温暖色调（金黄橙色米白），侧面视角，治愈系氛围，柔和光影
```

#### 场景2: 工作学习
```
整洁明亮的书桌，电脑屏幕发出柔和光线，桌上有笔记本和咖啡，
窗外是城市景观，专注高效的氛围，扁平插画风格，
蓝色和橙色配色，俯视角度，现代简约
```

#### 场景3: 成长突破
```
一个人站在山顶俯瞰风景，双臂张开拥抱阳光，
象征突破和成长，励志氛围，手绘插画风格，
温暖明亮色调，背面视角，充满力量
```

### 正文配图（1248x832，3:2）

#### 场景4: 冥想平静
```
一个人盘腿坐在瑜伽垫上冥想，简约室内环境，
清晨柔和自然光，平静祥和氛围，极简插画风格，
莫兰迪色系（浅蓝米色淡粉），正面视角，留白构图，宁静治愈
```

#### 场景5: 团队协作
```
几个年轻人围坐讨论，桌上有笔记本和咖啡，
氛围轻松友好，扁平插画风格，明亮色调，
俯视角度，团队合作精神
```

#### 场景6: 阅读学习
```
温馨的阅读角落，舒适的椅子，书架，一杯茶，
柔和的灯光，安静专注的氛围，手绘插画风格，
暖色调（米色浅黄），侧面视角，温暖舒适
```

#### 场景7: 运动健康
```
公园晨跑，阳光洒在身上，绿树环绕，
充满活力的氛围，扁平插画风格，
明亮温暖色调（橙黄天蓝绿色），侧面视角，动感活力
```

## 提示词优化技巧

### 1. 具体化描述
❌ 差: "一个人工作"
✅ 好: "年轻人在整洁明亮的书桌前专注工作，电脑屏幕发出柔和光线"

### 2. 明确风格
❌ 差: "好看的图片"
✅ 好: "手绘插画风格，温暖色调，治愈系氛围"

### 3. 包含情绪
❌ 差: "清晨的房间"
✅ 好: "清晨阳光透过窗户，充满希望和活力的氛围"

### 4. 指定视角
❌ 差: "办公室场景"
✅ 好: "俯视角度的整洁办公桌，简洁现代"

### 5. 色调统一
同一篇文章的所有配图应使用统一的色调关键词：
- 温暖色调: warm tones, golden, orange
- 清新色调: fresh, light blue, pastel
- 专业色调: professional, deep blue, gray

## 错误处理

### 常见错误及解决方案

**错误 1**: `FileNotFoundError: [Errno 2] No such file or directory: 'images/cover.jpg'`
- **原因**: images 目录不存在
- **解决**: `mkdir -p images`

**错误 2**: `ValueError: Invalid size: 900x383`
- **原因**: Gemini API 不支持该尺寸
- **解决**: 使用 `1344x768`，后期裁剪为 900x383

**错误 3**: SSL/Network 错误
- **原因**: 网络连接问题或 API 限流
- **解决**: 等待 2-3 秒后重试，最多重试 3 次

**错误 4**: `Missing GEMINI_API_KEY`
- **原因**: 未配置环境变量
- **解决**: 检查 `~/.nanobanana.env` 文件

### 重试策略

图片生成失败时的重试流程：

```bash
# 第 1 次尝试
python3 ${SKILL_DIR}/scripts/nanobanana.py --prompt "..." --size 1344x768 --output images/cover.jpg

# 如果失败，等待 2 秒后重试
sleep 2
python3 ${SKILL_DIR}/scripts/nanobanana.py --prompt "..." --size 1344x768 --output images/cover.jpg

# 如果还失败，等待 3 秒后重试
sleep 3
python3 ${SKILL_DIR}/scripts/nanobanana.py --prompt "..." --size 1344x768 --output images/cover.jpg

# 3 次重试后仍失败 → 询问用户是否继续
```

## 最佳实践

### 1. 提前规划
- 先列出所有需要的配图
- 统一风格和色调关键词
- 确定每张图的尺寸

### 2. 使用唯一文件名
- ❌ 错误: `cover.jpg`, `pic1.jpg` (多篇文章会冲突)
- ✅ 正确: `ollama_glm4_cover.jpg`, `unsloth_pic1.jpg`
- 使用文章标题 slug 作为前缀

### 3. 测试生成
- 先生成 1-2 张测试
- 确认风格符合预期
- 再批量生成其余配图

### 4. 保持一致性
- 同一篇文章使用相同的风格关键词
- 色调保持统一（如都用"温暖色调"）
- 视角可以变化但不要过于跳跃

### 5. 命名规范
```
{article_slug}_cover.jpg          # 封面图
{article_slug}_pic1.jpg           # 第一张正文图
{article_slug}_pic2.jpg           # 第二张正文图
{article_slug}_pic3.jpg           # 第三张正文图
```

示例：
```
ollama_glm4_cover.jpg
ollama_glm4_pic1.jpg
ollama_glm4_pic2.jpg
```

## 完整示例：生成一篇文章的所有配图

```bash
# Step 1: 创建图片目录
mkdir -p images

# Step 2: 生成封面图（16:9）
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "清晨阳光透过窗户洒进房间，一个人在窗边伸展身体迎接新一天，温暖的金色光线，充满希望和活力，手绘插画风格，温暖色调（金黄橙色米白），侧面视角，治愈系氛围，柔和光影" \
  --size 1344x768 \
  --output images/early_rising_cover.jpg

# Step 3: 生成正文图 1（3:2）
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "清晨第一缕阳光洒在桌面上，咖啡杯冒着热气，旁边是打开的笔记本，窗外是渐亮的天空，温暖治愈的氛围，手绘插画风格，暖色调（橙黄米色），俯视45度角，宁静美好" \
  --size 1248x832 \
  --output images/early_rising_pic1.jpg

# Step 4: 生成正文图 2（3:2）
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "年轻人在整洁明亮的书桌前专注工作，电脑屏幕发出柔和光线，桌面有绿植和笔记本，充满活力和专注的氛围，扁平插画风格，蓝色和橙色配色，侧面视角，简洁现代" \
  --size 1248x832 \
  --output images/early_rising_pic2.jpg

# Step 5: 生成正文图 3（1:1）
python3 ${SKILL_DIR}/scripts/nanobanana.py \
  --prompt "一个人盘腿坐在瑜伽垫上冥想，简约室内环境，清晨柔和自然光，平静祥和氛围，极简插画风格，莫兰迪色系（浅蓝米色淡粉），正面视角，留白构图，宁静治愈" \
  --size 1024x1024 \
  --output images/early_rising_pic3.jpg

# Step 6: 验证所有图片已生成
ls -lh images/

# Step 7: 上传到 CDN
picgo upload images/*.jpg

# Step 8: 清理本地文件
rm -rf images/
```

## 总结

使用 nanobanana Python 脚本可以：
- ✅ 直接生成图片，无需手动操作
- ✅ 支持 10 种精确尺寸，适配不同场景
- ✅ 中文提示词友好
- ✅ 自动保存到指定路径
- ✅ 与文章生成流程无缝集成

**推荐工作流**：
1. 创建 images 目录
2. 分析文章配图需求
3. 编写提示词（参考模板）
4. 使用 Bash 工具调用 nanobanana.py 批量生成
5. 验证所有图片
6. 上传到 CDN
7. 在文章中引用 CDN URL
8. 清理本地文件
