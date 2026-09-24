r"""
PR #49：`task:update` 权限语义收敛测试

背景（负责人复审方案）：
  普通任务成员本就不应提交任务进度，但 builder 角色模板却带着 task:update，
  导致 /me/permissions 暴露一个「调用即 403」的权限，同时权限管理页面会把模板权限
  视为锁定项，使管理员无法再把 task:update 作为「手动权限」授予 builder。

修复后的语义：
  - builder 模板不再包含 task:update；
  - owner / leader 仍按资源归属提交进度，不要求额外权限；
  - operator / super_admin 通过 task:manage 提交进度；
  - task:update 只作为管理员手动授予的平台级权限存在（可更新不属于自己的任务进度）。

覆盖：
  1. 角色模板断言
  2. /me/permissions 三态（默认无 → 授予后有 → 撤销后无）
  3. 真实授权链路（全程走 PUT /admin/users/{user_id}/authorization，不直接插表）

运行：
    uv run pytest tests/test_task_update_permission.py -v
"""

from sqlalchemy import select

from app.core.permissions import ROLE_PERMISSIONS
from app.models.task import Task
from app.models.user import User
from app.services.task import create_task

API = "/api/v1"
AUTHORIZATION_PATH = f"{API}/admin/users/{{user_id}}/authorization"


def authorization_url(user_id: str) -> str:
    return AUTHORIZATION_PATH.replace("{user_id}", user_id)


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _register_user(client, fake_redis, *, username: str, phone: str) -> dict:
    """注册用户并拿到 token（JWT 角色仍是注册默认的 requester，鉴权以数据库为准）。"""
    await fake_redis.set(f"sms_code:register:{phone}", "123456", ex=300)
    reg = await client.post(
        f"{API}/auth/register",
        json={
            "username": username,
            "phone": phone,
            "password": "pass1234",
            "sms_code": "123456",
        },
    )
    assert reg.status_code == 200, reg.text
    data = reg.json()["data"]
    return {"id": data["user"]["id"], "token": data["access_token"]}


async def _set_role(db_session, user_id: str, role: str) -> None:
    user = (await db_session.execute(select(User).where(User.id == user_id))).scalar_one()
    user.role = role
    await db_session.commit()


async def _login(client, username: str) -> str:
    resp = await client.post(
        f"{API}/auth/login", json={"username": username, "password": "pass1234"}
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]["access_token"]


async def _make_super_admin(client, fake_redis, db_session, *, username: str, phone: str) -> dict:
    account = await _register_user(client, fake_redis, username=username, phone=phone)
    await _set_role(db_session, account["id"], "super_admin")
    account["token"] = await _login(client, username)
    return account


async def _me_permissions(client, token: str) -> list[str]:
    resp = await client.get(f"{API}/me/permissions", headers=_auth(token))
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]


async def _authorize(client, admin_token: str, user_id: str, permission_ids: list[str]):
    """通过真实授权接口设置手动权限（替换语义）。"""
    return await client.put(
        authorization_url(user_id),
        json={
            "role": "builder",
            "manual_permission_ids": permission_ids,
            "reason": "PR#49 task:update 权限收敛验收",
        },
        headers=_auth(admin_token),
    )


async def _set_task_status(db_session, task_id: str, status: str) -> None:
    task = await db_session.get(Task, task_id)
    task.status = status
    await db_session.commit()


async def _progress_token(db_session, task_id: str) -> str:
    """进度乐观锁令牌 = 任务当前 updated_at 的 ISO 字符串（每次成功提交都会推进）。"""
    task = await db_session.get(Task, task_id)
    await db_session.refresh(task)
    assert task.updated_at is not None, "任务 updated_at 为空，无法构造乐观锁令牌"
    return task.updated_at.isoformat()


async def _submit_progress(
    client, db_session, token: str, task_id: str, *, stage: str, base_stage: str
):
    return await client.post(
        f"{API}/tasks/{task_id}/progress",
        json={
            "stage": stage,
            "content": "task:update 权限链路测试",
            "base_stage": base_stage,
            "expected_updated_at": await _progress_token(db_session, task_id),
        },
        headers=_auth(token),
    )


# ---------------------------------------------------------------------------
# 1. 角色模板断言
# ---------------------------------------------------------------------------


def test_builder_template_no_longer_declares_task_update():
    """builder 模板不含 task:update，避免 /me/permissions 暴露不可用权限。"""
    assert "task:update" not in ROLE_PERMISSIONS["builder"]
    # 变更范围最小化：只动 builder，operator / super_admin 的平台级能力不受影响
    assert "task:manage" in ROLE_PERMISSIONS["operator"]
    assert "task:update" in ROLE_PERMISSIONS["operator"]
    assert "task:manage" in ROLE_PERMISSIONS["super_admin"]


