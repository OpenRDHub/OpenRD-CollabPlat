r"""
用户手动权限的「业务接口级」生效测试（PR #49 复审 P1）

复审结论：新的手动权限虽然能写入数据库并出现在 /me/permissions 的最终权限列表中，
但大量真实业务接口仍然直接判断角色（role in ("operator", "super_admin")），
没有读取最终权限，导致后台授权后业务接口依旧 403。

本文件针对复审点名的权限逐个验证（不只看 /me/permissions 返回值，而是调用真实业务接口）：
  1. 低角色用户获得手动授权后，可以成功执行对应业务操作；
  2. 撤销手动授权后，同一旧 Token 再次调用接口立即返回 403；
  3. 需求归档检查的是 demand:archive，而不是 demand:reject；
  4. 非超级管理员即使拥有 admin:user，也不能解锁超级管理员账号。

覆盖权限：member:approve / member:invite / member:manage / task:update / task:status /
          file:upload / file:delete / demand:reply / demand:archive / message:manage

运行：
    uv run pytest tests/test_manual_permission_business.py -v
"""

import uuid

import pytest
from sqlalchemy import delete, select

from app.models.admin import UserPermission
from app.models.demand import Demand, DemandReply
from app.models.file import File
from app.models.task import Task
from app.models.team import JoinApplication, TaskMember
from app.models.user import User
from app.services.task import create_task
from app.utils.security import create_access_token, hash_password

API = "/api/v1"
VALID_PDF = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\n%%EOF\n"
THREAD_ID = "thread-manual-perm"


def auth_headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id, user.role)}"}


async def _create_user(db_session, role: str, label: str) -> User:
    suffix = uuid.uuid4().hex[:10]
    user = User(
        id=suffix,
        platform_id=f"U{suffix[:8]}",
        username=f"mp_{label}_{suffix[:6]}",
        phone=f"139{suffix[:8]}",
        password_hash=hash_password("Test123!"),
        role=role,
        nickname=f"{label}-{suffix[:4]}",
    )
    db_session.add(user)
    await db_session.commit()
    return user


async def _grant(db_session, user: User, *permission_ids: str) -> None:
    """模拟后台手动授权（与 PUT /admin/users/{id}/authorization 落库结果一致）。

    granted_by 有外键约束，指向真实存在且具备 admin:role 的授权人。
    """
    grantor = (
        await db_session.execute(select(User).where(User.role == "super_admin"))
    ).scalars().first()
    if grantor is None:
        grantor = await _create_user(db_session, "super_admin", "grantor")

    for permission_id in permission_ids:
        db_session.add(
            UserPermission(
                id=uuid.uuid4().hex,
                user_id=user.id,
                permission_id=permission_id,
                granted_by=grantor.id,
                reason="PR49 复审：业务级权限回归",
            )
        )
    await db_session.commit()


async def _revoke_all(db_session, user: User) -> None:
    await db_session.execute(delete(UserPermission).where(UserPermission.user_id == user.id))
    await db_session.commit()


async def _me_permissions(client, user: User) -> list[str]:
    resp = await client.get(f"{API}/me/permissions", headers=auth_headers(user))
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


async def _set_task_status(db_session, task_id: str, status: str) -> None:
    task = await db_session.get(Task, task_id)
    task.status = status
    await db_session.commit()


async def _progress_token(db_session, task_id: str) -> str:
    """进度乐观锁令牌 = 任务当前 updated_at 的 ISO 字符串。

    上游 B11 起，POST /tasks/{id}/progress 的 expected_updated_at 为必填：
    服务层 submit_progress 会无条件比对 task.updated_at == expected_updated_at，
    因此每次成功提交都会推进令牌，必须逐次重取。

    refresh 不可省略：请求走的是 get_db 的独立 session，而测试 session 是
    expire_on_commit=False，不刷新会读到旧值，导致成功用例被误判为 409。
    """
    task = await db_session.get(Task, task_id)
    await db_session.refresh(task)
    assert task.updated_at is not None, "任务 updated_at 为空，无法构造乐观锁令牌"
    return task.updated_at.isoformat()


async def _make_application(db_session, task_id: str, user: User) -> JoinApplication:
    application = JoinApplication(
        id=uuid.uuid4().hex,
        task_id=task_id,
        user_id=user.id,
        role="开发",
        status="pending",
    )
    db_session.add(application)
    await db_session.commit()
    return application


