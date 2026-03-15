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
