# 代码设计优化方案

## Context

经过对微信公众号管理系统代码库的深入分析，发现了多个可以优化的地方，包括代码重复、不一致性、依赖管理等问题。这些优化将提高代码质量、可维护性和可扩展性。

## 推荐优化方案

### 第一阶段：高优先级优化（立即实施）

#### 1. 统一错误处理
**问题**：各服务的错误处理方式不一致，有的使用 fmt.Errorf 包装，有的直接返回错误。

**优化文件**：
- `api/internal/service/article.go`
- `api/internal/service/user.go`
- `api/internal/service/publish.go`
- 其他所有服务文件

**实施内容**：
- 统一使用 `fmt.Errorf("operation: %w", err)` 模式包装错误
- 确保错误信息包含足够的上下文
- 保持原始错误类型以便类型断言

#### 2. 标准化服务构造函数
**问题**：服务构造函数不一致，有的返回值，有的返回指针，参数列表差异大。

**优化文件**：
- `api/internal/service/*.go`（所有服务文件）

**实施内容**：
- 所有服务构造函数统一返回指针 `*ServiceName`
- 参数过多时（>3个）使用选项模式 `WithXXX()` 方法
- 保持构造函数命名统一 `NewServiceName()`

#### 3. 修复任务管理器的错误处理
**问题**：`task_manager.go` 中使用 panic 处理任务创建错误。

**优化文件**：
- `api/internal/service/task_manager.go`

**实施内容**：
- 将 `CreateTask` 方法的返回类型从 `string` 改为 `(string, error)`
- 移除 panic，改为返回错误
- 更新调用方以处理错误

#### 4. 改进密码加密强度
**问题**：使用硬编码的 `bcrypt.DefaultCost`，无法配置。

**优化文件**：
- `api/internal/service/user.go`
- `api/pkg/options/options.go`

**实施内容**：
- 在配置中添加 `PasswordCost` 选项
- 允许通过环境变量 `WECHAT_AUTH_PASSWORD_COST` 配置
- 保持默认值为 `bcrypt.DefaultCost`

### 第二阶段：中优先级优化（短期实施）

#### 5. 创建基础仓库类（使用泛型）
**问题**：多个仓库有重复的 CRUD 代码。

**优化文件**：
- 新建 `api/internal/repository/base.go`
- 修改 `api/internal/repository/article.go`
- 修改 `api/internal/repository/user.go`
- 其他仓库文件

**实施内容**：
- 创建泛型基础仓库 `BaseRepository[T Model]`
- 实现通用的 GetByID、List、Create、Update、Delete 方法
- 重构现有仓库以继承基础仓库

#### 6. 使用 Wire 依赖注入
**问题**：手动依赖注入容易出错且难以维护。

**优化文件**：
- 新建 `api/internal/app/wire.go`
- 修改 `api/internal/app/app.go`

**实施内容**：
- 引入 `github.com/google/wire`
- 创建 Wire 配置文件
- 定义 Provider 函数
- 生成依赖注入代码

#### 7. 提取配置管理
**问题**：配置加载逻辑在多个地方重复。

**优化文件**：
- 新建 `api/pkg/config/config.go`
- 修改 `api/cmd/server/main.go`
- 修改 `api/cmd/create-user/main.go`

**实施内容**：
- 创建统一的配置加载包
- 支持多环境配置（dev/staging/prod）
- 增强配置验证

#### 8. 优化中间件框架
**问题**：中间件组合不够灵活。

**优化文件**：
- `api/internal/middleware/middleware.go`

**实施内容**：
- 支持中间件链式调用
- 添加条件中间件（只在特定路由应用）
- 增强中间件测试覆盖

### 第三阶段：低优先级优化（长期优化）

#### 9. 增强存储接口
**优化文件**：
- `api/pkg/storage/storage.go`
- 各存储实现文件

**实施内容**：
- 支持流上传 `UploadStream`
- 支持范围下载 `DownloadRange`
- 添加元数据获取 `GetMetadata`

#### 10. 改进微信客户端
**优化文件**：
- `api/thirdparty/wechat/client.go`

**实施内容**：
- 使用更高效的 token 缓存策略
- 添加请求限流
- 改进错误重试机制

## 关键文件修改清单

| 优先级 | 文件路径 | 修改内容 |
|-------|---------|---------|
| 高 | `api/internal/service/task_manager.go` | 修复 panic，返回错误 |
| 高 | `api/internal/service/*.go` | 统一错误处理和构造函数 |
| 高 | `api/internal/service/user.go` | 密码加密强度配置 |
| 中 | `api/internal/repository/base.go` | 新建基础仓库 |
| 中 | `api/internal/app/wire.go` | 新建 Wire 配置 |
| 中 | `api/pkg/config/config.go` | 新建配置管理 |
| 中 | `api/internal/middleware/middleware.go` | 优化中间件 |
| 低 | `api/pkg/storage/storage.go` | 增强存储接口 |
| 低 | `api/thirdparty/wechat/client.go` | 改进微信客户端 |

## 可复用的现有代码

1. **options 包** (`api/pkg/options/`) - 已有的配置结构可以复用
2. **response 包** (`api/pkg/response/`) - 统一响应格式已实现
3. **middleware 包** (`api/internal/middleware/`) - 现有中间件框架可扩展
4. **util 包** (`api/pkg/util/`) - 工具函数库可重用

## 验证计划

### 测试方法
1. **单元测试**：运行 `go test ./api/internal/service/...` 验证服务层改动
2. **集成测试**：启动服务并测试 API 端点
3. **手动验证**：使用前端 UI 测试关键功能流程

### 关键验证点
- 文章创建、编辑、删除流程正常
- 用户登录认证正常
- 微信同步功能正常
- 任务管理功能正常
- 错误信息正确显示

### 回滚计划
如遇问题，使用 git 回滚到优化前的状态：
```bash
git checkout <commit-before-optimization>
```