async def _make_demand(db_session, creator: User, *, owner: User | None = None) -> Demand:
    demand = Demand(
        id=f"D{uuid.uuid4().hex[:10]}",
        title="手动权限业务验收需求",
        description="复审 P1 用例",
        urgency="medium",
        status="communicating",
        creator_id=creator.id,
        owner_id=owner.id if owner else None,
    )
    db_session.add(demand)
    await db_session.commit()
    return demand


async def _make_reply(db_session, demand: Demand, sender: User) -> DemandReply:
    reply = DemandReply(
        id=uuid.uuid4().hex,
        demand_id=demand.id,
        thread_id=THREAD_ID,
        sender_id=sender.id,
        sender_role=sender.role,
        content="他人发的消息",
    )
    db_session.add(reply)
    await db_session.commit()
    return reply


@pytest.fixture
def isolated_storage(tmp_path, monkeypatch):
    monkeypatch.setattr("app.services.file.get_storage_root", lambda: tmp_path)
    return tmp_path


@pytest.fixture
async def scene(db_session):
    """一个「招募中」任务 + 成员/队长/负责人/无关者/申请人 五类真实用户。"""
    operator = await _create_user(db_session, "operator", "operator")
    member = await _create_user(db_session, "builder", "member")
    leader = await _create_user(db_session, "builder", "leader")
    owner = await _create_user(db_session, "builder", "owner")
    stranger = await _create_user(db_session, "builder", "stranger")
    applicant = await _create_user(db_session, "builder", "applicant")

    task = await create_task(
        db_session,
        title="手动权限业务验收任务",
        description="复审 P1 用例",
        task_type="工具开发项目",
        priority="medium",
        owner_id=owner.id,
        leader_id=leader.id,
    )
    await db_session.refresh(task)

    membership = TaskMember(
        id=uuid.uuid4().hex,
        task_id=task.id,
        user_id=member.id,
        role="队员",
        duty="开发",
        source="invite",
        status="active",
    )
    db_session.add(membership)
    await db_session.commit()

    return {
        "operator": operator,
        "member": member,
        "leader": leader,
        "owner": owner,
        "stranger": stranger,
        "applicant": applicant,
        "task_id": task.id,
        "membership_id": membership.id,
    }


# ---------------------------------------------------------------------------
# 1. member:approve —— 组队申请审批（复审典型示例）
# ---------------------------------------------------------------------------


async def test_member_approve_uses_permission_not_role(client, db_session, scene):
    member = scene["member"]
    task_id = scene["task_id"]

    # 低角色 builder（非队长）没有 member:approve → 403
    application = await _make_application(db_session, task_id, scene["applicant"])
    denied = await client.post(
        f"{API}/tasks/{task_id}/join-applications/{application.id}/approve",
        json={"duty": "开发"},
        headers=auth_headers(member),
    )
    assert denied.status_code == 403, denied.text

    # 后台手动授予 member:approve → /me/permissions 体现 + 真实接口放行
    await _grant(db_session, member, "member:approve")
    assert "member:approve" in await _me_permissions(client, member)

    application = await _make_application(db_session, task_id, scene["stranger"])
    allowed = await client.post(
        f"{API}/tasks/{task_id}/join-applications/{application.id}/approve",
        json={"duty": "开发"},
        headers=auth_headers(member),
    )
    assert allowed.status_code == 200, allowed.text

    # 撤销手动授权后，同一 Token 立即失去审批能力
    await _revoke_all(db_session, member)
    assert "member:approve" not in await _me_permissions(client, member)

    third = await _make_application(db_session, task_id, scene["leader"])
    revoked = await client.post(
        f"{API}/tasks/{task_id}/join-applications/{third.id}/reject",
        json={"reason": "撤销授权后应被拒绝"},
        headers=auth_headers(member),
    )
    assert revoked.status_code == 403, revoked.text


async def test_leader_still_approves_without_manual_permission(client, db_session, scene):
    """资源归属规则保留：队长无需任何手动授权即可审批。"""
    application = await _make_application(db_session, scene["task_id"], scene["applicant"])
    resp = await client.post(
        f"{API}/tasks/{scene['task_id']}/join-applications/{application.id}/approve",
        json={"duty": "开发"},
        headers=auth_headers(scene["leader"]),
    )
    assert resp.status_code == 200, resp.text


# ---------------------------------------------------------------------------
# 2. member:invite —— 邀请成员
# ---------------------------------------------------------------------------


