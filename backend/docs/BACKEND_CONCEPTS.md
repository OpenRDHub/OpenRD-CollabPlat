# Python 后端项目结构与核心概念

> 面向前端工程师的后端知识入门，用你熟悉的前端概念做类比。

## 1. 项目结构解析

```
backend/
├── app/                     ← 应用源码（类似前端的 src/）
│   ├── main.py              ← 应用入口（类似 main.ts）
│   ├── config.py            ← 环境配置（类似 vite.config.ts 读取 .env）
│   ├── database.py          ← 数据库连接（前端没有对应物）
│   ├── models/              ← 数据库表定义（类似 TypeScript interface，但映射到真实数据库表）
│   ├── schemas/             ← 请求/响应数据结构（类似 zod schema 或 TS type）
│   ├── api/v1/              ← 路由层（类似 router/，定义 URL → 处理函数的映射）
│   ├── services/            ← 业务逻辑层（前端类比：stores/ 里的 actions）
│   ├── dependencies/        ← 依赖注入（类似 Vue 的 provide/inject）
│   └── utils/               ← 工具函数（和前端一样）
├── alembic/                 ← 数据库迁移（下面详细解释）
├── tests/                   ← 测试（类似前端的 __tests__/）
├── .env                     ← 环境变量（和前端 .env 完全一样的概念）
├── pyproject.toml           ← 项目配置（等同于 package.json）
└── uv.lock                  ← 依赖锁定（等同于 pnpm-lock.yaml）
```

### 各层职责详解

#### app/main.py — 应用入口

相当于前端的 `main.ts`。它做三件事：
- 创建 FastAPI 应用实例（类似 `createApp()`）
- 注册中间件（类似 `app.use()`）
- 挂载路由（类似 `app.use(router)`）

```python
# 前端类比
# const app = createApp(App)
# app.use(router)
# app.mount('#app')

# 后端实际代码
app = FastAPI()
app.add_middleware(CORSMiddleware, ...)
app.include_router(v1_router)
```

#### app/config.py — 配置管理

前端用 `import.meta.env.VITE_XXX` 读环境变量，后端用 pydantic-settings 做同样的事，但多了类型校验和默认值。

```python
class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://localhost/openrd"
    jwt_secret_key: str = "change-me"
    app_port: int = 8000
```

好处：启动时如果 `.env` 缺少必填字段，直接报错，不会带着空值跑起来。

#### app/api/v1/ — 路由层

和前端 router 概念完全一致，只不过前端路由映射的是「URL → 页面组件」，后端路由映射的是「URL + HTTP 方法 → 处理函数」。

```python
# 前端路由
# { path: '/tasks', component: TaskList }

# 后端路由
@router.get("/tasks")
async def list_tasks():
    ...

@router.post("/tasks")
async def create_task(body: CreateTaskRequest):
    ...
```

#### app/schemas/ — 数据结构定义

这是 Pydantic 模型，作用等同于前端的 zod schema 或 TypeScript interface。区别是：
- **前端 interface**：编译时检查，运行时消失
- **Pydantic schema**：运行时校验，请求进来时自动验证，不合法直接返回 422

```python
# 类比 zod
# const LoginSchema = z.object({ username: z.string().min(3), password: z.string().min(8) })

class LoginRequest(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=8)
```

#### app/models/ — 数据库模型（ORM 模型）

定义数据库表的结构。这个在前端没有直接对应物，因为前端不直接操作数据库。下面 ORM 章节详细解释。

#### app/services/ — 业务逻辑层

放核心业务逻辑的地方。类比前端 Pinia store 里的 actions：

- 路由层（api/）：接收请求，调用 service，返回响应 → 类似组件调用 store action
- 服务层（services/）：执行业务逻辑，操作数据库 → 类似 store action 调用 API

为什么要分层？和前端一样 — 组件不直接写业务逻辑，而是通过 store 来管理状态。后端的路由不直接写数据库操作，而是通过 service 来组织业务。

#### app/dependencies/ — 依赖注入

FastAPI 的依赖注入系统，概念上等同于 Vue 的 `provide/inject`。

