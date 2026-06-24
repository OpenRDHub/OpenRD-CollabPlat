# Findings

## 已确认的技术决策

- **数据库**: PostgreSQL (云服务 38.244.14.106:5432)，asyncpg 异步驱动
- **缓存**: Redis（Token 管理、验证码存储、频率限制）
- **认证**: JWT 双 Token（access 15min + refresh 7天，Redis 白名单轮换）
- **ORM**: SQLAlchemy 2.0 async + Alembic 迁移
- **文件存储**: 本地 + 阿里云 OSS 双模式（通过 STORAGE_BACKEND 切换）
- **短信**: 阿里云 Dysms（签名名：速通互联验证码）
- **platform_id**: 无业务含义序号格式 `ORD000001`

## 项目结构已就位

```
backend/
├── app/main.py          # FastAPI 入口
├── app/config.py        # pydantic-settings 配置
├── app/database.py      # async engine + session
├── app/models/base.py   # Base + TimestampMixin + SoftDeleteMixin
├── app/schemas/common.py # ApiResponse + PaginatedData + PageParams
├── app/api/v1/router.py # /api/v1/health ✅
├── app/dependencies/database.py # get_db
├── alembic/             # 异步迁移已配置
└── tests/               # pytest + httpx 测试
```

## API 设计文档状态

- 已补充 9 个数据模型（JoinApplication、Assignment、TaskProgress、File、SystemLog 等）
- 已补充 JWT Payload 结构和 Redis 存储策略
- 已补充权限模型说明（角色模板 + 手动追加 + 动态业务权限）
- 已补充 PATCH /demands/{demand_id} 和 GET /admin/system-logs/{log_id}
- platform_id 改为 ORD + 6位序号

## 环境配置

- .env.example 含完整配置项（数据库/Redis/JWT/OSS/短信）及中文注释
- DATABASE_URL 格式: `postgresql+asyncpg://user:pass@host:port/db`
- 启动命令: `uv run uvicorn app.main:app --reload --port 8000`
