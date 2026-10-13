# OpenRD 罕见病需求协作平台

让真实需求连接愿意行动的人。

OpenRD 是面向罕见病患者、家属、志愿者和平台运营人员的协作平台。需求者提交生活与服务中的具体问题，产品经理负责沟通、评估并将需求转化为可执行任务，共建者申请加入队伍、参与开发和交付，形成从需求提出到成果交付的协作闭环。

本仓库采用前后端单仓库结构，包含 Vue 前端、FastAPI 后端、业务文档和静态原型。

> README 草稿，整理日期：2026-10-12。内容依据当前移动端适配分支及既有项目文档编写；功能合入情况以目标分支为准，本文不代表生产发布声明。

## 产品流程与角色

```text
需求提交 → 审核与沟通 → 转化为任务 → 发布到任务大厅
         → 共建者申请加入 → 队伍协作与进度更新 → 成果交付
```

| 角色 | 主要职责 |
| --- | --- |
| 需求者 | 提交需求、补充信息、跟踪处理情况 |
| 共建者 | 浏览任务、申请加入队伍、参与协作和成果交付 |
| 产品经理 | 审核与沟通需求、创建和管理任务、协调进度 |
| 超级管理员 | 管理用户与权限、查看系统日志、维护平台治理 |

后端负责身份、权限和业务状态校验。前端菜单与路由限制用于改善操作体验，不能替代后端授权。

## 功能范围

| 模块 | 已有代码范围 |
| --- | --- |
| 身份与资料 | 注册、登录、找回密码、引导页、个人资料 |
| 需求 | 提交、我的需求、详情与沟通、后台审核与任务转化 |
| 任务与团队 | 任务大厅、我的任务、任务详情、加入申请、队伍与进度管理 |
| 消息 | 分类、详情、未读统计及相关消息操作 |
| 管理后台 | 需求管理、任务管理、用户管理、权限管理、系统日志 |
| 文件与统计 | 文件相关接口、平台统计、当前用户统计 |

社区交流、积分激励、医护认证和 AI 需求优化属于后续规划，不列为当前已交付能力。

### 移动端适配

移动端适配已覆盖共享导航与侧栏、用户核心页面、认证页面、辅助页面和五类后台管理页面，主要改动包括：

- 在窄屏下重排多栏内容，后台及个人业务表格使用带字段标签的卡片布局。
- 优化筛选器、分页和操作区，关键触控区域以 44px 为基线。
- 为弹窗、抽屉和底部操作区处理动态视口、滚动区域与安全区。
- 增加输入框聚焦可见性处理，并完善详情返回、403/404 返回及弹窗无障碍语义。
- 补齐 `/api/v1/stats`、`/api/v1/me/stats` 的浏览器 Mock handler，减少演示验收中的接口缺失错误。

验收视口为 `375×667`、`390×844`、`430×932`、`768×1024` 和 `1440×900`。既有检查覆盖了核心路由的窄屏溢出、后台多视口布局及部分弹窗；全路由交互矩阵、iOS Safari/Android 软键盘、横竖屏与真机安全区仍需继续验收。

相关方案见 [移动端响应式适配技术方案与实施路线图](docs/移动端响应式适配技术方案与实施路线图.md)。其中分期状态为历史记录，最新进度以代码和 PR 为准。

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 前端 | Vue 3、TypeScript、Vite、Vue Router、Pinia、Axios |
| UI 与模拟接口 | Reka UI、本地 Ord UI 组件与设计 Token、MSW |
| 后端 | Python 3.12+、FastAPI、Uvicorn、SQLAlchemy 异步 ORM、asyncpg |
| 数据与认证 | PostgreSQL、Redis、Alembic、JWT、bcrypt |
| 质量工具 | vue-tsc、ESLint、Oxlint、pytest、Ruff、GitHub Actions |

## 仓库结构