最典型的用法：每个需要登录的接口，都需要「当前用户」信息。不是每个路由函数自己去解析 Token，而是声明一个依赖，框架自动注入。

```python
# 类比 Vue
# const user = inject('currentUser')

# FastAPI
@router.get("/me")
async def get_me(user = Depends(get_current_user)):
    return user
```

#### alembic/ — 数据库迁移

数据库的「版本管理」。类比：

- 你改了前端代码 → git 帮你追踪变更
- 你改了数据库表结构 → alembic 帮你追踪变更

假设你给 User 表加了一个字段，alembic 会生成一个「迁移文件」（类似 git commit），记录这次结构变更。部署到服务器时，运行迁移命令就能自动更新数据库结构，不用手动改。

```bash
# 生成迁移（类似 git add + git commit）
uv run alembic revision --autogenerate -m "add phone field to user"

# 执行迁移（类似 git push 后服务器拉取代码）
uv run alembic upgrade head
```

---

## 2. ORM — 用代码操作数据库

### 什么是 ORM

ORM (Object-Relational Mapping) 让你用 Python 代码操作数据库，而不是写 SQL 语句。

类比：前端你不会直接操作 DOM（`document.createElement`），而是用 Vue/React 的组件系统。ORM 就是数据库的「组件系统」。

### 没有 ORM vs 有 ORM

```python
# 没有 ORM — 手写 SQL（类似手动操作 DOM）
result = await db.execute("SELECT * FROM users WHERE id = '123'")

# 有 ORM — 用 Python 对象操作（类似用 Vue 组件）
user = await db.get(User, "123")
user.nickname = "新昵称"
await db.commit()
```

### SQLAlchemy 模型定义

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True)
    nickname: Mapped[str] = mapped_column(String(50))
    role: Mapped[str] = mapped_column(String(20))
```

这段代码等同于这条 SQL：

```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(32) UNIQUE,
    nickname VARCHAR(50),
    role VARCHAR(20)
);
```

但你永远不需要手写这条 SQL — 定义好 Python 类，alembic 自动帮你生成并执行。

### models/ vs schemas/ 的区别

这是初学者最容易混淆的点：

| | models/ | schemas/ |
|---|---|---|
| 用途 | 定义数据库表结构 | 定义 API 请求/响应结构 |
| 库 | SQLAlchemy | Pydantic |
| 类比 | 数据库里的表 | 前端的 TypeScript interface |
| 持久化 | 数据存在硬盘上 | 只在内存中存在 |

为什么要分开？因为数据库里存了 `password_hash`，但 API 响应绝对不能返回这个字段。model 是完整的数据结构，schema 是对外暴露的结构。

---

## 3. PostgreSQL — 关系型数据库

### 什么是数据库

前端的数据存在哪里？
- 浏览器内存（Pinia store）→ 刷新就没了
- localStorage → 只在一个浏览器里
- 后端数据库 → 所有用户共享、永久保存

PostgreSQL（简称 PG）就是这个「永久保存数据」的地方。

### 为什么选 PostgreSQL

| 数据库 | 定位 | 类比 |
|---|---|---|
| SQLite | 单文件数据库，适合本地/小项目 | 类似 localStorage |
| MySQL | 中规中矩，互联网常用 | 类似 Webpack — 够用但有些老 |
| PostgreSQL | 功能最强，类型系统丰富 | 类似 Vite — 现代、强大、社区活跃 |

PG 的优势：支持 JSON 字段、全文搜索、事务严格、数据一致性强。对于本项目（需求管理、任务协作、权限控制），数据一致性极其重要。

### 表、行、列

```
前端类比：
- 数据库 = 一个完整的应用状态
- 表 (table) = 一个 store（如 userStore、taskStore）
- 行 (row) = store 里的一条数据
- 列 (column) = 数据的字段

