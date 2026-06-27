import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.team import Assignment, JoinApplication, TaskMember


async def get_team_detail(db: AsyncSession, task_id: str) -> dict:
    members_stmt = select(TaskMember).where(
        TaskMember.task_id == task_id, TaskMember.is_deleted == 0
    )
    members = (await db.execute(members_stmt)).scalars().all()

    apps_stmt = select(JoinApplication).where(
        JoinApplication.task_id == task_id, JoinApplication.is_deleted == 0
    )
    applications = (await db.execute(apps_stmt)).scalars().all()

    assignments_stmt = select(Assignment).where(
        Assignment.task_id == task_id, Assignment.is_deleted == 0
    )
    assignments = (await db.execute(assignments_stmt)).scalars().all()

    task_stmt = select(Task).where(Task.id == task_id)
    task = (await db.execute(task_stmt)).scalar_one_or_none()
    leader_id = task.leader_id if task else None

    return {
        "task_id": task_id,
        "leader_id": leader_id,
        "members": list(members),
        "applications": list(applications),
        "assignments": list(assignments),
    }


async def create_join_application(
    db: AsyncSession,
    *,
    task_id: str,
    user_id: str,
    role: str,
    skills: list[str] | None = None,
    reason: str | None = None,
) -> JoinApplication | None:
    existing_stmt = select(JoinApplication).where(
        JoinApplication.task_id == task_id,
        JoinApplication.user_id == user_id,
        JoinApplication.status == "pending",
        JoinApplication.is_deleted == 0,
    )
    existing = (await db.execute(existing_stmt)).scalar_one_or_none()
    if existing:
        return None

    app = JoinApplication(
        id=uuid.uuid4().hex,
        task_id=task_id,
        user_id=user_id,
        role=role,
        skills=json.dumps(skills, ensure_ascii=False) if skills else None,
        reason=reason,
        status="pending",
    )
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return app


async def approve_application(
    db: AsyncSession,
    application: JoinApplication,
    *,
    reviewer_id: str,
    duty: str | None = None,
) -> TaskMember:
    application.status = "approved"
    application.reviewer_id = reviewer_id

    member = TaskMember(
        id=uuid.uuid4().hex,
        task_id=application.task_id,
        user_id=application.user_id,
        role=application.role,
        duty=duty,
        source="application",
        status="active",
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


async def reject_application(
    db: AsyncSession,
    application: JoinApplication,
    *,
    reviewer_id: str,
    reason: str,
) -> JoinApplication:
    application.status = "rejected"
    application.reviewer_id = reviewer_id
    application.reject_reason = reason
    await db.commit()
    await db.refresh(application)
    return application


async def get_application_by_id(db: AsyncSession, application_id: str) -> JoinApplication | None:
    stmt = select(JoinApplication).where(
        JoinApplication.id == application_id, JoinApplication.is_deleted == 0
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def invite_member(
    db: AsyncSession,
    *,
    task_id: str,
    user_id: str,
    role: str,
    duty: str | None = None,
) -> TaskMember:
    member = TaskMember(
        id=uuid.uuid4().hex,
        task_id=task_id,
        user_id=user_id,
        role=role,
        duty=duty,
        source="invite",
        status="active",
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


async def get_member_by_id(db: AsyncSession, member_id: str) -> TaskMember | None:
    stmt = select(TaskMember).where(
        TaskMember.id == member_id, TaskMember.is_deleted == 0
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def update_member(
    db: AsyncSession,
    member: TaskMember,
    *,
    role: str | None = None,
    duty: str | None = None,
) -> TaskMember:
    if role is not None:
        member.role = role
    if duty is not None:
        member.duty = duty
    await db.commit()
    await db.refresh(member)
    return member


async def transfer_leader(
    db: AsyncSession,
    *,
    task_id: str,
    new_leader_id: str,
) -> Task | None:
    task_stmt = select(Task).where(Task.id == task_id)
    task = (await db.execute(task_stmt)).scalar_one_or_none()
    if not task:
        return None
    task.leader_id = new_leader_id
    await db.commit()
    await db.refresh(task)
    return task


async def save_assignments(
    db: AsyncSession,
    *,
    task_id: str,
    assignments_data: list[dict],
) -> list[Assignment]:
    incoming_ids = {item["id"] for item in assignments_data if item.get("id")}

    existing_stmt = select(Assignment).where(
        Assignment.task_id == task_id, Assignment.is_deleted == 0
    )
    existing = (await db.execute(existing_stmt)).scalars().all()

    for ex in existing:
        if ex.id not in incoming_ids:
            ex.is_deleted = 1
            ex.deleted_at = datetime.now(timezone.utc)

    result = []
    for item in assignments_data:
        if item.get("id"):
            for ex in existing:
                if ex.id == item["id"]:
                    ex.title = item["title"]
                    ex.owner_id = item.get("owner_id")
                    ex.deliverable = item.get("deliverable")
                    ex.due_time = item.get("due_time")
                    ex.status = item.get("status", "todo")
                    result.append(ex)
                    break
        else:
            new_assignment = Assignment(
                id=uuid.uuid4().hex,
                task_id=task_id,
                title=item["title"],
                owner_id=item.get("owner_id"),
                deliverable=item.get("deliverable"),
                due_time=item.get("due_time"),
                status=item.get("status", "todo"),
            )
            db.add(new_assignment)
            result.append(new_assignment)

    await db.commit()
    for r in result:
        await db.refresh(r)
    return result


async def is_task_member_or_leader(db: AsyncSession, task_id: str, user_id: str) -> bool:
    task_stmt = select(Task).where(Task.id == task_id)
    task = (await db.execute(task_stmt)).scalar_one_or_none()
    if task and task.leader_id == user_id:
        return True

    member_stmt = select(TaskMember).where(
        TaskMember.task_id == task_id,
        TaskMember.user_id == user_id,
        TaskMember.is_deleted == 0,
        TaskMember.status == "active",
    )
    member = (await db.execute(member_stmt)).scalar_one_or_none()
    return member is not None