```text
OpenRD-CollabPlat/
├── frontend/
│   ├── src/api/          API 客户端与业务接口
│   ├── src/components/   共享组件与 Ord UI
│   ├── src/composables/  共享交互逻辑
│   ├── src/mocks/        MSW handler 与模拟数据
│   ├── src/views/        业务页面
│   └── tests/            前端契约与响应式检查
├── backend/
│   ├── app/              路由、服务、模型、schema 与配置
│   ├── alembic/          数据库迁移
│   └── tests/            后端自动化测试
├── docs/                 PRD、API、技术方案与历史归档
├── demo/                 静态高保真原型与角色演示
├── showcase/             展示资料
├── .github/workflows/    CI 工作流
├── DEVELOPMENT.md        开发指引
└── LICENSE               MIT 许可证
```

## 本地开发

### 环境要求

- Node.js `^20.19.0` 或 `>=22.12.0`，建议使用 Node.js 22。
- Python 3.12+ 与 uv。
- 可连接的 PostgreSQL 和 Redis。现有 CI 使用 PostgreSQL 16、Redis 7。

获取代码：

```bash
git clone https://github.com/OpenRDHub/OpenRD-CollabPlat.git
cd OpenRD-CollabPlat
git switch develop
```

### 启动后端

```bash
cd backend
cp .env.example .env
uv sync
```

Windows PowerShell 可使用 `Copy-Item .env.example .env`。编辑 `backend/.env`，至少配置 `DATABASE_URL`、`REDIS_URL` 和随机生成的 `JWT_SECRET_KEY`，随后执行：

```bash
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- 健康检查：`http://127.0.0.1:8000/api/v1/health`
- Swagger：`http://127.0.0.1:8000/docs`

短信验证码和文件服务需要按实际使用场景配置；完整变量见 [backend/.env.example](backend/.env.example)。根目录 `.env.example` 仅作为配置参考，不替代后端运行配置。

### 启动前端

在另一终端执行：

```bash
cd frontend
npm ci
npm run dev
```

默认地址为 `http://127.0.0.1:5173`，Vite 将 `/api/v1` 代理到 `http://127.0.0.1:8000`。前端默认连接真实后端。

### Mock 演示模式

需要独立演示前端时，在 `frontend/.env.local` 中设置：

```dotenv
VITE_ENABLE_MOCK=true
```

重启开发服务器后生效。只有小写字符串 `true` 会启用 MSW，并且仅用于开发模式；生产构建不加载 MSW 浏览器运行时。缺失或其他值均保持真实 API 模式。

Mock 模式下未覆盖的 `/api/v1/` 请求会明确报错，避免悄悄混用真实后端。Mock 用于演示和前端检查，真实鉴权、业务持久化与权限验收需要连接后端验证。

## API 与认证

API 统一前缀为 `/api/v1`，具体契约以 FastAPI 路由、schema 和 Swagger 为准。

受保护接口必须携带登录后获得的有效 access token：

```http
Authorization: Bearer <access_token>
```

例如，`GET /api/v1/me/stats` 查询当前用户的需求数和任务成员关系数，必须登录；缺少、无效、过期或已吊销的 Token 会返回 `401`。这表示身份验证未通过。身份有效但缺少操作权限时返回 `403`。

前端 API 客户端会自动附加已保存的 Token，收到 `401` 后清理登录凭证并跳转登录页；当前客户端未实现完整自动刷新流程。`GET /api/v1/stats` 是平台统计接口，当前后端路由不要求登录，不应把所有接口都描述为必须携带 Token。

## 测试与质量验证

### 前端

```bash
cd frontend
npm run type-check
npm run test:contract
npm run test:responsive
npm run build
npm run test:bundle-contract
```

- `type-check`：Vue 与 TypeScript 类型检查。
- `test:contract`：默认真实 API 模式、接口调用与业务契约检查。
- `test:responsive`：响应式规则与关键页面结构契约检查。
- `build`：类型检查和生产构建。
- `test:bundle-contract`：在构建后检查产物未包含 MSW 浏览器运行时。

