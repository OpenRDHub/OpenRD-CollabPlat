# Demo 业务场景接口映射

## 1. 文档说明

本文档把 `demo/all-pages/` 中所有涉及后端接口的业务功能，映射到 `docs/API设计文档.md` 中已设计的 API。用途是给前端迁移 demo、后端实现接口、联调测试提供页面级索引。

约定：

- 页面路径均以 `demo/all-pages/` 为基准。
- API 路径均以 `/api/v1` 为前缀。
- “建议补充接口”表示当前 `API设计文档.md` 尚未定义，但 demo 页面存在对应业务动作。
- 导航跳转、Tab 切换、弹窗打开/关闭、复制链接、前端表单校验等纯前端行为不需要调用业务接口，除非表格中另有说明。

## 2. 全局公共能力

| 业务功能 | 使用接口 | 触发页面/位置 | 说明 |
| --- | --- | --- | --- |
| 当前登录用户信息 | `GET /me` | 所有登录后页面的头像卡片、昵称、角色展示 | 页面初始化时获取当前用户基础信息 |
| 当前用户权限 | `GET /me/permissions` | 工作台、管理页按钮显隐、详情页视角权限 | 前端用于菜单、按钮、视角切换的展示控制；后端接口仍需独立鉴权 |
| 未读消息数 | `GET /messages/unread-count` | 导航栏消息红点、工作台提醒 | 登录后全局拉取，可定时刷新 |
| 退出登录 | `POST /auth/logout` | 头像卡片中的“退出登录” | 提交 `refresh_token`，服务端吊销登录态 |
| 上传附件 | `POST /files` | 需求提交、需求沟通、任务资源、头像 | 先上传文件拿到 `file_id`，再把 `file_id` 放入业务接口 |
| 查看/下载附件 | `GET /files/{file_id}` | 需求详情、任务详情、沟通附件 | 按业务对象校验访问权限 |
| 删除附件 | `DELETE /files/{file_id}` | 文件未绑定时的取消上传、管理删除 | 逻辑删除，更新 `is_deleted/deleted_at/deleted_by` |

## 3. 页面级接口映射

### 3.1 `index.html` Demo 集合页

该页面主要是 demo 导航集合，不需要业务接口。

| 业务功能 | 使用接口 | 说明 |
| --- | --- | --- |
| 展示页面入口 | 无 | 静态导航 |

### 3.2 `login.html` 登录页

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 登录 | `POST /auth/login` | 点击“登录 OpenRD”提交表单 | 使用账户名/平台号和密码换取双 Token |
| 登录后获取当前用户 | `GET /me` | 登录成功后进入工作台前 | 可用于判断是否完成账号初始化、角色跳转 |
| 登录后获取权限 | `GET /me/permissions` | 登录成功后 | 用于构建工作台菜单和按钮权限 |

### 3.3 `register.html` 注册页

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 获取短信验证码 | `POST /auth/sms-code` | 点击“获取验证码” | `scene=register` |
| 注册账号 | `POST /auth/register` | 点击“注册”提交表单 | 提交昵称、账户名/平台号、密码、手机号、验证码、初始角色 |
| 注册后进入账号初始化 | `POST /auth/onboarding` | 不在本页调用 | 注册成功后跳转到账号初始化页完成 |

### 3.4 `forgot-password.html` 忘记密码页

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 获取重置密码验证码 | `POST /auth/sms-code` | 点击“获取验证码” | `scene=reset_password` |
| 重置密码 | `POST /auth/password/reset` | 点击“确认重置” | 提交账户名/平台号、手机号、验证码、新密码 |

### 3.5 `account-onboarding.html` 账号初始化页

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 获取当前用户 | `GET /me` | 页面初始化 | 展示当前账号和初始化状态 |
| 保存初始化信息 | `POST /auth/onboarding` | 最后一步点击完成/下一步 | 保存身份、关注病种、能力标签、简介、地区等 |
| 更新个人资料补充字段 | `PATCH /me/profile` | 初始化信息需要同步到个人资料时 | 可与 `POST /auth/onboarding` 合并实现，也可由后端在 onboarding 内部更新 |

