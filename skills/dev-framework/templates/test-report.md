# 测试报告

> 由 Tester Agent 生成 | {日期}

## 结论: {PASS / FAIL}

## 测试概要

| 指标 | 值 |
|------|-----|
| 总用例数 | {n} |
| 通过 | {n} |
| 失败 | {n} |
| 跳过 | {n} |
| 覆盖率 | {n}% |

## 失败用例

| 用例 | 文件 | 错误信息 |
|------|------|----------|
| {test_name} | {file} | {error} |

（无失败用例时此表为空）

## 测试命令

```bash
{实际执行的测试命令}
```

## 数据库测试（has_database 项目）

> 仅当 `has_database: true` 时填写此 section。无数据库项目删除此 section。

### 数据库测试概要

| 检查项 | 结果 | 备注 |
|--------|------|------|
| 测试方案 | Interface Mock / SQLite 内存 / testcontainers | {实际使用的方案} |
| Docker 可用 | YES / NO / N/A | {仅 testcontainers 方案需要} |
| Repository CRUD 测试 | PASS / FAIL | {通过数/总数} |
| 数据隔离验证 | PASS / FAIL / SKIP | {测试间是否独立} |
| Migration 测试 | PASS / FAIL / SKIP | {表结构是否正确创建} |

### 数据库测试用例

| 用例 | 类型 | 结果 | 备注 |
|------|------|------|------|
| {test_name} | 单元/集成 | PASS / FAIL | {备注} |

### 数据库测试判定

- Repository CRUD 测试失败 → **FAIL**
- 数据隔离失败 → **FAIL**
- Docker 不可用导致 testcontainers 跳过 → **Warning**（不影响 PASS/FAIL）
- DB 集成测试跳过（环境限制） → **DB Integration Test Skipped**

## 外部 API 测试（has_external_api 项目）

> 仅当 `has_external_api: true` 时填写此 section。无外部 API 项目删除此 section。

### API 测试概要

| 检查项 | 结果 | 备注 |
|--------|------|------|
| Mock 方案 | Interface Mock / httptest / MSW / responses | {实际使用的方案} |
| 正常响应测试 | PASS / FAIL | {200/201 场景} |
| 错误响应测试 | PASS / FAIL / SKIP | {4xx/5xx 场景} |
| 超时/网络错误测试 | PASS / FAIL / SKIP | {timeout/connection refused} |

### API 测试用例

| 用例 | 模拟场景 | 结果 | 备注 |
|------|----------|------|------|
| {test_name} | {200 OK / 404 / timeout} | PASS / FAIL | {备注} |

### API 测试判定

- API Client 测试失败 → **FAIL**
- 仅测 happy path，缺少错误场景 → **Warning**
- 所有 API 测试通过 → API 测试 PASS

## 服务端验收测试（API 服务项目）

> 仅当 `has_api_server: true` 时填写此 section。非 API 服务项目删除此 section。

### 服务端验收概要

| 检查项 | 结果 | 备注 |
|--------|------|------|
| 编译成功 | YES / NO | {编译命令和耗时} |
| 服务启动 | YES / NO | {端口号或失败原因} |
| Health 端点 | PASS / FAIL / N/A | {响应状态码} |
| API 端点验收 | {通过数}/{总数} | {概要} |
| 持久化验证 | PASS / FAIL / SKIP | {重启后数据保留情况} |

### 端点测试用例

| 端点 | 方法 | 场景 | 期望 | 实际 | 结果 |
|------|------|------|------|------|------|
| {/api/xxx} | {GET/POST} | {正常/错误/边界} | {期望状态码+响应} | {实际状态码+响应} | PASS / FAIL |

### 持久化验证详情

| 步骤 | 操作 | 结果 | 备注 |
|------|------|------|------|
| 1 | 创建测试数据 | {数据概要} | |
| 2 | 关停并重启服务 | {重启成功/失败} | |
| 3 | 验证数据存在 | PASS / FAIL | {对比结果} |
| 4 | 验证计数器/序列 | PASS / FAIL | {新数据 ID 是否连续} |

### 服务端验收判定

- API 端点正常路径返回错误 → **FAIL**
- 持久化验证失败 → **FAIL**
- 服务无法启动 → **FAIL**
- 错误路径返回码不符预期 → **Warning**
- 服务端验收跳过（环境限制） → **Server Acceptance Test Skipped**

## 浏览器测试（前端项目 / 涉及前端文件变更）

> 当 `has_frontend: true` 或开发过程中涉及前端文件变更（.html/.css/.jsx/.tsx/.vue/.svelte 等）时填写此 section。无前端相关变更的项目删除此 section。

### 浏览器测试概要

| 检查项 | 结果 | 备注 |
|--------|------|------|
| Playwright 可用 | YES / NO | {版本或安装失败原因} |
| Dev Server 启动 | YES / NO | {端口号或失败原因} |
| Console JS Errors | 0 / {n} 个 | {错误摘要} |
| Active Browser Pages | {n} 个活跃 / {n} 个意外弹出 | {页面泄漏情况} |
| DOM 选择器验证 | PASS / FAIL / SKIP | {通过数/总数} |
| 交互测试 | PASS / FAIL / SKIP | {场景摘要} |

### 截图

| 视口 | 截图路径 | 状态 |
|------|----------|------|
| 桌面 (1280x720) | `.plan/artifacts/screenshots/desktop.png` | {已生成 / 失败} |
| 移动端 (375x667) | `.plan/artifacts/screenshots/mobile.png` | {已生成 / 失败} |
| {交互状态} | `.plan/artifacts/screenshots/{name}.png` | {已生成} |

### 操作录制与回放

| Artifact | 路径 | 说明 |
|----------|------|------|
| Playwright Trace | `.plan/artifacts/recordings/trace.zip` | 含操作日志、DOM 快照、逐步截图、网络请求 |
| 浏览器视频 | `.plan/artifacts/recordings/*.webm` | 完整操作过程视频录制 |

**Trace 回放**：`npx playwright show-trace .plan/artifacts/recordings/trace.zip`（本地浏览器打开，逐步回放每个操作的截图、DOM 状态和网络请求）

### 响应式测试

| 断点 | 宽度 | 布局验证 | 备注 |
|------|------|----------|------|
| mobile | 375px | PASS / FAIL | {布局描述} |
| tablet | 768px | PASS / FAIL | {布局描述} |
| desktop | 1280px | PASS / FAIL | {布局描述} |

### Console 错误详情

（无 console error 时此 section 为空）

```
{console error 详细输出}
```

### Active Browser Pages

| 页面 URL | 标题 | 来源 | 状态 | 备注 |
|----------|------|------|------|------|
| {url} | {title} | 测试创建 / 弹出窗口 | 已关闭 / 未关闭 | {备注} |

- **意外弹出页面**: {0 / n} 个（非测试主动创建的页面）
- **页面泄漏**: {0 / n} 个（测试结束时仍未关闭的页面）

### 浏览器测试判定

- Console JS error → **FAIL**
- 关键 DOM 选择器不存在 → **FAIL**
- 交互验证失败 → **FAIL**
- 意外弹出页面（非测试主动创建） → **Warning**
- 测试结束时有未关闭的页面泄漏 → **Warning**
- 仅截图无法自动比对 → **Manual Review Needed**
- 浏览器测试跳过（安装/启动失败） → **Browser Test Skipped**（不影响单元测试结论）

## 建议

{测试覆盖不足的区域或改进建议}
