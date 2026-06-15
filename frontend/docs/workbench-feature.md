# 工作台功能开发文档

## 功能概述

工作台页面（Workbench）是用户登录后的核心工作区，根据用户角色展示个性化的统计信息和功能入口。

## 实现的功能

### 1. 页面组件
- **路径**: `/workbench` (也可通过 `/dashboard` 访问)
- **文件**: `frontend/src/views/WorkbenchView.vue`
- **权限**: 需要登录认证

### 2. 核心功能

#### 2.1 角色自适应
根据用户的真实角色自动展示对应的工作台：
- **运营管理员 (operator)**: 需求沟通、任务转化相关功能
- **共建者 (builder)**: 任务大厅、队伍协作相关功能
- **需求者 (requester)**: 需求提交、需求查看相关功能
- **超级管理员 (admin)**: 全局管理功能

#### 2.2 统计卡片区域
每个角色展示不同的关键指标：

**运营管理员**:
- 待沟通需求：2 (仅展示当前运管自己的会话)
- 可转化需求：1 (信息充分，可生成任务工单)
- 已转化追踪：0 (转化后进入任务详情查看)

**共建者**:
- 可申请任务：8 (任务大厅公开招募中)
- 进行中任务：3 (我参与的开发任务)
- 已完成任务：12 (累计交付成果)

**需求者**:
- 待审核需求：1 (等待运管审核处理)
- 沟通中需求：2 (运管正在补齐信息)
- 已转化任务：5 (需求已生成任务工单)

**超级管理员**:
- 总用户数：248 (平台注册用户)
- 总需求数：156 (所有需求记录)
- 总任务数：89 (所有任务记录)
- 活跃队伍：32 (进行中的协作队伍)

#### 2.3 功能卡片网格
每个角色展示不同的功能入口：

**运营管理员功能**:
- 个人信息
- 消息中心
- 需求沟通
- 我的任务
- 我的需求

**共建者功能**:
- 任务大厅
- 我的任务
- 队伍协作
- 个人信息
- 消息中心

**需求者功能**:
- 提交需求
- 我的需求
- 需求详情
- 个人信息
- 消息中心

**超级管理员功能**:
- 用户管理
- 需求管理
- 任务管理
- 系统日志
- 个人信息
- 消息中心

#### 2.4 交互功能
- **卡片点击**: 点击功能卡片后显示 Toast 提示，然后跳转到对应页面
- **悬停效果**: 卡片悬停时显示边框高亮和阴影效果
- **过渡动画**: 平滑的 translateX 过渡效果

#### 2.5 背景装饰
- **Ambient Ring**: 右上角的圆环装饰
- **Ambient Node**: 左下角的节点装饰
- 创造沉浸式的视觉体验

## 技术实现

### 角色映射逻辑
```typescript
const activeRole = computed(() => {
  const role = auth.userRole || 'requester'
  // 将系统角色映射到工作台角色
  if (role === 'admin') return 'admin'
  if (role === 'operator') return 'operator'
  if (role === 'builder') return 'builder'
  return 'requester' // 默认为需求者
})
```

### 数据结构

#### 角色配置
```typescript
interface RoleConfig {
  title: string          // 工作台标题
  description: string    // 工作台描述
  tileSummary: string    // 功能区说明
  metrics: Metric[]      // 统计指标
  tiles: string[]        // 功能卡片键名列表
}

interface Metric {
  title: string          // 指标标题
  value: string          // 指标数值
  note: string           // 指标说明
  tone: string           // 背景色调
}
```

#### 功能卡片
```typescript
interface Tile {
  title: string          // 卡片标题
  desc: string           // 卡片描述
  badge: string          // 徽章文字
  icon: string           // 图标字符
  color: string          // 图标颜色
  bg: string             // 图标背景色
  route: string          // 跳转路由
}
```

## 设计复刻对比

| 元素 | 原型设计 | 实现状态 |
|------|---------|---------|
| Hero 卡片 | ✅ | ✅ 完全复刻 |
| 背景装饰（ring + node） | ✅ | ✅ 完全复刻 |
| 统计卡片网格 | ✅ | ✅ 完全复刻 |
| 功能卡片网格 | ✅ | ✅ 完全复刻 |
| 卡片悬停效果 | ✅ | ✅ 完全复刻 |
| 响应式布局 | ✅ | ✅ 完全复刻 |
| Toast 通知 | ✅ | ✅ 使用 OrdToast |

## 样式实现

### 核心样式特点
- 使用 CSS 变量（`--ord-color-*`, `--ord-space-*`）
- 玻璃态效果（`backdrop-filter: blur(16px)`）
- 级联阴影（`--ord-shadow-cascade`）
- 平滑过渡动画（`--ord-transition-base`）
- 不使用 Tailwind CSS

### 响应式断点
- `1100px`: 网格从 4 列变为 2 列
- `900px`: 网格变为单列，移除背景装饰
- `520px`: 缩小标题字号

## 路由配置

```typescript
{ 
  path: '/workbench', 
  name: 'workbench', 
  component: () => import('@/views/WorkbenchView.vue'), 
  meta: { requiresAuth: true } 
}
{ 
  path: '/dashboard', 
  redirect: '/workbench' 
}
```

## 测试访问

1. 启动开发服务器：
```bash
cd frontend
npm run dev
```

2. 访问页面：
- 直接访问：`http://localhost:5173/workbench`
- 或者：`http://localhost:5173/dashboard`
- 需要先登录

3. 测试不同角色：
- 使用不同角色的账号登录
- 观察工作台显示的内容差异

## 功能测试清单

- [ ] 查看统计卡片是否正确显示
- [ ] 查看功能卡片是否正确显示
- [ ] 点击功能卡片，查看 Toast 提示
- [ ] 验证路由跳转是否正确
- [ ] 测试卡片悬停效果
- [ ] 测试响应式布局（调整浏览器宽度）
- [ ] 测试不同角色的工作台差异

## 与 DashboardView 的关系

- **DashboardView**: 旧的工作台组件（简单版本）
- **WorkbenchView**: 新的工作台组件（完整复刻版本）
- `/dashboard` 现在重定向到 `/workbench`
- 保留 DashboardView 是为了向后兼容

## 后续工作

### 短期
1. 与后端 API 对接，获取真实的统计数据
2. 实现统计数据的实时更新
3. 添加加载状态和错误处理
4. 完善各个功能卡片的跳转逻辑

### 中期
1. 添加快捷操作区域
2. 实现最近动态展示
3. 添加待办事项提醒
4. 优化移动端体验

### 长期
1. 个性化工作台配置
2. 自定义功能卡片排序
3. 数据可视化图表
4. 工作台小组件系统

## 相关文件

- `/frontend/src/views/WorkbenchView.vue` - 工作台主组件
- `/frontend/src/views/DashboardView.vue` - 旧版工作台（保留）
- `/frontend/src/router/index.ts` - 路由配置
- `/demo/operator/workbench.html` - 运管工作台原型
- `/demo/all-pages/workbench.html` - 完整工作台原型

## 设计原则

1. **角色驱动**: 根据用户角色自动适配内容
2. **信息层次**: 重要信息优先展示
3. **快速导航**: 一键直达常用功能
4. **视觉舒适**: 柔和的色彩和动画
5. **响应式**: 适配各种设备尺寸
