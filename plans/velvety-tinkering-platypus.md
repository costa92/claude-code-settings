# 修复：微信草稿上传图片丢失问题

## 背景

当前将 Markdown 文章上传到微信公众号草稿箱需要多个手动步骤，且存在以下问题：
1. **外部图片被微信过滤**：文章中的 CDN 图片链接（如 `cdn.jsdelivr.net`）在上传后不显示
2. **封面图需手动处理**：需单独上传封面图获取 `media_id`，再手动构建 JSON
3. **内容提取繁琐**：需手动提取 `wechat-container` div、移除 h1 标题
4. **每次上传都要重复大量 Python/Shell 操作**

## 方案：创建 `upload_draft.py` 一键上传脚本

新建 `/home/hellotalk/.claude/skills/wechat-article-converter/scripts/upload_draft.py`，一条命令完成全流程：

```bash
python3 upload_draft.py article.md --theme coffee
```

### 自动化流程

```
article.md
    ↓ Step 1: 解析 YAML frontmatter（title, description）
    ↓ Step 2: 调用 convert_to_wechat.py 转换 HTML（--no-preview-mode）
    ↓ Step 3: 扫描 HTML 中所有 <img> 外部链接
    ↓ Step 4: 逐个上传图片到微信素材库（调用 Go 后端 download_and_upload）
    ↓ Step 5: 替换 HTML 中的图片 URL（CDN → mmbiz.qpic.cn）
    ↓ Step 6: 提取封面图 media_id，从内容中移除封面图
    ↓ Step 7: 移除 h1 标题（避免与草稿标题重复）
    ↓ Step 8: 构建 draft JSON，调用 Go 后端 create_draft 上传
    ↓
微信公众号草稿箱 ✅
```

## 修改文件

### 1. 新建 `scripts/upload_draft.py`

**核心逻辑**：

```python
# CLI 参数
upload_draft.py <md_file> [--theme coffee] [--author 月影] [--cover cover.jpg]

# 主要函数
parse_frontmatter(md_path)      # 解析 YAML 获取 title/description
convert_markdown(md_path, theme) # 调用现有 convert_to_wechat.py
upload_image(url)                # 调用 Go 后端 download_and_upload，解析 JSON 响应
process_images(html)             # 扫描 img、逐个上传、替换 URL、提取封面
build_and_upload_draft(html, metadata)  # 构建 JSON、调用 create_draft
```

**关键设计决策**：

| 决策 | 选择 | 原因 |
|------|------|------|
| 图片上传顺序 | **逐个串行** | 避免 Go 后端临时文件 `/tmp/md2wechat_download_.jpg` 竞态 |
| 封面识别 | alt 含"封面" 或第一张图 | 符合文章约定 |
| 封面处理 | 上传后从正文移除 | 微信单独显示封面 |
| h1 处理 | 从正文移除 | 草稿 JSON 有独立 title 字段 |
| 默认作者 | "月影" | SKILL.md 规定 |
| JSON 解析 | 提取 Go 后端输出中最后一个 `{"success":...}` 块 | Go 后端混合输出 log + JSON |

### 2. 更新 `SKILL.md`

在 SKILL.md 中添加：
- `upload_draft.py` 命令说明和参数
- 更新"草稿箱上传"章节，推荐使用新脚本
- 更新 Trigger Behavior，草稿上传时优先使用此脚本

## 验证方式

```bash
# 测试完整流程
python3 scripts/upload_draft.py anthropic-prompt-cache-bug.md --theme coffee

# 预期输出：
# 1. 转换成功日志
# 2. 逐个图片上传进度
# 3. 草稿上传成功，返回 media_id
# 4. 微信后台可见草稿，图片正常显示
```
