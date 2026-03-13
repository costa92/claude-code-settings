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

## Lint / Format
- Format: `npx prettier --write .`
- Lint: `npx eslint .`
- Type check: `npx tsc --noEmit`

## 惯用模式
- 组件: 函数组件 + hooks，避免 class 组件
- 状态: 简单用 useState，复杂用 useReducer 或 Zustand
- 副作用: useEffect 必须有 cleanup
- 类型: 优先 interface 而非 type alias

## 常见陷阱（Reviewer 关注）
- useEffect 缺少依赖或依赖过多导致无限渲染
- 组件内直接定义对象/数组导致重渲染（应 useMemo）
- key prop 使用 index 而非唯一 ID
- 未处理 loading/error 状态
- 服务端组件与客户端组件混用（Next.js App Router）
