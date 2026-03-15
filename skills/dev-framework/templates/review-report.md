# 代码审查报告

> 由 Reviewer Agent 生成 | {日期}

## 结论: {PASS / FAIL}

## 审查范围

{审查的文件列表和变更概要}

## 编译与测试验证

| 检查项 | 命令 | 结果 |
|--------|------|------|
| 编译/类型检查 | {go vet / tsc --noEmit / mypy} | PASS / FAIL |
| 单元测试 | {go test / npm test / pytest} | PASS / FAIL（N passed, M failed） |
| 竞态检测（如适用） | {go test -race} | PASS / FAIL |

{如有失败，粘贴关键错误输出}

## 发现

### Critical（必须修复）

{无 / 列表}

### Important（建议修复）

{无 / 列表}

### Suggestions（可选改进）

{无 / 列表}

## 语言特定检查（{language}）

{基于语言 Profile 的专项检查结果}

## 安全检查

- [ ] 无硬编码密钥
- [ ] 输入已验证
- [ ] SQL 注入防护
- [ ] XSS 防护（如适用）
