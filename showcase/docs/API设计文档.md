# OpenRD 协作平台 API 设计文档

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 文档版本 | v0.1 |
| 文档状态 | 设计稿 |
| 创建日期 | 2026-06-09 |
| 适用范围 | P0 完整业务闭环，P1 预留接口草案 |
| 主要依据 | `docs/OpenRD协作平台PRD正式版.md`、`docs/OpenRD协作平台技术文档.md`、`demo/` 静态原型 |

本文档最初用于指导前后端实现。当前 FastAPI 后端和 Vue 前端均已初始化并包含实际接口代码；联调时应以运行中的 FastAPI OpenAPI、后端 schema 与前端 API 封装的对照结果为准。本文件仍可用于产品语义参考，但其中的路径、权限点、状态枚举和字段结构若与源码不同，应先更新契约并补充真实后端测试。

## 2. 通用约定

### 2.1 基础路径

所有业务接口统一使用版本前缀：

```text
/api/v1
```

健康检查和公开资源可按需独立暴露，但仍建议保留版本前缀。

### 2.2 认证方式

除注册、登录、验证码、重置密码、健康检查外，所有接口都必须携带：

```http
Authorization: Bearer <access_token>
```

Token 策略：

| Token | 有效期 | 用途 | 存储/校验 |
| --- | --- | --- | --- |
| `access_token` | 15 分钟 | API 请求鉴权 | JWT 签名和过期时间校验 |
| `refresh_token` | 7 天 | 换取新双 Token | Redis 白名单，一次性轮换 |

刷新成功后，旧 `refresh_token` 立即失效，防止重放。

### 2.3 响应格式

成功响应：

```json
{
  "code": "OK",
  "message": "success",
  "data": {}
}
```

分页响应：

```json
{
  "code": "OK",
  "message": "success",
  "data": {
    "items": [],
    "page": 1,
    "page_size": 20,
    "total": 0
  }
}
```

失败响应：

```json
{
  "code": "DEMAND_ALREADY_PROCESSED",
  "message": "该需求已被处理",
  "details": {
    "demand_id": "REQ-2418"
  }
}
```

### 2.4 通用查询参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `page` | integer | 1 | 页码，从 1 开始 |
| `page_size` | integer | 20 | 每页数量，最大 100 |
| `keyword` | string | - | 关键词搜索 |
| `sort` | string | `created_at_desc` | 排序方式 |
| `include_deleted` | integer | 0 | 是否包含逻辑删除数据，0 否，1 是；仅管理端接口可用 |

### 2.5 通用错误码

| HTTP 状态 | code | 说明 |
| --- | --- | --- |
| 400 | `BAD_REQUEST` | 参数格式错误或业务校验失败 |
| 401 | `UNAUTHORIZED` | 未登录、Token 缺失或过期 |
| 403 | `FORBIDDEN` | 已登录但无权限 |
| 404 | `NOT_FOUND` | 资源不存在 |
| 409 | `CONFLICT` | 资源状态冲突，例如重复转化 |
| 413 | `PAYLOAD_TOO_LARGE` | 附件超出大小限制 |
| 422 | `VALIDATION_ERROR` | 字段校验失败 |
| 500 | `INTERNAL_ERROR` | 服务端异常 |

### 2.6 时间与文件

- 时间统一使用 ISO 8601，例如 `2026-06-09T12:00:00+08:00`。
- 需求提交附件：最多 3 个，单个不超过 10MB。
- 需求沟通附件：最多 5 个，单个不超过 20MB。
- 文件先通过 `/files` 上传，业务接口只保存 `file_id` 列表。

### 2.7 整数标志位与逻辑删除

数据结构尽量避免使用布尔类型。需要表达“是/否”“开启/关闭”“已读/未读”等二元状态时，统一使用 integer 标志位：

| 值 | 含义 |
| --- | --- |
| `0` | 否、未完成、未读、未删除、关闭 |
| `1` | 是、已完成、已读、已删除、开启 |

所有删除均为逻辑删除，不做物理删除。可删除数据表统一保留以下审计字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `is_deleted` | integer | 是否已逻辑删除，0 否，1 是 |
| `deleted_at` | string | 删除时间，未删除为空 |
| `deleted_by` | string | 删除操作人 ID，未删除为空 |

列表接口默认只返回 `is_deleted = 0` 的数据。管理端如需查看已删除数据，应显式增加 `include_deleted=1` 查询参数，并校验管理员权限。

## 3. 角色、权限与状态

### 3.1 角色

| 角色值 | 名称 | 说明 |
| --- | --- | --- |
| `requester` | 需求者 | 患者或患者家属，提交需求并跟踪状态 |
| `builder` | 共建者 | 志愿者或开发者，浏览任务并参与协作 |
| `operator` | 产品经理/运管 | 审核需求、沟通、转化任务、跟进任务 |
| `super_admin` | 超级管理员 | 用户、权限、日志和平台治理 |

### 3.2 核心权限点

| 权限点 | 说明 |
| --- | --- |
| `demand:view` | 查看需求 |
| `demand:create` | 提交需求 |
| `demand:reply` | 需求沟通回复 |
| `demand:convert` | 需求转化任务 |
| `demand:reject` | 驳回需求 |
| `demand:link` | 关联已有相似需求/任务 |
| `task:view` | 查看任务 |
| `task:join` | 申请加入队伍 |
| `task:update` | 更新任务信息或进度 |
| `task:manage` | 管理任务状态和资源 |
| `member:view` | 查看队伍成员 |
| `member:approve` | 审核加入申请 |
| `member:invite` | 邀请成员 |
| `task:assign` | 调整任务分工 |
| `message:view` | 查看消息 |
| `message:manage` | 管理消息状态 |
| `user:manage` | 用户管理 |
| `permission:manage` | 权限管理 |
| `log:view` | 查看系统日志 |
| `system:config` | 系统配置 |

### 3.3 需求状态

| 状态值 | 名称 | 说明 |
| --- | --- | --- |
| `pending_review` | 待审核 | 用户已提交，等待运管处理 |
| `communicating` | 沟通中 | 运管与需求者正在澄清 |
| `converted` | 已转任务 | 已创建新任务 |
| `linked` | 已关联 | 已关联到既有相似任务 |
| `rejected` | 已驳回 | 不进入任务流程 |
| `closed` | 已关闭 | 流程结束 |
| `archived` | 已归档 | 运营归档保留 |

### 3.4 任务与队伍状态

| 类型 | 状态值 | 名称 |
| --- | --- | --- |
| 任务 | `recruiting` | 招募中 |
| 任务 | `team_ready` | 组队完成 |
| 任务 | `in_progress` | 解决中 |
| 任务 | `pending_acceptance` | 待验收 |
| 任务 | `completed` | 已完成 |
| 任务 | `closed` | 已关闭 |
| 队伍 | `forming` | 组队中 |
| 队伍 | `ready` | 组队完成 |
| 队伍 | `collaborating` | 协作中 |
| 队伍 | `accepted` | 已验收 |
| 队伍 | `disbanded` | 已解散 |

## 4. 核心数据模型

