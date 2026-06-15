# feature/demand-submit 使用指南

## 快速开始

### 1. 启动开发服务器

```bash
cd frontend
npm run dev
```

访问：http://localhost:5173

### 2. 测试流程

#### 场景 1：提交需求

1. 登录后进入工作台（Dashboard）
2. 点击右上角"提需求"按钮
3. 填写需求信息：
   - **需求标题**（必填）：例如"希望记录复诊前的问题清单"
   - **需求详情**（必填）：详细描述问题和期望
   - **联系电话**或**微信号**（至少填一个）
   - **附件**（可选）：上传病历截图、需求草图等
   - 勾选隐私条款确认
4. 点击"提交需求"
5. 提交成功后会显示 Toast 提示，弹窗自动关闭

#### 场景 2：查看我的需求

1. 从 Dashboard 点击"我的需求"按钮
2. 或直接访问：http://localhost:5173/my-demands
3. 页面功能：
   - **统计卡片**：查看需求总数、待审核、已转任务、已关闭数量
   - **Tab 筛选**：切换查看不同生命周期的需求
   - **状态筛选**：按审核状态筛选
   - **搜索**：输入关键词搜索需求
   - **需求列表**：查看需求详情、提交时间、进度等
   - **分页**：每页 3 条，可翻页查看

#### 场景 3：查看需求详情

1. 在需求列表中点击"查看详情"按钮
2. 跳转到需求详情页（当前为占位页）
3. 实际详情页将在后续 Sprint 实现

## 页面路由

| 路由 | 页面 | 说明 |
|------|------|------|
| `/dashboard` | 工作台 | 包含"提需求"按钮 |
| `/my-demands` | 我的需求列表 | 查看、筛选、搜索需求 |
| `/demands/:id` | 需求详情 | 查看单个需求详情（占位） |

## 组件导入

### DemandSubmitDialog（需求提交弹窗）

```vue
<script setup>
import { ref } from 'vue'
import DemandSubmitDialog from '@/components/DemandSubmitDialog.vue'

const showDialog = ref(false)

const handleSuccess = () => {
  console.log('需求提交成功')
  // 刷新数据或跳转
}
</script>

<template>
  <button @click="showDialog = true">提需求</button>
  
  <DemandSubmitDialog
    v-model:open="showDialog"
    @submit-success="handleSuccess"
  />
</template>
```

## Mock 数据说明

当前使用 MSW（Mock Service Worker）模拟后端接口：

### 提交需求
- **接口**：`POST /api/v1/demands`
- **请求体**：
  ```json
  {
    "title": "需求标题",
    "description": "需求详情",
    "contact_phone": "手机号",
    "wechat_id": "微信号",
    "attachment_ids": ["file_123"]
  }
  ```
- **响应**：
  ```json
  {
    "code": "OK",
    "data": {
      "id": "REQ-1234567890",
      "status": "待审核"
    }
  }
  ```

### 获取我的需求
- **接口**：`GET /api/v1/me/demands`
- **查询参数**：
  - `status`：筛选状态
  - `keyword`：搜索关键词
  - `page`：页码（默认 1）
  - `page_size`：每页数量（默认 10）
- **响应**：分页数据格式

### 模拟数据
位置：`frontend/src/mocks/data/demands.ts`

包含 5 条不同状态的需求：
- REQ-2418：已转任务（68%）
- REQ-2432：沟通中（36%）
- REQ-2440：待审核（12%）
- REQ-2356：已关闭（100%）
- REQ-2380：已转任务（42%）

## 样式说明

### 设计令牌
所有颜色、间距、圆角都使用 CSS 变量，定义在 `frontend/src/styles/tokens.css`：

```css
--ord-color-blue: #146ef5;        /* 主色 */
--ord-color-blue-hover: #0055d4;  /* 按钮 hover */
--ord-color-gray-500: #5a5a5a;    /* 次要文字 */
--ord-radius-sm: 4px;             /* 按钮、输入框 */
--ord-radius-md: 8px;             /* 卡片、弹窗 */
--ord-shadow-cascade: ...;        /* 5 层阴影 */
```

### 响应式断点
- **桌面端**：>= 992px（4 列统计卡片）
- **平板端**：768px - 992px（2 列统计卡片）
- **移动端**：< 768px（1 列统计卡片，Tab 自适应）

## 开发规范

### 必须遵循
1. ✅ 所有 UI 组件从 `@/components/ui` 导入
2. ✅ 禁止引入第三方 UI 库（Element Plus、Naive UI 等）
3. ✅ 组件前缀必须是 `Ord`
4. ✅ 使用 scoped CSS + CSS 变量
5. ✅ 禁止硬编码颜色值
6. ✅ 禁止使用 Tailwind CSS

### 如需新组件
如果缺少组件，必须：
1. 先告知需要新建什么组件
2. 不要用第三方库替代
3. 基于 Reka UI 无头原语封装

详见：`frontend/CLAUDE.md`

## 常见问题

### Q1：提交需求后看不到新数据？
A：当前使用 Mock 数据，新提交的需求会添加到内存中。刷新页面后会重置。真实环境会持久化到数据库。

### Q2：需求详情页显示占位内容？
A：需求详情页将在后续 Sprint（feature/demand-detail）中实现。

### Q3：文件上传失败？
A：当前文件上传是模拟实现，只记录文件名。真实上传功能需要后端 `/api/v1/files` 接口支持。

### Q4：分页每页只显示 3 条？
A：这是为了方便测试分页功能。实际可以修改 `pageSize` 常量。

### Q5：搜索和筛选是前端实现的吗？
A：当前 Mock 实现是前端筛选。真实环境会调用后端接口，由后端处理筛选逻辑。

## 后续迭代计划

### Sprint 1（第 4 周）
- [ ] 需求详情页（多 Tab：基本信息、沟通记录、附件、状态流转）
- [ ] 需求管理页（运管视角）

### Sprint 2（第 5-6 周）
- [ ] 任务模块（任务列表、任务详情）
- [ ] 队伍管理

### Sprint 3（第 7-8 周）
- [ ] 管理后台（用户管理、权限管理、系统日志）
- [ ] 消息中心

## 联系方式

如有问题，请参考：
- PRD：`docs/OpenRD协作平台PRD正式版.md`
- 技术文档：`docs/OpenRD协作平台技术文档.md`
- 组件文档：`docs/OpenRD-UI组件库说明文档.md`
