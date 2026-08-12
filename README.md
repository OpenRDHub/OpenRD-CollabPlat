# OpenRD 罕见病运营管理平台

OpenRD 是面向罕见病社区的协作平台。平台让需求者提交真实问题，由产品经理评估、沟通并转化为任务，再由共建者参与任务开发和团队协作，最终帮助罕见病患者或家属解决具体问题。

## 当前项目状态

当前仓库已经从静态原型阶段进入前后端开发和联调阶段：

- `docs/OpenRD协作平台PRD正式版.md` 是当前正式 PRD。
- `docs/backup/` 保存历史冗余文档，仅作为归档参考。
- `demo/` 保存现有高保真静态 HTML 原型。
- `frontend/` 是 Vue 3 + Vite + TypeScript 应用，包含路由、状态管理、API 客户端、业务页面和 MSW 模拟接口。
- `backend/` 是 FastAPI + SQLAlchemy 异步 API 服务，使用 PostgreSQL、Redis、Alembic 和 JWT。
- `backend/alembic/versions/` 已包含用户、需求、任务、团队、消息、日志和文件相关迁移。
- `backend/tests/` 当前主要覆盖健康检查和认证流程，核心业务测试仍需补充。

当前仍处于开发联调阶段，不应直接视为生产就绪。前端开发环境默认启用 MSW；真实后端联调时必须设置 `VITE_ENABLE_MOCK=false`。部分跨端接口仍需统一，仓库也尚未提供完整的 CI/CD、生产监控和备份恢复方案。

## 仓库结构约定

本项目采用单仓库结构，前端和后端分别放在各自目录中：

```text
OpenRD/
├─ frontend/      前端项目目录
├─ backend/       后端项目目录
├─ docs/          当前正式 PRD 与历史文档归档
├─ demo/          静态原型与角色体验演示
├─ .env.example   环境变量示例
└─ README.md      项目总览
```

后续开发时，前端代码只放入 `frontend/`，后端代码只放入 `backend/`。跨端接口、环境变量、部署和协作规范在根目录或 `docs/` 中维护。

## 产品理解

正式 PRD 将平台定义为两套相互连接的业务系统：

1. 需求者与产品经理之间的需求接单系统。
2. 产品经理与共建者之间的项目开发协作系统。

核心流程：

```text
需求者提交需求
→ 产品经理审核、沟通、评估
→ 有价值的需求转化为任务
→ 任务发布到任务大厅
→ 共建者申请加入队伍并参与开发
→ 队伍交付成果
→ 任务完成，需求得到解决
```

## 核心角色

- 需求者：患者或患者家属，提交需求并跟踪需求状态。
- 共建者：志愿者或开发者，浏览任务大厅、认领任务并参与开发。
- 产品经理：平台运营人员，负责需求审核、需求沟通、任务转化和任务进度管理。
- 超级管理员：系统管理员，负责用户、权限、系统配置和安全审计。

## 当前功能范围

P0 功能包括：

- 用户注册、登录、忘记密码。
- 需求提交、需求审核、需求沟通和任务转化。
- 任务大厅、任务详情、任务认领和队伍协作。
- 用户管理、权限管理、需求管理、任务管理。
- 我的需求、我的任务、消息通知。
- 系统日志和关键操作审计。

当前不包含或后续再做：

- 社区交流功能。
- 积分和激励制度。
- 医护认证流程。
- AI 需求优化功能。

## 原型入口

静态原型入口：

```text
demo/index.html
```

角色体验入口：

- `demo/requester/index.html`：需求者体验。
- `demo/builder/index.html`：共建者体验。
- `demo/operator/index.html`：产品经理体验。
- `demo/superadmin/index.html`：超级管理员体验。
- `demo/all-pages/index.html`：完整页面快照。

## 本地开发

前端技术栈：

- Vue 3
- Vite
- TypeScript
- Vue Router
- Pinia
- Axios、Reka UI、MSW
- 基于现有原型沉淀的设计 Token 和组件体系

后端技术栈为 Python 3.12、FastAPI、SQLAlchemy、PostgreSQL、Alembic、Redis、JWT 和 bcrypt。

后端启动：

```bash
cd backend
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
```

前端启动：

```bash
cd frontend
npm install
npm run dev
```

Vite 默认运行于 `http://127.0.0.1:5173`，并将 `/api/v1` 代理到 `http://127.0.0.1:8000`。连接真实后端时，在 `frontend/.env.local` 中设置：

```dotenv
VITE_ENABLE_MOCK=false
```

开发准备说明见 [DEVELOPMENT.md](DEVELOPMENT.md)。

## 文档入口

当前正式 PRD 见 [docs/OpenRD协作平台PRD正式版.md](docs/OpenRD协作平台PRD正式版.md)。

文档目录说明见 [docs/README.md](docs/README.md)。

## 许可证

待定。