### 4.1 User

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | 用户 UUID |
| `platform_id` | string | 平台号，唯一 |
| `username` | string | 登录账户名，唯一 |
| `nickname` | string | 昵称 |
| `phone` | string | 手机号 |
| `avatar_url` | string | 头像地址 |
| `role` | string | 主角色 |
| `identity` | string | 用户身份说明 |
| `position` | string | 岗位/专业方向 |
| `intro` | string | 个人简介 |
| `status` | string | `active`、`locked`、`disabled` |
| `created_at` | string | 注册时间 |
| `onboarding_completed` | integer | 是否完成账号初始化，0 否，1 是 |
| `is_deleted` | integer | 是否已逻辑删除，0 否，1 是 |
| `deleted_at` | string | 删除时间 |
| `deleted_by` | string | 删除操作人 ID |

### 4.2 Demand

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | 需求编号，例如 `REQ-2418` |
| `title` | string | 需求标题 |
| `description` | string | 需求描述 |
| `urgency` | string | `low`、`medium`、`high` |
| `status` | string | 需求状态 |
| `convert_status` | string | 转化状态 |
| `creator_id` | string | 创建人 ID |
| `contact_phone` | string | 联系电话，可脱敏展示 |
| `attachment_ids` | string[] | 附件 ID |
| `linked_task_id` | string | 关联任务 ID |
| `linked_demand_id` | string | 相似需求 ID |
| `progress` | integer | 处理进度 0-100 |
| `feedback` | string | 平台反馈 |
| `created_at` | string | 创建时间 |
| `updated_at` | string | 更新时间 |
| `is_deleted` | integer | 是否已逻辑删除，0 否，1 是 |
| `deleted_at` | string | 删除时间 |
| `deleted_by` | string | 删除操作人 ID |

### 4.3 DemandReply

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | 回复 ID |
| `demand_id` | string | 需求 ID |
| `thread_id` | string | 会话 ID |
| `sender_id` | string | 发送人 |
| `sender_role` | string | `requester`、`operator`、`system` |
| `content` | string | 消息内容 |
| `attachment_ids` | string[] | 附件 ID |
| `is_revoked` | integer | 是否撤回，0 否，1 是 |
| `created_at` | string | 发送时间 |
| `is_deleted` | integer | 是否已逻辑删除，0 否，1 是 |
| `deleted_at` | string | 删除时间 |
| `deleted_by` | string | 删除操作人 ID |

### 4.4 Task

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | 任务编号，例如 `TASK-1042` |
| `demand_id` | string | 来源需求 ID |
| `title` | string | 任务标题 |
| `description` | string | 任务描述 |
| `task_type` | string | 任务类型 |
| `priority` | string | `low`、`medium`、`high` |
| `scope` | string | 工单范围 |
| `acceptance_criteria` | string | 验收标准 |
| `status` | string | 任务状态 |
| `team_status` | string | 队伍状态 |
| `progress` | integer | 进度 0-100 |
| `planned_end_time` | string | 计划完成时间 |
| `owner_id` | string | 转化/负责产品经理 |
| `leader_id` | string | 队长 ID |
| `resource_links` | object[] | 项目资源 |
| `file_ids` | string[] | 任务附件 |
| `created_at` | string | 创建时间 |
| `updated_at` | string | 更新时间 |
| `is_deleted` | integer | 是否已逻辑删除，0 否，1 是 |
| `deleted_at` | string | 删除时间 |
| `deleted_by` | string | 删除操作人 ID |

### 4.5 TaskMember

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | 成员记录 ID |
| `task_id` | string | 任务 ID |
| `user_id` | string | 用户 ID |
| `role` | string | 队伍内角色 |
| `duty` | string | 分工职责 |
| `member_type` | string | `leader`、`member`、`operator` |
| `status` | string | `active`、`pending`、`removed` |
| `joined_at` | string | 加入时间 |
| `is_deleted` | integer | 是否已逻辑删除，0 否，1 是 |
| `deleted_at` | string | 删除时间 |
| `deleted_by` | string | 删除操作人 ID |

### 4.6 Message

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | string | 消息 ID |
| `category` | string | `system`、`task`、`demand`、`team`、`reply` |
| `title` | string | 消息标题 |
| `summary` | string | 摘要 |
| `content` | string | 正文 |
| `sender` | string | 发送方 |
| `target_type` | string | `demand`、`task`、`permission` 等 |
| `target_id` | string | 关联对象 ID |
| `action_text` | string | 推荐操作 |
| `read_status` | integer | 阅读状态，0 未读，1 已读 |
| `created_at` | string | 创建时间 |
| `is_deleted` | integer | 是否已逻辑删除，0 否，1 是 |
| `deleted_at` | string | 删除时间 |
| `deleted_by` | string | 删除操作人 ID |

## 5. API 详情

### 5.1 认证与账号

#### POST `/auth/register`

新用户注册。

权限：公开。

请求体：

```json
{
  "username": "chenbei",
  "password": "OpenRD#2026",
  "nickname": "陈北",
  "phone": "15900000000",
  "sms_code": "123456",
  "role": "requester"
}
```

响应 `data`：

```json
{
  "user_id": "uuid",
  "platform_id": "requester_chenbei",
  "onboarding_required": 1
}
```

#### POST `/auth/login`

账户名和密码登录。

权限：公开。

请求体：

```json
{
  "username": "chenbei",
  "password": "OpenRD#2026"
}
```

响应 `data`：

```json
{
  "access_token": "jwt",
  "refresh_token": "jwt",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "platform_id": "requester_chenbei",
    "nickname": "陈北",
    "role": "requester"
  }
}
```

#### POST `/auth/refresh`

刷新双 Token。

权限：公开，需提交有效 `refresh_token`。

请求体：

```json
{
  "refresh_token": "jwt"
}
```

响应 `data`：同登录接口中的 Token 字段。

#### POST `/auth/logout`

退出登录并吊销当前 `refresh_token`。

权限：登录用户。

请求体：

```json
{
  "refresh_token": "jwt"
}
```

#### POST `/auth/sms-code`

发送短信验证码。

权限：公开。

请求体：

```json
{
  "phone": "15900000000",
  "scene": "register"
}
```

`scene` 可选值：`register`、`reset_password`。

#### POST `/auth/password/reset`

忘记密码重置。

权限：公开。

请求体：

```json
{
  "username": "chenbei",
  "phone": "15900000000",
  "sms_code": "123456",
  "new_password": "NewOpenRD#2026"
}
```

#### POST `/auth/onboarding`

账号初始化，补充身份、关注病种、能力标签等信息。

权限：登录用户。

请求体：

```json
{
  "identity": "患者家属",
  "interest_diseases": ["罕见遗传病"],
  "skills": ["需求整理"],
  "intro": "希望提交个人需求并跟踪协作进展"
}
```

### 5.2 当前用户

#### GET `/me`

获取当前用户信息。

权限：登录用户。

#### PATCH `/me/profile`

更新个人资料。

权限：登录用户。

请求体：

```json
{
  "nickname": "陈北",
  "avatar_file_id": "file_uuid",
  "position": "需求者",
  "intro": "关注复诊与用药提醒工具"
}
```

#### PATCH `/me/password`

修改登录密码。

权限：登录用户。

#### GET `/me/permissions`

获取当前用户有效权限点。

权限：登录用户。

### 5.3 需求提交与我的需求

#### POST `/demands`

提交需求。

权限：`demand:create`。

请求体：

```json
{
  "title": "复诊问题清单与用药提醒",
  "description": "希望记录复诊前问题，并支持每日用药提醒。",
  "urgency": "high",
  "contact_phone": "15900000000",
  "attachment_ids": ["file_uuid_1"]
}
```

