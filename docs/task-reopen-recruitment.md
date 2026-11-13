# 重新开放任务招募

仅增加 `in_progress → recruiting`；团队状态同步为 `forming`。队长、负责人或拥有最终 `task:status` 权限的用户可操作，普通成员无权回退。详情页的状态变更和管理后台均提供入口。

回退原因去除首尾空白后须为 1–500 个字符。成员、分工、申请、项目阶段、进度历史、附件及关联需求均保留。任务状态和 `task.reopen_recruitment` 审计记录在同一事务中提交；日志含操作者、角色、原因及前后任务/团队状态。状态接口锁定任务行后进行权限和流转检查。

回退后可提交新的加入申请。是否在审批成员后继续保持招募，属于 PR #73（https://github.com/OpenRDHub/OpenRD-CollabPlat/pull/73）的独立改动；本 PR 不复制它的审批逻辑。PR #71 合并时应保留新增的 `in_progress → recruiting` 分支。

不自动回退历史任务，不开放 `team_ready`、待验收、已完成或已关闭到招募中的流转。

## 验证

本地隔离测试：

```sh
python -m pytest --confcutdir=tests/isolated tests/isolated/test_task_reopen_recruitment.py -q
```

该文件默认使用内存 SQLite；设置 `APP_ENV=testing` 时使用配置中库名以 `_test` 结尾的 PostgreSQL 测试库（需预先迁移），供现有 PostgreSQL CI 一起运行。SQLite 不验证 PostgreSQL 行锁语义。
