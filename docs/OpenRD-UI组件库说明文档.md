# OpenRD-UI 组件库说明文档

## 概览

OpenRD-UI 是 OpenRD 协作平台的自建 Vue 3 组件库，基于 [Reka UI](https://reka-ui.com/) 无头组件原语构建，提供完整的 Webflow 风格视觉设计。

**核心特点：**

- 20 个生产就绪组件，覆盖平台所有 UI 模式
- 组件前缀 `Ord`（OpenRD 缩写），避免命名冲突
- Reka UI 提供交互行为与可访问性，自定义 CSS 提供视觉设计
- TypeScript 原生支持，完整类型推断
- 按需导入，支持 tree-shaking
- scoped CSS + CSS 变量，无第三方 CSS 框架依赖

---

## 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 `http://localhost:5173/dev` 查看组件预览页面。

### 导入组件

```vue
<script setup lang="ts">
import { OrdButton, OrdDialog, OrdBadge } from '@/components/ui'
</script>

<template>
  <OrdButton variant="primary" @click="handleSubmit">提交需求</OrdButton>
  <OrdBadge variant="green">已完成</OrdBadge>
</template>
```

---

## 设计令牌

所有样式通过 CSS 变量控制，定义在 `src/styles/tokens.css`：

### 颜色

| 变量 | 值 | 用途 |
|------|-----|------|
| `--ord-color-blue` | #146ef5 | 主色，CTA 按钮 |
| `--ord-color-blue-hover` | #0055d4 | 按钮 hover |
| `--ord-color-black` | #080808 | 正文文字 |
| `--ord-color-white` | #ffffff | 背景 |
| `--ord-color-purple` | #7a3dff | 辅助色 |
| `--ord-color-pink` | #ed52cb | 辅助色 |
| `--ord-color-green` | #00d722 | 成功状态 |
| `--ord-color-orange` | #ff6b00 | 警告状态 |
| `--ord-color-red` | #ee1d36 | 错误状态 |
| `--ord-color-yellow` | #ffae13 | 待处理状态 |
| `--ord-color-gray-800` | #222222 | 深灰文字 |
| `--ord-color-gray-700` | #363636 | 中灰文字 |
| `--ord-color-gray-500` | #5a5a5a | 浅灰文字 |
| `--ord-color-gray-300` | #ababab | 占位符 |
| `--ord-color-border` | #d8d8d8 | 边框 |
| `--ord-color-bg-subtle` | #f8f8f8 | 微妙背景 |

### 阴影

| 变量 | 用途 |
|------|------|
| `--ord-shadow-cascade` | 5 层级联阴影，用于卡片 |
| `--ord-shadow-nav` | 导航栏阴影 |
| `--ord-shadow-button` | 按钮 hover 阴影 |

### 圆角

| 变量 | 值 | 用途 |
|------|-----|------|
| `--ord-radius-sm` | 4px | 按钮、输入框 |
| `--ord-radius-md` | 8px | 卡片、弹窗 |
| `--ord-radius-lg` | 12px | 大容器 |
| `--ord-radius-full` | 9999px | 圆形头像 |

### 间距

`--ord-space-1` (4px) 到 `--ord-space-12` (48px)，以 4px 为基础单位递增。

---

## 组件清单

### P0 核心组件

| 组件 | 说明 | Reka UI |
|------|------|---------|
| OrdButton | 按钮 | 否 |
| OrdInput | 单行输入 | 否 |
| OrdTextarea | 多行输入 | 否 |
| OrdCard / OrdCardHeader / OrdCardContent | 卡片容器 | 否 |
| OrdBadge | 状态标签 | 否 |
| OrdTable / OrdTableHeader / OrdTableRow / OrdTableCell | 数据表格 | 否 |
| OrdDialog | 对话框 | 是 |

### P1 交互组件

| 组件 | 说明 | Reka UI |
|------|------|---------|
| OrdTabs / OrdTabsList / OrdTabsTrigger / OrdTabsContent | 选项卡 | 是 |
| OrdDropdown / OrdDropdownItem | 下拉菜单 | 是 |
| OrdSelect | 选择器 | 是 |
| OrdToastProvider + useToast() | 消息通知 | 是 |
| OrdPagination | 分页 | 否 |
| OrdNavbar | 顶部导航栏 | 否 |
| OrdSidebar | 侧边栏导航 | 否 |

### P2 专用组件

| 组件 | 说明 | Reka UI |
|------|------|---------|
| OrdAvatar | 头像 | 否 |
| OrdTooltip | 提示气泡 | 是 |
| OrdProgress | 进度条 | 否 |
| OrdTimeline | 时间线 | 否 |
| OrdFileUpload | 文件上传 | 否 |
| OrdEmptyState | 空状态 | 否 |
| OrdSearchBox | 搜索框 | 否 |

---

## 组件 API 详解

### OrdButton

```vue
<OrdButton variant="primary" size="md" :loading="false" :disabled="false">
  按钮文字
</OrdButton>
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| variant | `'primary' \| 'ghost' \| 'outline'` | `'primary'` | 样式变体 |
| size | `'sm' \| 'md' \| 'lg'` | `'md'` | 尺寸 |
| loading | `boolean` | `false` | 加载中状态 |
| disabled | `boolean` | `false` | 禁用状态 |

交互效果：hover 时 `translateX(6px)`，primary hover 显示蓝色阴影。

---

### OrdInput

```vue
<OrdInput v-model="value" type="text" placeholder="请输入" :error="false" :disabled="false" />
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| modelValue | `string` | — | 双向绑定值 |
| type | `string` | `'text'` | 输入类型 |
| placeholder | `string` | — | 占位文字 |
| error | `boolean` | `false` | 错误状态（红色边框） |
| disabled | `boolean` | `false` | 禁用状态 |

---

### OrdTextarea

```vue
<OrdTextarea v-model="value" placeholder="请输入" :rows="4" :error="false" :disabled="false" />
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| modelValue | `string` | — | 双向绑定值 |
| placeholder | `string` | — | 占位文字 |
| rows | `number` | `4` | 行数 |
| error | `boolean` | `false` | 错误状态 |
| disabled | `boolean` | `false` | 禁用状态 |

---

### OrdCard / OrdCardHeader / OrdCardContent

```vue
<OrdCard>
  <OrdCardHeader>标题</OrdCardHeader>
  <OrdCardContent>内容</OrdCardContent>
</OrdCard>
```

组合式组件，通过插槽组合使用。Card 自带级联阴影和毛玻璃效果。

---

### OrdBadge

```vue
<OrdBadge variant="blue">进行中</OrdBadge>
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| variant | `'blue' \| 'purple' \| 'green' \| 'orange' \| 'pink' \| 'red' \| 'gray'` | `'blue'` | 颜色变体 |

---

### OrdTable 系列

```vue
<OrdTable>
  <OrdTableHeader>
    <OrdTableCell header>列名</OrdTableCell>
  </OrdTableHeader>
  <OrdTableRow>
    <OrdTableCell>数据</OrdTableCell>
  </OrdTableRow>
</OrdTable>
```

OrdTableCell 的 `header` prop 控制渲染为 `<th>` 或 `<td>`。

---

### OrdDialog

```vue
<OrdDialog v-model:open="isOpen" title="对话框标题" description="描述文字">
  <p>主体内容</p>
  <template #footer>
    <OrdButton variant="ghost" @click="isOpen = false">取消</OrdButton>
    <OrdButton @click="confirm">确认</OrdButton>
  </template>
</OrdDialog>
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| open | `boolean` | `false` | 双向绑定，控制显隐 |
| title | `string` | — | 标题 |
| description | `string` | — | 描述 |

插槽：`default`（主体）、`trigger`（触发器）、`footer`（底部操作区）。

基于 Reka UI，自动处理焦点锁定、ESC 关闭、遮罩点击关闭。

---

### OrdTabs 系列

```vue
<OrdTabs default-value="tab1">
  <OrdTabsList>
    <OrdTabsTrigger value="tab1">标签1</OrdTabsTrigger>
    <OrdTabsTrigger value="tab2">标签2</OrdTabsTrigger>
  </OrdTabsList>
  <OrdTabsContent value="tab1">内容1</OrdTabsContent>
  <OrdTabsContent value="tab2">内容2</OrdTabsContent>
</OrdTabs>
```

基于 Reka UI，支持键盘左右切换。

---

### OrdDropdown / OrdDropdownItem

```vue
<OrdDropdown>
  <template #trigger>
    <OrdButton variant="ghost">菜单 ▾</OrdButton>
  </template>
  <OrdDropdownItem>选项1</OrdDropdownItem>
  <OrdDropdownItem>选项2</OrdDropdownItem>
</OrdDropdown>
```

基于 Reka UI，自动处理定位、键盘导航。

---

### OrdSelect

```vue
<OrdSelect v-model="value" :options="options" placeholder="请选择" />
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| modelValue | `string` | — | 双向绑定 |
| options | `{value: string, label: string}[]` | — | 选项列表 |
| placeholder | `string` | `'请选择'` | 占位文字 |

---

### OrdToast (useToast)

```ts
import { useToast } from '@/components/ui'

const { show } = useToast()

show({ title: '操作成功', description: '需求已提交', variant: 'success' })
show({ title: '操作失败', variant: 'error', duration: 5000 })
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| title | `string` | — | 标题（必填） |
| description | `string` | — | 描述 |
| variant | `'default' \| 'success' \| 'error'` | `'default'` | 样式 |
| duration | `number` | `3000` | 自动消失时间（ms） |

需要在 App.vue 中放置 `<OrdToastProvider>` 包裹应用。

---

### OrdPagination

```vue
<OrdPagination v-model:current-page="page" :total="100" :page-size="10" />
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| currentPage | `number` | `1` | 双向绑定当前页 |
| total | `number` | — | 总条数 |
| pageSize | `number` | `10` | 每页条数 |

---

### OrdNavbar

```vue
<OrdNavbar>
  <template #brand>OpenRD</template>
  <template #center>导航内容</template>
  <template #actions>
    <OrdButton size="sm">操作</OrdButton>
  </template>
</OrdNavbar>
```

固定定位在页面顶部，高度 76px，毛玻璃背景。

---

### OrdSidebar

```vue
<OrdSidebar :items="items" @select="handleSelect" />
```

| Prop | 类型 | 说明 |
|------|------|------|
| items | `{label: string, icon?: string, to?: string, active?: boolean}[]` | 导航项 |

事件：`select(item)` — 点击某项时触发。

---

### OrdAvatar

```vue
<OrdAvatar name="张三" size="md" />
<OrdAvatar name="李明华" src="/avatar.jpg" size="lg" />
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| name | `string` | — | 显示名（必填，用于生成首字母） |
| src | `string` | — | 头像图片地址 |
| size | `'sm' \| 'md' \| 'lg'` | `'md'` | 尺寸（28/36/48px） |

---

### OrdTooltip

```vue
<OrdTooltip content="提示文字" side="top">
  <OrdButton>悬停我</OrdButton>
</OrdTooltip>
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| content | `string` | — | 提示内容 |
| side | `'top' \| 'bottom' \| 'left' \| 'right'` | `'top'` | 弹出方向 |
| delayDuration | `number` | `200` | 延迟显示（ms） |

---

### OrdProgress

```vue
<OrdProgress :value="68" variant="gradient" />
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| value | `number` | — | 进度值（0-100） |
| variant | `'blue' \| 'gradient'` | `'blue'` | 样式 |

---

### OrdTimeline

```vue
<OrdTimeline :items="items" />
```

| Prop | 类型 | 说明 |
|------|------|------|
| items | `{title: string, status: 'done'\|'active'\|'pending', description?: string, date?: string}[]` | 时间线节点 |

---

### OrdFileUpload

```vue
<OrdFileUpload v-model="files" accept=".pdf,.docx" multiple />
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| modelValue | `File[]` | `[]` | 双向绑定文件列表 |
| accept | `string` | `'*'` | 接受的文件类型 |
| multiple | `boolean` | `false` | 是否多选 |

支持拖拽上传和点击选择。

---

### OrdEmptyState

```vue
<OrdEmptyState>
  <template #icon>🔍</template>
  <template #title>暂无数据</template>
  <template #description>还没有任何记录</template>
  <template #action>
    <OrdButton size="sm">创建</OrdButton>
  </template>
</OrdEmptyState>
```

插槽：`icon`、`title`、`description`、`action`，均为可选。

---

### OrdSearchBox

```vue
<OrdSearchBox v-model="keyword" placeholder="搜索..." width="300px" />
```

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| modelValue | `string` | — | 双向绑定搜索值 |
| placeholder | `string` | `'搜索...'` | 占位文字 |
| width | `string` | `'260px'` | 宽度 |

---

## 开发规范

### 命名规则

| 规则 | 说明 |
|------|------|
| 组件前缀 `Ord` | 所有组件以 Ord 开头 |
| PascalCase | 组件文件名和导出名 |
| CSS 类名 | BEM-like：`.ord-button--primary` |
| Props | camelCase |

### 样式规则

- 使用 scoped CSS + CSS 变量
- 不使用 Tailwind CSS
- 不硬编码颜色值，必须引用 `--ord-*` 变量
- 组件内使用 `var(--ord-transition-base)` 作为统一过渡时长

### 新增组件流程

1. 评估是否能用现有组件组合实现
2. 确定是否需要 Reka UI 原语（有复杂交互/无障碍需求则用）
3. 参考 `demo/` 中对应页面的 HTML/CSS 实现
4. 在 `src/components/ui/{name}/` 下创建 Vue SFC
5. 在 `src/components/ui/index.ts` 中添加导出
6. 更新本文档的组件清单

---

## 项目结构

```
frontend/src/
├── styles/
│   ├── tokens.css              # 设计令牌
│   └── base.css                # 全局重置
├── components/ui/
│   ├── index.ts                # 统一导出
│   ├── button/OrdButton.vue
│   ├── input/OrdInput.vue
│   ├── input/OrdTextarea.vue
│   ├── card/OrdCard.vue
│   ├── card/OrdCardHeader.vue
│   ├── card/OrdCardContent.vue
│   ├── badge/OrdBadge.vue
│   ├── table/OrdTable.vue
│   ├── table/OrdTableHeader.vue
│   ├── table/OrdTableRow.vue
│   ├── table/OrdTableCell.vue
│   ├── dialog/OrdDialog.vue
│   ├── tabs/OrdTabs.vue
│   ├── tabs/OrdTabsList.vue
│   ├── tabs/OrdTabsTrigger.vue
│   ├── tabs/OrdTabsContent.vue
│   ├── dropdown/OrdDropdown.vue
│   ├── dropdown/OrdDropdownItem.vue
│   ├── select/OrdSelect.vue
│   ├── toast/OrdToastProvider.vue
│   ├── toast/OrdToast.vue
│   ├── toast/useToast.ts
│   ├── pagination/OrdPagination.vue
│   ├── navbar/OrdNavbar.vue
│   ├── sidebar/OrdSidebar.vue
│   ├── avatar/OrdAvatar.vue
│   ├── tooltip/OrdTooltip.vue
│   ├── progress/OrdProgress.vue
│   ├── timeline/OrdTimeline.vue
│   ├── file-upload/OrdFileUpload.vue
│   ├── empty-state/OrdEmptyState.vue
│   └── search-box/OrdSearchBox.vue
└── views/
    └── DevPlayground.vue       # 组件预览页
```

---

## 技术栈

| 依赖 | 版本 | 用途 |
|------|------|------|
| Vue | 3.5.32 | 框架 |
| Reka UI | 2.9.10 | 无头组件原语 |
| TypeScript | 6.0.0 | 类型安全 |
| Vite | 8.0.8 | 构建工具 |
| Vue Router | 5.0.4 | 路由 |
| Pinia | 3.0.4 | 状态管理 |
