import json
import uuid

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import get_permissions_for_role
from app.models.admin import SystemLog, UserPermission
from app.models.user import User


def _build_system_log(
    *,
    actor_id: str,
    actor_role: str | None = None,
    actor_nickname: str | None = None,
    action: str,
    module: str,
    target_type: str | None = None,
    target_id: str | None = None,
    target_name: str | None = None,
    risk_level: str = "low",
    detail: dict | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
    result: str = "success",
) -> SystemLog:
    return SystemLog(
        id=uuid.uuid4().hex,
        actor_id=actor_id,
        actor_role=actor_role,
        actor_nickname=actor_nickname,
        action=action,
        module=module,
        target_type=target_type,
        target_id=target_id,
        target_name=target_name,
        risk_level=risk_level,
        detail=json.dumps(detail, ensure_ascii=False) if detail else None,
        ip=ip,
        user_agent=user_agent,
        result=result,
    )


async def create_system_log(
    db: AsyncSession,
    *,
    actor_id: str,
    actor_role: str | None = None,
    actor_nickname: str | None = None,
    action: str,
    module: str,
    target_type: str | None = None,
    target_id: str | None = None,
    target_name: str | None = None,
    risk_level: str = "low",
    detail: dict | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
    result: str = "success",
    commit: bool = True,
) -> SystemLog:
    log = _build_system_log(
        actor_id=actor_id,
        actor_role=actor_role,
        actor_nickname=actor_nickname,
        action=action,
        module=module,
        target_type=target_type,
        target_id=target_id,
        target_name=target_name,
        risk_level=risk_level,
        detail=detail,
        ip=ip,
        user_agent=user_agent,
        result=result,
    )
    db.add(log)
    if commit:
        await db.commit()
        await db.refresh(log)
    return log


async def list_system_logs(
    db: AsyncSession,
    *,
    actor_id: str | None = None,
    action: str | None = None,
    module: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    risk_level: str | None = None,
    result: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[SystemLog], int]:
    base = select(SystemLog)
    if actor_id:
        base = base.where(SystemLog.actor_id == actor_id)
    if action:
        base = base.where(SystemLog.action == action)
    if module:
        base = base.where(SystemLog.module == module)
    if target_type:
        base = base.where(SystemLog.target_type == target_type)
    if target_id:
        base = base.where(SystemLog.target_id == target_id)
    if risk_level:
        base = base.where(SystemLog.risk_level == risk_level)
    if result:
        base = base.where(SystemLog.result == result)
    if keyword:
        like = f"%{keyword}%"
        base = base.where(
            or_(
                SystemLog.actor_nickname.ilike(like),
                SystemLog.target_name.ilike(like),
                SystemLog.action.ilike(like),
            )
        )

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    items_stmt = base.order_by(SystemLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(items_stmt)).scalars().all()
    return list(items), total


async def get_system_log_by_id(db: AsyncSession, log_id: str) -> SystemLog | None:
    stmt = select(SystemLog).where(SystemLog.id == log_id)
    return (await db.execute(stmt)).scalar_one_or_none()


# ---------------------------------------------------------------------------
# 用户手动权限（角色模板权限 ∪ 手动权限 = 最终权限）
# ---------------------------------------------------------------------------


async def get_manual_permissions(db: AsyncSession, user_id: str) -> set[str]:
    """查询某用户手动追加的权限集合。"""
    stmt = select(UserPermission.permission_id).where(UserPermission.user_id == user_id)
    rows = (await db.execute(stmt)).scalars().all()
    return set(rows)


async def get_effective_permissions(db: AsyncSession, user_id: str, role: str) -> set[str]:
    """最终权限 = 角色模板权限 ∪ 数据库手动权限。require_permissions 依赖此函数。"""
    role_permissions = get_permissions_for_role(role)
    manual_permissions = await get_manual_permissions(db, user_id)
    return role_permissions | manual_permissions


