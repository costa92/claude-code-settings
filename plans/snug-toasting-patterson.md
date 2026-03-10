# osbuilder 模板缺陷修复计划

## Context

在上一轮代码优化完成后，我们对生成的项目进行了编译验证，发现了 5 个预存的模板缺陷。这些缺陷导致特定配置下生成的项目无法通过 `protoc`、`go build` 或 `go vet`。所有问题均出在模板文件仓库 `osbuilder-templates` 中，无需修改 osbuilder 生成器代码本身。

---

## Bug 1: cronjob.proto 硬编码 proto import 路径

**文件** (2 个):
- `osbuilder-templates/project/pkg/api/jobserver/v1/cronjob.proto:7`
- `osbuilder-templates/project/pkg/api/apiserver/v1/cronjob.proto:7`（未使用但应修正）

**现状**:
```proto
import "jobserver/{{.M.APIVersion}}/job.proto";
```

**问题**: 当 JobServer 的 `binaryName` 为 `tf-worker` 时，组件名为 `worker`，proto 输出目录为 `pkg/api/worker/v1/`，但 import 路径硬编码为 `jobserver/...`，导致 `protoc` 编译失败。同一文件第 4 行和第 10 行已正确使用 `{{$D.Name}}`。

**修复**: 第 7 行改为:
```proto
import "{{$D.Name}}/{{.M.APIVersion}}/job.proto";
```

---

## Bug 2: gRPC requestid.go 缺少 string() 类型转换

**文件**: `osbuilder-templates/project/internal/pkg/middleware/grpc/requestid.go:22,29`

**现状**:
```go
if requestIDs := md[known.XRequestID]; len(requestIDs) > 0 {        // 第 22 行
md.Append(known.XRequestID, requestID)                               // 第 29 行
```

**问题**: `known.XRequestID` 类型为 `headerKey`（自定义 string 类型），`metadata.MD` 为 `map[string][]string`，类型不匹配导致 `go build` 失败。其他 4 个框架（Gin/Echo/GoZero/Kratos）均已正确使用 `string()` 转换。

**修复**:
```go
if requestIDs := md[string(known.XRequestID)]; len(requestIDs) > 0 { // 第 22 行
md.Append(string(known.XRequestID), requestID)                       // 第 29 行
```

---

## Bug 3: JobServer model.go Value() 方法复制 protobuf 互斥锁

**文件**: `osbuilder-templates/project/internal/jobserver/model/model.go:44,66,88,130`

**现状**:
```go
func (status CronJobStatus) Value() (driver.Value, error) {   // 值接收器
    return json.Marshal(status)                                 // 复制了内含 sync.Mutex 的 MessageState
}
```
同样的问题出现在 `JobParams`(66)、`JobResults`(88)、`JobM`(130) 的 `Value()` 方法。

**问题**: protobuf 生成的类型包含 `protoimpl.MessageState`（含 `sync.Mutex`），值接收器会复制互斥锁，`go vet` 报 "copies lock value"。`Scan()` 方法已使用指针接收器。

**修复**: 4 处值接收器改为指针接收器:
```go
func (status *CronJobStatus) Value() (driver.Value, error) { ... }  // 第 44 行
func (params *JobParams) Value() (driver.Value, error) { ... }      // 第 66 行
func (result *JobResults) Value() (driver.Value, error) { ... }     // 第 88 行
func (job *JobM) Value() (driver.Value, error) { ... }              // 第 130 行
```
注: `JobConditions` 的 `Value()`（第 110 行）不受影响，因为它是 `[]*v1.JobCondition` 切片类型。

---

## Bug 4: 结构化 Makefile 缺少 CMD_DIRS 定义

**文件**: `osbuilder-templates/project/scripts/make-rules/common.mk`（第 9 行之后插入）

**现状**: `common.mk` 定义了 `PROJ_ROOT_DIR` 但未定义 `CMD_DIRS`。`golang.mk:26` 和 `image.mk:38` 使用 `CMD_DIRS` 并在为空时报错退出。

**修复**: 在 `common.mk` 第 10 行（`OUTPUT_DIR` 定义之后）插入:
```makefile
# 自动发现 cmd 目录下的所有命令
CMD_DIRS := $(wildcard $(PROJ_ROOT_DIR)/cmd/*)
```

---

## Bug 5: FalseCondition 传入原始错误字符串作为格式化串

**文件**: `osbuilder-templates/project/internal/jobserver/watcher/job/llmtrain/event.go:172`

**现状**:
```go
cond = jobconditionsutil.FalseCondition(event.FSM.Current(), event.Err.Error())
```

**问题**: `FalseCondition` 签名为 `(t, messageFormat string, messageArgs ...any)`，内部使用 `fmt.Sprintf(messageFormat, messageArgs...)`。直接传入错误字符串作为格式化串，若包含 `%` 字符则输出错误。`go vet` 报 "non-constant format string"。

**修复**:
```go
cond = jobconditionsutil.FalseCondition(event.FSM.Current(), "%s", event.Err.Error())
```

---

## 修改文件清单

所有文件路径相对于 `/home/hellotalk/code/go/src/github.com/costa92/osbuilder-templates/`

| Bug | 文件 | 行号 | 改动 |
|-----|------|------|------|
| 1a | `project/pkg/api/jobserver/v1/cronjob.proto` | 7 | `"jobserver/"` → `"{{$D.Name}}/"` |
| 1b | `project/pkg/api/apiserver/v1/cronjob.proto` | 7 | 同上 |
| 2 | `project/internal/pkg/middleware/grpc/requestid.go` | 22, 29 | 添加 `string()` 转换 |
| 3 | `project/internal/jobserver/model/model.go` | 44, 66, 88, 130 | 值接收器 → 指针接收器 |
| 4 | `project/scripts/make-rules/common.mk` | 10 后插入 | 添加 `CMD_DIRS` 定义 |
| 5 | `project/internal/jobserver/watcher/job/llmtrain/event.go` | 172 | 添加 `"%s"` 格式化串 |

## 验证

1. 使用 osbuilder 生成 fullstack 测试项目（WebServer + JobServer + MQServer + CLITool，Job binaryName 使用非默认名称如 `tf-worker`）
2. 运行 `protoc` 编译 proto 文件 — 验证 Bug 1 修复
3. 运行 `go build ./...` — 验证 Bug 2 修复 + 整体编译
4. 运行 `go vet ./...` — 验证 Bug 3、Bug 5 修复
5. 运行 `make build`（结构化 Makefile 项目）— 验证 Bug 4 修复
6. 生成 gRPC 单独项目验证 Bug 2 修复