### 3.6 `home.html` 社区主页、任务大厅、需求大厅、提需求

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 任务大厅列表 | `GET /tasks` | 页面初始化、切换任务大厅、搜索、分页 | 支持 `keyword/status/team_status/page/page_size` |
| 需求大厅列表 | `GET /demands` | 切换需求大厅、搜索、分页 | 用于公开/登录后可见的需求列表 |
| 查看任务详情 | `GET /tasks/{task_id}` | 点击任务“详情”进入详情页 | 本页通常只跳转，详情页再请求 |
| 查看需求详情 | `GET /demands/{demand_id}` | 点击需求“详情”进入详情页 | 本页通常只跳转，详情页再请求 |
| 提交需求前上传附件 | `POST /files` | 选择附件后或提交前 | `biz_type=demand_attachment` |
| 提交需求 | `POST /demands` | “提交需求”表单提交 | 提交标题、描述、联系方式、紧急程度、附件 ID |
| 提交需求后消息触发 | 后端内部触发 | `POST /demands` 成功后 | 生成运管端待审核消息，不由前端单独调用 |

### 3.7 `workbench.html` 工作台

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 获取当前用户 | `GET /me` | 页面初始化 | 判断角色：需求者、共建者、运管、超管 |
| 获取当前权限 | `GET /me/permissions` | 页面初始化 | 控制功能磁贴 |
| 工作台统计：我的需求 | `GET /me/demands` | 需求者工作台 | 可取待审核、沟通中、已转任务数量 |
| 工作台统计：我的任务 | `GET /me/tasks` | 共建者工作台 | 可取待处理、进行中、已完成数量 |
| 工作台统计：需求管理 | `GET /demands` | 运管/超管工作台 | 可取待审核、沟通中等数量 |
| 工作台统计：任务管理 | `GET /tasks` | 运管/超管工作台 | 可取解决中、招募中、已完成等数量 |
| 工作台统计：用户管理 | `GET /admin/users` | 超管工作台 | 可取总用户、管理员数量 |
| 工作台统计：系统日志 | `GET /admin/system-logs` | 超管工作台 | 可取高风险事件、今日日志数量 |

### 3.8 `my-demands.html` 我的需求

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 我的需求列表 | `GET /me/demands` | 页面初始化、Tab 切换、状态筛选、搜索、分页 | 支持 `status/keyword/page/page_size` |
| 我的需求统计 | `GET /me/demands` | 页面初始化 | 可通过同一列表接口返回分页外统计，或前端按接口数据计算 |
| 查看需求详情 | `GET /demands/{demand_id}` | 点击“查看详情”跳转后 | 详情页请求 |
| 查看关联任务 | `GET /tasks/{task_id}` | 点击关联任务进入任务详情 | 如列表已返回 `linked_task_id`，详情页再请求 |

### 3.9 `demand-detail.html` 需求详情

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 获取需求详情 | `GET /demands/{demand_id}` | 页面初始化 | 返回基础信息、状态、反馈、附件、时间线、沟通会话 |
| 查看联系方式 | `GET /demands/{demand_id}` | 点击“查看” | 可由详情接口按权限返回脱敏/明文联系方式；无权限返回脱敏 |
| 上传沟通附件 | `POST /files` | 发送沟通前选择附件 | `biz_type=reply_attachment` |
| 发送沟通消息 | `POST /demands/{demand_id}/replies` | 点击“发送消息/发送回复” | 产品经理询问或需求者回复 |
| 撤回沟通消息 | `POST /demands/{demand_id}/replies/{reply_id}/revoke` | 消息右键“撤回” | 使用 `is_revoked=1`，不物理删除 |
| 转化任务 | `POST /demands/{demand_id}/convert` | 点击“生成任务工单” | 提交任务标题、类型、优先级、范围、验收标准 |
| 关联已有类似需求 | `POST /demands/{demand_id}/link-similar` | 选择类似需求/任务 | 当前需求变为 `linked` |
| 查看转化后的任务 | `GET /tasks/{task_id}` | 转化成功后跳转任务详情 | 任务详情页请求 |
| 下载附件 | `GET /files/{file_id}` | 点击需求或沟通附件 | 按权限校验 |