users 表：
┌──────────┬──────────┬────────┬───────────┐
│ id       │ username │ role   │ nickname  │
├──────────┼──────────┼────────┼───────────┤
│ uuid-001 │ chenbei  │ req    │ 陈北      │
│ uuid-002 │ shenyue  │ builder│ 沈月      │
└──────────┴──────────┴────────┴───────────┘
```

### 关系

表和表之间有关系（这就是「关系型数据库」名字的由来）：

- 一个用户可以提交多个需求 → User **一对多** Demand
- 一个任务有多个成员，一个成员参与多个任务 → Task **多对多** User（通过 TaskMember 中间表）

### 连接字符串

```
postgresql+asyncpg://user:password@host:port/dbname
│           │         │     │       │    │     │
│           │         │     │       │    │     └─ 数据库名
│           │         │     │       │    └─ 端口 (默认 5432)
│           │         │     │       └─ 服务器地址
│           │         │     └─ 密码
│           │         └─ 用户名
│           └─ 驱动 (asyncpg = Python 异步 PG 驱动)
└─ 数据库类型
```

---

## 4. Redis — 内存缓存数据库

### 什么是 Redis

如果 PostgreSQL 是「硬盘上的存储柜」，Redis 就是「桌面上的便利贴」。

- PG：数据安全、持久、但读写相对慢（需要磁盘 IO）
- Redis：数据存在内存里、极快（纳秒级）、但重启后可能丢失

### 本项目怎么用 Redis

| 用途 | 说明 | 类比 |
|---|---|---|
| Token 白名单 | 记录哪些 refresh_token 有效 | 类似 sessionStorage 存登录态 |
| Token 黑名单 | 登出后让 access_token 立即失效 | 类似前端清除 cookie |
| 频率限制 | 60秒内只能发一次验证码 | 类似前端的防抖/节流 |
| 缓存 | 热点数据缓存，减少数据库查询 | 类似前端的 computed 缓存 |

### Redis 的数据结构

Redis 不是「表」结构，而是 Key-Value 存储（类似 JavaScript 的 Map）：

```javascript
// 前端类比
const redis = new Map()
redis.set("refresh:user123:token_abc", "1")       // 15分钟后自动删除
redis.set("sms_cooldown:15900000000", "1")        // 60秒后自动删除
redis.get("refresh:user123:token_abc")            // "1" 或 null
```

关键特性：**TTL（自动过期）**。设置一个 key 时可以指定过期时间，到期自动消失。这对 Token 管理极为方便。

---

## 5. JWT — 无状态认证

### 登录认证的演变

**Session 方式**（传统）：
1. 用户登录 → 服务器生成 session，存在服务器内存/Redis
2. 返回 session_id（cookie）
3. 每次请求带 cookie → 服务器查找 session → 确认身份

**JWT 方式**（现代）：
1. 用户登录 → 服务器生成 JWT Token（一段加密字符串）
2. Token 里包含了用户信息（id、role），用密钥签名
3. 每次请求带 Token → 服务器用密钥验证签名 → 直接从 Token 解出用户信息

### JWT 长什么样

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyXzEyMyIsInJvbGUiOiJvcGVyYXRvciJ9.xxxxx
│                      │                                                    │
│ Header               │ Payload（用户信息）                                  │ Signature
│ {"alg":"HS256"}      │ {"sub":"user_123","role":"operator","exp":...}      │ 签名验证
```

前端类比：JWT 就像一张「签名的身份证」。
- 身份证上写了你是谁（payload）
- 有防伪标记（signature）
- 有有效期（exp）
- 验证时只需要看防伪标记是否正确，不需要去派出所（数据库）查

### 双 Token 策略

为什么需要两个 Token？

| | access_token | refresh_token |
|---|---|---|
| 有效期 | 15 分钟 | 7 天 |
| 用途 | 每次请求带上，证明身份 | access_token 过期后用它换新的 |
| 存储 | 前端内存（Pinia store） | 前端 localStorage 或 cookie |
| 安全性 | 即使泄露，15分钟就失效 | 一次性使用，用完换新的 |

流程：
```
1. 登录 → 拿到 access_token + refresh_token
2. 正常请求 → 带 access_token
3. access_token 过期 → 用 refresh_token 换新双 Token
4. refresh_token 也过期 → 重新登录
```

前端类比：类似 OAuth 的 access_token / refresh_token，或者想象成「日票」和「周卡」。

---

## 6. 文件存储

