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

开发环境默认连接真实后端，无需配置环境变量。Vite 会将 `/api/v1` 代理至 `http://127.0.0.1:8000`。

只有需要独立演示 Mock 数据时，才在 `.env.local` 中显式启用 MSW：

```dotenv
VITE_ENABLE_MOCK=true
```

除小写字符串 `true` 外的任何值都会保持 MSW 关闭。生产构建不会加载 MSW。Mock 模式下未覆盖的 `/api/v1` 请求会明确报错，避免与真实接口静默混用。

## 常用命令

```bash
npm run dev
npm run type-check
npm run test:contract
npm run lint
npm run build
npm run preview
```

`test:contract` 校验 MSW 必须显式启用，并防止启动入口恢复为默认 Mock。CI 还会在生产构建后运行 `test:bundle-contract`，确保 MSW 浏览器运行时代码未进入产物。`lint` 当前会自动修复文件；项目尚未配置完整的组件或端到端测试命令。

## 当前注意事项

- API 基础路径固定为 `/api/v1`。
- 401 会清除 access token 并跳转登录页；完整自动刷新仍需完善。
- 菜单、路由、Mock 和后端权限点必须统一命名。
- 验收需求、任务、团队和管理后台流程时保持 MSW 关闭；只有 Mock 演示环境设置 `VITE_ENABLE_MOCK=true`。
