# 任务与团队状态联动

任务状态变更接口（详情页及管理后台共用）和审批加入后的自动组队统一同步团队状态：

| 任务状态 | 团队状态 |
| --- | --- |
| recruiting | forming |
| team_ready / in_progress / pending_acceptance | collaborating |
| completed | accepted |
| closed | ended |

项目阶段 `stage` 保持独立。完成不代表开源，关闭不代表验收通过。
`ended` 存储于现有字符串字段，无需新增数据库列；前后端应一起发布。

## 历史数据

脚本**不会**随发布自动运行，需运维手动执行。

### 1. 预览（不写入）

在部署环境的 backend 目录使用已安装依赖的 Python，加载目标数据库配置后执行：

```sh
python -m scripts.repair_task_team_status
```

默认只列出将被修改的记录，**不会写入任何数据**。输出形如：

```
TASK-1: team_ready -> in_progress
TASK-2: in_progress, forming -> collaborating
Would repair 2 tasks
```

### 2. 备份

核对输出后，先备份任务表（或整库）：

```sh
pg_dump -h <host> -U <user> -d <db> -t tasks > tasks_backup_$(date +%F).sql
```

### 3. 写入

```sh
python -m scripts.repair_task_team_status --apply
```

写入时锁定任务行并在**一次事务**内提交，失败则整体回滚；重复运行不会重复修改（幂等）。

### 写入范围

脚本会做两类修复：

1. **团队状态对齐**：按上表修正与任务状态不一致的 `team_status`。此修复遍历**所有未删除任务，
   含已完成/已关闭等终态任务**——例如 `closed/forming` 会被修正为 `closed/ended`，
   `completed/forming` 会被修正为 `completed/accepted`。
2. **存量「待处理」迁移**：`team_ready` 环节已从流程中移除（招募中组队完成后直接进入解决中），
   脚本会将这些历史任务推进为 `in_progress`，并同步其 `team_status` 为 `collaborating`。

脚本**不会**更改项目阶段（`stage`）与进度历史，**不会修改任何任务的 `status` 字段**
（唯一例外是第 2 类中 `team_ready -> in_progress` 的存量迁移），也不会改动终态任务的
任务状态——但终态任务**不一致的 `team_status` 仍会被修正**。做备份与影响评估时
请以两类修复的并集为准，不要按「终态任务完全不动」估算。

### 软删除任务的处理（重要）

脚本**跳过软删除任务**（`is_deleted = 1`），不会迁移其状态。因此：

- 若一个历史任务在脚本运行前已被软删除，其状态仍为 `team_ready`；
- 之后通过「恢复任务」接口恢复时，**恢复操作本身不会改变任务状态**，该任务会以 `team_ready` 重新出现在列表中。

兼容期代码已保证这类任务与页面展示一致，无需额外处理：

| 场景 | 行为 |
| --- | --- |
| 详情页推进到「待验收」 | 允许（`team_ready` 与 `in_progress` 流转能力一致） |
| 列表按「解决中」筛选 | 命中（筛选别名同时匹配 `team_ready`） |
| 详情页「申请加入」 | 允许（后端与前端入口均已放行 `team_ready`） |

如需彻底清理，可在恢复任务后重跑本脚本，或直接将其状态推进为 `in_progress`。

## 回归验证

使用数据库名以 `_test` 结尾的专用测试库，并完成现有迁移后：

```sh
python -m pytest tests/test_task_team_status.py tests/test_legacy_team_ready_compat.py \
  tests/test_task_status_permission.py tests/test_team_membership_persistence.py
```

本机无法运行 PostgreSQL（如 Docker 未启动）时，可用 SQLite 独立探针验证兼容行为，
无需数据库环境：

```sh
python -m scripts.verify_team_ready_compat
```

探针在内存 SQLite 中复现三类场景并断言修复生效：状态流转接受、已删除筛选命中、
脚本写入范围与幂等。退出码 0 表示全部通过。

其中 `test_legacy_team_ready_compat.py` 覆盖兼容期关键路径：

- 未迁移任务与「删除后恢复」的历史任务推进到「待验收」均返回 200；
- 按「解决中」筛选（含 `deleted=true`）命中历史 `team_ready`，且不误召回「招募中」；
- 加入申请接口接受 `team_ready`，且前端 `canApply` 不再只认「招募中」。

`test_task_team_status.py` 覆盖脚本的迁移与幂等性：

- 预览模式不写入；
- `--apply` 后状态与 `team_status` 同步、`stage` 不变；
- 重复运行返回 0，不重复修改。
