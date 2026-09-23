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
- 通过后端分页表格展示所有需求
- 支持的列：
  - 需求编号
  - 需求详情（标题 + 描述）
  - 创建时间
  - 需求状态（待审核、沟通中、已转任务、已关联、已驳回、已关闭、已归档）
  - 转化状态（未转化、已转化、已关联）
  - 发布者 ID
  - 关联任务
  - 进度条
  - 操作按钮（详情、编辑）

#### 2.3 筛选功能
- 关键字搜索：由后端搜索需求编号、标题、描述和关联任务编号
- 需求状态筛选：前端传递英文枚举，仅在展示层转换为中文
- 转化状态筛选：全部 / 已转化 / 已关联

#### 2.4 分页
- 服务端分页，每页显示 8 条记录
- 筛选或切页时重新请求 `GET /api/v1/demands`

#### 2.5 编辑弹窗
- 只读字段：需求编号、发布者 ID、创建时间
- 可编辑字段：负责运营 ID、进度（0-100）、平台反馈
- 状态变更必须调用转化、驳回、关联或归档 action 接口，不通过通用 PATCH 伪造
- 保存成功后重新读取列表和统计数据

#### 2.6 导出功能
- 导出需求数据（按当前筛选条件）

## 技术实现

### API 层
- **文件**: `frontend/src/api/demands.ts`
- **唯一合同**:
  - `GET /api/v1/demands` - 获取分页列表、统计和导出数据
  - `GET /api/v1/demands/:id` - 获取需求详情
  - `PATCH /api/v1/demands/:id` - 仅更新 `progress` / `feedback` / `owner_id`
  - `POST /api/v1/demands/:id/convert` - 转化为任务
  - `POST /api/v1/demands/:id/reject` - 驳回需求
  - `POST /api/v1/demands/:id/link-similar` - 关联需求或任务
  - `POST /api/v1/demands/:id/archive` - 归档需求

### Mock 数据
- **文件**: `frontend/src/mocks/handlers/demands.ts`
- 与真实后端使用同一路径、英文枚举和字段名
- 不维护管理端专属的 localStorage 补丁数据模型

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

### Demand 接口
```typescript
interface Demand {
  id: string                    // 需求编号
  title: string                 // 需求标题
  description: string           // 需求描述
  urgency: string
  status: 'pending_review' | 'communicating' | 'converted' | 'linked' | 'rejected' | 'closed' | 'archived'
  convert_status: '' | 'converted' | 'linked' | null
  creator_id: string            // 发布者 ID
  linked_task_id: string | null // 关联任务 ID
  linked_demand_id: string | null
  progress: number              // 进度 (0-100)
  feedback: string | null       // 平台反馈
  owner_id?: string | null      // 负责运营 ID
  created_at: string            // 创建时间
  updated_at: string            // 更新时间
}
```

## 后续工作

1. 添加批量操作功能
2. 完善权限控制
3. 添加更多筛选条件（如紧急程度、提交时间范围）
4. 优化移动端响应式布局

## 相关文件

- `/frontend/src/views/DemandManagementView.vue` - 主页面组件
- `/frontend/src/api/demands.ts` - 需求 API 的唯一前端定义
- `/frontend/src/mocks/handlers/demands.ts` - 与真实 API 合同一致的 Mock 处理器
- `/frontend/src/router/index.ts` - 路由配置
- `/demo/all-pages/demand-management.html` - 原型参考
