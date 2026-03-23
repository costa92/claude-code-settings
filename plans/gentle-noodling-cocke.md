# 修复飞书同步流程

## Context

飞书同步功能的完整流程（连接检测 → 浏览文档 → 预览 → 同步到文章列表）无法走通。
根本原因是 **数据库缺少飞书同步所需的列**（`source`, `source_id`, `synced_at`, `platform_links`），导致写入文章时 SQL 报错。此外前端和后端还有多处逻辑缺陷需要一并修复。

## 问题清单

| # | 严重程度 | 问题 | 影响 |
|---|---------|------|------|
| 1 | **致命** | `articles` 表缺少 `source`, `source_id`, `synced_at`, `platform_links` 列，无对应 migration | sync 写库必定失败 |
| 2 | **高** | 图片下载失败时整个 sync 中止 | 有图片的文档全部同步失败 |
| 3 | **中** | 新文章未设置 `SyncedAt`、`Author`、`WordCount` | 数据不完整 |
| 4 | **中** | 文档标题仅从 heading 提取，无 heading 时为空 | 文章列表显示空标题 |
| 5 | **低** | 前端 `created_time`/`modified_time` 为 Unix 时间戳字符串，`new Date()` 无法解析 | 文件列表显示 "Invalid Date" |
| 6 | **低** | 前端不区分文件类型，非 docx 文件也能点击同步 | 同步 sheet/bitable 等会报错 |

## 修复方案

### 1. 新增数据库 migration（致命）

**文件**: `migrations/000008_add_feishu_columns.up.sql` (新建)
**文件**: `migrations/000008_add_feishu_columns.down.sql` (新建)

```sql
-- up
ALTER TABLE articles ADD COLUMN IF NOT EXISTS source VARCHAR(32);
ALTER TABLE articles ADD COLUMN IF NOT EXISTS source_id VARCHAR(128);
ALTER TABLE articles ADD COLUMN IF NOT EXISTS synced_at TIMESTAMPTZ;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS platform_links JSONB;

CREATE UNIQUE INDEX IF NOT EXISTS idx_source_source_id
    ON articles (source, source_id)
    WHERE source IS NOT NULL AND source_id IS NOT NULL;
```

### 2. 图片处理容错（高）

**文件**: `internal/service/feishu_sync.go`

`processImages` 中单张图片下载失败时跳过（保留 placeholder），而非终止整个 sync。改用 `slog.Warn` 记录，并在 markdown 中保留占位符或插入提示文字。

### 3. 补全新文章字段（中）

**文件**: `internal/service/feishu_sync.go`

在 `SyncDocument` 创建新文章时补全：
- `SyncedAt: &now`
- `Author: s.cfg.Article.DefaultAuthor`（如果非空）
- 同步完成后计算 `WordCount`（使用 `utf8.RuneCountInString` 对 markdown 做简单字数统计）

### 4. 标题提取增强（中）

**文件**: `internal/service/feishu_sync.go`

当 `blockconv.BlocksToMarkdown` 返回空标题时，调用 `feishuClient.GetDocumentMeta(ctx, docToken)` 获取文档标题作为兜底。

### 5. 前端时间戳解析（低）

**文件**: `web/src/components/feishu/FileList.tsx`

`formatDate` 函数增加对 Unix 时间戳字符串的处理：
```ts
function formatDate(dateStr: string): string {
  const ts = Number(dateStr);
  const d = !isNaN(ts) && ts > 1e9 ? new Date(ts * 1000) : new Date(dateStr);
  ...
}
```

### 6. 前端文件类型过滤（低）

**文件**: `web/src/components/feishu/FileList.tsx`

同步按钮仅对 `type === 'docx'` 的文件显示。对 `doc`/`sheet` 等类型显示 "不支持" 提示。

## 涉及文件汇总

| 文件 | 操作 |
|------|------|
| `migrations/000008_add_feishu_columns.up.sql` | **新建** |
| `migrations/000008_add_feishu_columns.down.sql` | **新建** |
| `internal/service/feishu_sync.go` | 修改（问题 2, 3, 4） |
| `web/src/components/feishu/FileList.tsx` | 修改（问题 5, 6） |

## 验证步骤

1. `make migrate-up` 确认 migration 执行无报错
2. `go test ./...` 确认后端测试通过
3. 启动服务，在飞书同步页面：
   - 连接状态显示 "已连接"
   - 输入文件夹 token → 文件列表正常加载，日期显示正确
   - 非 docx 文件不显示同步按钮
   - 点击 docx 文档的 "同步" → 文章创建成功，跳转到编辑页
   - 文章列表中可看到新同步的文章，标题、作者、字数正常
