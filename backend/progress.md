# Progress Log

## Session 1 — 2026-06-24

### feature/backend-init 分支（已完成 ✅）

完成内容：
- [x] 安装 pyenv-win + Python 3.12.10
- [x] 安装 uv 0.11.23 包管理器
- [x] 初始化项目（pyproject.toml + uv.lock）
- [x] 安装全部生产依赖 + 开发依赖
- [x] 替换 aiosqlite → asyncpg（PostgreSQL 异步驱动）
- [x] 创建完整项目目录结构（app/models/schemas/api/services/dependencies/utils）
- [x] 编写 config.py（pydantic-settings，支持 .env）
- [x] 编写 database.py（SQLAlchemy async engine + session）
- [x] 编写 models/base.py（Base + TimestampMixin + SoftDeleteMixin）
- [x] 编写 schemas/common.py（ApiResponse + PaginatedData + PageParams）
- [x] 编写 app/main.py（FastAPI 入口 + CORS + 路由挂载）
- [x] 编写 api/v1/router.py（/api/v1/health 端点）
- [x] 初始化 Alembic（异步模板 + 从 .env 读取 DATABASE_URL）
- [x] 编写 tests/test_health.py（✅ PASSED）
- [x] 创建 .env.example（完整配置项含中文注释：数据库/Redis/JWT/OSS/短信）
- [x] 创建 backend/.gitignore
- [x] 完善 API 设计文档（补充数据模型、JWT、权限模型、缺失接口）
- [x] 编写 GETTING_STARTED.md 入门教程
- [x] 编写 docs/BACKEND_CONCEPTS.md 概念解释文档
- [x] 更新 docs/前端后端开发任务分配计划.md（后端分支规划）

### 待用户操作
- [ ] 复制 .env.example → .env，填入实际数据库连接串和配置
- [ ] git add + commit + push feature/backend-init
- [ ] 创建 PR 合入 main
- [ ] 从 main 拉出 feature/backend-auth 开始下一阶段

### feature/backend-auth 分支（已完成 ✅）

完成内容：
- [x] app/utils/redis.py — Redis 异步客户端池（init/close/get_client）
- [x] app/utils/security.py — bcrypt 密码哈希 + JWT 签发/解析
- [x] app/models/user.py — User ORM 模型（UUID pk、platform_id、全字段）
- [x] app/models/__init__.py — 导入 User 让 Alembic 可检测
- [x] Alembic 迁移 — users 表 + platform_id_seq 序列
- [x] app/core/permissions.py — ROLE_PERMISSIONS 静态映射（4 角色）
- [x] app/schemas/auth.py — 7 组请求/响应 Schema + UserOut
- [x] app/services/user.py — User CRUD + platform_id 生成
- [x] app/services/sms.py — 验证码发送/校验（Redis 存储 + stub 打印）
- [x] app/services/auth.py — register/login/refresh/logout/reset_password/onboarding
- [x] app/dependencies/redis.py — get_redis 依赖
- [x] app/dependencies/auth.py — get_current_user/require_roles/require_permissions
- [x] app/api/v1/auth.py — 7 个认证端点路由
- [x] app/api/v1/router.py — 挂载 auth_router
- [x] app/main.py — lifespan 中 init/close Redis
- [x] tests/conftest.py — fakeredis + NullPool 测试隔离
- [x] tests/test_auth.py — 6 个测试用例全部通过
- [x] passlib 替换为 bcrypt 直接调用（兼容 bcrypt 5.x）
- [x] pyproject.toml 依赖更新（+bcrypt, +fakeredis, -passlib）
