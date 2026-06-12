# OpenRD 前端开发规范

## 组件使用规则（强制）

- 所有 UI 组件必须从 `@/components/ui` 导入
- 禁止引入 Element Plus、Naive UI、Ant Design Vue 或任何第三方 UI 库
- 组件前缀为 `Ord`，如 OrdButton、OrdDialog、OrdBadge
- 如果需要的组件不存在，先告知用户需要新建什么，不要用第三方替代
- 组件基于 Reka UI 无头原语 + 自定义 CSS，不要引入额外的组件库

## 可用组件

- OrdButton: variant="primary|ghost|outline" size="sm|md|lg" loading, disabled
- OrdInput: v-model, type, placeholder, error, disabled
- OrdTextarea: v-model, placeholder, rows, error, disabled
- OrdCard / OrdCardHeader / OrdCardContent
- OrdBadge: variant="blue|purple|green|orange|pink|red|gray"
- OrdTable / OrdTableHeader / OrdTableRow / OrdTableCell (header prop)
- OrdDialog: v-model:open, title, description, 插槽: trigger/default/footer
- OrdTabs / OrdTabsList / OrdTabsTrigger / OrdTabsContent
- OrdDropdown / OrdDropdownItem: 插槽 #trigger + 菜单项
- OrdSelect: v-model, :options="[{value,label}]", placeholder
- useToast(): show({ title, description, variant: 'default'|'success'|'error', duration })
- OrdPagination: v-model:current-page, :total, :page-size
- OrdNavbar: 插槽 #brand / #center / #actions (fixed 定位, 76px 高度)
- OrdSidebar: :items="[{label,icon?,to?,active?}]" @select
- OrdAvatar: name, src?, size="sm|md|lg"
- OrdTooltip: content, side="top|bottom|left|right", delayDuration
- OrdProgress: :value="0-100" variant="blue|gradient"
- OrdTimeline: :items="[{title, status:'done'|'active'|'pending', description?, date?}]"
- OrdFileUpload: v-model, accept, multiple
- OrdEmptyState: 插槽 #icon / #title / #description / #action
- OrdSearchBox: v-model, placeholder, width

## 样式规则

- 使用 scoped CSS + CSS 变量（定义在 src/styles/tokens.css）
- 不使用 Tailwind CSS，不硬编码颜色值
- 颜色引用 var(--ord-color-*)，间距 var(--ord-space-*)
- 圆角: --ord-radius-sm (4px) 按钮/输入框, --ord-radius-md (8px) 卡片/弹窗
- 阴影: --ord-shadow-cascade (卡片), --ord-shadow-nav (导航栏)
- 过渡: var(--ord-transition-base) = 180ms ease
- 按钮 hover 效果: translateX(6px)
- CSS 类名使用 BEM-like: .ord-{component}--{variant}

## App 配置

- App.vue 已包含 OrdToastProvider，直接使用 useToast() 即可
- 路由在 src/router/index.ts 中配置
- /dev 路由为组件预览页（仅开发模式）

## 参考

- 组件预览: npm run dev 后访问 /dev
- 完整 API 文档: docs/OpenRD-UI组件库说明文档.md
- 设计参考: demo/all-pages/ 下的 HTML 原型页面
- 设计令牌: src/styles/tokens.css