async def test_member_invite_uses_permission_not_role(client, db_session, scene):
    member = scene["member"]
    task_id = scene["task_id"]
    payload = {"platform_id": scene["stranger"].platform_id, "suggested_role": "测试"}

    denied = await client.post(
        f"{API}/tasks/{task_id}/members/invite",
        json=payload,
        headers=auth_headers(member),
    )
    assert denied.status_code == 403, denied.text

    await _grant(db_session, member, "member:invite")
    allowed = await client.post(
        f"{API}/tasks/{task_id}/members/invite",
        json={"platform_id": scene["applicant"].platform_id, "suggested_role": "测试"},
        headers=auth_headers(member),
    )
    assert allowed.status_code == 200, allowed.text

    await _revoke_all(db_session, member)
    revoked = await client.post(
        f"{API}/tasks/{task_id}/members/invite",
        json=payload,
        headers=auth_headers(member),
    )
    assert revoked.status_code == 403, revoked.text


# ---------------------------------------------------------------------------
# 3. member:manage —— 成员管理（改成员信息）
# ---------------------------------------------------------------------------


async def test_member_manage_uses_permission_not_role(client, db_session, scene):
    member = scene["member"]
    task_id = scene["task_id"]
    url = f"{API}/tasks/{task_id}/members/{scene['membership_id']}"

    denied = await client.patch(url, json={"duty": "重构"}, headers=auth_headers(member))
    assert denied.status_code == 403, denied.text

    await _grant(db_session, member, "member:manage")
    allowed = await client.patch(url, json={"duty": "重构"}, headers=auth_headers(member))
    assert allowed.status_code == 200, allowed.text
    assert allowed.json()["data"]["duty"] == "重构"

    await _revoke_all(db_session, member)
    revoked = await client.patch(url, json={"duty": "再改"}, headers=auth_headers(member))
    assert revoked.status_code == 403, revoked.text


# ---------------------------------------------------------------------------
# 4. task:update —— 提交进度（手动授权视为平台级能力）
# ---------------------------------------------------------------------------


async def test_task_update_manual_grant_allows_progress(client, db_session, scene):
    task_id = scene["task_id"]
    await _set_task_status(db_session, task_id, "in_progress")
    stranger = scene["stranger"]

    # 无关 builder：builder 模板已不含 task:update（见 test_task_update_permission.py），
    # 没有任何手动授权 → 必须叠加归属校验 → 403
    denied = await client.post(
        f"{API}/tasks/{task_id}/progress",
        json={
            "stage": "develop",
            "content": "越权尝试",
            "base_stage": "team",
            "expected_updated_at": await _progress_token(db_session, task_id),
        },
        headers=auth_headers(stranger),
    )
    assert denied.status_code == 403, denied.text

    # 后台手动授予 task:update → 视为平台级更新权限，放行
    await _grant(db_session, stranger, "task:update")
    allowed = await client.post(
        f"{API}/tasks/{task_id}/progress",
        json={
            "stage": "develop",
            "content": "手动授权后提交",
            "base_stage": "team",
            "expected_updated_at": await _progress_token(db_session, task_id),
        },
        headers=auth_headers(stranger),
    )
    assert allowed.status_code == 200, allowed.text

    await _revoke_all(db_session, stranger)
    revoked = await client.post(
        f"{API}/tasks/{task_id}/progress",
        json={
            "stage": "beta",
            "content": "撤销后提交",
            "base_stage": "develop",
            "expected_updated_at": await _progress_token(db_session, task_id),
        },
        headers=auth_headers(stranger),
    )
    assert revoked.status_code == 403, revoked.text


async def test_task_progress_still_allows_owner_and_denies_plain_member(client, db_session, scene):
    """收紧语义保留：负责人放行，普通成员（非队长/负责人）仍被拒绝。"""
    task_id = scene["task_id"]
    await _set_task_status(db_session, task_id, "in_progress")

    by_owner = await client.post(
        f"{API}/tasks/{task_id}/progress",
        json={
            "stage": "develop",
            "content": "负责人提交",
            "base_stage": "team",
            "expected_updated_at": await _progress_token(db_session, task_id),
        },
        headers=auth_headers(scene["owner"]),
    )
    assert by_owner.status_code == 200, by_owner.text

    by_member = await client.post(
        f"{API}/tasks/{task_id}/progress",
        json={
            "stage": "develop",
            "content": "普通成员提交",
            "base_stage": "develop",
            "expected_updated_at": await _progress_token(db_session, task_id),
        },
        headers=auth_headers(scene["member"]),
    )
    assert by_member.status_code == 403, by_member.text


# ---------------------------------------------------------------------------
# 5. task:status —— 推进任务阶段
# ---------------------------------------------------------------------------


