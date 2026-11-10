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

前后端配套发布，不需要数据库迁移。刷新页面、切换大厅或重新进入详情时读取最新数据，不使用实时推送。

验证：

```sh
cd backend
python -m pytest --confcutdir=tests/isolated tests/isolated/test_hall_project_progress.py tests/isolated/test_task_deletion.py -q -p no:cacheprovider
```

测试使用内存 SQLite，覆盖筛选分页、个人及管理端历史保留、阶段和状态变更、删除恢复、缺失关联及批量查询。前端执行 `npm run build` 和 `npm run test:contract`。
