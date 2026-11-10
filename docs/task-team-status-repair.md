# 任务与团队状态联动

任务状态变更接口（详情页及管理后台共用）统一同步团队状态：

| 任务状态 | 团队状态 |
| --- | --- |
| recruiting | forming |
| team_ready / in_progress / pending_acceptance | collaborating |
| completed | accepted |
| closed | ended |

项目阶段 `stage` 保持独立。完成不代表开源，关闭不代表验收通过。
审批加入只增加或重新激活成员，不自动结束招募。队长确认组队完成后，通过详情页的“变更任务状态”将任务从“招募中”改为“待处理”；负责人及拥有任务状态变更权限的用户也可按现有权限操作。确认前，其他共建者仍可申请加入。
此变更不回退历史任务状态，已经处于“待处理”或“解决中”的任务不会自动恢复招募。
`ended` 存储于现有字符串字段，无需新增数据库列；前后端应一起发布。

## 历史数据

在部署环境的 backend 目录使用已安装依赖的 Python，加载目标数据库配置后执行：

```sh
python -m scripts.repair_task_team_status
```

默认只列出不一致记录，不写入。核对输出并备份数据库后执行：

```sh
python -m scripts.repair_task_team_status --apply
```

写入时锁定任务行并在一次事务内修复；跳过软删除和未知任务状态，重复运行不会重复修改。
脚本不会更改任务状态、项目阶段或进度历史。发布代码不会自动修复历史数据。

## 回归验证

使用数据库名以 `_test` 结尾的专用测试库，并完成现有迁移后：

```sh
python -m pytest tests/test_task_team_status.py tests/test_task_status_permission.py tests/test_team_membership_persistence.py
```
