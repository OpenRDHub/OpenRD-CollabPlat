"""Preview mismatched team statuses; use --apply to repair them atomically.

同时迁移已移除的「待处理(team_ready)」历史任务：直接推进到「解决中(in_progress)」，
并同步其 team_status，避免存量数据停留在不存在的环节。
"""

import argparse
import asyncio

from sqlalchemy import select

from app.database import async_session_factory, engine
from app.models.task import Task
from app.services.task_status import TEAM_STATUS_BY_TASK_STATUS


async def repair(db, *, apply: bool = False) -> int:
    statement = select(Task).where(Task.is_deleted == 0).order_by(Task.id)
    if apply:
        statement = statement.with_for_update()
    tasks = (await db.execute(statement)).scalars().all()
    count = 0
    for task in tasks:
        if task.status == "team_ready":
            print(f"{task.id}: team_ready -> in_progress")
            count += 1
            if apply:
                task.status = "in_progress"
                task.team_status = TEAM_STATUS_BY_TASK_STATUS["in_progress"]
            continue
        expected = TEAM_STATUS_BY_TASK_STATUS.get(task.status)
        if expected is None or expected == task.team_status:
            continue
        print(f"{task.id}: {task.status}, {task.team_status} -> {expected}")
        count += 1
        if apply:
            task.team_status = expected
    if apply:
        await db.commit()
    return count


async def main(apply: bool) -> None:
    try:
        async with async_session_factory() as db:
            count = await repair(db, apply=apply)
        print(f"{'Repaired' if apply else 'Would repair'} {count} tasks")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Write repairs to the configured database")
    asyncio.run(main(parser.parse_args().apply))