响应 `data`：

```json
{
  "id": "REQ-2418",
  "status": "pending_review"
}
```

业务规则：

- 标题、描述、紧急程度必填。
- 附件最多 3 个，单个不超过 10MB。
- 创建成功后状态为 `pending_review`。
- 创建成功后触发运管端待审核消息。

#### GET `/me/demands`

获取我提交的需求。

权限：登录用户。

查询参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `status` | string | 需求状态 |
| `keyword` | string | 搜索标题、反馈、任务号 |
| `page` | integer | 页码 |
| `page_size` | integer | 每页数量 |

#### GET `/demands/{demand_id}`

获取需求详情。

权限：`demand:view`。

返回内容包括需求基础信息、附件、平台反馈、处理时间线、关联任务和可见沟通会话。

#### POST `/demands/{demand_id}/replies`

发送需求沟通消息。

权限：需求发布者或有 `demand:reply` 权限的运管。

请求体：

```json
{
  "thread_id": "thread_uuid",
  "content": "请补充药物类型、记录频率，以及是否需要家属共同查看。",
  "attachment_ids": []
}
```

业务规则：

- 需求发布者可回复与自己相关的需求。
- 运管默认只可查看和回复自己发起的沟通会话；超级管理员可按管理权限查看全部。
- 需求沟通附件最多 5 个，单个不超过 20MB。
- 新回复触发对方消息提醒。

#### POST `/demands/{demand_id}/replies/{reply_id}/revoke`

撤回需求沟通消息。

权限：消息发送者本人，或超级管理员。

业务规则：

- 撤回后保留审计记录。
- 前端展示为“该发言已撤回”。

### 5.4 需求管理与转化

#### GET `/demands`

管理端需求列表，也可用于需求大厅。

权限：`demand:view`。

查询参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `status` | string | 需求状态 |
| `convert_status` | string | 转化状态 |
| `owner_id` | string | 负责运管 |
| `keyword` | string | 搜索需求、状态、团队、任务号 |

#### POST `/demands/{demand_id}/convert`

将需求转化为任务。

权限：`demand:convert`。

请求体：

```json
{
  "thread_id": "thread_uuid",
  "title": "复诊问题清单与用药提醒",
  "task_type": "工具开发",
  "priority": "medium",
  "scope": "用药提醒 API、复诊前问题清单和提醒关闭配置。",
  "acceptance_criteria": "1. 明确需求边界。\n2. 输出可认领任务说明。\n3. 保留来源需求。",
  "planned_end_time": "2026-06-30T23:59:59+08:00"
}
```

响应 `data`：

```json
{
  "demand_id": "REQ-2418",
  "task_id": "TASK-1042",
  "demand_status": "converted",
  "task_status": "recruiting"
}
```

业务规则：

- 只能转化 `pending_review` 或 `communicating` 状态需求。
- 已转化、已关联、已关闭需求不可重复转化。
- 转化后自动关联原需求 ID。
- 转化产品经理自动加入任务队伍，默认成为初始队长；后续可转移队长。
- 触发需求者消息通知。
- 写入系统日志。

#### POST `/demands/{demand_id}/reject`

驳回需求。

权限：`demand:reject`。

请求体：

```json
{
  "reason": "需求描述过于模糊，长期未补充关键信息。"
}
```

业务规则：

- 驳回理由必填。
- 触发需求者消息通知。

#### POST `/demands/{demand_id}/link-similar`

关联已有相似需求或任务。

权限：`demand:link`。

请求体：

```json
{
  "target_demand_id": "REQ-2356",
  "target_task_id": "TASK-1024",
  "reason": "当前需求与既有复诊问题清单任务相似，不重复创建任务。"
}
```

业务规则：

- 当前需求状态变为 `linked`。
- 不创建新任务。
- 需求者可在详情页跳转到关联任务。

#### POST `/demands/{demand_id}/archive`

归档需求。

权限：`demand:reject` 或超级管理员。

### 5.5 任务大厅与任务详情

#### GET `/tasks`

任务大厅列表。

权限：`task:view`。

查询参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `status` | string | 任务状态 |
| `team_status` | string | 队伍状态 |
| `keyword` | string | 搜索任务、需求、状态、团队 |
| `page` | integer | 页码 |
| `page_size` | integer | 每页数量 |

返回列表字段：

| 字段 | 说明 |
| --- | --- |
| `id` | 任务编号 |
| `title` | 标题 |
| `description` | 摘要 |
| `status` | 任务状态 |
| `team_status` | 队伍状态 |
| `progress` | 进度 |
| `planned_end_time` | 计划完成时间 |
| `created_at` | 创建时间 |

#### GET `/tasks/{task_id}`

任务详情。

权限：`task:view`。

返回内容包括任务基础信息、来源需求、验收标准、项目资源、附件、里程碑、团队成员、当前用户在任务中的角色和可执行动作。

#### PATCH `/tasks/{task_id}`

编辑任务核心信息。

权限：`task:manage`。

请求体：

```json
{
  "title": "用药提醒 API 与消息队列联调",
  "description": "完成 API 字段确认、队列重试策略和前端联调说明。",
  "task_type": "后端接口",
  "priority": "medium",
  "scope": "提醒服务接口、异常补偿、前端联调说明。",
  "acceptance_criteria": "1. 字段定义完整。\n2. 重试策略明确。\n3. 联调用例通过。",
  "planned_end_time": "2026-06-30T23:59:59+08:00"
}
```

业务规则：

- 已完成或已关闭任务禁止修改核心验收标准。
- 关键信息变更后通知队伍成员。
- 写入系统日志。

#### POST `/tasks/{task_id}/status`

变更任务状态。

权限：`task:manage`。

请求体：

```json
{
  "status": "pending_acceptance",
  "reason": "团队已提交交付物，等待需求者验收。"
}
```

允许流转：

```text
recruiting -> team_ready -> in_progress -> pending_acceptance -> completed
```

特殊关闭由管理员执行：任意非 completed 状态可转为 `closed`，必须填写原因。

#### POST `/tasks/{task_id}/progress`

提交任务进度或协作更新。

权限：任务成员或 `task:update`。

请求体：

```json
{
  "progress": 68,
  "content": "已补充接口字段与异常重试策略。",
  "file_ids": ["file_uuid_1"]
}
```

#### POST `/tasks/{task_id}/resources`

更新任务项目资源。

权限：队长或 `task:manage`。

请求体：

```json
{
  "resource_links": [
    {
      "name": "任务仓库",
      "url": "https://github.com/openrd/demo-task"
    }
  ],
  "file_ids": ["file_uuid_1"],
  "actions": ["提交接口联调说明", "同步异常重试策略"]
}
```

### 5.6 队伍与成员协作

#### GET `/tasks/{task_id}/team`

获取任务队伍详情。

权限：`member:view`。

返回内容包括队长、成员列表、加入申请、分工计划、协作阶段。

#### POST `/tasks/{task_id}/join-applications`

申请加入任务队伍。

权限：`task:join`。

请求体：

```json
{
  "role": "后端开发",
  "skills": ["API 设计", "消息队列"],
  "reason": "可以补充摘要结果保存接口和任务数据结构。"
}
```

业务规则：

