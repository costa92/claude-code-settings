# 添加更多微信公众号主题

## Context
当前系统只有 3 个主题（简洁白、科技蓝、暖色调），用户希望在同步到微信公众号时有更多风格选择。需要新增约 13 个主题覆盖不同风格，并修改启动逻辑将 `themes/` 目录下的所有 JSON 主题自动种入数据库。

## 改动

### 1. 新增 13 个主题 JSON 文件（`themes/` 目录）

| 文件名 | display_name | 风格 |
|--------|-------------|------|
| elegant.json | 优雅黑 | 黑色主调，金色点缀，高端感 |
| github.json | GitHub 风 | 模仿 GitHub Markdown 渲染风格 |
| juejin.json | 掘金蓝 | 掘金社区风格，蓝色主调 |
| chinese-red.json | 中国红 | 红色主题，适合节日/文化类文章 |
| minimalist.json | 极简灰 | 极度简洁，大量留白 |
| ocean.json | 深海蓝 | 深蓝渐进色系，适合技术深度文章 |
| forest.json | 森林绿 | 绿色自然系 |
| lavender.json | 薰衣草紫 | 柔和紫色调 |
| sunset.json | 日落橙 | 暖橙色调 |
| rose.json | 玫瑰粉 | 粉色柔和系 |
| notion.json | Notion 风 | 模仿 Notion 简洁排版 |
| dark-monokai.json | 暗夜代码 | 深色背景，代码优先风格 |
| vintage.json | 复古报刊 | 报纸/杂志印刷风 |

每个主题需定义完整的 style keys（wrapper, h1-h3, p, a, strong, em, code_inline, code_block, code_block_wrapper, code_block_header, blockquote, ul, ol, li, img, table, th, td, hr, del）。

### 2. 修改 `api/app/app.go` - 启动时自动种入所有主题

将 `ensureDefaultTheme()` 改为 `ensureBuiltinThemes()`：
- 用 `converter.LoadThemes("themes/")` 加载 `themes/` 目录下所有 JSON 文件
- 对每个主题，检查数据库是否已存在（by name），不存在则创建
- 已存在的主题不覆盖（保留用户可能的自定义修改）

关键文件：
- `api/app/app.go` (line 152, 214-225)
- `api/converter/theme.go` - LoadThemes() 已存在，可直接复用

### 3. 更新测试

更新 `api/converter/converter_test.go` 和相关测试确保新主题可加载。

## 验证
1. `go test ./converter/...` - 确保所有测试通过
2. `go build ./...` - 确保编译通过
3. 启动服务后调用 `GET /api/v1/themes` 确认所有主题已加载