### 3.10 `demand-management.html` 需求管理

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 需求管理列表 | `GET /demands` | 页面初始化、搜索、审核状态筛选、转化状态筛选、分页 | 运管/超管使用 |
| 查看需求详情 | `GET /demands/{demand_id}` | 点击“详情” | 跳转详情页 |
| 编辑需求处理信息 | 建议优先使用具体动作接口 | 点击“保存修改” | demo 是直接编辑状态；正式实现建议拆成转化、驳回、关联、归档等动作 |
| 转化需求 | `POST /demands/{demand_id}/convert` | 保存时选择已转化并填写任务信息 | 生成任务并关联需求 |
| 驳回需求 | `POST /demands/{demand_id}/reject` | 保存时选择已驳回并填写理由 | 当前 API 已支持，demo 需补驳回理由字段 |
| 关联相似需求 | `POST /demands/{demand_id}/link-similar` | 保存时填写已有任务/需求 | 当前需求关联到既有任务 |
| 归档需求 | `POST /demands/{demand_id}/archive` | 保存时选择关闭/归档 | 逻辑归档，不删除数据 |
| 普通字段编辑 | 建议补充：`PATCH /demands/{demand_id}` | demo 中编辑标题、进度、反馈 | 当前 API 文档没有通用需求编辑接口，如要保留该管理能力建议补充 |
| 导出需求 | 建议补充：`GET /demands/export` | 点击“导出需求” | 当前 API 文档没有导出接口 |

### 3.11 `task-management.html` 任务管理

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 任务管理列表 | `GET /tasks` | 页面初始化、搜索、状态筛选、团队筛选、分页 | 运管/超管使用 |
| 查看任务详情 | `GET /tasks/{task_id}` | 点击“详情” | 跳转详情页 |
| 编辑任务基础信息 | `PATCH /tasks/{task_id}` | 编辑标题、任务类型、优先级、范围、验收标准等 | 当前任务详情和管理页都可复用 |
| 变更任务状态 | `POST /tasks/{task_id}/status` | 修改任务状态并保存 | 例如招募中、解决中、待验收、已完成、已关闭 |
| 提交任务进度 | `POST /tasks/{task_id}/progress` | 修改进度或备注 | 记录运营侧判断、阻塞点、下一步动作 |
| 转移队长 | `POST /tasks/{task_id}/leader/transfer` | 修改队长字段并保存 | demo 中可编辑队长 |
| 导出任务 | 建议补充：`GET /tasks/export` | 点击“导出任务” | 当前 API 文档没有导出接口 |

### 3.12 `my-tasks.html` 我的任务

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 我的任务列表 | `GET /me/tasks` | 页面初始化、Tab 切换、状态筛选、搜索、分页 | 支持 `tab/status/keyword/page/page_size` |
| 我的任务统计 | `GET /me/tasks` | 页面初始化 | 可通过同一列表接口返回统计，或前端计算 |
| 查看任务详情 | `GET /tasks/{task_id}` | 点击“查看详情”跳转后 | 详情页请求 |
| 同步最新状态 | `GET /me/tasks` | 点击“同步” | 重新拉取列表 |

### 3.13 `task-detail.html` 任务详情

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 获取任务详情 | `GET /tasks/{task_id}` | 页面初始化 | 返回任务信息、状态、进度、来源需求、资源、附件、成员、里程碑 |
| 查看来源需求 | `GET /demands/{demand_id}` | 点击“需求详情”跳转后 | 需求详情页请求 |
| 获取队伍详情 | `GET /tasks/{task_id}/team` | 页面初始化或点击队伍详情 | 可由任务详情内嵌返回，也可单独请求 |
| 提交协作更新 | `POST /tasks/{task_id}/progress` | 点击“提交更新/提交协作更新” | 记录成员进度、说明、附件 |
| 编辑任务信息 | `PATCH /tasks/{task_id}` | 队长点击“编辑”并保存 | 修改任务类型、优先级、范围、验收标准等 |
| 更新项目资源 | `POST /tasks/{task_id}/resources` | 保存资源、附件、协作动作 | 维护资源链接、文件和待处理动作 |
| 上传任务附件 | `POST /files` | 添加任务文件前 | `biz_type=task_file` |
| 下载任务附件 | `GET /files/{file_id}` | 点击附件 | 按任务成员/管理权限校验 |

