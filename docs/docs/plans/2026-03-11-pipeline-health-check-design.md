# 内容流水线静态健康检查设计

**日期**: 2026-03-11
**状态**: 已批准

## 背景

完成 article-generator 图片流程 14 项修复后，需对内容流水线全链路 6 个 skill 进行静态健康检查，确保各环节配置完整、引用正确。

## 检查范围

6 个 skill：content-planner → article-generator → content-reviewer → wechat-seo-optimizer → wechat-article-converter → content-repurposer

## 检查矩阵

| 检查项 | 说明 |
|--------|------|
| 文件引用完整性 | SKILL.md 中引用的 .md/.py 文件是否存在 |
| 脚本依赖 | Python scripts 的 import 是否可用 |
| 交叉引用一致性 | 引用其他 skill 的名称是否与实际目录名匹配 |
| 调用链方向 | A→B 中 A 提到 B 的方式是否正确 |
| 配置引用 | env.json 字段引用是否与 env.example.json 模板一致 |

## 并行分组

- **Agent 1**: content-planner + content-reviewer
- **Agent 2**: article-generator + wechat-seo-optimizer
- **Agent 3**: wechat-article-converter + content-repurposer

## 输出格式

每个 skill 输出：通过/问题数 + 问题列表，最终合并为汇总表。