async def test_task_status_uses_permission_not_role(client, db_session, scene):
    task_id = scene["task_id"]
    await _set_task_status(db_session, task_id, "in_progress")
    stranger = scene["stranger"]

    denied = await client.post(
        f"{API}/tasks/{task_id}/status",
        json={"status": "pending_acceptance"},
        headers=auth_headers(stranger),
    )
    assert denied.status_code == 403, denied.text

    await _grant(db_session, stranger, "task:status")
    allowed = await client.post(
        f"{API}/tasks/{task_id}/status",
        json={"status": "pending_acceptance"},
        headers=auth_headers(stranger),
    )
    assert allowed.status_code == 200, allowed.text

    await _set_task_status(db_session, task_id, "in_progress")
    await _revoke_all(db_session, stranger)
    revoked = await client.post(
        f"{API}/tasks/{task_id}/status",
        json={"status": "pending_acceptance"},
        headers=auth_headers(stranger),
    )
    assert revoked.status_code == 403, revoked.text


# ---------------------------------------------------------------------------
# 6. file:upload / file:delete —— 文件权限
# ---------------------------------------------------------------------------


async def _upload(client, user: User) -> str:
    resp = await client.post(
        f"{API}/files",
        headers=auth_headers(user),
        files={"file": ("proof.pdf", VALID_PDF, "application/pdf")},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]["file_id"]


async def test_file_upload_requires_file_upload_permission(client, db_session, isolated_storage):
    """无 file:upload 最终权限的角色不能上传（此前只校验登录态）。"""
    nobody = await _create_user(db_session, "guest", "noperm")
    denied = await client.post(
        f"{API}/files",
        headers=auth_headers(nobody),
        files={"file": ("proof.pdf", VALID_PDF, "application/pdf")},
    )
    assert denied.status_code == 403, denied.text

    await _grant(db_session, nobody, "file:upload")
    file_id = await _upload(client, nobody)
    assert file_id


async def test_file_delete_uses_permission_not_role(client, db_session, isolated_storage, scene):
    uploader = scene["owner"]
    stranger = scene["stranger"]
    file_id = await _upload(client, uploader)

    denied = await client.delete(f"{API}/files/{file_id}", headers=auth_headers(stranger))
    assert denied.status_code == 403, denied.text

    await _grant(db_session, stranger, "file:delete")
    allowed = await client.delete(f"{API}/files/{file_id}", headers=auth_headers(stranger))
    assert allowed.status_code == 200, allowed.text

    record = await db_session.get(File, file_id)
    await db_session.refresh(record)
    assert record.is_deleted == 1, "拥有 file:delete 的用户应能删除他人文件"


async def test_file_delete_still_allows_uploader(client, db_session, isolated_storage, scene):
    """资源归属规则保留：上传者本人无需 file:delete 即可删除自己的文件。"""
    uploader = await _create_user(db_session, "requester", "uploader")
    file_id = await _upload(client, uploader)
    resp = await client.delete(f"{API}/files/{file_id}", headers=auth_headers(uploader))
    assert resp.status_code == 200, resp.text


# ---------------------------------------------------------------------------
# 7. demand:reply —— 沟通区发言
# ---------------------------------------------------------------------------


async def test_demand_reply_uses_permission_not_role(client, db_session, scene):
    creator = scene["operator"]
    demand = await _make_demand(db_session, creator)
    stranger = scene["stranger"]
    payload = {"thread_id": THREAD_ID, "content": "手动授权后发言"}

    denied = await client.post(
        f"{API}/demands/{demand.id}/replies", json=payload, headers=auth_headers(stranger)
    )
    assert denied.status_code == 403, denied.text

    await _grant(db_session, stranger, "demand:reply")
    allowed = await client.post(
        f"{API}/demands/{demand.id}/replies", json=payload, headers=auth_headers(stranger)
    )
    assert allowed.status_code == 200, allowed.text

    await _revoke_all(db_session, stranger)
    revoked = await client.post(
        f"{API}/demands/{demand.id}/replies",
        json={"thread_id": THREAD_ID, "content": "撤销后发言"},
        headers=auth_headers(stranger),
    )
    assert revoked.status_code == 403, revoked.text


async def test_demand_creator_can_reply_without_manual_permission(client, db_session, scene):
    """需求创建者属于资源归属，无需 demand:reply 模板权限即可发言。"""
    creator = await _create_user(db_session, "requester", "creator")
    demand = await _make_demand(db_session, creator)
    resp = await client.post(
        f"{API}/demands/{demand.id}/replies",
        json={"thread_id": THREAD_ID, "content": "创建者发言"},
        headers=auth_headers(creator),
    )
    assert resp.status_code == 200, resp.text


# ---------------------------------------------------------------------------
# 8. demand:archive —— 归档检查的是 archive 而不是 reject
# ---------------------------------------------------------------------------


