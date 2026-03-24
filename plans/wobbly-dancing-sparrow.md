# article-craft Pipeline 修复计划

## Context

article-craft 的 SKILL.md 文档描述了心跳监控、自检规则、状态传递等机制，但实际 Python 脚本中未实现这些功能。导致：
- 图片生成挂死无法检测
- Review 的 11 条规则靠 Claude 手动执行，容易遗漏
- Skill 间无状态传递，用户需多次提供文件路径
- RecoveryManager 已定义但未集成

## Phase 1：Critical（阻塞发布流程）

### Task 1.1：心跳集成到 generate_and_upload_images.py

**文件**: `~/.claude/plugins/article-craft/scripts/generate_and_upload_images.py`

- 添加 `--heartbeat` CLI 参数
- 导入 `~/.claude/skills/images/scripts/heartbeat.py` 的 `HeartbeatMonitor`
- 在 main() 中：`--heartbeat` 时启动心跳，在 finally 中停止
- 心跳写入 `{article_path}.heartbeat` 和 `{article_path}.lock`

### Task 1.2：RecoveryManager 集成到 main()

**文件**: 同上

- 在 `--process-file` 模式下自动创建备份 (`.bak`)
- 在 batch/parallel 执行前后调用 `record_step()`
- 每张图片完成后调用 `record_image_processed()`
- 成功时 `cleanup()`，失败时保留 `.state` 和 `.bak`

### Task 1.3：创建 review_selfcheck.py

**新文件**: `~/.claude/plugins/article-craft/scripts/review_selfcheck.py`

自动化 11 条自检规则的独立脚本：

| 规则 | 检测方式 |
|------|---------|
| 1. 红旗词 | regex 匹配 27 个词/短语 |
| 2. Hook 长度 | 提取首段，计算中文字符 ≤100 |
| 3. 禁用结尾 | 最后非空段匹配 7 个模式 |
| 4. Description | YAML frontmatter 解析，≤120 字 |
| 5. 反 AI 结构 | 连续段落开头词检测 + 第一人称计数 ≥2 |
| 6. 章节深度 | 按 ## 分节，每节 ≥2 个代码块 |
| 7. 重复图片 | 同 ## 下 alt-text 相似度检测 |
| 8. 外链 | 正文中裸 URL（非 markdown 链接格式）|
| 9. Mermaid 残留 | ` ```mermaid ` 检测 |
| 10. 独立参考部分 | `## 参考资料` 标题检测 |
| 11. 占位符残留 | `<!-- IMAGE:` / `<!-- SCREENSHOT:` CRITICAL GATE |

**CLI**:
```bash
python3 review_selfcheck.py /path/to/article.md          # 文本报告
python3 review_selfcheck.py /path/to/article.md --json    # JSON 输出
python3 review_selfcheck.py /path/to/article.md --gate-only  # 仅 Rule 11
```

**退出码**: 0 = 全部通过，1 = 有违规

### Task 1.4：创建 pipeline_state.py

**新文件**: `~/.claude/plugins/article-craft/scripts/pipeline_state.py`

简单的 JSON 状态文件管理：

```python
class PipelineState:
    # 状态文件: {article_dir}/.article-craft-state.json
    def mark_started(stage: str)
    def mark_completed(stage: str, result: Any)
    def mark_failed(stage: str, error: str)
    def is_stage_complete(stage: str) -> bool
    def get_all_stages() -> Dict
    def cleanup()
```

Stage 名称约定: `requirements`, `verify`, `write`, `screenshot`, `images`, `review_selfcheck`, `review_scorer`, `publish`

### Task 1.5：更新 SKILL.md 文档

- `images/SKILL.md`: 添加 `--heartbeat` 参数说明
- `review/SKILL.md`: Phase 1 中调用 `review_selfcheck.py` 脚本
- `orchestrator/SKILL.md`: 引用 pipeline_state.py 检查状态

## Phase 2：Important（功能完善）

### Task 2.1：publish 使用 SmartDirectoryMatcher

**文件**: `publish/SKILL.md`

添加指令：发布前先运行 SmartDirectoryMatcher 自动匹配目录，匹配成功则建议给用户确认，失败则询问。

### Task 2.2：content-reviewer 降级逻辑

**文件**: `review/SKILL.md`

添加显式降级：如果 `/content-reviewer` 不可用，使用 `review_selfcheck.py` 结果作为唯一质量门槛（11 条规则全通过 = 可发布）。

### Task 2.3：VerificationCache 集成

**文件**: `verify/SKILL.md`

添加指令：使用 config.py 的 VerificationCache 避免重复检查链接和命令。

## Phase 3：Nice to have

### Task 3.1：--resume 恢复支持

在 generate_and_upload_images.py 中添加 `--resume` 参数，读取 `.state` 文件跳过已处理图片。

### Task 3.2：文档补全

- images/SKILL.md 补充 `--probe`、`--keep-files` 参数说明
- 清理 config.py 中未使用的代码注释

## 关键文件清单

| 文件 | 操作 | Phase |
|------|------|-------|
| `plugins/article-craft/scripts/generate_and_upload_images.py` | 修改（心跳+Recovery） | 1 |
| `plugins/article-craft/scripts/review_selfcheck.py` | 新建 | 1 |
| `plugins/article-craft/scripts/pipeline_state.py` | 新建 | 1 |
| `skills/images/SKILL.md` | 更新 | 1 |
| `skills/review/SKILL.md` | 更新 | 1 |
| `skills/orchestrator/SKILL.md` | 更新 | 1 |
| `skills/publish/SKILL.md` | 更新 | 2 |
| `skills/verify/SKILL.md` | 更新 | 2 |

## 验证方案

1. **心跳**: `--heartbeat --dry-run` 验证文件创建和清理
2. **Recovery**: 故意使图片失败，验证 `.bak` 和 `.state` 保留
3. **review_selfcheck.py**: 用含已知违规的文章测试各规则检测
4. **pipeline_state.py**: 单元测试状态转换
5. **向后兼容**: 不带新参数运行，行为与修改前完全一致
6. **端到端**: `/article-craft --series` 运行完整管道，验证心跳监控 + 自检 + 状态传递