### 3.14 `team-detail.html` 队伍详情

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 获取队伍详情 | `GET /tasks/{task_id}/team` | 页面初始化 | 返回队长、成员、申请、分工、协作阶段 |
| 申请加入队伍 | `POST /tasks/{task_id}/join-applications` | 其他入口点击“加入队伍” | 本页主要处理申请，申请入口也可能在任务详情或大厅 |
| 通过加入申请 | `POST /tasks/{task_id}/join-applications/{application_id}/approve` | 队长点击“通过” | 可附带职责 `duty` |
| 拒绝加入申请 | `POST /tasks/{task_id}/join-applications/{application_id}/reject` | 队长点击“拒绝” | 应填写拒绝理由 |
| 邀请成员 | `POST /tasks/{task_id}/members/invite` | 点击“邀请成员”并保存 | 提交平台号、建议角色、邀请说明、截止时间 |
| 更新成员职责 | `PATCH /tasks/{task_id}/members/{member_id}` | 调整单个成员职责 | demo 当前没有单成员编辑弹窗，后续可接入 |
| 转移队长 | `POST /tasks/{task_id}/leader/transfer` | 队长转移场景 | demo 描述中有队长转移逻辑 |
| 保存任务分工 | `PUT /tasks/{task_id}/assignments` | 点击“保存分工” | 新增、删除、修改分工都通过整体保存；删除分工应逻辑删除或状态标记 |

### 3.15 `message-center.html` 消息中心

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 消息列表 | `GET /messages` | 页面初始化、分类切换、搜索、只看未读 | 支持 `category/unread_only/keyword/page/page_size` |
| 未读统计 | `GET /messages/unread-count` | 页面初始化、处理消息后刷新 | 展示总未读和分类未读 |
| 消息详情 | `GET /messages/{message_id}` | 点击“详情” | 读取详情时自动标记为已读 |
| 标记单条已读 | `POST /messages/{message_id}/read` | 点击“已读” | 更新 `read_status=1` |
| 全部已读 | `POST /messages/read-all` | 点击“全部已读” | 当前用户全部消息设为已读 |
| 删除消息 | `DELETE /messages/{message_id}` | 点击“删除” | 用户侧逻辑删除，不物理删除 |
| 跳转关联对象 | `GET /demands/{demand_id}` 或 `GET /tasks/{task_id}` | 点击推荐操作后进入业务详情 | 根据 `target_type/target_id` 判断 |

### 3.16 `profile.html` 个人信息

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 获取个人资料 | `GET /me` | 页面初始化 | 展示平台号、昵称、手机号、身份、职业、地区、标签、简介 |
| 保存个人资料 | `PATCH /me/profile` | 点击“保存资料” | 更新昵称、手机号、职业、地区、标签、简介等 |
| 上传头像 | `POST /files` | 选择头像文件时 | 当前 demo 是文字头像；真实文件头像使用 `biz_type=avatar` |
| 修改密码 | `PATCH /me/password` | 如果个人中心增加修改密码入口 | 当前 demo 页面未展示，但 API 已有 |

### 3.17 `user-management.html` 用户管理

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 用户列表 | `GET /admin/users` | 页面初始化、搜索、分页 | 支持 `keyword/role/status/page/page_size` |
| 用户详情 | `GET /admin/users/{user_id}` | 点击编辑前 | 拉取完整用户信息 |
| 保存用户信息 | `PATCH /admin/users/{user_id}` | 编辑弹窗点击“保存修改” | 修改昵称、手机号、角色、岗位、简介等 |
| 锁定用户 | `POST /admin/users/{user_id}/lock` | 用户异常或安全处理 | demo 工作台描述有禁用/锁定场景 |
| 解锁用户 | `POST /admin/users/{user_id}/unlock` | 解除锁定 | 与锁定配套 |
| 导出 CSV | 建议补充：`GET /admin/users/export` | 点击“导出 CSV” | 当前 API 文档没有导出接口 |

### 3.18 `permission-management.html` 权限管理

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 角色列表 | `GET /admin/roles` | 页面初始化 | 获取角色模板 |
| 权限点列表 | `GET /admin/permissions` | 页面初始化 | 获取可配置权限点 |
| 用户列表/成员权限列表 | `GET /admin/users` | 页面初始化、搜索、角色筛选、分页 | 可扩展返回用户有效权限摘要 |
| 编辑角色模板 | `PATCH /admin/roles/{role_id}` | 修改角色模板权限 | demo 主要展示成员追加权限，角色模板接口用于模板维护 |
| 创建新角色 | `POST /admin/roles` | 添加技术审核员等新角色 | PRD 场景中包含创建新角色 |
| 追加成员手动权限 | `PUT /admin/users/{user_id}/permissions` | 编辑成员权限并保存 | 保存 `manual_permission_ids` |
| 变更用户角色模板 | `PATCH /admin/users/{user_id}` | 弹窗中修改角色模板 | 角色变化后权限立即生效 |

### 3.19 `system-log.html` 系统日志

