# 技术设计: {项目名称}

> 由 Architect Agent 生成 | {日期}

## 技术选型

| 维度 | 选择 | 理由 |
|------|------|------|
| 语言 | {language} | |
| 框架 | {framework} | |
| 数据库 | {db} | |
| 其他 | | |

## 架构概览

{架构描述，可包含 ASCII 图}

## 数据模型

{表结构、类型定义或 Schema}

## API 定义

| 方法 | 路径 | 描述 | 请求体 | 响应 |
|------|------|------|--------|------|
| {METHOD} | {/path} | {描述} | {body} | {response} |

## 目录结构

```
{项目目录结构}
```

## 关键实现细节

{复杂逻辑的实现说明}

## 测试策略

> 当 project.yaml 中 `has_database: true` 或 `has_external_api: true` 时必须填写此 section。

### 数据库测试方案

| 层级 | 方案 | 说明 |
|------|------|------|
| 单元测试 | {Interface Mock / 内存 DB} | {如何隔离数据库依赖} |
| 集成测试 | {SQLite 内存 / testcontainers / 事务回滚} | {如何验证真实 DB 操作} |

### 外部 API 测试方案

| 层级 | 方案 | 说明 |
|------|------|------|
| 单元测试 | {Interface Mock} | {如何隔离外部 API} |
| 集成测试 | {httptest / MSW / responses} | {如何模拟外部 API 响应} |

### 测试基础设施

- 测试数据库: {SQLite :memory: / Docker PG / 无}
- 外部服务 Mock: {httptest.Server / MSW / responses / 无}
- Setup/Teardown: {migration + seed / fixture / 事务回滚}

## 风险与待决事项

- {风险或待决}

## Task List

### Task 1: {名称}
<!-- task-meta
files: [path/to/file1, path/to/file2]
deps: []
wave: 1
-->
- 描述: {要实现什么}

### Task 2: {名称}
<!-- task-meta
files: [path/to/file1, path/to/file3]
deps: [Task 1]
wave: 2
-->
- 描述: {要实现什么}
