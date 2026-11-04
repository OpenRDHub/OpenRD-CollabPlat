"""Preview mismatched team statuses; use --apply to repair them atomically."""

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
