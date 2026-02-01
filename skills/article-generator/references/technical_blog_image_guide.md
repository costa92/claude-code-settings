# 技术博客配图指南

## 配图定位

技术博客的配图目标：
- **辅助理解**: 帮助读者理解技术概念和流程
- **提升可读性**: 打破大段文字,降低阅读疲劳
- **专业性**: 展现技术专业度,避免过度装饰
- **简洁性**: 信息密度高,避免冗余元素

---

## 配图类型

### 1. 封面图 (Cover Image)

**尺寸要求:** 16:9 比例 (1344x768px)

**设计原则:**
- **主题相关**: 与文章技术主题直接相关
- **简洁专业**: 避免花哨装饰,突出技术感
- **可选元素**: Logo、图标、简短标题
- **色调统一**: 与品牌风格一致

**类型选择:**
- **图标型**: 技术图标 + 简洁背景 (推荐)
- **架构型**: 简化的架构示意图
- **代码型**: 关键代码片段展示
- **抽象型**: 科技感几何图形/渐变

**示例提示词 (Gemini):**
```
Modern software development illustration, Docker container icon, 
blue and orange gradient background, minimalist tech style, 
clean professional design, 16:9 aspect ratio
```

---

### 2. 节奏图 (Rhythm Images)

**使用位置:** 每 400-600 字配一张

**尺寸要求:** 3:2 比例 (1248x832px)

**作用:** 
- 分隔章节,提供视觉呼吸点
- 强化关键概念
- 增强文章可读性

**类型:**
- **技术插画**: 抽象表达技术概念
- **流程示意**: 简化的流程图
- **对比图**: 方案对比、前后对比
- **数据可视化**: 简单的图表

**示例提示词:**
```
Software architecture diagram showing microservices communication,
flat design, technical illustration, blue and white color scheme,
simple and clean, 3:2 aspect ratio
```

---

### 3. 技术图表

#### 3.1 架构图

**目的:** 展示系统架构、组件关系

**设计要点:**
- 组件清晰标注
- 数据流向明确
- 层次关系清楚
- 避免过度复杂

**工具推荐:**
- Draw.io (免费)
- Excalidraw (手绘风格)
- Figma (专业设计)
- PlantUML (代码生成)

#### 3.2 流程图

**目的:** 展示操作流程、算法逻辑

**符号规范:**
- 矩形: 操作步骤
- 菱形: 判断分支
- 椭圆: 开始/结束
- 箭头: 流程方向

#### 3.3 时序图

**目的:** 展示组件间交互时序

**要点:**
- 角色/对象清晰
- 消息传递明确
- 时间顺序正确

#### 3.4 数据可视化

**图表类型:**
- 柱状图: 数据对比
- 折线图: 趋势变化
- 饼图: 占比关系 (少用)
- 表格: 参数对比

---

## AI 配图生成流程

### 步骤 1: 分析配图需求

根据技术文章内容识别需要配图的位置:

```markdown
1. 封面图 (必需)
   - 主题: 文章核心技术
   - 风格: 简洁科技感
   
2. 架构图 (如有系统设计)
   - 手绘或工具生成
   
3. 节奏图 (每 400-600 字)
   - 位置: 主要章节开头
   - 数量: 3000 字文章约 4-6 张
   
4. 技术图表 (如有复杂概念)
   - 流程图
   - 时序图
   - 数据对比
```

### 步骤 2: 选择配图风格

**技术博客推荐风格:**

- ✅ **扁平插画风** (推荐)
  - 现代、简洁、专业
  - 适合: 技术概念、产品介绍
  
- ✅ **极简抽象风**
  - 几何图形、线条、渐变
  - 适合: 封面图、节奏图

- ✅ **手绘风** (Excalidraw 风格)
  - 亲和力强、易于理解
  - 适合: 架构图、流程图

- ⚠️ **3D 渲染风** (慎用)
  - 高端但可能过于花哨
  - 适合: 特定主题文章

- ❌ **摄影风** (不推荐)
  - 与技术主题关联弱
  - 除非是人物访谈类

### 步骤 3: 编写 Gemini 提示词

**提示词结构:**
```
[主体内容] + [风格] + [色调] + [质量要求] + [尺寸比例]
```

**封面图示例:**
```
Modern cloud computing concept, server cluster illustration,
flat design style, blue and purple gradient background,
minimalist professional tech aesthetic, clean composition,
high quality, 16:9 aspect ratio
```

**节奏图示例:**
```
Database replication architecture diagram,
PostgreSQL master-slave setup illustration,
flat design technical drawing, blue and white color scheme,
simple clean lines, professional style,
3:2 aspect ratio
```

**抽象概念图示例:**
```
Abstract representation of API integration,
connecting nodes with data flow,
minimalist geometric design, tech blue color,
professional illustration, clean background,
3:2 aspect ratio
```

### 步骤 4: 生成与优化

**使用 nanobanana.py 生成:**

```bash
# 封面图 (16:9)
python3 scripts/nanobanana.py \
  --prompt "Your cover image prompt here" \
  --size 1344x768 \
  --output images/article_cover.jpg

# 节奏图 (3:2)
python3 scripts/nanobanana.py \
  --prompt "Your rhythm image prompt here" \
  --size 1248x832 \
  --output images/article_pic1.jpg
```

**批量生成 (推荐):**

