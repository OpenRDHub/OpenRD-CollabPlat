# OpenRD 后端

基于 FastAPI 的异步 API 服务，已包含应用入口、配置、数据库模型、Pydantic schema、服务层、API 路由、Alembic 迁移和基础测试。

## 技术栈

Python 3.12+、FastAPI、Uvicorn、SQLAlchemy 2/asyncpg、PostgreSQL、Alembic、Redis、JWT、bcrypt、pytest 和 Ruff。

## 快速启动

```bash
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

请先配置可用的 PostgreSQL、Redis 和非默认 JWT 密钥。

- 健康检查：`GET http://127.0.0.1:8000/api/v1/health`
- Swagger：`http://127.0.0.1:8000/docs`
- 调试页面：`http://127.0.0.1:8000/testdemo/`

## 常用命令

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "description"
```

## 当前实现

代码已包含认证、用户、需求、任务、团队、消息、文件、统计、角色、权限和系统日志模块，以及相关数据库迁移。“代码存在”不等于已经完成生产验证；当前测试主要覆盖健康检查和认证基础流程。

## 已知缺口

- 部分管理员需求、用户权限和团队查询接口尚未与前端完全对齐。
- “我的任务”前后端路径需要统一。
- 权限响应结构和权限点命名需要统一契约。
- 生产级短信防刷、私有附件、安全审计和数据生命周期仍需加固。
- 尚未提供完整容器化、CI/CD、监控和备份恢复体系。

后端是身份、权限和业务状态的事实来源；前端按钮隐藏不能替代后端授权。完整变量说明见 `.env.example`，详细步骤见 [GETTING_STARTED.md](GETTING_STARTED.md)。
