# OpenRD 后端开发入门

本指南基于当前已存在的 FastAPI 工程，不需要重新创建 Hello World 或逐个安装核心依赖。

## 1. 前置条件

Python 3.12+、uv、PostgreSQL 和 Redis。

## 2. 安装依赖

```bash
uv sync
```

依赖已声明在 `pyproject.toml`，实际版本由 `uv.lock` 锁定。

## 3. 配置环境

```bash
cp .env.example .env
```

至少修改：

```dotenv
DATABASE_URL=postgresql+asyncpg://user:password@127.0.0.1:5432/openrd
REDIS_URL=redis://127.0.0.1:6379/0
JWT_SECRET_KEY=replace-with-a-random-secret
```

## 4. 初始化数据库

```bash
uv run alembic upgrade head
```

迁移目录已经包含用户、需求、任务、团队、消息、日志和文件相关版本。

## 5. 启动服务

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- 健康检查：`http://127.0.0.1:8000/api/v1/health`
- Swagger：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`

## 6. 连接前端

前端 Vite 已代理 `/api/v1`。在 `frontend/.env.local` 中关闭模拟接口：

```dotenv
VITE_ENABLE_MOCK=false
```

未关闭 MSW 时，页面可能继续使用浏览器模拟数据。

## 7. 测试和质量

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
```

当前测试主要覆盖认证和健康检查。新增业务接口时应补充服务、权限和 API 集成测试。

## 8. 数据库模型变更

```bash
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head
```

提交前人工检查生成的迁移，不要改写已经被其他环境执行过的历史迁移。

## 9. 联调注意事项

- API 前缀是 `/api/v1`。
- `/openapi.json` 是当前可执行接口描述，但前端、Mock 和后端仍有部分契约差异。
- 修改响应或权限点时，同步更新前端类型、MSW 和测试。
- 不要把 `testdemo/` 或 Mock 成功作为完整端到端验收。
- 生产前还需要部署、密钥、监控、备份恢复、安全和隐私方案。