async def test_demand_archive_checks_archive_permission(client, db_session, scene):
    creator = await _create_user(db_session, "requester", "archive_creator")
    demand = await _make_demand(db_session, creator)
    actor = await _create_user(db_session, "requester", "archiver")

    # 没有 demand:archive → 403
    denied = await client.post(
        f"{API}/demands/{demand.id}/archive", headers=auth_headers(actor)
    )
    assert denied.status_code == 403, denied.text

    # 只有 demand:reject → 仍然不能归档（原来误用 demand:reject 会放行）
    await _grant(db_session, actor, "demand:reject")
    wrong_perm = await client.post(
        f"{API}/demands/{demand.id}/archive", headers=auth_headers(actor)
    )
    assert wrong_perm.status_code == 403, wrong_perm.text

    # 授予 demand:archive → 放行
    await _grant(db_session, actor, "demand:archive")
    allowed = await client.post(
        f"{API}/demands/{demand.id}/archive", headers=auth_headers(actor)
    )
    assert allowed.status_code == 200, allowed.text

    await db_session.refresh(demand)
    assert demand.status == "archived"


# ---------------------------------------------------------------------------
# 9. message:manage —— 撤回他人消息
# ---------------------------------------------------------------------------


async def test_message_manage_uses_permission_not_role(client, db_session, scene):
    creator = await _create_user(db_session, "requester", "msg_creator")
    sender = await _create_user(db_session, "builder", "msg_sender")
    demand = await _make_demand(db_session, creator)
    moderator = await _create_user(db_session, "builder", "moderator")

    reply = await _make_reply(db_session, demand, sender)
    denied = await client.post(
        f"{API}/demands/{demand.id}/replies/{reply.id}/revoke",
        headers=auth_headers(moderator),
    )
    assert denied.status_code == 403, denied.text

    await _grant(db_session, moderator, "message:manage")
    allowed = await client.post(
        f"{API}/demands/{demand.id}/replies/{reply.id}/revoke",
        headers=auth_headers(moderator),
    )
    assert allowed.status_code == 200, allowed.text

    await db_session.refresh(reply)
    assert reply.is_revoked == 1


async def test_reply_sender_can_revoke_without_manual_permission(client, db_session, scene):
    """资源归属规则保留：本人撤回自己的消息不需要 message:manage。"""
    creator = await _create_user(db_session, "requester", "self_creator")
    demand = await _make_demand(db_session, creator)
    reply = await _make_reply(db_session, demand, creator)
    resp = await client.post(
        f"{API}/demands/{demand.id}/replies/{reply.id}/revoke",
        headers=auth_headers(creator),
    )
    assert resp.status_code == 200, resp.text


# ---------------------------------------------------------------------------
# 10. 解锁超级管理员守卫（复审 P2）
# ---------------------------------------------------------------------------


async def test_unlock_super_admin_requires_super_admin(client, db_session):
    """普通用户即使被手动授予 admin:user，也不能解锁超级管理员账号。"""
    unlocked_normal = await _create_user(db_session, "builder", "normal_user")
    locked_normal = await _create_user(db_session, "builder", "locked_normal")
    locked_super = await _create_user(db_session, "super_admin", "locked_super")
    other_super = await _create_user(db_session, "super_admin", "active_super")
    for user in (locked_super, locked_normal):
        user.is_locked = 1
    await db_session.commit()

    # 非超管角色默认没有 admin:user（全是超管才有），这里手动补上以命中守卫
    assert "admin:user" not in await _me_permissions(client, unlocked_normal)
    await _grant(db_session, unlocked_normal, "admin:user")
    assert "admin:user" in await _me_permissions(client, unlocked_normal)

    # 拥有 admin:user 的普通用户：不能解锁超级管理员
    forbidden = await client.post(
        f"{API}/admin/users/{locked_super.id}/unlock", headers=auth_headers(unlocked_normal)
    )
    assert forbidden.status_code == 403, forbidden.text
    assert "只有超级管理员可以解锁超级管理员" in forbidden.json()["detail"]

    # 普通管理员仍可按预期解锁普通用户
    ok_normal = await client.post(
        f"{API}/admin/users/{locked_normal.id}/unlock", headers=auth_headers(unlocked_normal)
    )
    assert ok_normal.status_code == 200, ok_normal.text

    # 超级管理员可以解锁其他超级管理员
    ok_super = await client.post(
        f"{API}/admin/users/{locked_super.id}/unlock", headers=auth_headers(other_super)
    )
    assert ok_super.status_code == 200, ok_super.text

    await db_session.refresh(locked_super)
    assert locked_super.is_locked == 0