| 业务功能 | 使用接口 | 触发时机 | 说明 |
| --- | --- | --- | --- |
| 系统日志列表 | `GET /admin/system-logs` | 页面初始化、模块筛选、风险筛选、结果筛选、搜索、分页 | 支持 `actor_id/action/target_type/target_id/start_time/end_time`，建议补充 `keyword/module/risk/result` |
| 日志详情 | `GET /admin/system-logs` | 点击单条“详情” | 当前 API 只有列表，可用列表返回详情字段，或建议补充详情接口 |
| 导出系统日志 | 建议补充：`GET /admin/system-logs/export` | 点击导出 | 当前 API 文档没有导出接口 |

## 4. 按核心业务流汇总

### 4.1 注册登录与账号初始化

| 业务链路 | 接口顺序 |
| --- | --- |
| 注册 | `POST /auth/sms-code` -> `POST /auth/register` -> `POST /auth/onboarding` |
| 登录 | `POST /auth/login` -> `GET /me` -> `GET /me/permissions` -> `GET /messages/unread-count` |
| 忘记密码 | `POST /auth/sms-code` -> `POST /auth/password/reset` |
| 退出登录 | `POST /auth/logout` |

### 4.2 需求提交到转化任务

| 业务链路 | 接口顺序 |
| --- | --- |
| 需求者提交需求 | `POST /files` -> `POST /demands` -> `GET /me/demands` |
| 运管查看并沟通 | `GET /demands` -> `GET /demands/{demand_id}` -> `POST /demands/{demand_id}/replies` |
| 需求者补充材料 | `POST /files` -> `POST /demands/{demand_id}/replies` |
| 运管转化任务 | `POST /demands/{demand_id}/convert` -> `GET /tasks/{task_id}` |
| 运管关联已有任务 | `POST /demands/{demand_id}/link-similar` |
| 运管驳回/归档 | `POST /demands/{demand_id}/reject` 或 `POST /demands/{demand_id}/archive` |

### 4.3 任务协作

| 业务链路 | 接口顺序 |
| --- | --- |
| 浏览任务大厅 | `GET /tasks` -> `GET /tasks/{task_id}` |
| 加入队伍 | `POST /tasks/{task_id}/join-applications` |
| 队长审核申请 | `GET /tasks/{task_id}/team` -> `POST /tasks/{task_id}/join-applications/{application_id}/approve` 或 `POST /tasks/{task_id}/join-applications/{application_id}/reject` |
| 队长邀请成员 | `POST /tasks/{task_id}/members/invite` |
| 调整分工 | `PUT /tasks/{task_id}/assignments` |
| 提交进度 | `POST /tasks/{task_id}/progress` |
| 维护资源 | `POST /files` -> `POST /tasks/{task_id}/resources` |
| 任务管理 | `PATCH /tasks/{task_id}` -> `POST /tasks/{task_id}/status` |

### 4.4 管理治理

| 业务链路 | 接口顺序 |
| --- | --- |
| 用户管理 | `GET /admin/users` -> `GET /admin/users/{user_id}` -> `PATCH /admin/users/{user_id}` |
| 锁定/解锁用户 | `POST /admin/users/{user_id}/lock` 或 `POST /admin/users/{user_id}/unlock` |
| 权限管理 | `GET /admin/roles` + `GET /admin/permissions` -> `PUT /admin/users/{user_id}/permissions` |
| 创建角色 | `POST /admin/roles` |
| 修改角色权限 | `PATCH /admin/roles/{role_id}` |
| 查看系统日志 | `GET /admin/system-logs` |

## 5. 当前建议补充的 API

以下能力在 demo 中出现，但当前 `API设计文档.md` 尚未定义成正式接口。建议后续补充。

| 建议接口 | 对应页面 | 用途 | 优先级 |
| --- | --- | --- | --- |
| `PATCH /demands/{demand_id}` | `demand-management.html` | 管理端编辑需求标题、反馈、进度等非动作字段 | P0 |
| `GET /demands/export` | `demand-management.html` | 导出需求列表 | P1 或管理增强 |
| `GET /tasks/export` | `task-management.html` | 导出任务列表 | P1 或管理增强 |
| `GET /admin/users/export` | `user-management.html` | 导出用户 CSV | P1 或管理增强 |
| `GET /admin/system-logs/{log_id}` | `system-log.html` | 查看单条日志详情 | P0 |
| `GET /admin/system-logs/export` | `system-log.html` | 导出系统日志 | P1 或安全审计增强 |

