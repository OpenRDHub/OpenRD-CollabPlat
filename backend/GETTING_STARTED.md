# OpenRD 后端开发入门教程

> 面向前端开发者的 Python 后端快速上手指南，基于 uv + FastAPI。

## 1. 概念对照

先建立前后端工具链的心智映射：

| 你熟悉的 (前端) | 对应的 (Python 后端) | 说明 |
|---|---|---|
| pnpm add xxx | `uv add xxx` | 安装依赖 |
| pnpm install | `uv sync` | 从 lockfile 还原环境 |
| pnpm remove xxx | `uv remove xxx` | 移除依赖 |
| package.json | `pyproject.toml` | 项目配置和依赖声明 |
| pnpm-lock.yaml | `uv.lock` | 锁定版本 |
| node_modules | `.venv` | 依赖安装目录 |
| npx | `uvx` | 临时运行工具 |
| pnpm dev / vite dev | `uv run uvicorn main:app --reload` | 启动开发服务器 |
| ESLint + Prettier | `ruff` | 代码检查 + 格式化 |
| TypeScript 类型 | Python type hints + Pydantic | 类型约束 |

## 2. 安装核心依赖

在 `backend/` 目录下执行以下命令：

```bash
# Web 框架 (类似 Express/Koa)
uv add fastapi

# ASGI 服务器 (类似 node 运行时，负责启动 HTTP 服务)
uv add uvicorn[standard]

# ORM 数据库操作 (类似 Prisma/TypeORM)
uv add sqlalchemy

# 异步数据库驱动 (SQLAlchemy 的异步引擎需要)
uv add aiosqlite

# 数据库迁移工具 (类似 prisma migrate)
uv add alembic

# 数据校验 (FastAPI 内置使用，类似 zod/yup)
# 注意：fastapi 已自带 pydantic，不需要单独装

# JWT 认证
uv add python-jose[cryptography]

# 密码加密 (bcrypt)
uv add passlib[bcrypt]

# Redis 客户端 (用于 Token 白名单/黑名单)
uv add redis

# 环境变量管理 (类似 dotenv)
uv add pydantic-settings

# 一条命令装完所有的写法：
# uv add fastapi "uvicorn[standard]" sqlalchemy aiosqlite alembic "python-jose[cryptography]" "passlib[bcrypt]" redis pydantic-settings
```

## 3. 安装开发依赖

```bash
# 代码检查和格式化 (类似 eslint + prettier)
uv add --dev ruff

# 测试框架 (类似 vitest/jest)
uv add --dev pytest pytest-asyncio

# HTTP 测试客户端
uv add --dev httpx
```

> `--dev` 等同于 pnpm 的 `-D`，只在开发时使用，不会进入生产环境。

## 4. 验证安装

安装完成后，你的 `pyproject.toml` 的 `[project]` 部分会自动更新（和 package.json 一样）。

运行以下命令确认一切正常：

```bash
# 查看已安装的包 (类似 pnpm list)
uv pip list

# 验证 Python 和 FastAPI 可用
uv run python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"
```

## 5. 写一个 Hello World

你的 `main.py` 现在应该是空的或有默认内容。替换为：

```python
from fastapi import FastAPI

app = FastAPI(title="OpenRD API", version="0.1.0")


@app.get("/")
async def root():
    return {"message": "Hello OpenRD"}


@app.get("/health")
async def health():
    return {"status": "ok"}
```

## 6. 启动开发服务器

```bash
uv run uvicorn main:app --reload --port 8000
```

参数说明：
- `main:app` → 文件名:FastAPI实例变量名（类似 vite 的入口配置）
- `--reload` → 文件变更自动重启（类似 vite 的 HMR）
- `--port 8000` → 端口号

启动后访问：
- http://localhost:8000 → API 根路径
- http://localhost:8000/docs → **自动生成的 Swagger UI**（类似 Postman，但内置！）
- http://localhost:8000/redoc → 另一种风格的 API 文档

> Swagger UI 是 FastAPI 最爽的特性之一 — 写好代码，文档和测试界面自动生成。

## 7. 快速理解 FastAPI 核心概念

### 7.1 路由 (类似 Express Router)

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])

@router.post("/login")
async def login():
    ...

@router.post("/register")
async def register():
    ...
```

### 7.2 请求体校验 (类似 zod schema)

```python
from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=8)

@router.post("/login")
async def login(body: LoginRequest):  # 自动校验，不合法直接返回 422
    print(body.username)  # 类型安全，有补全
    ...
```

### 7.3 响应模型 (类似 TypeScript interface 定义返回类型)

```python
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest):
    ...
    return LoginResponse(
        access_token="xxx",
        refresh_token="xxx",
        expires_in=900,
    )
```

### 7.4 依赖注入 (类似 Vue 的 provide/inject，但更强大)

```python
from fastapi import Depends

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # 解析 JWT，查询用户
    ...
    return user

@router.get("/me")
async def get_me(user = Depends(get_current_user)):
    # user 已经是当前登录用户了
    return user
```

### 7.5 中间件 (类似 Express middleware)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端地址
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 8. 项目结构预览

安装好依赖后，最终项目结构会是这样：

```
backend/
├── .venv/                  # 虚拟环境 (gitignore)
├── app/                    # 应用主目录
│   ├── __init__.py
│   ├── main.py             # FastAPI 入口
│   ├── config.py           # 配置管理
│   ├── database.py         # 数据库连接
│   ├── models/             # SQLAlchemy 模型 (数据库表定义)
│   ├── schemas/            # Pydantic 模型 (请求/响应结构)
│   ├── api/                # 路由层
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── demands.py
│   │   │   ├── tasks.py
│   │   │   └── ...
│   ├── services/           # 业务逻辑层
│   ├── dependencies/       # 依赖注入 (认证、权限)
│   └── utils/              # 工具函数
├── alembic/                # 数据库迁移
├── tests/                  # 测试
├── pyproject.toml          # 项目配置
├── uv.lock                 # 依赖锁定
└── .env                    # 环境变量 (gitignore)
```

## 9. 常用命令速查

```bash
# 启动开发服务器
uv run uvicorn app.main:app --reload --port 8000

# 添加依赖
uv add <package>
uv add --dev <package>    # 开发依赖

# 移除依赖
uv remove <package>

# 运行测试
uv run pytest

# 代码检查
uv run ruff check .

# 代码格式化
uv run ruff format .

# 数据库迁移
uv run alembic revision --autogenerate -m "描述"
uv run alembic upgrade head
```

## 10. 注意事项

1. **不要手动激活 venv** — 用 `uv run` 前缀执行命令，它会自动使用 .venv 环境。
2. **uv.lock 要提交到 git** — 和 pnpm-lock.yaml 一样，保证团队环境一致。
3. **.venv 加入 .gitignore** — 和 node_modules 一样不提交。
4. **.env 加入 .gitignore** — 包含密钥等敏感信息。
5. **Python 用缩进而非花括号** — 4 个空格，VSCode 会自动处理。
6. **async/await 和 JS 一样** — FastAPI 原生支持异步，写法几乎相同。

## 11. 下一步

装好依赖、跑通 Hello World 后，把项目交给我，我来搭建完整的项目骨架并实现 API。你需要做的：

1. 按第 2、3 节安装依赖
2. 按第 5、6 节跑通 Hello World
3. 打开 http://localhost:8000/docs 看看自动生成的文档
4. 感受下改代码后自动重启的开发体验

玩够了就告诉我，我来接手后续开发。