- 同一用户不可重复提交待审核申请。
- 申请提交后通知队长。
- 超过 24 小时未处理时，触发运管提醒。

#### POST `/tasks/{task_id}/join-applications/{application_id}/approve`

通过加入申请。

权限：队长或 `member:approve`。

请求体：

```json
{
  "duty": "API 与队列联调"
}
```

#### POST `/tasks/{task_id}/join-applications/{application_id}/reject`

拒绝加入申请。

权限：队长或 `member:approve`。

请求体：

```json
{
  "reason": "当前阶段暂不需要该角色。"
}
```

#### POST `/tasks/{task_id}/members/invite`

邀请成员加入队伍。

权限：队长或 `member:invite`。

请求体：

```json
{
  "platform_id": "backend_shenyue",
  "suggested_role": "后端开发",
  "reason": "补齐接口联调阶段所需角色。",
  "due_time": "2026-06-05T23:59:59+08:00"
}
```

#### PATCH `/tasks/{task_id}/members/{member_id}`

更新成员职责。

权限：队长或 `task:assign`。

#### POST `/tasks/{task_id}/leader/transfer`

转移队长。

权限：当前队长、负责产品经理或超级管理员。

请求体：

```json
{
  "new_leader_id": "uuid",
  "reason": "成员表现优异，转为任务队长。"
}
```

#### PUT `/tasks/{task_id}/assignments`

保存任务分工。

权限：队长或 `task:assign`。

请求体：

```json
{
  "assignments": [
    {
      "title": "脱敏边界确认",
      "owner_id": "uuid",
      "deliverable": "脱敏字段清单",
      "due_time": "2026-05-29T23:59:59+08:00",
      "status": "doing"
    }
  ]
}
```

### 5.7 我的任务

#### GET `/me/tasks`

获取我参与、负责或待处理的任务。

权限：登录用户。

查询参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `tab` | string | `all`、`pending`、`doing`、`done` |
| `status` | string | 任务状态 |
| `keyword` | string | 搜索任务、角色、待处理动作 |

### 5.8 消息中心

#### GET `/messages`

消息列表。

权限：`message:view`。

查询参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `category` | string | `all`、`system`、`task`、`demand`、`team`、`reply` |
| `unread_only` | integer | 是否只看未读，0 否，1 是 |
| `keyword` | string | 搜索标题、摘要、关联对象 |

#### GET `/messages/unread-count`

获取未读消息数。

权限：`message:view`。

响应 `data`：

```json
{
  "total": 3,
  "by_category": {
    "task": 1,
    "demand": 1,
    "team": 1
  }
}
```

#### GET `/messages/{message_id}`

消息详情。读取详情时自动标记为已读。

权限：`message:view`。

#### POST `/messages/{message_id}/read`

标记单条消息已读。

权限：消息接收者。

#### POST `/messages/read-all`

全部标记为已读。

权限：登录用户。

#### DELETE `/messages/{message_id}`

删除消息。该操作为用户侧逻辑删除，不物理删除消息记录。

权限：消息接收者。

业务规则：

- 删除时更新消息接收关系中的 `is_deleted = 1`、`deleted_at`、`deleted_by`。
- 删除为用户侧逻辑删除，不影响系统审计。
- 消息对应业务不存在时，详情返回失效提示信息。

### 5.9 用户管理

#### GET `/admin/users`

用户列表。

权限：`user:manage`。

查询参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `keyword` | string | 搜索平台号、昵称、手机号 |
| `role` | string | 角色筛选 |
| `status` | string | 用户状态 |

#### GET `/admin/users/{user_id}`

用户详情。

权限：`user:manage`。

#### PATCH `/admin/users/{user_id}`

编辑用户信息和角色。

权限：`user:manage`。

请求体：

```json
{
  "nickname": "易然",
  "phone": "13800000000",
  "role": "operator",
  "position": "产品经理",
  "intro": "负责需求审核、转化工单和用户沟通。"
}
```

业务规则：

- 用户 UUID 不可修改。
- 至少保留一个超级管理员。
- 角色变更后权限立即生效。
- 写入系统日志。

#### POST `/admin/users/{user_id}/lock`

锁定用户。

权限：`user:manage`。

#### POST `/admin/users/{user_id}/unlock`

解锁用户。

权限：`user:manage`。

### 5.10 权限管理

#### GET `/admin/roles`

角色列表。

权限：`permission:manage`。

#### POST `/admin/roles`

创建角色。

权限：`permission:manage`。

请求体：

```json
{
  "name": "技术审核员",
  "code": "tech_reviewer",
  "permission_ids": ["task:view", "task:update", "log:view"]
}
```

业务规则：

- 角色名称和 `code` 唯一。
- 至少选择一个权限点。

#### PATCH `/admin/roles/{role_id}`

编辑角色权限。

权限：`permission:manage`。

#### GET `/admin/permissions`

权限点列表。

权限：`permission:manage`。

#### PUT `/admin/users/{user_id}/permissions`

为用户追加模板外手动权限。

权限：`permission:manage`。

请求体：

```json
{
  "manual_permission_ids": ["member:approve", "task:assign"],
  "reason": "临时支援任务协作管理。"
}
```

业务规则：

- 用户有效权限 = 角色模板权限 + 手动追加权限。
- 高敏权限追加必须写入系统日志。

### 5.11 系统日志

#### GET `/admin/system-logs`

系统日志列表。

权限：`log:view`。

查询参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `actor_id` | string | 操作人 |
| `action` | string | 操作类型 |
| `target_type` | string | 目标类型 |
| `target_id` | string | 目标 ID |
| `start_time` | string | 开始时间 |
| `end_time` | string | 结束时间 |

必须记录的关键操作：

- 登录失败、异常登录、用户锁定。
- 用户角色变更。
- 权限模板变更和手动授权。
- 需求转化、驳回、关联、归档。
- 任务核心信息编辑、状态变更、队长转移。
- 队伍申请通过或拒绝。

### 5.12 文件上传

#### POST `/files`

上传文件。

权限：登录用户。

请求格式：`multipart/form-data`。

字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `file` | file | 文件内容 |
| `biz_type` | string | `demand_attachment`、`reply_attachment`、`task_file`、`avatar` |

响应 `data`：

```json
{
  "file_id": "file_uuid",
  "filename": "补充说明.md",
  "size": 102400,
  "url": "/api/v1/files/file_uuid"
}
```

#### GET `/files/{file_id}`

下载或查看文件。

权限：根据业务对象校验。

#### DELETE `/files/{file_id}`

删除未绑定或本人上传的文件。该操作为逻辑删除，不物理删除文件记录。

权限：上传者或管理员。

业务规则：

- 更新文件记录 `is_deleted = 1`、`deleted_at`、`deleted_by`。
- 如文件已绑定业务对象，普通用户不可删除；管理员删除也必须写入系统日志。

## 6. P1 预留接口草案

P1 接口仅作为命名和边界预留，字段和业务规则需在 P1 PRD 稳定后单独评审。

### 6.1 AI 需求整理

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/ai/demands/draft` | 根据用户原始描述生成需求草稿 |
| POST | `/ai/demands/{demand_id}/summarize` | 对已有需求生成摘要、边界和待澄清问题 |

### 6.2 需求投票与排行榜

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/demands/{demand_id}/votes` | 为需求投票 |
| POST | `/demands/{demand_id}/votes/cancel` | 取消投票，逻辑保留投票记录 |
| GET | `/demands/rankings` | 获取需求排行榜 |

