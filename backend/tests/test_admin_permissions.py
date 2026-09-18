r"""
用户手动权限接口与鉴权测试（方案三）

覆盖链路：
  GET/PUT /api/v1/admin/users/{user_id}/permissions
    → services/admin.py::set_user_manual_permissions（替换语义 + 同事务审计日志）
    → dependencies/auth.py::require_permissions（最终权限 = 模板 ∪ 手动）

运行：
    uv run pytest tests/test_admin_permissions.py -v
"""

import uuid

from sqlalchemy import select

from app.models.admin import SystemLog, UserPermission

API = "/api/v1"
PERMISSIONS_PATH = f"{API}/admin/users/{{user_id}}/permissions"
SYSTEM_LOGS_PATH = f"{API}/admin/system-logs"


def permissions_url(user_id: str) -> str:
    return PERMISSIONS_PATH.replace("{user_id}", user_id)


def _uid(prefix: str = "id") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


async def _register_user(client, fake_redis, *, username: str, phone: str) -> dict:
    """注册一个用户并登录，返回 {id, token}。"""
    await fake_redis.set(f"sms_code:register:{phone}", "123456", ex=300)
    reg = await client.post(
        f"{API}/auth/register",
        json={"username": username, "phone": phone, "password": "pass1234", "sms_code": "123456"},
    )
    assert reg.status_code == 200, reg.text
    data = reg.json()["data"]
    return {"id": data["user"]["id"], "token": data["access_token"]}


async def _set_role(db_session, user_id: str, role: str) -> None:
    from app.models.user import User

    user = (
        await db_session.execute(select(User).where(User.id == user_id))
    ).scalar_one()
    user.role = role
    await db_session.commit()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _login(client, username: str) -> str:
    resp = await client.post(f"{API}/auth/login", json={"username": username, "password": "pass1234"})
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]["access_token"]


# ---------------------------------------------------------------------------
# 1. 查询角色模板、手动和最终权限
# ---------------------------------------------------------------------------


async def test_get_permissions_returns_template_manual_and_effective(client, fake_redis, db_session):
    admin = await _register_user(client, fake_redis, username="perm_admin_01", phone="13900000101")
    await _set_role(db_session, admin["id"], "super_admin")
    admin_token = await _login(client, "perm_admin_01")

    target = await _register_user(client, fake_redis, username="perm_target_01", phone="13900000102")

    resp = await client.get(permissions_url(target["id"]), headers=_auth(admin_token))
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["role"] == "requester"
    assert "demand:create" in data["template_permission_ids"]
    assert data["manual_permission_ids"] == []
    assert data["effective_permission_ids"] == sorted(set(data["template_permission_ids"]))


# ---------------------------------------------------------------------------
# 2. 添加手动权限
# ---------------------------------------------------------------------------


