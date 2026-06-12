# 基于 Reka UI 的 OpenRD 组件库搭建指南

## 1. 为什么选择 Reka UI

[Reka UI](https://reka-ui.com/) 是 Vue 3 的无头（headless）组件库，前身为 Radix Vue。它提供：

- **无样式原语**：只提供行为和可访问性，样式完全由你控制
- **WAI-ARIA 合规**：键盘导航、屏幕阅读器支持开箱即用
- **组合式 API**：slot-based 设计，灵活组合
- **TypeScript 原生**：完整类型推断

这意味着我们可以将 `demo/` 中已验证的视觉设计（Webflow 风格）与 Reka UI 的交互原语结合，得到一个既好看又无障碍的组件库。

---

## 2. 项目结构

```
frontend/
├── src/
│   ├── components/
│   │   └── ui/                    # 自建组件库目录
│   │       ├── button/
│   │       │   ├── Button.vue
│   │       │   └── index.ts
│   │       ├── card/
│   │       │   ├── Card.vue
│   │       │   ├── CardHeader.vue
│   │       │   ├── CardContent.vue
│   │       │   └── index.ts
│   │       ├── dialog/
│   │       │   ├── Dialog.vue
│   │       │   ├── DialogContent.vue
│   │       │   ├── DialogTitle.vue
│   │       │   └── index.ts
│   │       ├── input/
│   │       │   ├── Input.vue
│   │       │   └── index.ts
│   │       ├── table/
│   │       │   ├── Table.vue
│   │       │   ├── TableHeader.vue
│   │       │   ├── TableRow.vue
│   │       │   ├── TableCell.vue
│   │       │   └── index.ts
│   │       ├── badge/
│   │       │   ├── Badge.vue
│   │       │   └── index.ts
│   │       ├── tabs/
│   │       │   ├── Tabs.vue
│   │       │   ├── TabsList.vue
│   │       │   ├── TabsTrigger.vue
│   │       │   ├── TabsContent.vue
│   │       │   └── index.ts
│   │       ├── dropdown/
│   │       │   ├── Dropdown.vue
│   │       │   ├── DropdownItem.vue
│   │       │   └── index.ts
│   │       ├── select/
│   │       │   ├── Select.vue
│   │       │   └── index.ts
│   │       ├── toast/
│   │       │   ├── Toast.vue
│   │       │   └── index.ts
│   │       └── index.ts           # 统一导出
│   ├── styles/
│   │   ├── tokens.css             # 设计变量（从 demo 提取）
│   │   └── base.css               # 全局重置 + 排版
│   └── ...
```

---

## 3. 安装依赖

```bash
npm install reka-ui
# 或
pnpm add reka-ui
```

Reka UI 支持 tree-shaking，只打包实际使用的组件。

---

## 4. 设计令牌提取

从 `demo/index.html` 的 CSS 变量中提取设计令牌，创建 `src/styles/tokens.css`：

```css
:root {
  /* Colors */
  --color-black: #080808;
  --color-white: #ffffff;
  --color-blue: #146ef5;
  --color-blue-hover: #0055d4;
  --color-blue-400: #3b89ff;
  --color-purple: #7a3dff;
  --color-pink: #ed52cb;
  --color-green: #00d722;
  --color-orange: #ff6b00;
  --color-yellow: #ffae13;
  --color-red: #ee1d36;
  --color-gray-800: #222222;
  --color-gray-700: #363636;
  --color-gray-500: #5a5a5a;
  --color-gray-300: #ababab;
  --color-border: #d8d8d8;
  --color-border-hover: #898989;
  --color-bg-subtle: #f8f8f8;

  /* Shadows */
  --shadow-cascade: rgba(0,0,0,0) 0px 84px 24px,
    rgba(0,0,0,0.01) 0px 54px 22px,
    rgba(0,0,0,0.04) 0px 30px 18px,
    rgba(0,0,0,0.08) 0px 13px 13px,
    rgba(0,0,0,0.09) 0px 3px 7px;

  /* Typography */
  --font-sans: 'WF Visual Sans Variable', Arial, sans-serif;
  --font-mono: 'Inconsolata', ui-monospace, monospace;

  /* Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
}
```

---

## 5. 组件映射：Demo → Reka UI 原语

| Demo 组件 | Reka UI 原语 | 说明 |
|-----------|-------------|------|
| `.primary-button` / `.ghost-button` | 无需原语（纯样式） | Button 是纯样式组件，无复杂交互 |
| Modal / Dialog | `DialogRoot`, `DialogTrigger`, `DialogPortal`, `DialogContent`, `DialogTitle` | 焦点锁定、ESC 关闭、遮罩 |
| 下拉菜单 | `DropdownMenuRoot`, `DropdownMenuTrigger`, `DropdownMenuContent`, `DropdownMenuItem` | 键盘导航、定位 |
| 选择器 | `SelectRoot`, `SelectTrigger`, `SelectContent`, `SelectItem` | 可搜索、虚拟滚动 |
| Tabs 切换 | `TabsRoot`, `TabsList`, `TabsTrigger`, `TabsContent` | 键盘左右切换 |
| Toast 通知 | `ToastRoot`, `ToastTitle`, `ToastDescription`, `ToastAction` | 自动消失、堆叠 |
| Tooltip | `TooltipRoot`, `TooltipTrigger`, `TooltipContent` | 延迟显示、定位 |
| 表格 | 无需原语（纯结构） | 纯 HTML table + 样式 |
| 表单输入 | 无需原语（原生 input） | 样式包装 |
| Badge | 无需原语（纯样式） | span + class |

**原则**：只在需要复杂交互行为（焦点管理、键盘导航、弹层定位）时使用 Reka UI 原语，纯视觉组件直接用 Vue 模板 + CSS。

---

## 6. 组件实现示例

### 6.1 Button（纯样式，无需 Reka UI）

```vue
<!-- src/components/ui/button/Button.vue -->
<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'ghost' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
}

withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
})
</script>

<template>
  <button
    class="rd-button"
    :class="[`rd-button--${variant}`, `rd-button--${size}`]"
    :disabled="disabled"
  >
    <slot />
  </button>
</template>

<style scoped>
.rd-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 42px;
  padding: 0 16px;
  border-radius: var(--radius-sm);
  font-family: var(--font-sans);
  font-size: 15px;
  font-weight: 600;
  line-height: 1.5;
  border: 1px solid transparent;
  cursor: pointer;
  transition: transform 180ms ease, background 180ms ease,
    border-color 180ms ease, box-shadow 180ms ease;
}

.rd-button:hover {
  transform: translateX(6px);
}

.rd-button:disabled {
  opacity: 0.5;
  pointer-events: none;
}

.rd-button--primary {
  color: var(--color-white);
  background: var(--color-blue);
  border-color: var(--color-blue);
}

.rd-button--primary:hover {
  background: var(--color-blue-hover);
  border-color: var(--color-blue-hover);
  box-shadow: 0 14px 28px rgba(20, 110, 245, 0.22);
}

.rd-button--ghost {
  color: var(--color-black);
  background: var(--color-white);
  border-color: var(--color-border);
}

.rd-button--ghost:hover {
  color: var(--color-blue);
  border-color: var(--color-blue);
}

.rd-button--outline {
  color: var(--color-blue);
  background: transparent;
  border-color: var(--color-blue);
}

.rd-button--sm { min-height: 32px; padding: 0 12px; font-size: 13px; }
.rd-button--lg { min-height: 48px; padding: 0 24px; font-size: 16px; }
</style>
```

### 6.2 Dialog（使用 Reka UI 原语）

```vue
<!-- src/components/ui/dialog/Dialog.vue -->
<script setup lang="ts">
import {
  DialogRoot,
  DialogTrigger,
  DialogPortal,
  DialogOverlay,
  DialogContent,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from 'reka-ui'

interface Props {
  title?: string
  description?: string
}

defineProps<Props>()
const open = defineModel<boolean>('open', { default: false })
</script>

<template>
  <DialogRoot v-model:open="open">
    <DialogTrigger as-child>
      <slot name="trigger" />
    </DialogTrigger>

    <DialogPortal>
      <DialogOverlay class="rd-dialog-overlay" />
      <DialogContent class="rd-dialog-content">
        <DialogTitle v-if="title" class="rd-dialog-title">
          {{ title }}
        </DialogTitle>
        <DialogDescription v-if="description" class="rd-dialog-desc">
          {{ description }}
        </DialogDescription>

        <slot />

        <DialogClose class="rd-dialog-close" aria-label="关闭">
          &times;
        </DialogClose>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>

<style scoped>
.rd-dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(8, 8, 8, 0.4);
  backdrop-filter: blur(4px);
  z-index: 1000;
  animation: fadeIn 150ms ease;
}

.rd-dialog-content {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: var(--color-white);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-cascade);
  padding: 32px;
  width: min(520px, calc(100vw - 48px));
  max-height: calc(100vh - 48px);
  overflow-y: auto;
  z-index: 1001;
  animation: scaleIn 200ms ease;
}

.rd-dialog-title {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 8px;
}

.rd-dialog-desc {
  font-size: 15px;
  color: var(--color-gray-500);
  margin-bottom: 24px;
}

.rd-dialog-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border: none;
  background: none;
  font-size: 20px;
  color: var(--color-gray-500);
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.rd-dialog-close:hover {
  background: var(--color-bg-subtle);
  color: var(--color-black);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scaleIn {
  from { opacity: 0; transform: translate(-50%, -50%) scale(0.96); }
  to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
}
</style>
```

### 6.3 Tabs（使用 Reka UI 原语）

```vue
<!-- src/components/ui/tabs/Tabs.vue -->
<script setup lang="ts">
import {
  TabsRoot,
  TabsList,
  TabsTrigger,
  TabsContent,
} from 'reka-ui'

interface Tab {
  value: string
  label: string
}

interface Props {
  tabs: Tab[]
  defaultValue?: string
}

const props = defineProps<Props>()
</script>

<template>
  <TabsRoot :default-value="props.defaultValue || props.tabs[0]?.value">
    <TabsList class="rd-tabs-list">
      <TabsTrigger
        v-for="tab in props.tabs"
        :key="tab.value"
        :value="tab.value"
        class="rd-tabs-trigger"
      >
        {{ tab.label }}
      </TabsTrigger>
    </TabsList>

    <TabsContent
      v-for="tab in props.tabs"
      :key="tab.value"
      :value="tab.value"
      class="rd-tabs-content"
    >
      <slot :name="tab.value" />
    </TabsContent>
  </TabsRoot>
</template>

<style scoped>
.rd-tabs-list {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  gap: 0;
}

.rd-tabs-trigger {
  padding: 12px 20px;
  font-family: var(--font-sans);
  font-size: 14px;
  font-weight: 500;
  color: var(--color-gray-500);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: color 150ms, border-color 150ms;
}

.rd-tabs-trigger:hover {
  color: var(--color-black);
}

.rd-tabs-trigger[data-state='active'] {
  color: var(--color-blue);
  border-bottom-color: var(--color-blue);
  font-weight: 600;
}

.rd-tabs-content {
  padding-top: 20px;
}
</style>
```

---

## 7. 从 Demo 抽离组件的步骤

### 第一步：识别可复用模式

浏览 `demo/` 中所有页面，标注重复出现的 UI 模式：

| 模式 | 出现频率 | 组件化优先级 |
|------|---------|-------------|
| Button（primary/ghost） | 每页 | P0 |
| Card 容器 | 每页 | P0 |
| 表单 Input / Textarea | 登录/注册/需求提交 | P0 |
| Badge 状态标签 | 列表页/详情页 | P0 |
| Table 数据表格 | 管理后台 | P0 |
| Modal 弹窗 | 审批/确认操作 | P0 |
| Tabs 选项卡 | 工作台/详情页 | P1 |
| Dropdown 菜单 | 导航/操作按钮 | P1 |
| Select 选择器 | 筛选/表单 | P1 |
| Toast 通知 | 操作反馈 | P1 |
| Pagination 分页 | 列表页 | P1 |
| Avatar 头像 | 用户卡片/团队 | P2 |
| Tooltip 提示 | 图标操作 | P2 |

### 第二步：提取样式到设计令牌

1. 从 `demo/index.html` 的 `:root` 中提取所有 CSS 变量到 `tokens.css`
2. 从各页面的公共样式中提取排版规则到 `base.css`
3. 确保组件只引用变量，不硬编码色值

### 第三步：逐个组件实现

对每个组件：

1. 确定是否需要 Reka UI 原语（有无复杂交互/可访问性需求）
2. 从 demo HTML 中提取结构和 class 命名
3. 用 Vue SFC 封装，props 控制变体
4. 用 scoped CSS 应用从 demo 提取的样式
5. 统一导出到 `components/ui/index.ts`

### 第四步：建立文档

在组件库 `index.ts` 中为每个组件添加 JSDoc 注释：

```ts
// src/components/ui/index.ts

/** 按钮组件 - variant: primary | ghost | outline, size: sm | md | lg */
export { default as RdButton } from './button/Button.vue'

/** 对话框 - 基于 Reka UI DialogRoot，支持 v-model:open */
export { default as RdDialog } from './dialog/Dialog.vue'

/** 选项卡 - 基于 Reka UI TabsRoot，传入 tabs 数组 + 命名插槽 */
export { default as RdTabs } from './tabs/Tabs.vue'

// ...
```

---

## 8. 统一导出与使用约定

```ts
// src/components/ui/index.ts
export { default as RdButton } from './button/Button.vue'
export { default as RdCard, RdCardHeader, RdCardContent } from './card'
export { default as RdDialog } from './dialog/Dialog.vue'
export { default as RdInput } from './input/Input.vue'
export { default as RdBadge } from './badge/Badge.vue'
export { default as RdTable } from './table/Table.vue'
export { default as RdTabs } from './tabs/Tabs.vue'
export { default as RdDropdown } from './dropdown/Dropdown.vue'
export { default as RdSelect } from './select/Select.vue'
export { default as RdToast } from './toast/Toast.vue'
```

使用方式：

```vue
<script setup>
import { RdButton, RdDialog, RdBadge } from '@/components/ui'
</script>

<template>
  <RdButton variant="primary" @click="handleSubmit">提交需求</RdButton>
  <RdBadge variant="blue">待审核</RdBadge>
  <RdDialog title="确认操作" v-model:open="showDialog">
    <p>确定要提交这个需求吗？</p>
  </RdDialog>
</template>
```

---

## 9. 命名规范

| 规则 | 说明 |
|------|------|
| 前缀 `Rd` | 所有组件以 `Rd` 开头（OpenRD 缩写），避免与第三方冲突 |
| PascalCase | 组件文件名和导出名使用 PascalCase |
| 多词组件 | `RdCardHeader`、`RdTabsTrigger` 而非 `RdCard-Header` |
| CSS 类名 | BEM-like：`.rd-button`、`.rd-button--primary`、`.rd-dialog-overlay` |
| Props | camelCase，布尔值用 `is` / `has` 前缀：`isLoading`、`hasIcon` |

---

## 10. AI 辅助开发时的提示词指南

当团队成员使用 AI（Claude、Cursor、Copilot 等）开发时，需要在提示中指导 AI 使用自建组件库而非随意引入第三方组件。

### 10.1 项目级 AI 指令文件

在项目根目录创建 `CLAUDE.md`（或 `.cursorrules`）：

```markdown
# OpenRD 前端开发规范

## 组件使用规则

1. 所有 UI 组件必须从 `@/components/ui` 导入，不允许直接使用 Element Plus / Naive UI / 其他第三方 UI 库
2. 组件前缀为 `Rd`，如 RdButton、RdDialog、RdBadge
3. 如果需要的组件不存在，先检查 `src/components/ui/` 目录下是否有类似组件可扩展
4. 组件基于 Reka UI 无头原语 + 自定义样式，不要引入额外的组件库

## 设计系统

- 颜色变量定义在 `src/styles/tokens.css`
- 主色：var(--color-blue) #146ef5
- 文字色：var(--color-black) #080808
- 边框：var(--color-border) #d8d8d8
- 圆角：4px（按钮）、8px（卡片）
- 阴影：使用 var(--shadow-cascade) 5 层级联阴影
- 按钮 hover 效果：translateX(6px)

## 可用组件列表

- RdButton: variant="primary|ghost|outline" size="sm|md|lg"
- RdCard / RdCardHeader / RdCardContent
- RdDialog: title, description, v-model:open
- RdInput: type, placeholder, disabled
- RdBadge: variant="blue|purple|green|orange|pink|red"
- RdTable / RdTableHeader / RdTableRow / RdTableCell
- RdTabs: tabs=[{value, label}], 内容用命名插槽 #value
- RdDropdown / RdDropdownItem
- RdSelect: options=[{value, label}], v-model
- RdToast: 通过 useToast() composable 调用

## 样式规则

- 不使用 Tailwind CSS
- 使用 scoped CSS + CSS 变量
- 类名使用 BEM-like：.rd-component--variant
- 不硬编码颜色值，必须引用 CSS 变量
```

### 10.2 每次对话的提示模板

团队成员在使用 AI 编写代码时，可在对话开头加入以下提示：

```
我在开发 OpenRD 协作平台的前端页面。请遵循以下规则：

1. UI 组件只使用项目自建的 Rd 组件库（从 @/components/ui 导入）
2. 不要引入 Element Plus、Ant Design Vue 或其他第三方 UI 库
3. 组件基于 Reka UI 无头原语，样式使用 CSS 变量（定义在 tokens.css）
4. 可用组件：RdButton, RdCard, RdDialog, RdInput, RdBadge, RdTable, RdTabs, RdDropdown, RdSelect, RdToast
5. 设计风格：Webflow 风格，主色 #146ef5，4px 圆角，5 层级联阴影，hover translateX(6px)

如果需要的组件尚未实现，请先告诉我需要新建什么组件，不要用第三方替代。
```

### 10.3 Cursor Rules 示例（.cursorrules）

```
You are working on the OpenRD frontend project (Vue 3 + TypeScript + Reka UI).

CRITICAL RULES:
- NEVER import from element-plus, naive-ui, ant-design-vue, vuetify, or any third-party UI library
- ALWAYS import UI components from '@/components/ui'
- All components are prefixed with 'Rd': RdButton, RdDialog, RdBadge, etc.
- Use CSS variables from 'src/styles/tokens.css' for all colors, spacing, and shadows
- Components use Reka UI headless primitives for accessibility (Dialog, Dropdown, Select, Tabs, Toast, Tooltip)
- Simple visual components (Button, Card, Badge, Input, Table) are pure Vue + CSS

Available components and their APIs:
- <RdButton variant="primary|ghost|outline" size="sm|md|lg" :disabled="bool">
- <RdCard> <RdCardHeader> <RdCardContent>
- <RdDialog title="..." v-model:open="bool"> content </RdDialog>
- <RdInput v-model="val" type="text|password|email" placeholder="...">
- <RdBadge variant="blue|purple|green|orange|pink|red">
- <RdTabs :tabs="[{value, label}]"> <template #tabValue> content </template> </RdTabs>
- <RdSelect :options="[{value, label}]" v-model="val">
- useToast().show({ title, description, variant })

Design tokens (use var(--xxx) in CSS, NEVER hardcode):
- --color-blue: #146ef5 (primary)
- --color-black: #080808 (text)
- --color-border: #d8d8d8
- --radius-sm: 4px (buttons), --radius-md: 8px (cards)
- --shadow-cascade: 5-layer shadow for elevated cards
```

---

## 11. 组件库扩展流程

当需要新组件时：

1. **评估**：是否能用现有组件组合实现？
2. **选型**：是否需要 Reka UI 原语？（有复杂交互/无障碍需求则用）
3. **参考**：查看 `demo/` 中对应页面的 HTML/CSS 实现
4. **实现**：在 `src/components/ui/` 下新建目录，编写 Vue SFC
5. **导出**：在 `index.ts` 中添加导出
6. **文档**：更新 CLAUDE.md 中的组件列表
7. **通知**：告知团队成员新组件可用

---

## 12. 总结

```
Demo (静态 HTML/CSS)
    ↓ 提取样式
tokens.css + base.css (设计令牌)
    ↓ 组合
Reka UI 原语 (行为 + 可访问性) + 自定义样式 (Webflow 视觉)
    ↓ 封装
Rd 组件库 (RdButton, RdDialog, RdTabs...)
    ↓ 约束
CLAUDE.md / .cursorrules (AI 使用指南)
    ↓ 使用
业务页面开发
```

核心思路：**Reka UI 管交互，Demo 管视觉，Rd 组件库管封装，AI 规则管约束**。