`npm run lint` 会自动修复文件，执行后应检查差异。响应式契约检查不能替代真实浏览器视觉及交互验收。

### 后端

测试必须使用名称以 `_test` 结尾的专用数据库，例如 `openrd_test`。测试夹具会清空业务表并重置相关序列，禁止连接开发业务库或生产库。

在当前终端配置测试环境（不要使用生产密钥），例如 PowerShell：

```powershell
cd backend
$env:APP_ENV = 'testing'
$env:DATABASE_URL = 'postgresql+asyncpg://openrd:replace-with-test-password@127.0.0.1:5432/openrd_test'
$env:REDIS_URL = 'redis://127.0.0.1:6379/0'
$env:JWT_SECRET_KEY = 'local-test-only-secret-do-not-use-in-production'
uv run alembic upgrade head
uv run ruff check .
uv run pytest
```

请先创建专用测试数据库并填写实际测试连接信息。现有测试覆盖认证、需求契约与隐私、任务管理与进度、团队成员持久化、手动权限、消息未读统计、文件授权与生命周期、用户统计等模块；具体通过数量以本次运行和 CI 结果为准。

### 持续集成

仓库已包含后端测试、前端构建和前端真实 API 默认模式契约工作流。工作流按路径变化触发，当前前端构建流程包含类型检查、构建、契约和生产包检查；响应式测试仍需显式运行。

“Frontend real API contract”校验的是默认请求模式及构建契约，不代表已启动真实后端完成所有端到端业务验证。

## 部署与验收

前端构建产物位于 `frontend/dist/`。生产环境需要将 `/api/v1` 转发到后端，并为 Vue Router 的 History 路由配置 SPA 回退；Vite 开发代理不会随静态产物自动部署。

上线前需要结合部署环境完成：

- HTTPS、生产密钥、数据库迁移与持久化配置。
- 前后端跨域或同源反向代理配置；当前后端 CORS 配置主要面向本地开发地址。
- 短信服务、文件存储、访问控制和文件扫描策略配置。
- 监控告警、日志、数据库及文件备份，以及恢复演练。
- 真实后端关键业务联调、角色权限验收及移动设备测试。

当前仓库中的功能实现、CI 和浏览器检查不等同于完整生产部署与运营验证。

## 参与协作

通过 [Issues](https://github.com/OpenRDHub/OpenRD-CollabPlat/issues) 提交缺陷和需求，通过 Pull Request 提交代码或文档改进。反馈 UI 问题时请注明路由、设备、视口、浏览器和复现步骤。

建议每个独立改动从最新 `develop` 创建分支。接口改动应同步更新后端、前端 API 类型、Mock 与测试，避免模拟行为和真实契约分离。

后续 PR 依赖前一个 PR 时，应在依赖合入并同步基线之后再请求最终审批。审批后基线或差异发生变化，GitHub 可能按保护规则撤销旧审批，需要重新审查；不要通过关闭保护规则绕过审查。

## 文档与原型

- [正式 PRD](docs/OpenRD协作平台PRD正式版.md)
- [API 设计文档](docs/API设计文档.md)
- [平台技术文档](docs/OpenRD协作平台技术文档.md)
- [UI 组件库说明](docs/OpenRD-UI组件库说明文档.md)
- [移动端适配技术方案](docs/移动端响应式适配技术方案与实施路线图.md)
- [文档目录说明](docs/README.md)
- [开发指引](DEVELOPMENT.md)
- [前端说明](frontend/README.md) / [后端说明](backend/README.md)

静态原型入口为 `demo/index.html`，角色演示位于 `demo/requester/`、`demo/builder/`、`demo/operator/`、`demo/superadmin/`。静态原型不连接真实业务服务。

部分历史文档仍包含旧阶段描述；运行配置、接口和功能状态请优先核对当前代码与 CI。`docs/backup/` 及根目录历史进度文件用于归档参考。

## 许可证

本项目采用 [MIT License](LICENSE)，版权归 OpenRDHub 所有。