### 6.3 子任务

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/tasks/{task_id}/subtasks` | 子任务列表 |
| POST | `/tasks/{task_id}/subtasks` | 创建子任务 |
| PATCH | `/subtasks/{subtask_id}` | 编辑子任务 |
| POST | `/subtasks/{subtask_id}/claim` | 认领子任务 |

### 6.4 相似需求提示

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/demands/similar` | 提交需求前根据标题和描述提示相似需求 |

## 7. 关键业务规则

1. 后端是身份、权限、需求状态、任务状态、消息状态和审计日志的唯一事实来源。
2. 前端可做按钮级权限展示，但所有接口必须在后端完成鉴权和授权。
3. 需求转化任务后必须保留 `demand_id`，确保来源可追溯。
4. 已转化、已关联、已关闭、已归档需求不可再次转化。
5. 任务完成后禁止修改验收标准等核心字段，除非超级管理员执行带原因的特殊处理。
6. 队伍加入申请必须由队长或拥有 `member:approve` 权限的用户处理。
7. 所有管理端关键操作必须写入 `system_logs`。
8. 至少保留一个超级管理员账户。
9. 需求沟通消息允许撤回，使用 `is_revoked = 1` 标记，不物理删除记录。
10. 消息中心删除仅影响用户侧展示，使用逻辑删除标记，不删除业务事件和系统日志。
11. 所有删除类接口必须更新 `is_deleted`、`deleted_at`、`deleted_by`，不得直接物理删除数据。

## 8. 验收与测试场景

### 8.1 P0 闭环测试

| 场景 | 预期结果 |
| --- | --- |
| 注册、登录、刷新 Token、退出登录 | Token 策略正确，旧 refresh_token 失效 |
| 需求者提交需求 | 需求状态为 `pending_review`，运管收到待审核消息 |
| 运管发起沟通，需求者回复 | 双方消息可见，未读数正确 |
| 运管转化任务 | 生成任务，需求状态为 `converted`，需求者收到通知 |
| 共建者申请加入队伍 | 队长收到申请消息 |
| 队长通过申请 | 用户成为任务成员，队伍成员列表更新 |
| 成员提交进度 | 任务时间线更新，队伍成员可见 |
| 运管变更任务为待验收并完成 | 任务状态按规则流转，需求者收到消息 |
| 超管修改用户角色 | 权限立即生效，系统日志有记录 |
| 超管追加手动权限 | 有效权限更新，高敏权限写入日志 |

### 8.2 权限测试

| 场景 | 预期结果 |
| --- | --- |
| 未登录访问业务接口 | 返回 401 |
| 需求者调用需求转化接口 | 返回 403 |
| 非需求发布者回复需求 | 返回 403 |
| 非队长审批加入申请 | 返回 403，除非有 `member:approve` |
| 普通用户访问系统日志 | 返回 403 |

### 8.3 异常测试

| 场景 | 预期结果 |
| --- | --- |
| 重复转化同一需求 | 返回 409 `DEMAND_ALREADY_PROCESSED` |
| 上传附件超过限制 | 返回 413 或 422 |
| refresh_token 重放 | 返回 401 |
| 降权最后一个超级管理员 | 返回 409 |
| 两个运管同时处理同一需求 | 后提交方返回 409，并提示需求已被处理 |
| 消息关联对象已失效 | 消息详情提示“该内容已失效” |

# Demo 业务场景接口映射

## 1. 文档说明

本文档把 `demo/all-pages/` 中所有涉及后端接口的业务功能，映射到 `docs/API设计文档.md` 中已设计的 API。用途是给前端迁移 demo、后端实现接口、联调测试提供页面级索引。

约定：

- 页面路径均以 `demo/all-pages/` 为基准。
- API 路径均以 `/api/v1` 为前缀。
- “建议补充接口”表示当前 `API设计文档.md` 尚未定义，但 demo 页面存在对应业务动作。
- 导航跳转、Tab 切换、弹窗打开/关闭、复制链接、前端表单校验等纯前端行为不需要调用业务接口，除非表格中另有说明。

## 2. 全局公共能力

| 业务功能         | 使用接口                     | 触发页面/位置                            | 说明                                                         |
| ---------------- | ---------------------------- | ---------------------------------------- | ------------------------------------------------------------ |
| 当前登录用户信息 | `GET /me`                    | 所有登录后页面的头像卡片、昵称、角色展示 | 页面初始化时获取当前用户基础信息                             |
| 当前用户权限     | `GET /me/permissions`        | 工作台、管理页按钮显隐、详情页视角权限   | 前端用于菜单、按钮、视角切换的展示控制；后端接口仍需独立鉴权 |
| 未读消息数       | `GET /messages/unread-count` | 导航栏消息红点、工作台提醒               | 登录后全局拉取，可定时刷新                                   |
| 退出登录         | `POST /auth/logout`          | 头像卡片中的“退出登录”                   | 提交 `refresh_token`，服务端吊销登录态                       |
| 上传附件         | `POST /files`                | 需求提交、需求沟通、任务资源、头像       | 先上传文件拿到 `file_id`，再把 `file_id` 放入业务接口        |
| 查看/下载附件    | `GET /files/{file_id}`       | 需求详情、任务详情、沟通附件             | 按业务对象校验访问权限                                       |
| 删除附件         | `DELETE /files/{file_id}`    | 文件未绑定时的取消上传、管理删除         | 逻辑删除，更新 `is_deleted/deleted_at/deleted_by`            |

## 3. 页面级接口映射

### 3.1 `index.html` Demo 集合页

该页面主要是 demo 导航集合，不需要业务接口。

| 业务功能     | 使用接口 | 说明     |
| ------------ | -------- | -------- |
| 展示页面入口 | 无       | 静态导航 |

### 3.2 `login.html` 登录页

| 业务功能           | 使用接口              | 触发时机                  | 说明                                   |
| ------------------ | --------------------- | ------------------------- | -------------------------------------- |
| 登录               | `POST /auth/login`    | 点击“登录 OpenRD”提交表单 | 使用账户名/平台号和密码换取双 Token    |
| 登录后获取当前用户 | `GET /me`             | 登录成功后进入工作台前    | 可用于判断是否完成账号初始化、角色跳转 |
| 登录后获取权限     | `GET /me/permissions` | 登录成功后                | 用于构建工作台菜单和按钮权限           |

### 3.3 `register.html` 注册页

| 业务功能             | 使用接口                | 触发时机           | 说明                                                    |
| -------------------- | ----------------------- | ------------------ | ------------------------------------------------------- |
| 获取短信验证码       | `POST /auth/sms-code`   | 点击“获取验证码”   | `scene=register`                                        |
| 注册账号             | `POST /auth/register`   | 点击“注册”提交表单 | 提交昵称、账户名/平台号、密码、手机号、验证码、初始角色 |
| 注册后进入账号初始化 | `POST /auth/onboarding` | 不在本页调用       | 注册成功后跳转到账号初始化页完成                        |

### 3.4 `forgot-password.html` 忘记密码页