async def test_put_adds_manual_permissions(client, fake_redis, db_session):
    admin = await _register_user(client, fake_redis, username="perm_admin_02", phone="13900000201")
    await _set_role(db_session, admin["id"], "super_admin")
    admin_token = await _login(client, "perm_admin_02")

    target = await _register_user(client, fake_redis, username="perm_target_02", phone="13900000202")

    resp = await client.put(
        permissions_url(target["id"]),
        json={"manual_permission_ids": ["demand:archive", "file:delete"], "reason": "负责归档清理"},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["manual_permission_ids"] == ["demand:archive", "file:delete"]
    assert "demand:archive" in data["effective_permission_ids"]
    assert "demand:archive" not in data["template_permission_ids"]


# ---------------------------------------------------------------------------
# 3. 撤销手动权限（PUT 替换语义）
# ---------------------------------------------------------------------------


async def test_put_replaces_and_removes_manual_permissions(client, fake_redis, db_session):
    admin = await _register_user(client, fake_redis, username="perm_admin_03", phone="13900000301")
    await _set_role(db_session, admin["id"], "super_admin")
    admin_token = await _login(client, "perm_admin_03")

    target = await _register_user(client, fake_redis, username="perm_target_03", phone="13900000302")

    put1 = await client.put(
        permissions_url(target["id"]),
        json={"manual_permission_ids": ["demand:archive", "file:delete"], "reason": "首次授权"},
        headers=_auth(admin_token),
    )
    assert put1.status_code == 200

    # 替换为仅剩 file:delete → demand:archive 应被移除
    put2 = await client.put(
        permissions_url(target["id"]),
        json={"manual_permission_ids": ["file:delete"], "reason": "撤销归档权限"},
        headers=_auth(admin_token),
    )
    assert put2.status_code == 200
    data = put2.json()["data"]
    assert data["manual_permission_ids"] == ["file:delete"]
    assert "demand:archive" not in data["effective_permission_ids"]

    # 数据库层面确认记录已删除
    rows = (
        await db_session.execute(
            select(UserPermission).where(
                UserPermission.user_id == target["id"],
                UserPermission.permission_id == "demand:archive",
            )
        )
    ).scalars().all()
    assert rows == []


# ---------------------------------------------------------------------------
# 4. 重复权限不会重复存储
# ---------------------------------------------------------------------------


async def test_put_deduplicates_permission_ids(client, fake_redis, db_session):
    admin = await _register_user(client, fake_redis, username="perm_admin_04", phone="13900000401")
    await _set_role(db_session, admin["id"], "super_admin")
    admin_token = await _login(client, "perm_admin_04")

    target = await _register_user(client, fake_redis, username="perm_target_04", phone="13900000402")

    resp = await client.put(
        permissions_url(target["id"]),
        json={"manual_permission_ids": ["demand:archive", "demand:archive", "file:delete"], "reason": "去重测试"},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["manual_permission_ids"] == ["demand:archive", "file:delete"]

    rows = (
        await db_session.execute(
            select(UserPermission).where(UserPermission.user_id == target["id"])
        )
    ).scalars().all()
    assert len(rows) == 2


# ---------------------------------------------------------------------------
# 5. 非法权限 ID 被拒绝
# ---------------------------------------------------------------------------


async def test_put_rejects_invalid_permission_ids(client, fake_redis, db_session):
    admin = await _register_user(client, fake_redis, username="perm_admin_05", phone="13900000501")
    await _set_role(db_session, admin["id"], "super_admin")
    admin_token = await _login(client, "perm_admin_05")

    target = await _register_user(client, fake_redis, username="perm_target_05", phone="13900000502")

    resp = await client.put(
        permissions_url(target["id"]),
        json={"manual_permission_ids": ["demand:archive", "not:a:permission"], "reason": "非法 ID"},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 400
    assert "not:a:permission" in resp.json()["detail"]

    # 无任何权限被写入
    rows = (
        await db_session.execute(
            select(UserPermission).where(UserPermission.user_id == target["id"])
        )
    ).scalars().all()
    assert rows == []


# ---------------------------------------------------------------------------
# 6. 空调整原因被拒绝
# ---------------------------------------------------------------------------


async def test_put_rejects_empty_reason(client, fake_redis, db_session):
    admin = await _register_user(client, fake_redis, username="perm_admin_06", phone="13900000601")
    await _set_role(db_session, admin["id"], "super_admin")
    admin_token = await _login(client, "perm_admin_06")

    target = await _register_user(client, fake_redis, username="perm_target_06", phone="13900000602")

    resp = await client.put(
        permissions_url(target["id"]),
        json={"manual_permission_ids": ["demand:archive"], "reason": "   "},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 7. 目标用户不存在时返回 404
# ---------------------------------------------------------------------------


async def test_put_and_get_return_404_for_missing_user(client, fake_redis, db_session):
    admin = await _register_user(client, fake_redis, username="perm_admin_07", phone="13900000701")
    await _set_role(db_session, admin["id"], "super_admin")
    admin_token = await _login(client, "perm_admin_07")

    missing_id = _uid("missing")
    resp_get = await client.get(permissions_url(missing_id), headers=_auth(admin_token))
    assert resp_get.status_code == 404

    resp_put = await client.put(
        permissions_url(missing_id),
        json={"manual_permission_ids": [], "reason": "目标不存在"},
        headers=_auth(admin_token),
    )
    assert resp_put.status_code == 404


# ---------------------------------------------------------------------------
# 8. 非管理员访问时返回 403
# ---------------------------------------------------------------------------


async def test_non_admin_gets_403(client, fake_redis, db_session):
    requester = await _register_user(client, fake_redis, username="perm_req_08", phone="13900000801")
    target = await _register_user(client, fake_redis, username="perm_target_08", phone="13900000802")

    resp_get = await client.get(permissions_url(target["id"]), headers=_auth(requester["token"]))
    assert resp_get.status_code == 403

    resp_put = await client.put(
        permissions_url(target["id"]),
        json={"manual_permission_ids": ["demand:archive"], "reason": "越权尝试"},
        headers=_auth(requester["token"]),
    )
    assert resp_put.status_code == 403


# ---------------------------------------------------------------------------
# 9. 权限修改后 require_permissions 立即生效
# ---------------------------------------------------------------------------


async def test_manual_permission_takes_effect_immediately(client, fake_redis, db_session):
    admin = await _register_user(client, fake_redis, username="perm_admin_09", phone="13900000901")
    await _set_role(db_session, admin["id"], "super_admin")
    admin_token = await _login(client, "perm_admin_09")

    builder = await _register_user(client, fake_redis, username="perm_builder_09", phone="13900000902")
    await _set_role(db_session, builder["id"], "builder")
    # 重新登录，让 token 携带 builder 角色
    builder_token = await _login(client, "perm_builder_09")

    # builder 没有 admin:log → 403
    before = await client.get(SYSTEM_LOGS_PATH, headers=_auth(builder_token))
    assert before.status_code == 403

    # 管理员手动追加 admin:log
    grant = await client.put(
        permissions_url(builder["id"]),
        json={"manual_permission_ids": ["admin:log"], "reason": "临时审计支援"},
        headers=_auth(admin_token),
    )
    assert grant.status_code == 200

    # 追加后立即生效 → 200
    after = await client.get(SYSTEM_LOGS_PATH, headers=_auth(builder_token))
    assert after.status_code == 200

    # 撤销后又恢复 403
    revoke = await client.put(
        permissions_url(builder["id"]),
        json={"manual_permission_ids": [], "reason": "审计支援结束"},
        headers=_auth(admin_token),
    )
    assert revoke.status_code == 200
    final = await client.get(SYSTEM_LOGS_PATH, headers=_auth(builder_token))
    assert final.status_code == 403


# ---------------------------------------------------------------------------
# 10. 权限变更产生完整系统日志
# ---------------------------------------------------------------------------


async def test_permission_change_writes_audit_log(client, fake_redis, db_session):
    admin = await _register_user(client, fake_redis, username="perm_admin_10", phone="13900001001")
    await _set_role(db_session, admin["id"], "super_admin")
    admin_token = await _login(client, "perm_admin_10")

    target = await _register_user(client, fake_redis, username="perm_target_10", phone="13900001002")

    await client.put(
        permissions_url(target["id"]),
        json={"manual_permission_ids": ["demand:archive"], "reason": "首次授权"},
        headers=_auth(admin_token),
    )
    await client.put(
        permissions_url(target["id"]),
        json={"manual_permission_ids": ["file:delete"], "reason": "改授文件删除"},
        headers=_auth(admin_token),
    )

    logs = (
        await db_session.execute(
            select(SystemLog).where(
                SystemLog.action == "update_user_permissions",
                SystemLog.target_id == target["id"],
            )
        )
    ).scalars().all()
    assert len(logs) == 2

    import json as _json

    second = sorted(logs, key=lambda log: log.created_at)[1]
    detail = _json.loads(second.detail)
    assert detail["added"] == ["file:delete"]
    assert detail["removed"] == ["demand:archive"]
    assert detail["reason"] == "改授文件删除"
    assert detail["operator"] == admin["id"]
    assert second.actor_id == admin["id"]
    assert second.target_type == "user"


# ---------------------------------------------------------------------------
# 11. 数据库异常时权限和日志一起回滚
# ---------------------------------------------------------------------------


async def test_permission_and_log_rollback_together(
    client, fake_redis, db_session, monkeypatch
):
    admin = await _register_user(client, fake_redis, username="perm_admin_11", phone="13900001101")
    await _set_role(db_session, admin["id"], "super_admin")
    admin_token = await _login(client, "perm_admin_11")

    target = await _register_user(client, fake_redis, username="perm_target_11", phone="13900001102")

    # 先写入一条手动权限作为初始状态
    put1 = await client.put(
        permissions_url(target["id"]),
        json={"manual_permission_ids": ["demand:archive"], "reason": "初始授权"},
        headers=_auth(admin_token),
    )
    assert put1.status_code == 200

    # 模拟审计日志写入失败：权限与日志在同一事务中，应整体回滚
    def _boom(*args, **kwargs):
        raise RuntimeError("simulated log failure")

    monkeypatch.setattr("app.services.admin._build_permission_change_log", _boom)

    put2 = await client.put(
        permissions_url(target["id"]),
        json={"manual_permission_ids": ["file:delete"], "reason": "应回滚的变更"},
        headers=_auth(admin_token),
    )
    assert put2.status_code == 500

    # 权限保持初始状态，没有被部分写入
    get1 = await client.get(permissions_url(target["id"]), headers=_auth(admin_token))
    assert get1.status_code == 200
    assert get1.json()["data"]["manual_permission_ids"] == ["demand:archive"]

    # 失败的变更没有留下审计日志
    import json as _json

    logs = (
        await db_session.execute(
            select(SystemLog).where(
                SystemLog.action == "update_user_permissions",
                SystemLog.target_id == target["id"],
            )
        )
    ).scalars().all()
    reasons = [_json.loads(log.detail)["reason"] for log in logs]
    assert "应回滚的变更" not in reasons
    assert "初始授权" in reasons


# ---------------------------------------------------------------------------
# 补充：/me/permissions 返回最终权限
# ---------------------------------------------------------------------------


async def test_me_permissions_includes_manual(client, fake_redis, db_session):
    admin = await _register_user(client, fake_redis, username="perm_admin_12", phone="13900001201")
    await _set_role(db_session, admin["id"], "super_admin")
    admin_token = await _login(client, "perm_admin_12")

    requester = await _register_user(client, fake_redis, username="perm_req_12", phone="13900001202")

    # 授权前：requester 模板里没有 demand:archive
    before = await client.get(f"{API}/me/permissions", headers=_auth(requester["token"]))
    assert before.status_code == 200
    assert "demand:archive" not in before.json()["data"]

    await client.put(
        permissions_url(requester["id"]),
        json={"manual_permission_ids": ["demand:archive"], "reason": "首页展示需要"},
        headers=_auth(admin_token),
    )

    after = await client.get(f"{API}/me/permissions", headers=_auth(requester["token"]))
    assert after.status_code == 200
    assert "demand:archive" in after.json()["data"]


# ---------------------------------------------------------------------------
# 补充：超级管理员不能通过手动权限接口调整
# ---------------------------------------------------------------------------


async def test_super_admin_target_rejected(client, fake_redis, db_session):
    admin = await _register_user(client, fake_redis, username="perm_admin_13", phone="13900001301")
    await _set_role(db_session, admin["id"], "super_admin")
    admin_token = await _login(client, "perm_admin_13")

    another_admin = await _register_user(client, fake_redis, username="perm_sa_13", phone="13900001302")
    await _set_role(db_session, another_admin["id"], "super_admin")

    resp = await client.put(
        permissions_url(another_admin["id"]),
        json={"manual_permission_ids": ["demand:archive"], "reason": "尝试调整超管"},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 400
