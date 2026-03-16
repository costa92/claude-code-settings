# Go Language Profile

## 检测标志
- `go.mod` 文件存在

## 项目结构规范
```
cmd/           # 应用入口
internal/      # 私有包
pkg/           # 公共包
api/           # API 定义（proto, swagger）
configs/       # 配置文件
test/          # 集成测试
```

## 测试
- 命令: `go test ./... -v -race -cover`
- 覆盖率: `go test ./... -coverprofile=coverage.out && go tool cover -func=coverage.out`
- 框架: 标准库 `testing`，可选 `testify`
- 覆盖率门槛: ≥ 70%（低于此值在测试报告中标注 Warning）

## 服务端验收测试
- 编译: `go build -o /tmp/test-server .`
- 启动: `PORT=18080 BASE_URL=http://localhost:18080 /tmp/test-server &`
- 等待就绪: `for i in $(seq 1 10); do curl -sf http://localhost:18080/health && break || sleep 1; done`
- 关停: `pkill -f test-server`
- 测试端口: 18080（避免与开发端口 8080 冲突）

## Lint / Format
- Format: `gofmt -w .` 或 `goimports -w .`
- Lint: `golangci-lint run ./...`
- 必须通过: `go vet ./...`

## 惯用模式
- 错误处理: `if err != nil { return fmt.Errorf("context: %w", err) }`
- 接口: 消费方定义接口，实现方提供结构体
- 并发: 优先 channel，避免共享内存
- 命名: camelCase（导出用 PascalCase），包名短小

## Developer 编码检查清单

编码完成后、提交 Reviewer 前，必须逐项自检：

- [ ] 返回值是副本而非内部指针（map/slice/struct 不可泄漏内部引用）
- [ ] slice 操作前校验边界（page/offset/limit 等参数 ≤0 时安全处理）
- [ ] 所有公共接口定义为 interface（消费方定义，实现方提供 struct + 编译时断言 `var _ Interface = (*Impl)(nil)`）
- [ ] 定义 sentinel errors（`var ErrNotFound = errors.New("not found")`），不要用字符串比较
- [ ] 并发访问的字段使用 sync.Mutex/RWMutex 或 atomic 操作
- [ ] **修改 interface 或函数签名时，所有实现（含 test mock）和调用点已同步更新**
- [ ] `go vet ./...` 和 `go test -race ./...` 零告警（**必须实际运行，不可跳过**）
- [ ] error 不被吞（不用 `_ = doSomething()`），至少 log

## 常见陷阱（Reviewer 关注）
- goroutine 泄漏（缺少 context cancel）
- race condition（缺少 -race 标志）
- nil pointer dereference
- defer 在循环中的行为
- error 被吞（`_ = doSomething()`）

## 数据库测试

当 project.yaml 中 `has_database: true` 时，Developer 和 Tester 需遵循以下策略：

### 推荐方案（按优先级）

| 方案 | 适用场景 | 示例 |
|------|----------|------|
| **SQLite 内存模式** | 轻量 SQL 项目（无 PG/MySQL 专用语法） | `sql.Open("sqlite3", ":memory:")` |
| **testcontainers-go** | 需要真实 MySQL/PG/Redis | `postgres.Run(ctx, "postgres:16")` |
| **Interface Mock** | 单元测试隔离 DB 层 | 定义 `Repository` interface，注入 mock 实现 |

### 测试隔离模式

```go
// 方式 1: Interface 隔离（单元测试）
type UserRepository interface {
    Save(ctx context.Context, user *User) error
    FindByID(ctx context.Context, id string) (*User, error)
}

// mock 实现
type MockUserRepo struct {
    data map[string]*User
}

// 方式 2: 事务回滚隔离（集成测试）
func TestWithTx(t *testing.T) {
    tx, _ := db.Begin()
    defer tx.Rollback()
    repo := NewRepo(tx)
    // ... 测试后自动回滚
}

// 方式 3: testcontainers（集成测试）
func TestWithPostgres(t *testing.T) {
    ctx := context.Background()
    pg, _ := postgres.Run(ctx, "postgres:16",
        postgres.WithDatabase("testdb"),
    )
    defer pg.Terminate(ctx)
    dsn, _ := pg.ConnectionString(ctx)
    // ... 用真实 PG 测试
}
```

### Developer 要求

- 所有数据库操作必须通过 interface 访问（消费方定义接口）
- Repository 构造函数接受 `*sql.DB` 或 `*sql.Tx` 参数，便于注入测试连接
- Migration 脚本放在 `migrations/` 或 `internal/db/migrations/`

## 外部 API 测试

当 project.yaml 中 `has_external_api: true` 时：

### 推荐方案

| 方案 | 适用场景 | 示例 |
|------|----------|------|
| **Interface Mock** | 单元测试 | 定义 `Client` interface，注入 mock |
| **httptest.Server** | 集成测试 | `httptest.NewServer(handler)` 模拟外部 API |
| **go-vcr** | 录制回放 | 首次真实请求录制，后续回放 |

```go
// Interface 隔离
type PaymentClient interface {
    Charge(ctx context.Context, amount int) (*Receipt, error)
}

// httptest 模拟外部 API
func TestExternalAPI(t *testing.T) {
    server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(200)
        json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
    }))
    defer server.Close()
    client := NewClient(server.URL) // 注入测试 URL
    // ...
}
```
