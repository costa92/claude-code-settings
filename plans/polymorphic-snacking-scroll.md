# Plan: 在页面显示任务同步进度

## Context

异步化改造完成后，后台已有 `TaskProgress`（step/current/total/description），`useTaskPolling` hook 也在轮询获取，但页面未展示实时进度。用户只看到「任务已提交...」静态文字，无法感知处理进展。

**目标**: 在 ArticlePreview 和 ArticleList 页面实时展示任务进度描述和进度条。

## 修改文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `web/src/hooks/useTaskPolling.ts` | 修改 | 暴露 `currentProgress` 便捷属性 |
| `web/src/components/TaskProgressBar.tsx` | 新建 | 进度条组件（步骤文字 + 进度条） |
| `web/src/pages/ArticlePreview.tsx` | 修改 | 按钮下方显示进度条组件 |
| `web/src/pages/ArticleList.tsx` | 修改 | 页面顶部显示进度 banner |

## Step 1: 修改 `web/src/hooks/useTaskPolling.ts`

新增返回值 `currentProgress`，取第一个活跃任务的 progress：

```typescript
// 新增返回
const currentProgress = useMemo(() => {
  const first = activeTasks.values().next().value;
  return first?.progress ?? null;
}, [activeTasks]);

return { activeTasks, addTask, hasActiveTasks, currentProgress };
```

## Step 2: 新建 `web/src/components/TaskProgressBar.tsx`

紧凑的进度指示组件，显示：
- 进度条（current/total 百分比，total=0 时用 indeterminate 动画）
- 描述文字（如 "已上传图片 2/5"）

```tsx
interface TaskProgressBarProps {
  progress: TaskProgress | null;
}

export function TaskProgressBar({ progress }: TaskProgressBarProps) {
  if (!progress) return null;
  const pct = progress.total > 0
    ? Math.round((progress.current / progress.total) * 100)
    : null;
  return (
    <div className="space-y-1.5 animate-in fade-in">
      <div className="flex justify-between text-[10px]">
        <span>{progress.description}</span>
        {pct !== null && <span>{pct}%</span>}
      </div>
      <div className="h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        {pct !== null ? (
          <div className="h-full bg-emerald-500 rounded-full transition-all"
               style={{ width: `${pct}%` }} />
        ) : (
          <div className="h-full bg-emerald-500 rounded-full animate-progress-indeterminate" />
        )}
      </div>
    </div>
  );
}
```

indeterminate 动画使用 Tailwind 自定义动画或 inline style。

## Step 3: 修改 `web/src/pages/ArticlePreview.tsx`

1. 从 `useTaskPolling` 解构 `currentProgress`
2. 在上传按钮和 syncError 之间插入 `<TaskProgressBar progress={currentProgress} />`
3. 按钮文字从静态 `uploadProgress` 改为 `currentProgress?.description`

## Step 4: 修改 `web/src/pages/ArticleList.tsx`

1. 从 `useTaskPolling` 解构 `currentProgress`
2. 在文章列表上方（按钮行下方）显示进度 banner：
   当 `currentProgress` 存在时渲染 `<TaskProgressBar />`，包裹在半透明卡片中

## 验证

1. `cd web && npx tsc --noEmit` — 类型检查通过
2. 浏览器验证：提交上传 → 进度条实时更新 → 完成后消失
