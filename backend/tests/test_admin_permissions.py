r"""
用户授权接口与鉴权测试（PR #49 第二轮：P1 安全修复）

覆盖链路：
  GET  /api/v1/admin/users/{user_id}/permissions      查询模板/手动/最终权限
  PUT  /api/v1/admin/users/{user_id}/authorization    单事务「角色+权限+日志」
    → services/admin.py::set_user_authorization（替换语义 + 同事务审计日志）
    → dependencies/auth.py::get_current_user（以数据库当前角色为准）
    → 五条防提权守卫 + PATCH/lock 接口角色守卫

运行：
    uv run pytest tests/test_admin_permissions.py -v
"""

import json as _json
import uuid

from sqlalchemy import select

from app.models.admin import SystemLog, UserPermission
from app.models.user import User

API = "/api/v1"
PERMISSIONS_PATH = f"{API}/admin/users/{{user_id}}/permissions"
AUTHORIZATION_PATH = f"{API}/admin/users/{{user_id}}/authorization"
SYSTEM_LOGS_PATH = f"{API}/admin/system-logs"
ADMIN_USERS_PATH = f"{API}/admin/users"
TASKS_PATH = f"{API}/tasks"


def permissions_url(user_id: str) -> str:
    return PERMISSIONS_PATH.replace("{user_id}", user_id)


def authorization_url(user_id: str) -> str:
    return AUTHORIZATION_PATH.replace("{user_id}", user_id)


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


async def _make_super_admin(client, fake_redis, db_session, *, username: str, phone: str) -> dict:
    """注册用户并提升为超级管理员，返回 {id, token}。"""
    account = await _register_user(client, fake_redis, username=username, phone=phone)
    await _set_role(db_session, account["id"], "super_admin")
    account["token"] = await _login(client, username)
    return account


# ---------------------------------------------------------------------------
# 1. 查询角色模板、手动和最终权限
# ---------------------------------------------------------------------------


async def test_get_permissions_returns_template_manual_and_effective(client, fake_redis, db_session):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_01", phone="13900000101")

    target = await _register_user(client, fake_redis, username="auth_target_01", phone="13900000102")

    resp = await client.get(permissions_url(target["id"]), headers=_auth(admin["token"]))
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["role"] == "requester"
    assert "demand:create" in data["template_permission_ids"]
    assert data["manual_permission_ids"] == []
    assert data["effective_permission_ids"] == sorted(set(data["template_permission_ids"]))


# ---------------------------------------------------------------------------
# 2. 添加手动权限
# ---------------------------------------------------------------------------