| 业务功能           | 使用接口                    | 触发时机         | 说明                                      |
| ------------------ | --------------------------- | ---------------- | ----------------------------------------- |
| 获取重置密码验证码 | `POST /auth/sms-code`       | 点击“获取验证码” | `scene=reset_password`                    |
| 重置密码           | `POST /auth/password/reset` | 点击“确认重置”   | 提交账户名/平台号、手机号、验证码、新密码 |

### 3.5 `account-onboarding.html` 账号初始化页

| 业务功能             | 使用接口                | 触发时机                       | 说明                                                         |
| -------------------- | ----------------------- | ------------------------------ | ------------------------------------------------------------ |
| 获取当前用户         | `GET /me`               | 页面初始化                     | 展示当前账号和初始化状态                                     |
| 保存初始化信息       | `POST /auth/onboarding` | 最后一步点击完成/下一步        | 保存身份、关注病种、能力标签、简介、地区等                   |
| 更新个人资料补充字段 | `PATCH /me/profile`     | 初始化信息需要同步到个人资料时 | 可与 `POST /auth/onboarding` 合并实现，也可由后端在 onboarding 内部更新 |

### 3.6 `home.html` 社区主页、任务大厅、需求大厅、提需求

| 业务功能           | 使用接口                   | 触发时机                             | 说明                                             |
| ------------------ | -------------------------- | ------------------------------------ | ------------------------------------------------ |
| 任务大厅列表       | `GET /tasks`               | 页面初始化、切换任务大厅、搜索、分页 | 支持 `keyword/status/team_status/page/page_size` |
| 需求大厅列表       | `GET /demands`             | 切换需求大厅、搜索、分页             | 用于公开/登录后可见的需求列表                    |
| 查看任务详情       | `GET /tasks/{task_id}`     | 点击任务“详情”进入详情页             | 本页通常只跳转，详情页再请求                     |
| 查看需求详情       | `GET /demands/{demand_id}` | 点击需求“详情”进入详情页             | 本页通常只跳转，详情页再请求                     |
| 提交需求前上传附件 | `POST /files`              | 选择附件后或提交前                   | `biz_type=demand_attachment`                     |
| 提交需求           | `POST /demands`            | “提交需求”表单提交                   | 提交标题、描述、联系方式、紧急程度、附件 ID      |
| 提交需求后消息触发 | 后端内部触发               | `POST /demands` 成功后               | 生成运管端待审核消息，不由前端单独调用           |

### 3.7 `workbench.html` 工作台

| 业务功能             | 使用接口                 | 触发时机        | 说明                                 |
| -------------------- | ------------------------ | --------------- | ------------------------------------ |
| 获取当前用户         | `GET /me`                | 页面初始化      | 判断角色：需求者、共建者、运管、超管 |
| 获取当前权限         | `GET /me/permissions`    | 页面初始化      | 控制功能磁贴                         |
| 工作台统计：我的需求 | `GET /me/demands`        | 需求者工作台    | 可取待审核、沟通中、已转任务数量     |
| 工作台统计：我的任务 | `GET /me/tasks`          | 共建者工作台    | 可取待处理、进行中、已完成数量       |
| 工作台统计：需求管理 | `GET /demands`           | 运管/超管工作台 | 可取待审核、沟通中等数量             |
| 工作台统计：任务管理 | `GET /tasks`             | 运管/超管工作台 | 可取解决中、招募中、已完成等数量     |
| 工作台统计：用户管理 | `GET /admin/users`       | 超管工作台      | 可取总用户、管理员数量               |
| 工作台统计：系统日志 | `GET /admin/system-logs` | 超管工作台      | 可取高风险事件、今日日志数量         |

### 3.8 `my-demands.html` 我的需求

| 业务功能     | 使用接口                   | 触发时机                                   | 说明                                                   |
| ------------ | -------------------------- | ------------------------------------------ | ------------------------------------------------------ |
| 我的需求列表 | `GET /me/demands`          | 页面初始化、Tab 切换、状态筛选、搜索、分页 | 支持 `status/keyword/page/page_size`                   |
| 我的需求统计 | `GET /me/demands`          | 页面初始化                                 | 可通过同一列表接口返回分页外统计，或前端按接口数据计算 |
| 查看需求详情 | `GET /demands/{demand_id}` | 点击“查看详情”跳转后                       | 详情页请求                                             |
| 查看关联任务 | `GET /tasks/{task_id}`     | 点击关联任务进入任务详情                   | 如列表已返回 `linked_task_id`，详情页再请求            |

### 3.9 `demand-detail.html` 需求详情

| 业务功能         | 使用接口                                              | 触发时机                | 说明                                                    |
| ---------------- | ----------------------------------------------------- | ----------------------- | ------------------------------------------------------- |
| 获取需求详情     | `GET /demands/{demand_id}`                            | 页面初始化              | 返回基础信息、状态、反馈、附件、时间线、沟通会话        |
| 查看联系方式     | `GET /demands/{demand_id}`                            | 点击“查看”              | 可由详情接口按权限返回脱敏/明文联系方式；无权限返回脱敏 |
| 上传沟通附件     | `POST /files`                                         | 发送沟通前选择附件      | `biz_type=reply_attachment`                             |
| 发送沟通消息     | `POST /demands/{demand_id}/replies`                   | 点击“发送消息/发送回复” | 产品经理询问或需求者回复                                |
| 撤回沟通消息     | `POST /demands/{demand_id}/replies/{reply_id}/revoke` | 消息右键“撤回”          | 使用 `is_revoked=1`，不物理删除                         |
| 转化任务         | `POST /demands/{demand_id}/convert`                   | 点击“生成任务工单”      | 提交任务标题、类型、优先级、范围、验收标准              |
| 关联已有类似需求 | `POST /demands/{demand_id}/link-similar`              | 选择类似需求/任务       | 当前需求变为 `linked`                                   |
| 查看转化后的任务 | `GET /tasks/{task_id}`                                | 转化成功后跳转任务详情  | 任务详情页请求                                          |
| 下载附件         | `GET /files/{file_id}`                                | 点击需求或沟通附件      | 按权限校验                                              |

### 3.10 `demand-management.html` 需求管理

| 业务功能         | 使用接口                                 | 触发时机                                           | 说明                                                         |
| ---------------- | ---------------------------------------- | -------------------------------------------------- | ------------------------------------------------------------ |
| 需求管理列表     | `GET /demands`                           | 页面初始化、搜索、审核状态筛选、转化状态筛选、分页 | 运管/超管使用                                                |
| 查看需求详情     | `GET /demands/{demand_id}`               | 点击“详情”                                         | 跳转详情页                                                   |
| 编辑需求处理信息 | 建议优先使用具体动作接口                 | 点击“保存修改”                                     | demo 是直接编辑状态；正式实现建议拆成转化、驳回、关联、归档等动作 |
| 转化需求         | `POST /demands/{demand_id}/convert`      | 保存时选择已转化并填写任务信息                     | 生成任务并关联需求                                           |
| 驳回需求         | `POST /demands/{demand_id}/reject`       | 保存时选择已驳回并填写理由                         | 当前 API 已支持，demo 需补驳回理由字段                       |
| 关联相似需求     | `POST /demands/{demand_id}/link-similar` | 保存时填写已有任务/需求                            | 当前需求关联到既有任务                                       |
| 归档需求         | `POST /demands/{demand_id}/archive`      | 保存时选择关闭/归档                                | 逻辑归档，不删除数据                                         |
| 普通字段编辑     | 建议补充：`PATCH /demands/{demand_id}`   | demo 中编辑标题、进度、反馈                        | 当前 API 文档没有通用需求编辑接口，如要保留该管理能力建议补充 |
| 导出需求         | 建议补充：`GET /demands/export`          | 点击“导出需求”                                     | 当前 API 文档没有导出接口                                    |

