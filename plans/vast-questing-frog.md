# 优化主题切换体验：选择即预览

## Context

当前在文章预览页面测试主题时，用户需要 3 步操作：
1. 在「基础」标签选择主题
2. 切换到「操作」标签
3. 点击「重新转换内容」按钮

需要优化为：选择主题后自动转换并刷新预览，1 步完成。

## 修改方案

### 文件：`web/src/pages/ArticlePreview.tsx`

**改动 1：主题下拉框 `onValueChange` 回调（第 290-293 行）**

将当前的：
```typescript
onValueChange={(val) => {
  setSelectedTheme(val || 'default');
  handleUpdateField({ theme: val || '' });
}}
```

改为：
```typescript
onValueChange={async (val) => {
  const theme = val || 'default';
  setSelectedTheme(theme);
  handleUpdateField({ theme: val || '' });
  // 自动触发转换
  if (!id || converting) return;
  setConverting(true);
  setError('');
  try {
    const res = await convertArticle(parseInt(id!, 10), theme);
    if (res.data.code === 0 && res.data.data) {
      setArticle(res.data.data);
      await loadPreview();
    }
  } catch {
    setError('转换失败');
  } finally {
    setConverting(false);
  }
}}
```

注意：不能直接调用 `handleConvert()`，因为 `handleConvert` 闭包中的 `selectedTheme` 还是旧值（setState 是异步的）。需要直接使用回调参数 `theme`。

**改动 2：在主题下拉框旁显示转换中状态**

在 Select 组件下方（第 307 行之后）加一行加载提示：
```tsx
{converting && (
  <p className="text-[10px] text-blue-500 flex items-center gap-1 ml-0.5">
    <RefreshCw size={10} className="animate-spin" /> 正在应用主题...
  </p>
)}
```

仅此 2 处改动，无需修改后端或 API 层。

## 验证

1. `cd web && npx tsc --noEmit` 确认无类型错误
2. 启动前后端，浏览器打开文章预览页
3. 在主题下拉框中切换不同主题，确认预览自动刷新
4. 确认转换期间显示「正在应用主题...」加载提示
5. 确认「操作」标签中的「重新转换内容」按钮仍正常工作
