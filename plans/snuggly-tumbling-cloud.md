# 从微信同步已发布文章

## Context
当前"从微信同步"功能只同步草稿箱内容（`BatchGetDrafts`），不同步已发布的文章。且如果本地发布到微信的文章，同步时会因为 `wechat_media_id` 匹配而被跳过。用户需要：
1. 同步微信已发布的内容（而非草稿）
2. 本项目发布到微信的内容，同步回来时应新增一条记录，而不是跳过

## 修改方案

### 1. WeChat Client 添加获取已发布文章列表 API
**文件**: `api/thirdparty/wechat/publish.go`

添加 `BatchGetPublished` 方法，调用微信 `freepublish/batchget` 接口获取已发布文章列表。

添加 `GetArticle` 方法，调用 `freepublish/getarticle` 接口获取已发布文章详情（包含 article_id）。

定义对应的 request/response 类型。

### 2. 更新 WeChatUploader 接口
**文件**: `api/internal/service/publish.go`

在 `WeChatUploader` 接口中添加：
- `BatchGetPublished(ctx, offset, count) (*BatchGetPublishedResponse, error)`
- `GetArticle(ctx, articleID string) (*GetArticleResponse, error)`

### 3. 修改 SyncFromWeChatInternal 逻辑
**文件**: `api/internal/service/publish.go`

- 改为调用 `BatchGetPublished` 获取已发布文章（替换 `BatchGetDrafts`）
- 修改去重逻辑：
  - 仍通过 `source_id` 去重（防止重复同步同一篇微信文章）
  - **移除** `GetByWeChatMediaID` 的跳过逻辑 — 本地发布到微信后，同步回来应创建新记录
- 新同步的文章 `source="wechat_published"`、`source_id=article_id`，与原有 `source="wechat"` 的草稿同步区分

### 4. 前端 SOURCE_MAP 更新
**文件**: `web/src/pages/ArticleList.tsx`

在 `SOURCE_MAP` 中添加 `wechat` 和 `wechat_published` 来源标识，显示为"微信同步"。

## 关键文件
- `api/thirdparty/wechat/publish.go` — 新增 API 方法
- `api/thirdparty/wechat/draft.go` — 参考现有类型结构
- `api/internal/service/publish.go` — 接口 + 同步逻辑
- `web/src/pages/ArticleList.tsx` — 来源展示

## 验证
1. `go build ./...` 编译通过
2. 前端无报错
3. 点击"从微信同步"后能拉取已发布文章
4. 本地已发布到微信的文章，同步回来出现为新增条目
