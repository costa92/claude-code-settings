# Theme Documentation & Live Preview

## Context

The `/themes` page (`ThemeManagement.tsx`) only has a table + edit dialog with raw key-value CSS inputs. Users have no documentation explaining what each style key does, and no way to preview how their theme renders. This makes theme configuration a guessing game.

**Goal**: Add style key documentation reference and a live preview panel that renders sample Markdown with the theme styles in real-time.

---

## Phase 1: Backend — Theme Preview Endpoint

### `internal/service/conversion.go`
Add method + sample markdown constant:
```go
func (s *ConversionService) PreviewWithStyles(ctx context.Context, styles map[string]string, markdown string) (string, error)
```
- Creates `converter.Theme` from styles map, converts markdown, returns HTML
- If markdown is empty, use built-in sample exercising all style keys (headings, bold, italic, code, blockquote, list, table, alert, link, hr, image)

### `internal/handler/theme.go`
- Inject `ConversionService` into `ThemeHandler` (update constructor)
- Add `Preview` handler: body `{ styles, markdown }` → calls `PreviewWithStyles` → returns `text/html`

### `internal/handler/router.go`
- Register `POST /api/v1/themes/preview`

### `cmd/server/main.go`
- Pass `ConversionService` to `NewThemeHandler()`

---

## Phase 2: Frontend — API

### `web/src/services/api.ts`
```typescript
export const previewThemeStyles = (styles: Record<string, string>, markdown?: string) =>
  api.post('/themes/preview', { styles, markdown }, {
    headers: { Accept: 'text/html' },
    transformResponse: [(data: string) => data],
  });
```

---

## Phase 3: Frontend — Enhanced Editor with Preview & Docs

### `web/src/pages/ThemeManagement.tsx`

Expand editor dialog to `max-w-7xl`, split into two columns:

**Left column (w-1/2)**: Name/display inputs + style editor (keep existing visual/JSON tabs) + collapsible docs reference

**Right column (w-1/2)**: Live preview panel
- Phone-style frame (reuse pattern from ArticlePreview.tsx)
- "刷新预览" button + auto-preview on style changes (500ms debounce)
- Collapsible sample markdown textarea with sensible default

**Style Key Docs Reference** — collapsible section with categorized table:

| 分类 | 键名 | 说明 |
|------|------|------|
| 基础排版 | `wrapper`, `p`, `h1`-`h3` | 容器、段落、标题 |
| 文本 | `strong`, `em`, `del`, `a` | 加粗、斜体、删除线、链接 |
| 代码 | `code_inline`, `code_block`, `code_block_wrapper`, `code_block_header` | 行内/块代码 |
| 列表 | `ul`, `ol`, `li` | 列表 |
| 引用 | `blockquote`, `hr` | 引用、分割线 |
| 表格 | `table`, `th`, `td` | 表格 |
| 图片 | `img` | 图片 |
| 提示框 | `alert_*`, `alert_title_*`, `alert_content_default` | GitHub/Obsidian callout |

---

## File Change Summary

| File | Change |
|------|--------|
| `internal/service/conversion.go` | Add `PreviewWithStyles()` + sample markdown |
| `internal/handler/theme.go` | Add `Preview` handler, inject ConversionService |
| `internal/handler/router.go` | Register `POST /themes/preview` |
| `cmd/server/main.go` | Pass ConversionService to ThemeHandler |
| `web/src/services/api.ts` | Add `previewThemeStyles()` |
| `web/src/pages/ThemeManagement.tsx` | Redesign editor: preview panel + docs |

---

## Verification

1. `go build ./...` — compiles
2. `go test ./...` — tests pass
3. `cd web && npx tsc --noEmit` — type-checks
4. Browser: `/themes` → edit theme → preview renders live
5. Browser: Change style → preview updates
6. Browser: Docs reference visible and categorized
