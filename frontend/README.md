# OpenRD 前端

Vue 3 + Vite + TypeScript 单页应用，包含需求者、共建者、产品经理和超级管理员四类角色的页面与路由。

## 技术栈

Vue 3、Vue Router、Pinia、Axios、Reka UI、本地 `Ord*` 组件、MSW、ESLint、Oxlint 和 `vue-tsc`。

## 安装和启动

要求 Node.js `^20.19.0` 或 `>=22.12.0`。

```bash
npm install
npm run dev
```

开发服务器默认监听 `http://127.0.0.1:5173`，并将 `/api/v1` 代理至 `http://127.0.0.1:8000`。

## Mock 与真实后端

开发环境默认启用 MSW。连接真实后端时创建 `.env.local`：

```dotenv
VITE_ENABLE_MOCK=false
```

生产构建不会加载 MSW，因为模拟服务只在 Vite 开发模式启动。Mock 成功不表示真实 API 已完成。

## 常用命令

```bash
npm run dev
npm run type-check
npm run lint
npm run build
npm run preview
```

`lint` 当前会自动修复文件。`package.json` 尚未配置前端单元、组件或端到端测试命令。

## 当前注意事项

- API 基础路径固定为 `/api/v1`。
- 401 会清除 access token 并跳转登录页；完整自动刷新仍需完善。
- 菜单、路由、Mock 和后端权限点必须统一命名。
- 验收需求、任务、团队和管理后台流程时必须关闭 MSW。
