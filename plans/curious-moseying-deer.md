# Plan: 合并 md2wechat 到 wechat-article-converter

## Context

项目中存在两个功能重叠的微信文章转换技能：
- **wechat-article-converter**：Python 引擎，7 个主题，成熟的 Markdown→WeChat HTML 转换、批量处理、预览服务器
- **md2wechat**：Go 二进制，独有的草稿箱上传、AI 图片生成、写作助手、去 AI 痕迹、AI 主题

两者触发条件重叠导致 Claude 选择不一致。目标：以 wechat-article-converter 为主，将 md2wechat 的独有功能作为扩展能力合并进来，然后移除 md2wechat。

## 合并策略

- Python 引擎保持不变（7 主题、转换、批量、预览）
- Go 二进制作为可选扩展后端（`md2wechat_backend.sh`）
- md2wechat 的 6 个参考文档复制到 wechat-article-converter
- SKILL.md 重写，统一文档所有功能
- 完成后删除 md2wechat 技能和插件注册

## 实施步骤

### Step 1: 复制文件到 wechat-article-converter

| 源文件 | 目标文件 | 操作 |
|--------|---------|------|
| `md2wechat/manifest.json` | `wechat-article-converter/manifest.json` | 复制 |
| `md2wechat/scripts/run.sh` | `wechat-article-converter/scripts/md2wechat_backend.sh` | 复制并重命名 |
| `md2wechat/references/themes.md` | `wechat-article-converter/references/md2wechat_themes.md` | 复制 |
| `md2wechat/references/wechat-api.md` | `wechat-article-converter/references/wechat_api.md` | 复制 |
| `md2wechat/references/image-syntax.md` | `wechat-article-converter/references/image_syntax.md` | 复制 |
| `md2wechat/references/humanizer.md` | `wechat-article-converter/references/humanizer.md` | 复制 |
| `md2wechat/references/writing-guide.md` | `wechat-article-converter/references/writing_styles.md` | 复制 |
| `md2wechat/references/html-guide.md` | `wechat-article-converter/references/wechat_html_spec.md` | 复制 |

### Step 2: 修复复制文件中的命令路径

所有复制的参考文档中：
- `bash skill/md2wechat/scripts/run.sh` → `bash ${SKILL_DIR}/scripts/md2wechat_backend.sh`
- `md2wechat` (裸命令) → `bash ${SKILL_DIR}/scripts/md2wechat_backend.sh`

### Step 3: 重写 SKILL.md

新结构：
```
---
name: wechat-article-converter
description: (更新描述，涵盖所有功能)
---

# WeChat Article Converter

## 核心功能（Python 引擎）      ← 保留现有内容
## 扩展功能（Go 后端）          ← 新增：草稿上传、AI图片、写作助手、去AI痕迹
## 主题选择                    ← 合并：7 Python主题 + 3 AI主题 + 6 API主题
## 使用方法                    ← 合并：Python CLI + Go CLI + 自然语言
## 工作流示例                  ← 合并两者场景
## 配置                       ← 合并：Python 依赖 + Go 环境变量
## CLI 命令参考                ← 合并两者命令
## 参考文档列表                ← 9 个参考文档
## 故障排除                    ← 合并两者
```

关键原则：扩展功能部分保持精简，详细信息引用 `references/` 文档。

### Step 4: 更新 INSTALL.md

添加 Go 后端可选依赖章节（curl/wget，环境变量说明）。

### Step 5: 删除 md2wechat 技能

```bash
git rm -r skills/md2wechat/
```

### Step 6: 清理插件注册

从 `plugins/installed_plugins.json` 移除 `"md2wechat@md2wechat-tools"` 条目。
可选：删除 `plugins/cache/md2wechat-tools/` 节省 ~25MB。

## 关键文件

- `skills/wechat-article-converter/SKILL.md` — 主要重写目标
- `skills/wechat-article-converter/INSTALL.md` — 小幅更新
- `skills/md2wechat/scripts/run.sh` — 复制源（Go 二进制包装器）
- `skills/md2wechat/manifest.json` — 复制源（版本管理）
- `skills/md2wechat/references/*` — 6 个参考文档复制源
- `plugins/installed_plugins.json` — 移除 md2wechat 条目

## 验证方法

1. Go 后端可用性：`bash skills/wechat-article-converter/scripts/md2wechat_backend.sh --help`
2. Python 引擎可用性：`python3 skills/wechat-article-converter/scripts/convert_to_wechat.py --help`
3. 确认 md2wechat 技能已删除
4. 确认插件注册已清理
5. 确认 SKILL.md 中无残留的 md2wechat 独立引用
