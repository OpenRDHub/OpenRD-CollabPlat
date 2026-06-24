# OpenRD 后端开发任务计划

## 目标

在 `feature/backend-init` 分支完成的基础上，按模块逐步实现完整的后端 API 服务，最终交付可与前端联调的生产级后端。

## 技术栈

- Python 3.12 + FastAPI + SQLAlchemy (async) + Alembic
- PostgreSQL (云服务) + Redis
- JWT 双 Token 认证
- 阿里云 OSS (文件存储) + 阿里云 Dysms (短信)
- uv 包管理 + ruff 代码检查 + pytest 测试

## 分支开发计划

### Phase 1: `feature/backend-auth` — 认证与鉴权
- **状态**: `pending`
- **内容**:
  - User 模型 + 数据库迁移
  - POST /auth/register — 注册
  - POST /auth/login — 登录（返回双 Token）
  - POST /auth/refresh — 刷新 Token
  - POST /auth/logout — 登出（吊销 Token）
  - POST /auth/sms-code — 发送短信验证码
  - POST /auth/password/reset — 重置密码
  - POST /auth/onboarding — 账号初始化
  - JWT 签发/校验工具
  - Redis Token 白名单/黑名单
  - 权限中间件（get_current_user 依赖注入）
  - RBAC 权限校验装饰器

### Phase 2: `feature/backend-user` — 用户模块
- **状态**: `pending`
- **依赖**: Phase 1
- **内容**:
  - GET /me — 当前用户信息
  - PATCH /me/profile — 更新个人资料
  - PATCH /me/password — 修改密码
  - GET /me/permissions — 获取有效权限
  - GET /admin/users — 用户列表
  - GET /admin/users/{user_id} — 用户详情
  - PATCH /admin/users/{user_id} — 编辑用户
  - POST /admin/users/{user_id}/lock — 锁定
  - POST /admin/users/{user_id}/unlock — 解锁

### Phase 3: `feature/backend-demand` — 需求模块
- **状态**: `pending`
- **依赖**: Phase 1
- **内容**:
  - Demand + DemandReply 模型 + 迁移
  - POST /demands — 提交需求
  - GET /me/demands — 我的需求列表
  - GET /demands — 管理端需求列表/需求大厅
  - GET /demands/{demand_id} — 需求详情
  - PATCH /demands/{demand_id} — 编辑需求管理信息
  - POST /demands/{demand_id}/replies — 发送沟通消息
  - POST /demands/{demand_id}/replies/{reply_id}/revoke — 撤回消息
  - POST /demands/{demand_id}/convert — 转化为任务
  - POST /demands/{demand_id}/reject — 驳回
  - POST /demands/{demand_id}/link-similar — 关联相似
  - POST /demands/{demand_id}/archive — 归档

### Phase 4: `feature/backend-task` — 任务模块
- **状态**: `pending`
- **依赖**: Phase 3
- **内容**:
  - Task + TaskProgress 模型 + 迁移
  - GET /tasks — 任务大厅列表
  - GET /tasks/{task_id} — 任务详情
  - PATCH /tasks/{task_id} — 编辑任务信息
  - POST /tasks/{task_id}/status — 变更任务状态
  - POST /tasks/{task_id}/progress — 提交进度
  - POST /tasks/{task_id}/resources — 更新项目资源
  - GET /me/tasks — 我的任务列表

### Phase 5: `feature/backend-team` — 队伍协作
- **状态**: `pending`
- **依赖**: Phase 4
- **内容**:
  - TaskMember + JoinApplication + Assignment 模型 + 迁移
  - GET /tasks/{task_id}/team — 队伍详情
  - POST /tasks/{task_id}/join-applications — 申请加入
  - POST .../approve — 通过申请
  - POST .../reject — 拒绝申请
  - POST /tasks/{task_id}/members/invite — 邀请成员
  - PATCH /tasks/{task_id}/members/{member_id} — 更新职责
  - POST /tasks/{task_id}/leader/transfer — 转移队长
  - PUT /tasks/{task_id}/assignments — 保存分工

### Phase 6: `feature/backend-message` — 消息中心
- **状态**: `pending`
- **依赖**: Phase 1（可并行于 Phase 3-5）
- **内容**:
  - Message + MessageRecipient 模型 + 迁移
  - GET /messages — 消息列表
  - GET /messages/unread-count — 未读数
  - GET /messages/{message_id} — 消息详情（自动已读）
  - POST /messages/{message_id}/read — 标记已读
  - POST /messages/read-all — 全部已读
  - DELETE /messages/{message_id} — 删除消息
  - 事件触发消息生成 service

### Phase 7: `feature/backend-admin` — 管理治理
- **状态**: `pending`
- **依赖**: Phase 2
- **内容**:
  - Role + UserPermission + SystemLog 模型 + 迁移
  - GET /admin/roles — 角色列表
  - POST /admin/roles — 创建角色
  - PATCH /admin/roles/{role_id} — 编辑角色
  - GET /admin/permissions — 权限点列表
  - PUT /admin/users/{user_id}/permissions — 追加手动权限
  - GET /admin/system-logs — 日志列表
  - GET /admin/system-logs/{log_id} — 日志详情

### Phase 8: `feature/backend-file` — 文件存储
- **状态**: `pending`
- **依赖**: Phase 1（可并行于 Phase 3-5）
- **内容**:
  - File 模型 + 迁移
  - POST /files — 上传文件
  - GET /files/{file_id} — 下载/查看文件
  - DELETE /files/{file_id} — 删除文件
  - services/storage.py — 本地/OSS 双模式抽象
  - 文件大小限制、类型校验
  - 按业务对象校验下载权限

## 依赖关系图

```
              Phase 1 (auth)
                   │
     ┌─────────────┼─────────────┬──────────┐
     ▼             ▼             ▼          ▼
Phase 2 (user) Phase 3 (demand) Phase 6   Phase 8
     │             │            (message)  (file)
     ▼             ▼
Phase 7 (admin) Phase 4 (task)
                   │
                   ▼
               Phase 5 (team)
```

## 关键约定

- API 前缀: `/api/v1`
- 响应格式: `{ "code": "OK", "message": "success", "data": {} }`
- 时间格式: ISO 8601
- 所有删除为逻辑删除
- 密码使用 bcrypt 加密
- 列表接口默认分页 page=1, page_size=20
