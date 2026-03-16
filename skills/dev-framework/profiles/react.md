# React / TypeScript Profile

## 检测标志
- `package.json` 存在且含 `react` 依赖
- 或 `tsconfig.json` 存在

## 项目结构规范
```
src/
  components/   # UI 组件
  hooks/        # 自定义 hooks
  lib/          # 工具函数
  app/          # 页面/路由（Next.js）或 pages/
  types/        # TypeScript 类型定义
```

## 测试
- 命令: `npm test` 或 `npx vitest run`
- 覆盖率: `npx vitest run --coverage`
- 框架: Vitest + React Testing Library
- 覆盖率门槛: ≥ 70%（低于此值在测试报告中标注 Warning）

## E2E / 浏览器测试
- 工具: Playwright（`pip install playwright && playwright install chromium`）
- Dev Server 启动: `npm run dev`（默认端口见 vite.config 或 package.json，通常 5173 或 3000）
- Dev Server Helper: `~/.claude/skills/webapp-testing/scripts/with_server.py`
- 截图命令示例:
  ```bash
  python3 ~/.claude/skills/webapp-testing/scripts/with_server.py \
    --server "npm run dev" --port 5173 \
    -- python3 browser_test.py
  ```
- 浏览器测试覆盖项:
  - 桌面截图 (1280x720) + 移动端截图 (375x667)
  - Console error 检查（有 JS error → FAIL）
  - DOM 结构验证（对照 ui-design.md 选择器）
  - 交互测试（表单提交、按钮点击、路由导航）
  - 响应式布局验证（对照 ui-design.md 断点定义）

## Lint / Format
- Format: `npx prettier --write .`
- Lint: `npx eslint .`
- Type check: `npx tsc --noEmit`

## 惯用模式
- 组件: 函数组件 + hooks，避免 class 组件
- 状态: 简单用 useState，复杂用 useReducer 或 Zustand
- 副作用: useEffect 必须有 cleanup
- 类型: 优先 interface 而非 type alias

## Developer 编码检查清单

编码完成后、提交 Reviewer 前，必须逐项自检：

- [ ] useEffect 依赖数组完整且精确（不遗漏、不多余）
- [ ] 组件内引用类型（对象/数组/函数）用 useMemo/useCallback 稳定化
- [ ] 列表渲染 key 使用唯一业务 ID 而非 index
- [ ] 所有异步操作有 loading + error + empty 三态处理
- [ ] 服务端/客户端组件边界明确（Next.js: "use client" 仅在需要时添加）
- [ ] 组件 props 用 interface 定义，必要字段不可为 optional
- [ ] **修改 interface/type/props 签名时，所有实现（含 test mock/stub）和调用点已同步更新**
- [ ] `npx tsc --noEmit` 和 `npx eslint .` 零告警（**必须实际运行，不可跳过**）

## 常见陷阱（Reviewer 关注）
- useEffect 缺少依赖或依赖过多导致无限渲染
- 组件内直接定义对象/数组导致重渲染（应 useMemo）
- key prop 使用 index 而非唯一 ID
- 未处理 loading/error 状态
- 服务端组件与客户端组件混用（Next.js App Router）

## API 测试

前端项目通常消费后端 API，需要对 API 调用层进行测试：

### 推荐方案

| 方案 | 适用场景 | 示例 |
|------|----------|------|
| **MSW (Mock Service Worker)** | 拦截 fetch/axios 请求 | `http.get('/api/users', resolver)` |
| **vitest mock** | 单元测试 mock 函数 | `vi.mock('../api/client')` |
| **nock** | Node.js 端 HTTP mock | Express/Next.js API routes 测试 |

### MSW 模式（推荐）

```typescript
// src/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({ id: params.id, name: 'Test User' });
  }),
  http.post('/api/users', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: '1', ...body }, { status: 201 });
  }),
];

// src/mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';
export const server = setupServer(...handlers);

// vitest.setup.ts
import { server } from './src/mocks/server';
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### API Route 测试（Next.js）

```typescript
// 直接测 API handler，不需要启动服务器
import { GET } from '@/app/api/users/route';
import { NextRequest } from 'next/server';

it('GET /api/users', async () => {
  const req = new NextRequest('http://localhost/api/users');
  const res = await GET(req);
  expect(res.status).toBe(200);
});
```

### Developer 要求

- API 调用层独立封装（如 `src/lib/api.ts`），不在组件内直接 fetch
- 所有 API 调用函数可独立 mock
- 错误状态（网络错误、4xx、5xx）有对应 UI 反馈
