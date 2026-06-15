# 需求管理功能开发文档

## 功能概述

需求管理页面（Demand Management）是为产品经理（PM）/ 超级管理员提供的需求审核、沟通和转化工具。

## 实现的功能

### 1. 页面组件
- **路径**: `/admin/demand-management`
- **文件**: `frontend/src/views/DemandManagementView.vue`
- **权限**: 需要 `admin:demands` 权限

### 2. 核心功能

#### 2.1 需求统计面板
- 显示总需求数、待审核、沟通中、已转任务、已关闭等统计数据
- 实时更新统计信息

#### 2.2 需求列表
- 表格展示所有需求
- 支持的列：
  - 需求编号
  - 需求详情（标题 + 描述）
  - 提交时间
  - 审核状态（待审核、沟通中、已转任务、已关闭）
  - 转化状态（未转化、待评估、已转化、开发中、已完成）
  - 发布者
  - 关联任务
  - 进度条
  - 操作按钮（详情、编辑）

#### 2.3 筛选功能
- 关键字搜索：支持搜索需求编号、标题、发布者、任务编号
- 审核状态筛选：全部 / 待审核 / 沟通中 / 已转任务 / 已关闭
- 转化状态筛选：全部 / 未转化 / 待评估 / 已转化 / 开发中 / 已完成

#### 2.4 分页
- 客户端分页，每页显示 10 条记录
- 分页组件集成

#### 2.5 编辑弹窗
- 只读字段：需求编号、发布者、提交时间
- 可编辑字段：
  - 需求详情（标题）
  - 关联任务 ID
  - 审核状态
  - 转化状态
  - 进度（0-100）
  - 平台反馈（多行文本）
- 保存后实时更新列表和统计数据

#### 2.6 导出功能
- 导出需求数据（按当前筛选条件）

## 技术实现

### API 层
- **文件**: `frontend/src/api/admin-demands.ts`
- **接口**:
  - `GET /api/admin/demands` - 获取需求列表
  - `GET /api/admin/demands/stats` - 获取统计数据
  - `GET /api/admin/demands/:id` - 获取单个需求
  - `PATCH /api/admin/demands/:id` - 更新需求
  - `GET /api/admin/demands/export` - 导出需求

### Mock 数据
- **文件**: `frontend/src/mocks/handlers/admin-demands.ts`
- 包含 5 条示例需求数据
- 模拟完整的 CRUD 操作

### 组件复用
严格遵循 `frontend/CLAUDE.md` 规范，使用以下组件：
- `OrdButton` - 按钮
- `OrdCard` - 卡片容器
- `OrdSearchBox` - 搜索框
- `OrdSelect` - 下拉选择
- `OrdTable` / `OrdTableHeader` / `OrdTableRow` / `OrdTableCell` - 表格
- `OrdBadge` - 状态标签
- `OrdProgress` - 进度条
- `OrdEmptyState` - 空状态
- `OrdPagination` - 分页
- `OrdDialog` - 弹窗
- `OrdInput` / `OrdTextarea` - 表单输入
- `useToast()` - Toast 通知

### 样式实现
- 使用 scoped CSS
- 使用 CSS 变量（定义在 `src/styles/tokens.css`）
- 不使用 Tailwind CSS
- 完全复刻 `demo/all-pages/demand-management.html` 的设计

## 路由配置

```typescript
{
  path: '/admin/demand-management',
  name: 'demand-management',
  component: () => import('@/views/DemandManagementView.vue'),
  meta: { requiresAuth: true, permission: 'admin:demands' }
}
```

## 测试访问

1. 启动开发服务器：
```bash
cd frontend
npm run dev
```

2. 访问页面：
- 直接访问：`http://localhost:5173/admin/demand-management`
- 需要先登录并具有管理员权限

## 数据结构

### AdminDemand 接口
```typescript
interface AdminDemand {
  id: string                    // 需求编号
  title: string                 // 需求标题
  description: string           // 需求描述
  submitted_at: string          // 提交时间
  review_status: '待审核' | '沟通中' | '已转任务' | '已关闭'
  convert_status: '未转化' | '待评估' | '已转化' | '开发中' | '已完成'
  publisher: string             // 发布者姓名
  publisher_id: string          // 发布者 ID
  task_id: string | null        // 关联任务 ID
  progress: number              // 进度 (0-100)
  feedback: string              // 平台反馈
  urgency: string               // 紧急程度
  contact_phone: string         // 联系电话
  created_at: string            // 创建时间
  updated_at: string            // 更新时间
}
```

## 后续工作

1. 与后端 API 对接
2. 添加批量操作功能
3. 添加需求详情页面的跳转逻辑
4. 完善权限控制
5. 添加更多筛选条件（如紧急程度、提交时间范围）
6. 优化移动端响应式布局

## 相关文件

- `/frontend/src/views/DemandManagementView.vue` - 主页面组件
- `/frontend/src/api/admin-demands.ts` - API 接口定义
- `/frontend/src/mocks/handlers/admin-demands.ts` - Mock 数据和处理器
- `/frontend/src/router/index.ts` - 路由配置
- `/demo/all-pages/demand-management.html` - 原型参考