### 为什么文件不存数据库

数据库擅长存结构化的文本数据（用户名、状态、数字），不擅长存大文件（图片、文档）。原因：
- 文件太大，塞进数据库会拖慢查询
- 数据库备份会变得巨大
- 文件读取不需要 SQL 查询能力

### 存储策略

```
用户上传文件 → 文件存到磁盘/云存储 → 数据库只存文件的元信息

File 表：
┌───────────┬─────────────────┬──────┬────────────────────┐
│ id        │ filename        │ size │ storage_path       │
├───────────┼─────────────────┼──────┼────────────────────┤
│ file_001  │ 说明文档.pdf     │ 2MB  │ /uploads/2026/06/… │
└───────────┴─────────────────┴──────┴────────────────────┘
```

业务接口只传 `file_id`，不传文件本身。类比前端：你在 `<img>` 标签里写的是 URL（指针），不是图片的二进制数据。

### 上传流程

```
前端                            后端
  │                               │
  │ ── POST /files (multipart) ──→│ → 存文件到 uploads/ 目录
  │ ←── { file_id: "xxx" } ──────│ → 存元信息到 File 表
  │                               │
  │ ── POST /demands ────────────→│ → 只保存 file_id 引用
  │    { attachment_ids: ["xxx"] } │
```

当前项目先用本地磁盘（`./uploads/`），后续可以无缝切换到阿里云 OSS 等云存储。

---

## 7. 请求生命周期

一个 API 请求从进来到返回，完整经过的路径：

```
HTTP 请求进入
    │
    ▼
┌─────────────────┐
│ 中间件 (CORS)   │  ← 类似 Vue Router 的全局守卫
└────────┬────────┘
         │
    ▼
┌─────────────────┐
│ 路由层 (api/)    │  ← 找到对应的处理函数
└────────┬────────┘
         │
    ▼
┌─────────────────┐
│ 依赖注入         │  ← 解析 Token、获取当前用户、检查权限
│ (dependencies/) │
└────────┬────────┘
         │
    ▼
┌─────────────────┐
│ Schema 校验      │  ← 验证请求体格式（自动，不合法直接 422）
│ (schemas/)      │
└────────┬────────┘
         │
    ▼
┌─────────────────┐
│ 业务逻辑         │  ← 执行具体业务（创建需求、转化任务…）
│ (services/)     │
└────────┬────────┘
         │
    ▼
┌─────────────────┐
│ 数据库操作       │  ← 读写 PostgreSQL
│ (models/ + ORM) │
└────────┬────────┘
         │
    ▼
┌─────────────────┐
│ 响应序列化       │  ← 按 Schema 格式化返回数据
│ (schemas/)      │
└─────────────────┘
         │
    ▼
HTTP 响应返回
```

前端类比整条链路：
```
用户点击按钮
→ 路由守卫检查权限
→ 组件 mounted
→ 调用 store action
→ store 调用 API
→ 处理响应更新状态
→ 组件渲染
```

---

## 8. 概念速查表

| 后端概念 | 一句话解释 | 前端最近似类比 |
|---|---|---|
| FastAPI | Python Web 框架 | Express / Koa |
| Uvicorn | HTTP 服务器，运行 FastAPI | Node.js 运行时 |
| SQLAlchemy | ORM，用代码操作数据库 | Prisma / TypeORM |
| PostgreSQL | 关系型数据库，持久存储 | —（前端无对应物） |
| Redis | 内存键值存储，极快 | Map + setTimeout 自动删除 |
| Alembic | 数据库迁移工具 | Prisma Migrate |
| Pydantic | 数据校验库 | zod / yup |
| JWT | 无状态认证令牌 | OAuth token |
| 中间件 | 请求前后的拦截处理 | Axios 拦截器 / 路由守卫 |
| 依赖注入 | 自动提供函数所需的依赖 | Vue provide/inject |
| async/await | 异步编程 | 和 JS 完全一样 |
| .env | 环境变量 | 和前端完全一样 |
| pyproject.toml | 项目配置 | package.json |
| uv.lock | 依赖锁定 | pnpm-lock.yaml |