async def get_user_permission_detail(db: AsyncSession, user: User) -> dict:
    """查询某用户的模板权限、手动权限与最终权限。"""
    template = get_permissions_for_role(user.role)
    manual = await get_manual_permissions(db, user.id)
    return {
        "role": user.role,
        "template_permission_ids": sorted(template),
        "manual_permission_ids": sorted(manual),
        "effective_permission_ids": sorted(template | manual),
    }


def _build_permission_change_log(
    *,
    actor: dict,
    user: User,
    added: list[str],
    removed: list[str],
    reason: str,
) -> SystemLog:
    """构造权限变更审计日志（权限写入与日志写入必须处于同一事务）。"""
    return _build_system_log(
        actor_id=actor["user_id"],
        actor_role=actor.get("role"),
        action="update_user_permissions",
        module="permission",
        target_type="user",
        target_id=user.id,
        target_name=user.nickname or user.username,
        risk_level="high",
        detail={
            "added": added,
            "removed": removed,
            "reason": reason,
            "operator": actor["user_id"],
        },
        result="success",
    )


def _build_role_change_log(
    *,
    actor: dict,
    user: User,
    old_role: str,
    new_role: str,
    reason: str,
) -> SystemLog:
    """构造角色变更审计日志（与角色写入处于同一事务）。"""
    return _build_system_log(
        actor_id=actor["user_id"],
        actor_role=actor.get("role"),
        action="update_user_role",
        module="permission",
        target_type="user",
        target_id=user.id,
        target_name=user.nickname or user.username,
        risk_level="high",
        detail={
            "old_role": old_role,
            "new_role": new_role,
            "reason": reason,
            "operator": actor["user_id"],
        },
        result="success",
    )


async def count_super_admins(db: AsyncSession) -> int:
    """统计未删除的超级管理员数量（用于「最后一个超管」保护）。"""
    stmt = select(func.count()).select_from(User).where(
        User.role == "super_admin", User.is_deleted == 0
    )
    return (await db.execute(stmt)).scalar_one()


async def _apply_manual_permissions(
    db: AsyncSession,
    *,
    user: User,
    manual_permission_ids: list[str],
    reason: str,
    actor: dict,
) -> None:
    """替换用户的全部手动权限（PUT 替换语义），只写不发提交。

    - 新增项写入 user_permissions（记录授权人与原因）
    - 移除项删除对应记录
    - 变更写入审计日志（由调用方统一 commit，保证同事务）
    """
    current = await get_manual_permissions(db, user.id)
    target = set(manual_permission_ids)  # 去重，重复权限不会重复存储
    added = sorted(target - current)
    removed = sorted(current - target)

    if removed:
        await db.execute(
            delete(UserPermission).where(
                UserPermission.user_id == user.id,
                UserPermission.permission_id.in_(removed),
            )
        )
    for permission_id in added:
        db.add(
            UserPermission(
                id=uuid.uuid4().hex,
                user_id=user.id,
                permission_id=permission_id,
                granted_by=actor["user_id"],
                reason=reason,
            )
        )

    db.add(
        _build_permission_change_log(
            actor=actor, user=user, added=added, removed=removed, reason=reason
        )
    )


async def set_user_authorization(
    db: AsyncSession,
    *,
    user: User,
    role: str,
    manual_permission_ids: list[str],
    reason: str,
    actor: dict,
) -> dict:
    """单事务原子完成：角色变更 + 手动权限替换 + 审计日志。

    - 角色有变化时写入 update_user_role 审计日志
    - 手动权限按替换语义更新并写入 update_user_permissions 审计日志
    - 任一操作失败则整体回滚，不会出现「角色改了但权限/日志没写」的中间态
    """
    old_role = user.role
    if role != old_role:
        user.role = role
        db.add(
            _build_role_change_log(
                actor=actor, user=user, old_role=old_role, new_role=role, reason=reason
            )
        )

    await _apply_manual_permissions(
        db, user=user, manual_permission_ids=manual_permission_ids, reason=reason, actor=actor
    )
    await db.commit()

    return await get_user_permission_detail(db, user)