### 3.11 `task-management.html` 任务管理

| 业务功能         | 使用接口                                | 触发时机                                     | 说明                                       |
| ---------------- | --------------------------------------- | -------------------------------------------- | ------------------------------------------ |
| 任务管理列表     | `GET /tasks`                            | 页面初始化、搜索、状态筛选、团队筛选、分页   | 运管/超管使用                              |
| 查看任务详情     | `GET /tasks/{task_id}`                  | 点击“详情”                                   | 跳转详情页                                 |
| 编辑任务基础信息 | `PATCH /tasks/{task_id}`                | 编辑标题、任务类型、优先级、范围、验收标准等 | 当前任务详情和管理页都可复用               |
| 变更任务状态     | `POST /tasks/{task_id}/status`          | 修改任务状态并保存                           | 例如招募中、解决中、待验收、已完成、已关闭 |
| 提交任务进度     | `POST /tasks/{task_id}/progress`        | 修改进度或备注                               | 记录运营侧判断、阻塞点、下一步动作         |
| 转移队长         | `POST /tasks/{task_id}/leader/transfer` | 修改队长字段并保存                           | demo 中可编辑队长                          |
| 导出任务         | 建议补充：`GET /tasks/export`           | 点击“导出任务”                               | 当前 API 文档没有导出接口                  |

### 3.12 `my-tasks.html` 我的任务

| 业务功能     | 使用接口               | 触发时机                                   | 说明                                     |
| ------------ | ---------------------- | ------------------------------------------ | ---------------------------------------- |
| 我的任务列表 | `GET /me/tasks`        | 页面初始化、Tab 切换、状态筛选、搜索、分页 | 支持 `tab/status/keyword/page/page_size` |
| 我的任务统计 | `GET /me/tasks`        | 页面初始化                                 | 可通过同一列表接口返回统计，或前端计算   |
| 查看任务详情 | `GET /tasks/{task_id}` | 点击“查看详情”跳转后                       | 详情页请求                               |
| 同步最新状态 | `GET /me/tasks`        | 点击“同步”                                 | 重新拉取列表                             |

### 3.13 `task-detail.html` 任务详情

| 业务功能     | 使用接口                          | 触发时机                    | 说明                                                         |
| ------------ | --------------------------------- | --------------------------- | ------------------------------------------------------------ |
| 获取任务详情 | `GET /tasks/{task_id}`            | 页面初始化                  | 返回任务信息、状态、进度、来源需求、资源、附件、成员、里程碑 |
| 查看来源需求 | `GET /demands/{demand_id}`        | 点击“需求详情”跳转后        | 需求详情页请求                                               |
| 获取队伍详情 | `GET /tasks/{task_id}/team`       | 页面初始化或点击队伍详情    | 可由任务详情内嵌返回，也可单独请求                           |
| 提交协作更新 | `POST /tasks/{task_id}/progress`  | 点击“提交更新/提交协作更新” | 记录成员进度、说明、附件                                     |
| 编辑任务信息 | `PATCH /tasks/{task_id}`          | 队长点击“编辑”并保存        | 修改任务类型、优先级、范围、验收标准等                       |
| 更新项目资源 | `POST /tasks/{task_id}/resources` | 保存资源、附件、协作动作    | 维护资源链接、文件和待处理动作                               |
| 上传任务附件 | `POST /files`                     | 添加任务文件前              | `biz_type=task_file`                                         |
| 下载任务附件 | `GET /files/{file_id}`            | 点击附件                    | 按任务成员/管理权限校验                                      |

### 3.14 `team-detail.html` 队伍详情

| 业务功能     | 使用接口                                                     | 触发时机               | 说明                                                         |
| ------------ | ------------------------------------------------------------ | ---------------------- | ------------------------------------------------------------ |
| 获取队伍详情 | `GET /tasks/{task_id}/team`                                  | 页面初始化             | 返回队长、成员、申请、分工、协作阶段                         |
| 申请加入队伍 | `POST /tasks/{task_id}/join-applications`                    | 其他入口点击“加入队伍” | 本页主要处理申请，申请入口也可能在任务详情或大厅             |
| 通过加入申请 | `POST /tasks/{task_id}/join-applications/{application_id}/approve` | 队长点击“通过”         | 可附带职责 `duty`                                            |
| 拒绝加入申请 | `POST /tasks/{task_id}/join-applications/{application_id}/reject` | 队长点击“拒绝”         | 应填写拒绝理由                                               |
| 邀请成员     | `POST /tasks/{task_id}/members/invite`                       | 点击“邀请成员”并保存   | 提交平台号、建议角色、邀请说明、截止时间                     |
| 更新成员职责 | `PATCH /tasks/{task_id}/members/{member_id}`                 | 调整单个成员职责       | demo 当前没有单成员编辑弹窗，后续可接入                      |
| 转移队长     | `POST /tasks/{task_id}/leader/transfer`                      | 队长转移场景           | demo 描述中有队长转移逻辑                                    |
| 保存任务分工 | `PUT /tasks/{task_id}/assignments`                           | 点击“保存分工”         | 新增、删除、修改分工都通过整体保存；删除分工应逻辑删除或状态标记 |

### 3.15 `message-center.html` 消息中心

| 业务功能     | 使用接口                                             | 触发时机                             | 说明                                               |
| ------------ | ---------------------------------------------------- | ------------------------------------ | -------------------------------------------------- |
| 消息列表     | `GET /messages`                                      | 页面初始化、分类切换、搜索、只看未读 | 支持 `category/unread_only/keyword/page/page_size` |
| 未读统计     | `GET /messages/unread-count`                         | 页面初始化、处理消息后刷新           | 展示总未读和分类未读                               |
| 消息详情     | `GET /messages/{message_id}`                         | 点击“详情”                           | 读取详情时自动标记为已读                           |
| 标记单条已读 | `POST /messages/{message_id}/read`                   | 点击“已读”                           | 更新 `read_status=1`                               |
| 全部已读     | `POST /messages/read-all`                            | 点击“全部已读”                       | 当前用户全部消息设为已读                           |
| 删除消息     | `DELETE /messages/{message_id}`                      | 点击“删除”                           | 用户侧逻辑删除，不物理删除                         |
| 跳转关联对象 | `GET /demands/{demand_id}` 或 `GET /tasks/{task_id}` | 点击推荐操作后进入业务详情           | 根据 `target_type/target_id` 判断                  |

### 3.16 `profile.html` 个人信息

| 业务功能     | 使用接口             | 触发时机                     | 说明                                                     |
| ------------ | -------------------- | ---------------------------- | -------------------------------------------------------- |
| 获取个人资料 | `GET /me`            | 页面初始化                   | 展示平台号、昵称、手机号、身份、职业、地区、标签、简介   |
| 保存个人资料 | `PATCH /me/profile`  | 点击“保存资料”               | 更新昵称、手机号、职业、地区、标签、简介等               |
| 上传头像     | `POST /files`        | 选择头像文件时               | 当前 demo 是文字头像；真实文件头像使用 `biz_type=avatar` |
| 修改密码     | `PATCH /me/password` | 如果个人中心增加修改密码入口 | 当前 demo 页面未展示，但 API 已有                        |

