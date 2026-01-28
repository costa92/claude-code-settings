# WeChat Article Converter - 主题与代码高亮配置说明

## 主题配色方案

每个主题都配置了匹配的代码语法高亮样式，确保整体视觉协调一致。

### 核心主题配置

| 主题 | 主色调 | 代码高亮样式 | 适用场景 |
|------|--------|-------------|----------|
| **tech** | 科技蓝 #4a90e2 | `default` | 技术文档、教程 |
| **warm** | 温暖橙 #d9730d | `autumn` | 生活分享、情感文章 |
| **simple** | 黑白灰 | `bw` (black & white) | 严肃评论、极简主义 |

### MD2 扩展主题配置

| 主题 | 主色调 | 代码高亮样式 | 适用场景 |
|------|--------|-------------|----------|
| **md2_classic** | Vue 绿 #42b983 | `friendly` | 清新文档、技术博客 |
| **md2_dark** | 深色 #2c3e50 | `monokai` | 极客风格、终端主题 |
| **md2_purple** | 优雅紫 #7b16ff | `material` | 现代设计、优雅风格 |

---

## Pygments 代码高亮样式详解

### Tech 主题 - `default`
```
- 关键字: 绿色 (#008000)
- 字符串: 红色 (#BA2121)
- 注释: 灰色 (#408080)
- 背景: 浅灰 (#f6f8fa)
特点: 清晰、专业、适合技术文档
```

### Warm 主题 - `autumn`
```
- 关键字: 深橙 (#AA5D1F)
- 字符串: 棕色 (#AA5500)
- 注释: 灰褐色 (#888888)
- 背景: 米色调
特点: 温暖、柔和、适合生活类内容
```

### Simple 主题 - `bw` (Black & White)
```
- 关键字: 黑色加粗
- 字符串: 黑色
- 注释: 灰色
- 背景: 白色/浅灰
特点: 极简、聚焦内容、适合严肃主题
```

### MD2 Classic 主题 - `friendly`
```
- 关键字: 蓝绿色 (#007020)
- 字符串: 深红 (#BB4444)
- 注释: 浅灰 (#60A0B0)
- 背景: 浅色
特点: 友好、清新、VuePress 风格
```

### MD2 Dark 主题 - `monokai`
```
- 关键字: 粉红 (#F92672)
- 字符串: 黄色 (#E6DB74)
- 注释: 灰色 (#75715E)
- 背景: 深灰 (#272822)
特点: 经典暗色、Sublime Text 默认主题
```

### MD2 Purple 主题 - `material` ⭐ 推荐
```
- 关键字: 紫罗兰 (#C792EA)
- 字符串: 绿松石 (#C3E88D)
- 注释: 蓝灰 (#546E7A)
- 数字: 橙色 (#F78C6C)
- 背景: 深色 (#263238)
特点: Material Design 配色，与紫色主题完美搭配
```

---

## 如何切换代码高亮样式

### 方法 1: 使用预设主题（推荐）
```bash
# 自动应用匹配的代码高亮
python3 scripts/convert_to_wechat.py article.md --theme md2_purple
```

### 方法 2: 自定义样式映射
编辑 `wechat_style.py`:
```python
THEME_PYGMENTS_STYLES = {
    "md2_purple": "material"  # 改为其他样式: monokai, vim, fruity 等
}
```

### 方法 3: 查看所有可用样式
```bash
python3 -c "from pygments.styles import get_all_styles; print(list(get_all_styles()))"
```

常用样式推荐：
- `monokai` - Sublime Text 经典
- `material` - Material Design
- `dracula` - Dracula 主题
- `github-dark` - GitHub 暗色
- `nord` - Nord 北欧风
- `one-dark` - Atom One Dark
- `solarized-dark` - Solarized 暗色
- `paraiso-dark` - Paraiso 暗色

---

## 主题选择建议

### 技术文章
- **首选**: `tech` (科技蓝) - 专业、清晰
- **备选**: `md2_classic` (经典绿) - 清新、友好

### 生活分享
- **首选**: `warm` (温暖橙) - 亲切、温馨
- **备选**: `simple` (极简黑白) - 聚焦内容

### 设计类文章
- **首选**: `md2_purple` (优雅紫) - 现代、设计感
- **备选**: `md2_dark` (终端黑) - 极客风格

### 极简主义
- **首选**: `simple` (黑白) - 纯粹、简洁
- **备选**: `tech` (科技蓝) - 专业、克制

---

## 对比示例

### 原始配置（不协调）
```
主题: md2_purple (紫色)
代码: default (绿色关键字)
问题: 紫色主题 + 绿色代码 = 视觉冲突
```

### 优化后（协调）
```
主题: md2_purple (紫色)
代码: material (紫罗兰关键字 + 现代配色)
优势: 整体协调、视觉统一、Material Design 风格
```

---

## 技术实现

代码位置：
- 主题 CSS: `wechat_style.py` - THEMES 字典
- 样式映射: `wechat_style.py` - THEME_PYGMENTS_STYLES 字典
- 应用逻辑: `convert_to_wechat.py` - WeChatConverter 类

关键代码：
```python
# 主题选择
self.pygments_style = THEME_PYGMENTS_STYLES.get(theme_name, "default")

# 应用到 Markdown 转换
extension_configs={
    "codehilite": {
        "pygments_style": self.pygments_style
    }
}
```

---

## 版本信息

**Version**: 1.1 (Code Theme Enhancement 2026-01-28)

**Changes**:
- 为每个主题配置了匹配的代码高亮样式
- md2_purple 使用 Material Design 配色
- 提升整体视觉协调性
- 输出时显示使用的代码高亮样式