async def test_authorization_adds_manual_permissions(client, fake_redis, db_session):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_02", phone="13900000201")

    target = await _register_user(client, fake_redis, username="auth_target_02", phone="13900000202")

    resp = await client.put(
        authorization_url(target["id"]),
        json={
            "role": "requester",
            "manual_permission_ids": ["demand:archive", "file:delete"],
            "reason": "负责归档清理",
        },
        headers=_auth(admin["token"]),
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["role"] == "requester"
    assert data["manual_permission_ids"] == ["demand:archive", "file:delete"]
    assert "demand:archive" in data["effective_permission_ids"]
    assert "demand:archive" not in data["template_permission_ids"]


# ---------------------------------------------------------------------------
# 3. 撤销手动权限（替换语义）
# ---------------------------------------------------------------------------


async def test_authorization_replaces_and_removes_manual_permissions(client, fake_redis, db_session):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_03", phone="13900000301")

    target = await _register_user(client, fake_redis, username="auth_target_03", phone="13900000302")

    put1 = await client.put(
        authorization_url(target["id"]),
        json={
            "role": "requester",
            "manual_permission_ids": ["demand:archive", "file:delete"],
            "reason": "首次授权",
        },
        headers=_auth(admin["token"]),
    )
    assert put1.status_code == 200

    # 替换为仅剩 file:delete → demand:archive 应被移除
    put2 = await client.put(
        authorization_url(target["id"]),
        json={"role": "requester", "manual_permission_ids": ["file:delete"], "reason": "撤销归档权限"},
        headers=_auth(admin["token"]),
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


async def test_authorization_deduplicates_permission_ids(client, fake_redis, db_session):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_04", phone="13900000401")

    target = await _register_user(client, fake_redis, username="auth_target_04", phone="13900000402")

    resp = await client.put(
        authorization_url(target["id"]),
        json={
            "role": "requester",
            "manual_permission_ids": ["demand:archive", "demand:archive", "file:delete"],
            "reason": "去重测试",
        },
        headers=_auth(admin["token"]),
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


async def test_authorization_rejects_invalid_permission_ids(client, fake_redis, db_session):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_05", phone="13900000501")

    target = await _register_user(client, fake_redis, username="auth_target_05", phone="13900000502")

    resp = await client.put(
        authorization_url(target["id"]),
        json={
            "role": "requester",
            "manual_permission_ids": ["demand:archive", "not:a:permission"],
            "reason": "非法 ID",
        },
        headers=_auth(admin["token"]),
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
# 6. 纯空格调整原因被拒绝
# ---------------------------------------------------------------------------


async def test_authorization_rejects_blank_reason(client, fake_redis, db_session):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_06", phone="13900000601")

    target = await _register_user(client, fake_redis, username="auth_target_06", phone="13900000602")

    resp = await client.put(
        authorization_url(target["id"]),
        json={"role": "requester", "manual_permission_ids": ["demand:archive"], "reason": "   "},
        headers=_auth(admin["token"]),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 7. 目标用户不存在时返回 404
# ---------------------------------------------------------------------------


async def test_authorization_returns_404_for_missing_user(client, fake_redis, db_session):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_07", phone="13900000701")

    missing_id = _uid("missing")
    resp_get = await client.get(permissions_url(missing_id), headers=_auth(admin["token"]))
    assert resp_get.status_code == 404

    resp_put = await client.put(
        authorization_url(missing_id),
        json={"role": "requester", "manual_permission_ids": [], "reason": "目标不存在"},
        headers=_auth(admin["token"]),
    )
    assert resp_put.status_code == 404


# ---------------------------------------------------------------------------
# 8. 非管理员访问时返回 403
# ---------------------------------------------------------------------------


async def test_non_admin_gets_403(client, fake_redis, db_session):
    requester = await _register_user(client, fake_redis, username="auth_req_08", phone="13900000801")
    target = await _register_user(client, fake_redis, username="auth_target_08", phone="13900000802")

    resp_get = await client.get(permissions_url(target["id"]), headers=_auth(requester["token"]))
    assert resp_get.status_code == 403

    resp_put = await client.put(
        authorization_url(target["id"]),
        json={"role": "requester", "manual_permission_ids": ["demand:archive"], "reason": "越权尝试"},
        headers=_auth(requester["token"]),
    )
    assert resp_put.status_code == 403


# ---------------------------------------------------------------------------
# 9. 手动权限修改后 require_permissions 立即生效
# ---------------------------------------------------------------------------


async def test_manual_permission_takes_effect_immediately(client, fake_redis, db_session):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_09", phone="13900000901")

    builder = await _register_user(client, fake_redis, username="auth_builder_09", phone="13900000902")
    await _set_role(db_session, builder["id"], "builder")
    builder_token = await _login(client, "auth_builder_09")

    # builder 没有 admin:log → 403
    before = await client.get(SYSTEM_LOGS_PATH, headers=_auth(builder_token))
    assert before.status_code == 403

    # 管理员手动追加 admin:log
    grant = await client.put(
        authorization_url(builder["id"]),
        json={"role": "builder", "manual_permission_ids": ["admin:log"], "reason": "临时审计支援"},
        headers=_auth(admin["token"]),
    )
    assert grant.status_code == 200

    # 追加后立即生效 → 200
    after = await client.get(SYSTEM_LOGS_PATH, headers=_auth(builder_token))
    assert after.status_code == 200

    # 撤销后又恢复 403
    revoke = await client.put(
        authorization_url(builder["id"]),
        json={"role": "builder", "manual_permission_ids": [], "reason": "审计支援结束"},
        headers=_auth(admin["token"]),
    )
    assert revoke.status_code == 200
    final = await client.get(SYSTEM_LOGS_PATH, headers=_auth(builder_token))
    assert final.status_code == 403


# ---------------------------------------------------------------------------
# 10. 权限变更产生完整系统日志
# ---------------------------------------------------------------------------


async def test_permission_change_writes_audit_log(client, fake_redis, db_session):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_10", phone="13900001001")

    target = await _register_user(client, fake_redis, username="auth_target_10", phone="13900001002")

    await client.put(
        authorization_url(target["id"]),
        json={"role": "requester", "manual_permission_ids": ["demand:archive"], "reason": "首次授权"},
        headers=_auth(admin["token"]),
    )
    await client.put(
        authorization_url(target["id"]),
        json={"role": "requester", "manual_permission_ids": ["file:delete"], "reason": "改授文件删除"},
        headers=_auth(admin["token"]),
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
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_11", phone="13900001101")

    target = await _register_user(client, fake_redis, username="auth_target_11", phone="13900001102")

    # 先写入一条手动权限作为初始状态
    put1 = await client.put(
        authorization_url(target["id"]),
        json={"role": "requester", "manual_permission_ids": ["demand:archive"], "reason": "初始授权"},
        headers=_auth(admin["token"]),
    )
    assert put1.status_code == 200

    # 模拟审计日志写入失败：权限与日志在同一事务中，应整体回滚
    def _boom(*args, **kwargs):
        raise RuntimeError("simulated log failure")

    monkeypatch.setattr("app.services.admin._build_permission_change_log", _boom)

    put2 = await client.put(
        authorization_url(target["id"]),
        json={"role": "requester", "manual_permission_ids": ["file:delete"], "reason": "应回滚的变更"},
        headers=_auth(admin["token"]),
    )
    assert put2.status_code == 500

    # 权限保持初始状态，没有被部分写入
    get1 = await client.get(permissions_url(target["id"]), headers=_auth(admin["token"]))
    assert get1.status_code == 200
    assert get1.json()["data"]["manual_permission_ids"] == ["demand:archive"]

    # 失败的变更没有留下审计日志
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
# 12. /me/permissions 返回最终权限
# ---------------------------------------------------------------------------


async def test_me_permissions_includes_manual(client, fake_redis, db_session):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_12", phone="13900001201")

    requester = await _register_user(client, fake_redis, username="auth_req_12", phone="13900001202")

    # 授权前：requester 模板里没有 demand:archive
    before = await client.get(f"{API}/me/permissions", headers=_auth(requester["token"]))
    assert before.status_code == 200
    assert "demand:archive" not in before.json()["data"]

    await client.put(
        authorization_url(requester["id"]),
        json={"role": "requester", "manual_permission_ids": ["demand:archive"], "reason": "首页展示需要"},
        headers=_auth(admin["token"]),
    )

    after = await client.get(f"{API}/me/permissions", headers=_auth(requester["token"]))
    assert after.status_code == 200
    assert "demand:archive" in after.json()["data"]


# ---------------------------------------------------------------------------
# 13. 守卫 1：不能修改自己的授权
# ---------------------------------------------------------------------------


async def test_cannot_modify_own_authorization(client, fake_redis, db_session):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_13", phone="13900001301")

    resp = await client.put(
        authorization_url(admin["id"]),
        json={"role": "super_admin", "manual_permission_ids": [], "reason": "调整自己"},
        headers=_auth(admin["token"]),
    )
    assert resp.status_code == 403
    assert "不能修改自己的授权" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# 14. 守卫 2：非超级管理员不能变更角色
# ---------------------------------------------------------------------------


async def test_non_super_cannot_change_role(client, fake_redis, db_session):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_14", phone="13900001401")

    # 运营管理员通过手动授权获得 admin:role（但不具备变更角色的资格）
    operator = await _register_user(client, fake_redis, username="auth_oper_14", phone="13900001402")
    await _set_role(db_session, operator["id"], "operator")
    grant = await client.put(
        authorization_url(operator["id"]),
        json={"role": "operator", "manual_permission_ids": ["admin:role"], "reason": "临时权限管理员"},
        headers=_auth(admin["token"]),
    )
    assert grant.status_code == 200

    target = await _register_user(client, fake_redis, username="auth_target_14", phone="13900001403")

    resp = await client.put(
        authorization_url(target["id"]),
        json={"role": "builder", "manual_permission_ids": [], "reason": "尝试变更角色"},
        headers=_auth(operator["token"]),
    )
    assert resp.status_code == 403
    assert "只有超级管理员可以变更角色" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# 15. 守卫 4：非超级管理员不能授予超出自身权限的权限
# ---------------------------------------------------------------------------


async def test_non_super_cannot_grant_beyond_own_permissions(client, fake_redis, db_session):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_15", phone="13900001501")

    # 运营管理员只有 admin:role 一个管理权限（admin:log 不在其权限范围内）
    operator = await _register_user(client, fake_redis, username="auth_oper_15", phone="13900001502")
    await _set_role(db_session, operator["id"], "operator")
    grant = await client.put(
        authorization_url(operator["id"]),
        json={"role": "operator", "manual_permission_ids": ["admin:role"], "reason": "临时权限管理员"},
        headers=_auth(admin["token"]),
    )
    assert grant.status_code == 200

    target = await _register_user(client, fake_redis, username="auth_target_15", phone="13900001503")

    # 授予自己没有的 admin:log → 403
    beyond = await client.put(
        authorization_url(target["id"]),
        json={"role": "requester", "manual_permission_ids": ["admin:log"], "reason": "越权授予"},
        headers=_auth(operator["token"]),
    )
    assert beyond.status_code == 403
    assert "超出自身权限范围" in beyond.json()["detail"]

    # 授予自己拥有的 admin:role → 允许
    within = await client.put(
        authorization_url(target["id"]),
        json={"role": "requester", "manual_permission_ids": ["admin:role"], "reason": "正常授予"},
        headers=_auth(operator["token"]),
    )
    assert within.status_code == 200


# ---------------------------------------------------------------------------
# 16. 守卫 3：非超级管理员不能调整超级管理员，也不能授予 super_admin 角色
# ---------------------------------------------------------------------------


async def test_non_super_cannot_touch_super_admin(client, fake_redis, db_session):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_16", phone="13900001601")

    operator = await _register_user(client, fake_redis, username="auth_oper_16", phone="13900001602")
    await _set_role(db_session, operator["id"], "operator")
    grant = await client.put(
        authorization_url(operator["id"]),
        json={"role": "operator", "manual_permission_ids": ["admin:role"], "reason": "临时权限管理员"},
        headers=_auth(admin["token"]),
    )
    assert grant.status_code == 200

    # 调整超级管理员目标 → 403
    touch_super = await client.put(
        authorization_url(admin["id"]),
        json={"role": "super_admin", "manual_permission_ids": [], "reason": "尝试调整超管"},
        headers=_auth(operator["token"]),
    )
    assert touch_super.status_code == 403
    assert "超级管理员" in touch_super.json()["detail"]

    # 把普通用户提升为 super_admin → 403
    target = await _register_user(client, fake_redis, username="auth_target_16", phone="13900001603")
    promote = await client.put(
        authorization_url(target["id"]),
        json={"role": "super_admin", "manual_permission_ids": [], "reason": "尝试制造超管"},
        headers=_auth(operator["token"]),
    )
    assert promote.status_code == 403


# ---------------------------------------------------------------------------
# 17. 守卫 5：最后一个超级管理员不能被降级
# ---------------------------------------------------------------------------


async def test_last_super_admin_cannot_be_demoted(client, fake_redis, db_session, monkeypatch):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_17", phone="13900001701")

    # 场景构造：目标也是超管，但系统中只剩 1 个超管（防止未来流程/并发场景移除最后一个超管）
    target = await _register_user(client, fake_redis, username="auth_sa_17", phone="13900001702")
    await _set_role(db_session, target["id"], "super_admin")

    async def _fake_count(db):
        return 1

    monkeypatch.setattr("app.api.v1.admin.count_super_admins", _fake_count)

    resp = await client.put(
        authorization_url(target["id"]),
        json={"role": "requester", "manual_permission_ids": [], "reason": "降级最后一个超管"},
        headers=_auth(admin["token"]),
    )
    assert resp.status_code == 400
    assert "最后一个超级管理员" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# 18. 角色降级后旧 Token 立即失效（鉴权以数据库当前角色为准）
# ---------------------------------------------------------------------------


async def test_role_downgrade_takes_effect_immediately(client, fake_redis, db_session):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_18", phone="13900001801")

    operator = await _register_user(client, fake_redis, username="auth_oper_18", phone="13900001802")
    await _set_role(db_session, operator["id"], "operator")
    # 不重新登录：故意使用注册时签发的旧 Token（JWT 中角色仍为 requester）

    # operator 拥有 task:manage → 权限检查通过（任务不存在返回 404 而非 403）
    before = await client.patch(
        f"{TASKS_PATH}/{_uid('task')}",
        json={"description": "test"},
        headers=_auth(operator["token"]),
    )
    assert before.status_code == 404

    # 超级管理员将 operator 降级为 requester
    downgrade = await client.put(
        authorization_url(operator["id"]),
        json={"role": "requester", "manual_permission_ids": [], "reason": "岗位调整"},
        headers=_auth(admin["token"]),
    )
    assert downgrade.status_code == 200
    assert downgrade.json()["data"]["role"] == "requester"

    # 同一个旧 Token：requester 没有 task:manage → 403（无需重新登录即生效）
    after = await client.patch(
        f"{TASKS_PATH}/{_uid('task')}",
        json={"description": "test"},
        headers=_auth(operator["token"]),
    )
    assert after.status_code == 403

    # /me/permissions 也随数据库角色实时变化
    perms = await client.get(f"{API}/me/permissions", headers=_auth(operator["token"]))
    assert perms.status_code == 200
    assert "task:manage" not in perms.json()["data"]


# ---------------------------------------------------------------------------
# 19. 角色变更产生独立审计日志
# ---------------------------------------------------------------------------


async def test_role_change_writes_audit_log(client, fake_redis, db_session):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_19", phone="13900001901")

    target = await _register_user(client, fake_redis, username="auth_target_19", phone="13900001902")

    resp = await client.put(
        authorization_url(target["id"]),
        json={"role": "builder", "manual_permission_ids": ["demand:archive"], "reason": "转共建者"},
        headers=_auth(admin["token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["role"] == "builder"

    logs = (
        await db_session.execute(
            select(SystemLog).where(
                SystemLog.action == "update_user_role",
                SystemLog.target_id == target["id"],
            )
        )
    ).scalars().all()
    assert len(logs) == 1
    detail = _json.loads(logs[0].detail)
    assert detail["old_role"] == "requester"
    assert detail["new_role"] == "builder"
    assert detail["reason"] == "转共建者"
    assert detail["operator"] == admin["id"]


# ---------------------------------------------------------------------------
# 20. 角色变更与权限变更原子生效（角色日志失败 → 角色不被修改）
# ---------------------------------------------------------------------------


async def test_role_change_and_permissions_atomic(client, fake_redis, db_session, monkeypatch):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_20", phone="13900002001")

    target = await _register_user(client, fake_redis, username="auth_target_20", phone="13900002002")

    def _boom(*args, **kwargs):
        raise RuntimeError("simulated role log failure")

    monkeypatch.setattr("app.services.admin._build_role_change_log", _boom)

    resp = await client.put(
        authorization_url(target["id"]),
        json={"role": "builder", "manual_permission_ids": ["demand:archive"], "reason": "应回滚的角色变更"},
        headers=_auth(admin["token"]),
    )
    assert resp.status_code == 500

    # 角色保持原状（未被部分写入）
    user = (
        await db_session.execute(select(User).where(User.id == target["id"]))
    ).scalar_one()
    assert user.role == "requester"

    # 手动权限同样没有写入
    rows = (
        await db_session.execute(
            select(UserPermission).where(UserPermission.user_id == target["id"])
        )
    ).scalars().all()
    assert rows == []


# ---------------------------------------------------------------------------
# 21. PATCH /admin/users/{id} 角色变更守卫
# ---------------------------------------------------------------------------


async def test_patch_user_role_guards(client, fake_redis, db_session, monkeypatch):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_21", phone="13900002101")

    # 运营管理员通过手动授权获得 admin:user（可以进用户管理，但不能改角色）
    operator = await _register_user(client, fake_redis, username="auth_oper_21", phone="13900002102")
    await _set_role(db_session, operator["id"], "operator")
    grant = await client.put(
        authorization_url(operator["id"]),
        json={"role": "operator", "manual_permission_ids": ["admin:user"], "reason": "用户管理支援"},
        headers=_auth(admin["token"]),
    )
    assert grant.status_code == 200

    target = await _register_user(client, fake_redis, username="auth_target_21", phone="13900002103")

    # 非超管改角色 → 403
    by_operator = await client.patch(
        f"{ADMIN_USERS_PATH}/{target['id']}",
        json={"role": "builder"},
        headers=_auth(operator["token"]),
    )
    assert by_operator.status_code == 403
    assert "只有超级管理员可以变更角色" in by_operator.json()["detail"]

    # 超管改自己的角色 → 403
    self_change = await client.patch(
        f"{ADMIN_USERS_PATH}/{admin['id']}",
        json={"role": "builder"},
        headers=_auth(admin["token"]),
    )
    assert self_change.status_code == 403
    assert "不能修改自己的角色" in self_change.json()["detail"]

    # 最后一个超管被降级 → 400（场景构造：count 固定为 1）
    another_super = await _register_user(client, fake_redis, username="auth_sa_21", phone="13900002104")
    await _set_role(db_session, another_super["id"], "super_admin")

    async def _fake_count(db):
        return 1

    monkeypatch.setattr("app.api.v1.user.count_super_admins", _fake_count)
    demote_last = await client.patch(
        f"{ADMIN_USERS_PATH}/{another_super['id']}",
        json={"role": "builder"},
        headers=_auth(admin["token"]),
    )
    assert demote_last.status_code == 400
    assert "最后一个超级管理员" in demote_last.json()["detail"]

    # 非角色字段不受守卫影响（运营管理员可以正常改昵称）
    ok = await client.patch(
        f"{ADMIN_USERS_PATH}/{target['id']}",
        json={"nickname": "新昵称"},
        headers=_auth(operator["token"]),
    )
    assert ok.status_code == 200


# ---------------------------------------------------------------------------
# 22. 锁定接口守卫：不能锁自己；超管只能被超管锁定；最后一个超管不可锁
# ---------------------------------------------------------------------------


async def test_lock_guards(client, fake_redis, db_session, monkeypatch):
    admin = await _make_super_admin(client, fake_redis, db_session, username="auth_admin_22", phone="13900002201")

    operator = await _register_user(client, fake_redis, username="auth_oper_22", phone="13900002202")
    await _set_role(db_session, operator["id"], "operator")
    grant = await client.put(
        authorization_url(operator["id"]),
        json={"role": "operator", "manual_permission_ids": ["admin:user"], "reason": "用户管理支援"},
        headers=_auth(admin["token"]),
    )
    assert grant.status_code == 200

    # 锁定自己 → 403
    lock_self = await client.post(
        f"{ADMIN_USERS_PATH}/{operator['id']}/lock",
        headers=_auth(operator["token"]),
    )
    assert lock_self.status_code == 403
    assert "不能锁定自己的账号" in lock_self.json()["detail"]

    # 非超管锁定超管 → 403
    lock_super = await client.post(
        f"{ADMIN_USERS_PATH}/{admin['id']}/lock",
        headers=_auth(operator["token"]),
    )
    assert lock_super.status_code == 403
    assert "只有超级管理员可以锁定超级管理员" in lock_super.json()["detail"]

    # 最后一个超管不可锁定：构造两名超管 A、B，monkeypatch count_super_admins=1，
    # 让 A 锁定 B 才会触发"最后一个超级管理员"守卫；若 A 直接锁定自己会先撞
    # "不能锁定自己的账号"，因此必须有第二个超管作为目标。
    another_super = await _register_user(
        client, fake_redis, username="auth_sa_22", phone="13900002204"
    )
    await _set_role(db_session, another_super["id"], "super_admin")

    async def _fake_count(_db):
        # 两个超管 A、B，仅暴露 1 个，模拟「系统剩最后一个」并发态
        return 1

    monkeypatch.setattr("app.api.v1.user.count_super_admins", _fake_count)
    lock_last = await client.post(
        f"{ADMIN_USERS_PATH}/{another_super['id']}/lock",
        headers=_auth(admin["token"]),
    )
    assert lock_last.status_code == 400
    assert "最后一个超级管理员" in lock_last.json()["detail"]

    # 解除 monkeypatch：A 锁普通用户 → 正常 200
    monkeypatch.undo()

    target = await _register_user(client, fake_redis, username="auth_target_22", phone="13900002203")
    ok = await client.post(
        f"{ADMIN_USERS_PATH}/{target['id']}/lock",
        headers=_auth(admin["token"]),
    )
    assert ok.status_code == 200


# ---------------------------------------------------------------------------
# 23. 锁定用户后旧 Token 立即失效（鉴权以数据库当前锁定态为准）
# ---------------------------------------------------------------------------


async def test_locked_user_old_token_is_rejected(client, fake_redis, db_session):
    admin = await _make_super_admin(
        client, fake_redis, db_session, username="auth_admin_23", phone="13900002301"
    )

    # 注册时即拿到 access token（JWT 角色 = requester）
    target = await _register_user(client, fake_redis, username="auth_target_23", phone="13900002302")

    # 锁定前：旧 Token 可访问 /me
    before = await client.get(f"{API}/me", headers=_auth(target["token"]))
    assert before.status_code == 200, before.text

    # 管理员锁定目标用户（JWT 中目标仍为 requester，数据库 is_locked 已被更新）
    lock_resp = await client.post(
        f"{ADMIN_USERS_PATH}/{target['id']}/lock",
        headers=_auth(admin["token"]),
    )
    assert lock_resp.status_code == 200, lock_resp.text

    # 同一个旧 Token：受保护接口立即 401（无需等到 JWT 自然过期）
    after = await client.get(f"{API}/me", headers=_auth(target["token"]))
    assert after.status_code == 401, after.text
    assert "锁定" in after.json()["detail"]

    # 校验其他受保护接口也立即拒绝
    me_perms = await client.get(f"{API}/me/permissions", headers=_auth(target["token"]))
    assert me_perms.status_code == 401
    assert "锁定" in me_perms.json()["detail"]


# ---------------------------------------------------------------------------
# 24. 两个超管并发互降：advisory lock 串行化「判断+变更」
# ---------------------------------------------------------------------------


async def test_concurrent_super_admin_demote_serialized(client, fake_redis, db_session):
    """两个超管同时互相降级，必须有至少一方被「最后一个超管」守卫拦截。"""
    import asyncio

    from app.services.admin import count_super_admins

    admin_a = await _make_super_admin(
        client, fake_redis, db_session, username="auth_admin_24a", phone="13900002401"
    )
    admin_b = await _make_super_admin(
        client, fake_redis, db_session, username="auth_admin_24b", phone="13900002402"
    )

    async def _demote(actor_token, target_id):
        return await client.put(
            authorization_url(target_id),
            json={"role": "requester", "manual_permission_ids": [], "reason": "并发降级测试"},
            headers=_auth(actor_token),
        )

    r1, r2 = await asyncio.gather(
        _demote(admin_a["token"], admin_b["id"]),
        _demote(admin_b["token"], admin_a["id"]),
    )

    codes = sorted([r1.status_code, r2.status_code])
    # 至少一方成功（200）、至少一方被拦截（400）
    assert 200 in codes and 400 in codes, f"期望 200/400 各一，实际 {codes}"

    n = await count_super_admins(db_session)
    assert n >= 1, f"至少应剩 1 个超管，实际 {n}"


async def test_concurrent_super_admin_lock_serialized(client, fake_redis, db_session):
    """两个超管同时互相锁定：至少有 1 个超管保持解锁。"""
    import asyncio

    admin_a = await _make_super_admin(
        client, fake_redis, db_session, username="auth_admin_25a", phone="13900002501"
    )
    admin_b = await _make_super_admin(
        client, fake_redis, db_session, username="auth_admin_25b", phone="13900002502"
    )

    async def _lock(actor_token, target_id):
        return await client.post(
            f"{ADMIN_USERS_PATH}/{target_id}/lock",
            headers=_auth(actor_token),
        )

    r1, r2 = await asyncio.gather(
        _lock(admin_a["token"], admin_b["id"]),
        _lock(admin_b["token"], admin_a["id"]),
    )

    codes = sorted([r1.status_code, r2.status_code])
    assert 200 in codes and 400 in codes, f"期望 200/400 各一，实际 {codes}"

    # 至少还有 1 个超管 未被锁
    not_locked = (
        await db_session.execute(
            select(User).where(
                User.id.in_([admin_a["id"], admin_b["id"]]),
                User.role == "super_admin",
                User.is_locked == 0,
            )
        )
    ).scalars().all()
    assert len(not_locked) >= 1, "至少应剩 1 个未锁定的超管"
