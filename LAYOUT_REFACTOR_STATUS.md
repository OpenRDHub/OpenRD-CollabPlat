# 重要提示 - Layout 重构未完成

## 当前状态

### ✅ 已完成
1. ✅ 创建 TopNavbar 组件 (`frontend/src/components/TopNavbar.vue`)
   - 完全复刻 demo 的顶部导航栏
   - 包含品牌 Logo、导航按钮、提需求按钮、个人信息下拉
   
2. ✅ 更新 HallView.vue
   - 添加了 TopNavbar
   - 添加了 page-shell 和 hall-main 容器
   - 页面背景渐变

3. ✅ 更新路由配置
   - 移除了 AppLayout 的嵌套路由
   - 改为平级路由

### ⚠️ 未完成

1. **DashboardView.vue 被删除了**
   - 需要重新创建完整的工作台界面
   - 参考：`demo/all-pages/workbench.html`
   - 结构：TopNavbar + page-shell + workbench-main + workbench-view

2. **MyDemandsView.vue 需要更新**
   - 需要添加 TopNavbar
   - 需要添加页面容器结构

3. **其他视图页面**
   - 所有需要认证的页面都需要添加 TopNavbar
   - 移除对 AppLayout 的依赖

## 🚨 紧急修复步骤

### 步骤 1：恢复 DashboardView.vue
```bash
git checkout frontend/src/views/DashboardView.vue
```

### 步骤 2：参考我创建的结构
查看 `frontend/src/components/TopNavbar.vue` 和更新后的 `HallView.vue`

### 步骤 3：手动重构每个页面
每个页面的结构应该是：
```vue
<template>
  <div class="page-shell">
    <TopNavbar />
    
    <main class="page-main">
      <div class="page-content">
        <!-- 原有内容 -->
      </div>
    </main>
  </div>
</template>

<style scoped>
.page-shell {
  min-height: 100vh;
  background: /* 渐变背景 */;
}

.page-main {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 94px 32px 32px;
}

.page-content {
  position: relative;
  width: min(1460px, 100%);
}
</style>
```

## 📋 需要重构的文件清单

- [ ] `frontend/src/views/DashboardView.vue` - **已删除，需重建**
- [ ] `frontend/src/views/MyDemandsView.vue` - 添加 TopNavbar
- [ ] `frontend/src/views/DemandDetailView.vue` - 添加 TopNavbar
- [ ] 其他所有需要认证的视图页面

## 💡 建议

由于重构工作量较大，建议：

**方案 A（推荐）**：恢复原有 AppLayout，保持现有结构
```bash
git checkout frontend/src/router/index.ts
git checkout frontend/src/views/DashboardView.vue
```

**方案 B**：继续完成重构
1. 重新创建 DashboardView.vue（复制 workbench.html 的结构）
2. 更新所有视图页面添加 TopNavbar
3. 测试所有路由和页面

**方案 C**：分步重构
1. 先恢复 DashboardView.vue
2. 只重构 HallView 和 DashboardView 两个主要页面
3. 其他页面保持使用 AppLayout（混合模式）

## 当前 Git 状态

未提交的更改：
- 新增：TopNavbar.vue
- 修改：HallView.vue（已更新）
- 修改：router/index.ts（已移除 AppLayout）
- 删除：DashboardView.vue（意外删除）

建议先提交 HallView 和 TopNavbar，然后恢复 DashboardView。
