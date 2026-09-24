ALL_PERMISSIONS = {
    "demand:create",
    "demand:view",
    "demand:reply",
    "demand:convert",
    "demand:reject",
    "demand:link",
    "demand:archive",
    "task:view",
    "task:join",
    "task:update",
    "task:manage",
    "task:status",
    "member:view",
    "member:approve",
    "member:invite",
    "member:manage",
    "message:view",
    "message:manage",
    "file:upload",
    "file:delete",
    "admin:user",
    "admin:role",
    "admin:log",
}

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "requester": {
        "demand:create",
        "demand:view",
        "task:view",
        "message:view",
        "file:upload",
    },
    # 注意：builder 模板刻意不包含 task:update。
    # 普通任务成员本就不能提交进度（POST /tasks/{id}/progress 只认 owner / leader /
    # task:manage / 手动授权），放进模板会让 /me/permissions 暴露一个实际不可用的权限，
    # 并锁死权限管理页面的复选框。task:update 只作为管理员手动授予的平台级权限存在。
    "builder": {
        "demand:create",
        "demand:view",
        "task:view",
        "task:join",
        "member:view",
        "message:view",
        "file:upload",
    },
    "operator": {
        "demand:create",
        "demand:view",
        "demand:reply",
        "demand:convert",
        "demand:reject",
        "demand:link",
        "demand:archive",
        "task:view",
        "task:update",
        "task:manage",
        "task:status",
        "member:view",
        "member:approve",
        "member:invite",
        "member:manage",
        "message:view",
        "message:manage",
        "file:upload",
        "file:delete",
    },
    "super_admin": ALL_PERMISSIONS,
}


def get_permissions_for_role(role: str) -> set[str]:
    return ROLE_PERMISSIONS.get(role, set())
