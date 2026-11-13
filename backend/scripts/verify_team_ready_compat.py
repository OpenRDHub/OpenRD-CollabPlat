"""历史 team_ready 兼容性验证（SQLite 独立探针，无需 PostgreSQL/Docker）。

复现评审报告的三个场景并验证修复：
  1. team_ready 历史任务（含删除后恢复）按页面「解决中」推进到「待验收」不再被拒。
  2. 已删除列表按「解决中」筛选不再漏掉 team_ready 历史任务。
  3. 修复脚本 --apply 的写入范围（迁移 team_ready、幂等、跳过软删除、stage 不变、
     终态任务 status 不变但其不一致的 team_status 仍会被对齐）。

用法（backend 目录）：
    python -m scripts.verify_team_ready_compat
退出码 0 表示全部通过。
"""

import asyncio
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  确保所有模型注册到 Base.metadata
from app.models.base import Base
from app.models.task import Task
from app.services.task import change_status, list_tasks
from scripts.repair_task_team_status import repair

PROBE_DB = "sqlite+aiosqlite:///:memory:"


def check(label: str, condition: bool, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}{f' — {detail}' if detail else ''}")
    return condition


async def probe_status_transition(session_factory) -> bool:
    """探针 1：未迁移 / 删除后恢复的 team_ready 任务推进到「待验收」。"""
    ok = True
    for scenario, is_deleted in (("未迁移", 0), ("删除后恢复", 1)):
        task_id = f"PROBE-ADV-{scenario}"
        task = Task(
            id=task_id, title="Legacy team_ready", status="team_ready",
            team_status="collaborating", stage="develop", is_deleted=is_deleted,
        )
        async with session_factory() as s:
            s.add(task)
            await s.commit()

            if is_deleted:
                # 模拟运维恢复路径：恢复本身不改状态，之后仍可推进
                task.is_deleted = 0
                await s.commit()
                await s.refresh(task)
                ok &= check(f"{scenario}: 恢复后状态保持 team_ready", task.status == "team_ready")

            result = await change_status(s, task, new_status="pending_acceptance")
            await s.refresh(task)
            ok &= check(
                f"{scenario}: team_ready -> pending_acceptance 被接受",
                result is not None and task.status == "pending_acceptance",
                f"实际 status={task.status}（旧代码在此返回拒绝，页面收到 400）",
            )
            ok &= check(f"{scenario}: team_status 同步 collaborating", task.team_status == "collaborating")
            ok &= check(f"{scenario}: stage 不被改动", task.stage == "develop")
    return ok


async def probe_deleted_filter(session_factory) -> bool:
    """探针 2：deleted=true & status=in_progress 命中历史 team_ready。"""
    async with session_factory() as s:
        s.add_all([
            Task(id="PROBE-DEL-PROG", title="in_progress", status="in_progress",
                 team_status="collaborating", is_deleted=1),
            Task(id="PROBE-DEL-READY", title="legacy team_ready", status="team_ready",
                 team_status="collaborating", is_deleted=1),
            Task(id="PROBE-DEL-REC", title="recruiting", status="recruiting",
                 team_status="forming", is_deleted=1),
        ])
        await s.commit()
        items, total = await list_tasks(s, status="in_progress", deleted=True, page_size=50)
        ids = {t.id for t in items}
        ok = check("已删除列表按「解决中」筛选返回条数 > 0", total > 0, f"total={total}（评审时为 0）")
        ok &= check("命中已删除 team_ready 历史任务", "PROBE-DEL-READY" in ids)
        ok &= check("命中 in_progress 任务", "PROBE-DEL-PROG" in ids)
        ok &= check("不误召回 recruiting", "PROBE-DEL-REC" not in ids)
        return ok


async def probe_repair_script(session_factory) -> bool:
    """探针 3：修复脚本预览不写入、--apply 迁移并幂等、跳过软删除、终态团队状态对齐。"""
    async with session_factory() as s:
        legacy = Task(id="PROBE-REPAIR-READY", title="Legacy ready", status="team_ready",
                      team_status="forming", stage="beta")
        closed = Task(id="PROBE-REPAIR-CLOSED", title="Closed terminal", status="closed",
                      team_status="forming", stage="beta")
        deleted = Task(id="PROBE-REPAIR-DEL", title="Deleted legacy", status="team_ready",
                       team_status="forming", stage="beta", is_deleted=1)
        s.add_all([legacy, closed, deleted])
        await s.commit()

        preview = await repair(s)
        await s.refresh(legacy)
        await s.refresh(closed)
        ok = check("预览模式不写入",
                   preview == 2 and legacy.status == "team_ready" and closed.team_status == "forming",
                   f"预览发现 {preview} 条，状态均未变")

        applied = await repair(s, apply=True)
        await s.refresh(legacy)
        await s.refresh(closed)
        await s.refresh(deleted)
        ok &= check("--apply 将 team_ready 推进为 in_progress",
                    legacy.status == "in_progress")
        ok &= check("team_status 同步 collaborating", legacy.team_status == "collaborating")
        ok &= check("stage 保持不变", legacy.stage == "beta")
        ok &= check("终态 closed 任务 status 不变", closed.status == "closed")
        ok &= check("终态任务不一致的 team_status 仍被对齐（forming -> ended）",
                    closed.team_status == "ended")
        ok &= check("跳过软删除任务", deleted.status == "team_ready")

        again = await repair(s, apply=True)
        ok &= check("重复运行幂等（返回 0）", again == 0)
        return ok


async def main() -> int:
    engine = create_async_engine(PROBE_DB, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # 逐个执行以保持输出顺序稳定
    ok1 = await probe_status_transition(session_factory)
    ok2 = await probe_deleted_filter(session_factory)
    ok3 = await probe_repair_script(session_factory)

    await engine.dispose()
    all_ok = ok1 and ok2 and ok3
    print()
    print("SQLite 探针结论：" + ("全部通过" if all_ok else "存在失败项"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
