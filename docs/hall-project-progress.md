# 大厅项目进展

需求大厅请求 `GET /api/v1/demands?hall_only=true`。后端在分页和总数统计前排除 `status=converted` 或 `convert_status=converted` 的记录；仅关联相似需求或任务的记录仍保留。默认列表和“我的需求”不应用此筛选，以保留立项历史。两个大厅均使用服务端搜索、分页和总数，不再只展示前 50 条数据。

需求列表、我的需求列表和详情通过 `linked_task_id` 读取任务当前信息，返回 `linked_project`：

| 字段 | 说明 |
| --- | --- |
| task_id | 关联任务编号，可为空 |
| availability | unlinked（未关联）、available（可用）、deleted（软删除）、missing（编号不存在） |
| status | 当前任务状态，仅在可用时返回 |
| team_status | 当前团队状态，仅在可用时返回 |
| stage | 当前项目阶段，仅在可用时返回 |

列表批量查询关联任务，不为每条需求单独查任务。需求详情区分需求流程状态与项目阶段；任务大厅和需求详情统一按 `team/develop/beta/opensource` 展示“组队/开发/内测/开源”。关闭或完成不会自动推断项目已开源。旧 `progress` 百分比和 `linked_task_deleted` 字段保留兼容。

已立项需求不会因关联任务被删除而重新出现在需求大厅。详情提示“关联任务已删除”；恢复后读取任务现有阶段和状态。缺失关联提示“暂未关联项目”或“关联项目不可用”，不按标题猜测或自动修复历史关联。本次未访问生产数据库，没有生成生产异常记录清单。

刷新页面、切换大厅或重新进入详情时读取最新数据，不使用实时推送。

## 发布顺序（必须执行数据库迁移）

本 PR 同时增加需求提交昵称功能，迁移 `m3a4b5c6d7e8`（前置版本 `l2f3a4b5c6d7`）为 `demands` 表新增可空的 `submitter_display_name VARCHAR(15)` 列。新后端 ORM 查询会立即读取该列；旧库未迁移时，需求大厅、列表及详情等接口会报缺列错误。

1. 先备份目标 PostgreSQL 数据库，并确认备份可恢复。
2. 将本版本迁移文件及依赖准备到部署环境，加载正确的目标数据库配置。此时不要启动依赖新列的后端。
3. 在 `backend` 目录执行：

   ```sh
   python -m alembic current
   python -m alembic upgrade head
   python -m alembic current
   ```

   `python -m alembic upgrade head` 等价于 `alembic upgrade head`。确认命令成功、版本已达当前发布包的 head，并确认 `demands.submitter_display_name` 列存在。迁移失败则停止发布新后端，先排查数据库状态。
4. 数据库升级成功后，再发布依赖该列的后端，并配套发布前端。新需求提交要求填写昵称，不能把旧前端与新后端作为长期运行组合。
5. 验证需求大厅、需求详情、新需求提交及历史账号昵称回退。历史行的新列保留 NULL，不批量覆盖历史昵称；显示时沿用账号昵称回退逻辑。

如需回滚应用，应保留新增的可空列；不要在新后端仍运行时删除该列。数据库降级会删除已保存的提交昵称，须另行评估并依赖备份恢复，不能当作常规应用回滚步骤。

验证：

```sh
cd backend
python -m pytest --confcutdir=tests/isolated tests/isolated/test_hall_project_progress.py tests/isolated/test_task_deletion.py -q -p no:cacheprovider
```

测试使用内存 SQLite，覆盖筛选分页、个人及管理端历史保留、阶段和状态变更、删除恢复、缺失关联及批量查询。前端执行 `npm run build` 和 `npm run test:contract`。


## 旧库升级验证

CI 保留从空库执行 `alembic upgrade head` 的检查，并增加独立 PostgreSQL 测试库升级检查：先迁移到 `l2f3a4b5c6d7`，插入历史账号和需求，再执行真正的 `alembic upgrade head`。验证新增列、历史字段和账号昵称不变、需求大厅/详情可读、历史昵称回退及新列可写。

仅在已迁移到 `l2f3a4b5c6d7` 的专用 PostgreSQL 测试库（数据库名以 `_test` 结尾）中执行：

```sh
cd backend
python -m scripts.verify_submitter_name_upgrade
```

脚本会插入测试数据并升级该测试库，不可对生产库运行。现有 SQLite 功能测试不替代 PostgreSQL 迁移验证。