### 3.17 `user-management.html` 用户管理

| 业务功能     | 使用接口                             | 触发时机               | 说明                                      |
| ------------ | ------------------------------------ | ---------------------- | ----------------------------------------- |
| 用户列表     | `GET /admin/users`                   | 页面初始化、搜索、分页 | 支持 `keyword/role/status/page/page_size` |
| 用户详情     | `GET /admin/users/{user_id}`         | 点击编辑前             | 拉取完整用户信息                          |
| 保存用户信息 | `PATCH /admin/users/{user_id}`       | 编辑弹窗点击“保存修改” | 修改昵称、手机号、角色、岗位、简介等      |
| 锁定用户     | `POST /admin/users/{user_id}/lock`   | 用户异常或安全处理     | demo 工作台描述有禁用/锁定场景            |
| 解锁用户     | `POST /admin/users/{user_id}/unlock` | 解除锁定               | 与锁定配套                                |
| 导出 CSV     | 建议补充：`GET /admin/users/export`  | 点击“导出 CSV”         | 当前 API 文档没有导出接口                 |

### 3.18 `permission-management.html` 权限管理

| 业务功能              | 使用接口                                 | 触发时机                         | 说明                                                |
| --------------------- | ---------------------------------------- | -------------------------------- | --------------------------------------------------- |
| 角色列表              | `GET /admin/roles`                       | 页面初始化                       | 获取角色模板                                        |
| 权限点列表            | `GET /admin/permissions`                 | 页面初始化                       | 获取可配置权限点                                    |
| 用户列表/成员权限列表 | `GET /admin/users`                       | 页面初始化、搜索、角色筛选、分页 | 可扩展返回用户有效权限摘要                          |
| 编辑角色模板          | `PATCH /admin/roles/{role_id}`           | 修改角色模板权限                 | demo 主要展示成员追加权限，角色模板接口用于模板维护 |
| 创建新角色            | `POST /admin/roles`                      | 添加技术审核员等新角色           | PRD 场景中包含创建新角色                            |
| 追加成员手动权限      | `PUT /admin/users/{user_id}/permissions` | 编辑成员权限并保存               | 保存 `manual_permission_ids`                        |
| 变更用户角色模板      | `PATCH /admin/users/{user_id}`           | 弹窗中修改角色模板               | 角色变化后权限立即生效                              |

### 3.19 `system-log.html` 系统日志

| 业务功能     | 使用接口                                  | 触发时机                                             | 说明                                                         |
| ------------ | ----------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------ |
| 系统日志列表 | `GET /admin/system-logs`                  | 页面初始化、模块筛选、风险筛选、结果筛选、搜索、分页 | 支持 `actor_id/action/target_type/target_id/start_time/end_time`，建议补充 `keyword/module/risk/result` |
| 日志详情     | `GET /admin/system-logs`                  | 点击单条“详情”                                       | 当前 API 只有列表，可用列表返回详情字段，或建议补充详情接口  |
| 导出系统日志 | 建议补充：`GET /admin/system-logs/export` | 点击导出                                             | 当前 API 文档没有导出接口                                    |

## 4. 按核心业务流汇总

### 4.1 注册登录与账号初始化

| 业务链路 | 接口顺序                                                     |
| -------- | ------------------------------------------------------------ |
| 注册     | `POST /auth/sms-code` -> `POST /auth/register` -> `POST /auth/onboarding` |
| 登录     | `POST /auth/login` -> `GET /me` -> `GET /me/permissions` -> `GET /messages/unread-count` |
| 忘记密码 | `POST /auth/sms-code` -> `POST /auth/password/reset`         |
| 退出登录 | `POST /auth/logout`                                          |

### 4.2 需求提交到转化任务

| 业务链路         | 接口顺序                                                     |
| ---------------- | ------------------------------------------------------------ |
| 需求者提交需求   | `POST /files` -> `POST /demands` -> `GET /me/demands`        |
| 运管查看并沟通   | `GET /demands` -> `GET /demands/{demand_id}` -> `POST /demands/{demand_id}/replies` |
| 需求者补充材料   | `POST /files` -> `POST /demands/{demand_id}/replies`         |
| 运管转化任务     | `POST /demands/{demand_id}/convert` -> `GET /tasks/{task_id}` |
| 运管关联已有任务 | `POST /demands/{demand_id}/link-similar`                     |
| 运管驳回/归档    | `POST /demands/{demand_id}/reject` 或 `POST /demands/{demand_id}/archive` |

### 4.3 任务协作

| 业务链路     | 接口顺序                                                     |
| ------------ | ------------------------------------------------------------ |
| 浏览任务大厅 | `GET /tasks` -> `GET /tasks/{task_id}`                       |
| 加入队伍     | `POST /tasks/{task_id}/join-applications`                    |
| 队长审核申请 | `GET /tasks/{task_id}/team` -> `POST /tasks/{task_id}/join-applications/{application_id}/approve` 或 `POST /tasks/{task_id}/join-applications/{application_id}/reject` |
| 队长邀请成员 | `POST /tasks/{task_id}/members/invite`                       |
| 调整分工     | `PUT /tasks/{task_id}/assignments`                           |
| 提交进度     | `POST /tasks/{task_id}/progress`                             |
| 维护资源     | `POST /files` -> `POST /tasks/{task_id}/resources`           |
| 任务管理     | `PATCH /tasks/{task_id}` -> `POST /tasks/{task_id}/status`   |

### 4.4 管理治理

| 业务链路      | 接口顺序                                                     |
| ------------- | ------------------------------------------------------------ |
| 用户管理      | `GET /admin/users` -> `GET /admin/users/{user_id}` -> `PATCH /admin/users/{user_id}` |
| 锁定/解锁用户 | `POST /admin/users/{user_id}/lock` 或 `POST /admin/users/{user_id}/unlock` |
| 权限管理      | `GET /admin/roles` + `GET /admin/permissions` -> `PUT /admin/users/{user_id}/permissions` |
| 创建角色      | `POST /admin/roles`                                          |
| 修改角色权限  | `PATCH /admin/roles/{role_id}`                               |
| 查看系统日志  | `GET /admin/system-logs`                                     |

## 5. 当前建议补充的 API

以下能力在 demo 中出现，但当前 `API设计文档.md` 尚未定义成正式接口。建议后续补充。

| 建议接口                          | 对应页面                 | 用途                                       | 优先级            |
| --------------------------------- | ------------------------ | ------------------------------------------ | ----------------- |
| `PATCH /demands/{demand_id}`      | `demand-management.html` | 管理端编辑需求标题、反馈、进度等非动作字段 | P0                |
| `GET /demands/export`             | `demand-management.html` | 导出需求列表                               | P1 或管理增强     |
| `GET /tasks/export`               | `task-management.html`   | 导出任务列表                               | P1 或管理增强     |
| `GET /admin/users/export`         | `user-management.html`   | 导出用户 CSV                               | P1 或管理增强     |
| `GET /admin/system-logs/{log_id}` | `system-log.html`        | 查看单条日志详情                           | P0                |
| `GET /admin/system-logs/export`   | `system-log.html`        | 导出系统日志                               | P1 或安全审计增强 |

