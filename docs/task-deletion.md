# 超级管理员删除与恢复任务

任务管理页为超级管理员显示删除按钮和“查看已删除任务”筛选。
删除需填写 1～500 字原因；已删除列表可查看原因、删除人、时间并恢复。
后端直接校验 super_admin 角色，task:manage 等手动授权不能获得删除权限。

## 发布

先在目标环境备份数据库并执行现有迁移流程：

```sh
cd backend
uv run alembic upgrade head
```

本次迁移为 `l2f3a4b5c6d7`，仅向 tasks 表新增可空 delete_reason 字段。
随后发布后端与前端。旧任务无需额外数据修复。
回退数据库前先回退应用；降级迁移会移除 delete_reason 列。

## 接口与行为

- POST /api/v1/tasks/{id}/delete，JSON：{"reason":"重复项目"}
- POST /api/v1/tasks/{id}/restore
- GET /api/v1/tasks?deleted=true，仅超级管理员可访问，返回删除信息。
- 普通任务列表和详情不返回已删除任务。重复删除或恢复返回 409。
- 删除和恢复与系统日志在同一事务内保存，日志保留删除原因。
- 保留任务状态、阶段、成员、进度与附件，不物理删除关联内容。
- 原始需求保持原状态和关联，不因删除自动重新立项；需求详情标注关联任务已删除。
- 普通用户不能通过已删除任务的团队、进度或附件入口继续访问。
- 恢复后恢复原业务状态与访问，不自动变成招募中。

## 验证

无需 PostgreSQL 的隔离测试（SQLite 内存库）：

```sh
uv run pytest --confcutdir=tests/isolated tests/isolated/test_task_deletion.py -q
```

覆盖删除/恢复、角色限制、原因校验、历史保留、列表/详情/团队/附件隔离、
个人统计和审计失败回滚。SQLite 不验证 PostgreSQL 行锁和并发语义。

在已迁移的专用 PostgreSQL 测试库中运行现有 tests/test_stats.py 及相关回归测试。
前端验证：`npm run build`。
