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

## Lint / Format
- Format: `gofmt -w .` 或 `goimports -w .`
- Lint: `golangci-lint run ./...`
- 必须通过: `go vet ./...`

## 惯用模式
- 错误处理: `if err != nil { return fmt.Errorf("context: %w", err) }`
- 接口: 消费方定义接口，实现方提供结构体
- 并发: 优先 channel，避免共享内存
- 命名: camelCase（导出用 PascalCase），包名短小

## 常见陷阱（Reviewer 关注）
- goroutine 泄漏（缺少 context cancel）
- race condition（缺少 -race 标志）
- nil pointer dereference
- defer 在循环中的行为
- error 被吞（`_ = doSomething()`）
