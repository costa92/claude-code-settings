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