def test_task_update_remains_a_grantable_permission():
    """task:update 仍留在权限全集里，否则管理员无法手动授予。"""
    from app.core.permissions import ALL_PERMISSIONS

    assert "task:update" in ALL_PERMISSIONS


# ---------------------------------------------------------------------------
# 2. /me/permissions 三态
# ---------------------------------------------------------------------------


async def test_me_permissions_reflects_manual_task_update(client, fake_redis, db_session):
    admin = await _make_super_admin(
        client, fake_redis, db_session, username="tu_admin_perms", phone="13900009201"
    )
    builder = await _register_user(client, fake_redis, username="tu_builder_perms", phone="13900009202")
    await _set_role(db_session, builder["id"], "builder")
    token = await _login(client, "tu_builder_perms")

    # 默认：builder 模板无 task:update
    assert "task:update" not in await _me_permissions(client, token)

    # 手动授予后出现
    grant = await _authorize(client, admin["token"], builder["id"], ["task:update"])
    assert grant.status_code == 200, grant.text
    assert "task:update" in await _me_permissions(client, token)

    # 撤销后消失
    revoke = await _authorize(client, admin["token"], builder["id"], [])
    assert revoke.status_code == 200, revoke.text
    assert "task:update" not in await _me_permissions(client, token)


# ---------------------------------------------------------------------------
# 3. 真实授权链路（端到端，不直接插表）
# ---------------------------------------------------------------------------


async def test_task_update_real_authorization_chain(client, fake_redis, db_session):
    """负责人复审方案第五节第 3 条：通过真实接口授权的完整链路。

    1. 创建普通 builder
    2. 默认权限不含 task:update
    3. 无法更新无归属关系的任务进度 → 403
    4. 超管通过授权接口授予 task:update
    5. /me/permissions 出现 task:update
    6. 用同一个旧 Token 再次提交进度 → 成功
    7. 通过授权接口撤销 task:update
    8. 同一个旧 Token 再次请求 → 立即恢复 403
    """
    admin = await _make_super_admin(
        client, fake_redis, db_session, username="tu_admin_chain", phone="13900009301"
    )

    # 任务负责人由另一个用户担任，保证目标 builder 与任务无任何归属关系
    owner = await _register_user(client, fake_redis, username="tu_owner_chain", phone="13900009302")
    await _set_role(db_session, owner["id"], "builder")

    # 1. 普通 builder
    builder = await _register_user(client, fake_redis, username="tu_outsider_chain", phone="13900009303")
    await _set_role(db_session, builder["id"], "builder")
    builder_token = await _login(client, "tu_outsider_chain")

    task = await create_task(
        db_session,
        title="task:update 真实授权链路任务",
        description="PR#49 复审用例",
        task_type="工具开发项目",
        priority="medium",
        owner_id=owner["id"],
    )
    await db_session.refresh(task)
    await _set_task_status(db_session, task.id, "in_progress")
    task_id = task.id

    # 2. 默认权限不含 task:update
    assert "task:update" not in await _me_permissions(client, builder_token)

    # 3. 无归属关系 → 403
    denied = await _submit_progress(
        client, db_session, builder_token, task_id, stage="develop", base_stage="team"
    )
    assert denied.status_code == 403, denied.text

    # 4. 超管通过真实授权接口手动授予
    grant = await _authorize(client, admin["token"], builder["id"], ["task:update"])
    assert grant.status_code == 200, grant.text
    assert grant.json()["data"]["manual_permission_ids"] == ["task:update"]
    assert "task:update" not in grant.json()["data"]["template_permission_ids"]

    # 5. /me/permissions 体现
    assert "task:update" in await _me_permissions(client, builder_token)

    # 6. 同一个旧 Token 再次提交 → 成功（无需重新登录）
    allowed = await _submit_progress(
        client, db_session, builder_token, task_id, stage="develop", base_stage="team"
    )
    assert allowed.status_code == 200, allowed.text

    # 7. 撤销授权
    revoke = await _authorize(client, admin["token"], builder["id"], [])
    assert revoke.status_code == 200, revoke.text
    assert revoke.json()["data"]["manual_permission_ids"] == []
    assert "task:update" not in await _me_permissions(client, builder_token)

    # 8. 同一个旧 Token 立即恢复 403
    revoked = await _submit_progress(
        client, db_session, builder_token, task_id, stage="beta", base_stage="develop"
    )
    assert revoked.status_code == 403, revoked.text
