# 事实验证与截图（仅完整模式）

### CLI/代码命令执行层级

```
文章中出现 CLI 命令 / 代码示例
        ↓
1. 检查本地是否有该工具
   Bash: which <工具名> 或 command -v <工具名>
        ↓ 有 → 直接执行，捕获 stdout/stderr
        ↓ 无
2. Docker 运行
   Bash: docker run --rm <对应镜像> <命令>
        ↓ 成功 → 捕获输出
        ↓ 失败 / Docker 不可用
3. 标记 ⚠️ [需要人工验证]
```

**常用工具对应 Docker 镜像**：

| 工具 | Docker 镜像 |
|------|------------|
| node / npm / npx | node:lts-alpine |
| python / pip | python:3.12-alpine |
| kubectl | bitnami/kubectl:latest |
| terraform | hashicorp/terraform:latest |
| go | golang:alpine |
| rust / cargo | rust:alpine |
| curl / wget | curlimages/curl:latest |

### 执行结果截图流程

1. 执行命令，捕获输出到变量
2. 将输出写入临时 HTML 文件（`/tmp/review-evidence/terminal.html`）：

```html
<!DOCTYPE html><html><body style="margin:0;background:#0d0d0d">
<div style="background:#1e1e1e;color:#d4d4d4;font-family:'Courier New',monospace;
            font-size:13px;padding:20px;border-radius:8px;white-space:pre-wrap;
            max-width:800px;margin:20px auto">
<span style="color:#569cd6">$</span> COMMAND_HERE
OUTPUT_HERE
</div></body></html>
```

3. 使用 webapp-testing（Playwright）打开 HTML 文件并截图：
   - 截图保存至 `/tmp/review-evidence/<工具名>-<时间戳>.png`
   - 若 webapp-testing 不可用，保留文字输出并标注"无截图"

4. 报告中引用截图路径

### 安全约束

只执行以下类型的命令（只读、无副作用）：
- `--help` / `--version` / `-v` / `-V`
- `list` / `get` / `show` / `describe`（kubectl、terraform 等）
- `node -e "console.log(...)"` 纯计算表达式
- `python -c "print(...)"` 纯计算表达式

**不执行**（标注「⚠️ 涉及副作用，跳过执行」）：
- 写操作：create、apply、deploy、push、install、rm、delete
- 网络请求：curl 到外部地址、wget
- 文件系统操作：mkdir、touch、mv、cp

### 验证报告格式

```markdown
#### 验证项：`docker --version`
- 验证方式：本地执行（docker 已安装）
- 截图：`/tmp/review-evidence/docker-version-20260305.png`
- 结论：✅ 版本 25.0.3，与文章描述一致

#### 验证项：`kubectl apply -f deployment.yaml`
- 本地检查：kubectl 未安装
- 降级方式：Docker bitnami/kubectl:latest
- 截图：`/tmp/review-evidence/kubectl-apply-20260305.png`
- 结论：❌ 命令报错（缺少 kubeconfig），文章未说明前置条件 → 扣 -2

#### 验证项：`git push --force origin main`
- 安全检查：涉及写操作
- 结论：⚠️ [涉及副作用，跳过执行，需人工验证]
```
