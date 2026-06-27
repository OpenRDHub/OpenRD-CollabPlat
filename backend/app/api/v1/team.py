from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user, require_permissions
from app.dependencies.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.team import (
    ApproveApplicationRequest,
    AssignmentOut,
    InviteMemberRequest,
    JoinApplicationOut,
    JoinApplicationRequest,
    RejectApplicationRequest,
    SaveAssignmentsRequest,
    TaskMemberOut,
    TeamDetailOut,
    TransferLeaderRequest,
    UpdateMemberRequest,
)
from app.services.task import get_task_by_id
from app.services.team import (
    approve_application,
    create_join_application,
    get_application_by_id,
    get_member_by_id,
    get_team_detail,
    invite_member,
    is_task_member_or_leader,
    reject_application,
    save_assignments,
    transfer_leader,
    update_member,
)
from app.services.user import get_user_by_platform_id

router = APIRouter(tags=["团队协作"])


@router.get("/tasks/{task_id}/team", response_model=ApiResponse[TeamDetailOut])
async def get_team(
    task_id: str,
    current_user: dict = Depends(require_permissions("member:view")),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    detail = await get_team_detail(db, task_id)
    return ApiResponse(data=TeamDetailOut(
        task_id=detail["task_id"],
        leader_id=detail["leader_id"],
        members=[TaskMemberOut.model_validate(m) for m in detail["members"]],
        applications=[JoinApplicationOut.model_validate(a) for a in detail["applications"]],
        assignments=[AssignmentOut.model_validate(a) for a in detail["assignments"]],
    ))


@router.post("/tasks/{task_id}/join-applications", response_model=ApiResponse[JoinApplicationOut])
async def post_join_application(
    task_id: str,
    body: JoinApplicationRequest,
    current_user: dict = Depends(require_permissions("task:join")),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    if task.status != "recruiting":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前任务状态不接受申请")

    app = await create_join_application(
        db,
        task_id=task_id,
        user_id=current_user["user_id"],
        role=body.role,
        skills=body.skills,
        reason=body.reason,
    )
    if app is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="已有待审核的申请")
    return ApiResponse(data=JoinApplicationOut.model_validate(app))


@router.post(
    "/tasks/{task_id}/join-applications/{application_id}/approve",
    response_model=ApiResponse[TaskMemberOut],
)
async def post_approve_application(
    task_id: str,
    application_id: str,
    body: ApproveApplicationRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    is_leader = task.leader_id == current_user["user_id"]
    has_perm = current_user["role"] in ("operator", "super_admin")
    if not is_leader and not has_perm:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无审批权限")

    application = await get_application_by_id(db, application_id)
    if not application or application.task_id != task_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="申请不存在")
    if application.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="申请已处理")

    member = await approve_application(
        db, application, reviewer_id=current_user["user_id"], duty=body.duty
    )
    return ApiResponse(data=TaskMemberOut.model_validate(member))


@router.post(
    "/tasks/{task_id}/join-applications/{application_id}/reject",
    response_model=ApiResponse[JoinApplicationOut],
)
async def post_reject_application(
    task_id: str,
    application_id: str,
    body: RejectApplicationRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    is_leader = task.leader_id == current_user["user_id"]
    has_perm = current_user["role"] in ("operator", "super_admin")
    if not is_leader and not has_perm:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无审批权限")

    application = await get_application_by_id(db, application_id)
    if not application or application.task_id != task_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="申请不存在")
    if application.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="申请已处理")

    result = await reject_application(
        db, application, reviewer_id=current_user["user_id"], reason=body.reason
    )
    return ApiResponse(data=JoinApplicationOut.model_validate(result))


@router.post("/tasks/{task_id}/members/invite", response_model=ApiResponse[TaskMemberOut])
async def post_invite_member(
    task_id: str,
    body: InviteMemberRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    is_leader = task.leader_id == current_user["user_id"]
    has_perm = current_user["role"] in ("operator", "super_admin")
    if not is_leader and not has_perm:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无邀请权限")

    target_user = await get_user_by_platform_id(db, body.platform_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="目标用户不存在")

    member = await invite_member(
        db,
        task_id=task_id,
        user_id=target_user.id,
        role=body.suggested_role,
    )
    return ApiResponse(data=TaskMemberOut.model_validate(member))


@router.patch("/tasks/{task_id}/members/{member_id}", response_model=ApiResponse[TaskMemberOut])
async def patch_member(
    task_id: str,
    member_id: str,
    body: UpdateMemberRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    is_leader = task.leader_id == current_user["user_id"]
    has_perm = current_user["role"] in ("operator", "super_admin")
    if not is_leader and not has_perm:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无修改权限")

    member = await get_member_by_id(db, member_id)
    if not member or member.task_id != task_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="成员不存在")

    updates = body.model_dump(exclude_unset=True)
    member = await update_member(db, member, **updates)
    return ApiResponse(data=TaskMemberOut.model_validate(member))


@router.post("/tasks/{task_id}/leader/transfer", response_model=ApiResponse)
async def post_transfer_leader(
    task_id: str,
    body: TransferLeaderRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    is_leader = task.leader_id == current_user["user_id"]
    is_owner = task.owner_id == current_user["user_id"]
    is_admin = current_user["role"] in ("operator", "super_admin")
    if not is_leader and not is_owner and not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无转移队长权限")

    is_member = await is_task_member_or_leader(db, task_id, body.new_leader_id)
    if not is_member:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="目标用户不是队伍成员")

    result = await transfer_leader(db, task_id=task_id, new_leader_id=body.new_leader_id)
    return ApiResponse(data={"task_id": task_id, "new_leader_id": body.new_leader_id})


@router.put("/tasks/{task_id}/assignments", response_model=ApiResponse[list[AssignmentOut]])
async def put_assignments(
    task_id: str,
    body: SaveAssignmentsRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")

    is_leader = task.leader_id == current_user["user_id"]
    has_perm = current_user["role"] in ("operator", "super_admin")
    if not is_leader and not has_perm:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无分工管理权限")

    assignments_data = [item.model_dump() for item in body.assignments]
    result = await save_assignments(db, task_id=task_id, assignments_data=assignments_data)
    return ApiResponse(data=[AssignmentOut.model_validate(a) for a in result])