创建 `images_config.json`:
```json
{
  "images": [
    {
      "name": "封面图",
      "prompt": "Docker containerization concept, modern tech...",
      "aspect_ratio": "16:9",
      "filename": "docker_guide_cover.jpg"
    },
    {
      "name": "架构示意",
      "prompt": "Microservices architecture diagram...",
      "aspect_ratio": "3:2",
      "filename": "docker_guide_pic1.jpg"
    }
  ]
}
```

执行:
```bash
python3 scripts/generate_and_upload_images.py \
  --config images_config.json \
  --resolution 2K
```

### 步骤 5: 后期处理

**尺寸优化:**
- 确保图片宽度统一 (如 1344px 或 1248px)
- 压缩文件大小 (< 500KB)

**上传 CDN:**
- 使用 PicGo 自动上传
- 或手动上传到 GitHub/图床

**嵌入文章:**
```markdown
![Docker 容器化概念](https://cdn.example.com/docker_guide_cover.jpg)
```

---

## 配图风格指南

### 颜色方案

**技术类主色调:**
- **蓝色系**: 科技、专业、可信 (推荐)
- **黑白灰**: 极简、高级感
- **蓝橙搭配**: 对比鲜明、现代
- **深色系**: 代码、终端主题

**避免:**
- ❌ 过于鲜艳的颜色 (粉红、亮黄)
- ❌ 混乱的多色组合
- ❌ 低对比度 (影响可读性)

### 字体使用

**图片中的文字 (如有):**
- 使用无衬线字体 (Sans-serif)
- 字号足够大 (至少 24px)
- 高对比度 (白底黑字或深色底浅色字)
- 避免艺术字体

---

## 配图数量建议

| 文章长度 | 封面图 | 节奏图 | 技术图表 | 总计 |
|---------|-------|-------|---------|------|
| 500-1000 字 | 1 | 1-2 | 0-1 | 2-4 |
| 1000-2000 字 | 1 | 2-3 | 1-2 | 4-6 |
| 2000-3000 字 | 1 | 4-5 | 2-3 | 7-9 |
| 3000+ 字 | 1 | 6-8 | 3-4 | 10-13 |

**原则:**
- 避免过度配图 (影响加载速度)
- 避免配图过少 (单调乏味)
- 每 400-600 字至少一张图

---

## 技术图表工具推荐

### 架构图/流程图
1. **Draw.io** (推荐)
   - 免费开源
   - 丰富的图标库
   - 支持导出多种格式

2. **Excalidraw**
   - 手绘风格
   - 简洁易用
   - 在线使用

3. **Mermaid** (代码生成)
   ```mermaid
   graph LR
       A[用户] --> B[API 网关]
       B --> C[微服务A]
       B --> D[微服务B]
   ```

4. **PlantUML** (代码生成)
   ```plantuml
   @startuml
   User -> API: 发送请求
   API -> Database: 查询数据
   Database -> API: 返回结果
   API -> User: 响应
   @enduml
   ```

### 数据可视化
1. **Charts.js** (Web)
2. **Matplotlib** (Python)
3. **D3.js** (复杂可视化)
4. **Google Charts** (简单图表)

---

## 配图检查清单

发布前检查:

- [ ] **尺寸规范**
  - [ ] 封面图 16:9 (1344x768px)
  - [ ] 节奏图 3:2 (1248x832px)
  
- [ ] **内容质量**
  - [ ] 图片清晰,无模糊/像素化
  - [ ] 与文章主题相关
  - [ ] 配图数量适中 (400-600字/图)
  
- [ ] **技术规范**
  - [ ] 使用 CDN 链接 (非本地路径)
  - [ ] 图片大小合理 (< 500KB)
  - [ ] Alt 文本描述清晰
  
- [ ] **风格统一**
  - [ ] 全文配图风格一致
  - [ ] 色调协调
  - [ ] 字体统一 (如有文字)
  
- [ ] **版权合规**
  - [ ] AI 生成或自己创作
  - [ ] 工具生成图表
  - [ ] 标注来源 (如使用第三方素材)

---

## Markdown 引用格式

标准格式:

```markdown
# 文章标题

![封面图：Docker 容器化指南](https://cdn.example.com/cover.jpg)

> [!abstract] 核心要点
> 文章摘要...

---

## 架构设计

![架构示意图：微服务通信流程](https://cdn.example.com/pic1.jpg)

**架构说明:**
- 组件A: 功能描述
- 组件B: 功能描述

---

## 安装配置

![流程图：安装步骤](https://cdn.example.com/pic2.jpg)

...
```

**命名规范:**
- 封面: `{article_slug}_cover.jpg`
- 节奏图: `{article_slug}_pic1.jpg`, `pic2.jpg` ...
- 技术图: `{article_slug}_architecture.jpg`, `flow.jpg` ...

---

## 最佳实践总结

1. **简洁第一**: 配图应简洁专业,避免花哨
2. **技术相关**: 确保配图与技术主题紧密相关
3. **适度使用**: 不要过度配图或过少配图
4. **统一风格**: 全文配图保持视觉风格一致
5. **CDN 托管**: 使用 CDN 确保加载速度
6. **Alt 文本**: 为图片添加描述性 alt 文本
7. **版权意识**: 使用合法来源的图片

---

**最后更新**: 2026-01-31
