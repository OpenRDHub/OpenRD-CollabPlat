import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.team import is_task_member_or_leader
from app.dependencies.auth import get_current_user, require_permissions
from app.dependencies.database import get_db
from app.schemas.common import ApiResponse, PaginatedData
from app.schemas.demand import (
    ConvertRequest,
    CreateDemandRequest,
    DemandDetail,
    DemandOut,
    DemandReplyOut,
    DemandUpdateRequest,
    LinkSimilarRequest,
    RejectRequest,
    ReplyRequest,
)
from app.services.demand import (
    archive_demand,
    convert_demand,
    create_demand,
    create_reply,
    get_demand_by_id,
    get_reply_by_id,
    link_similar,
    list_demands,
    list_my_demands,
    list_replies,
    reject_demand,
    revoke_reply,
    update_demand,
)

router = APIRouter(tags=["需求"])

# ==================== 新增：统一的需求访问守卫 ====================
async def can_access_demand(
    demand_id: str,
    current_user: dict = Depends(require_permissions("demand:view")),  # 第一层：系统权限
    db: AsyncSession = Depends(get_db),
) -> any:  # 返回 demand 对象
    """
    需求访问守卫（双层校验）：
    1. 校验用户是否拥有 demand:view 系统权限
    2. 校验需求是否存在（404）
    3. 校验用户是否是创建者、被分配PM(owner)、运营或超管（403）
    """
    demand = await get_demand_by_id(db, demand_id)
    if not demand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="需求不存在")
    
    user_id = current_user["user_id"]
    user_role = current_user["role"]
    
    is_creator = demand.creator_id == user_id
    is_owner = demand.owner_id == user_id  # 被分配PM/运营
    is_authorized = user_role in ("operator", "super_admin")

     # 新增：检查是否是关联任务的队伍成员（含队长）
    is_task_member = False
    if demand.linked_task_id:
        is_task_member = await is_task_member_or_leader(db, demand.linked_task_id, user_id)
    
    if not (is_creator or is_owner or is_authorized or is_task_member):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该需求")
    
    return demand
# ==================== 新增结束 ====================

def _parse_attachment_ids(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def _demand_to_out(d) -> DemandOut:
    return DemandOut(
        id=d.id,
        title=d.title,
        urgency=d.urgency,
        status=d.status,
        convert_status=d.convert_status,
        creator_id=d.creator_id,
        progress=d.progress,
        feedback=d.feedback,
        linked_task_id=d.linked_task_id,
        linked_demand_id=d.linked_demand_id,
        owner_id=d.owner_id,
        created_at=d.created_at,
        updated_at=d.updated_at,
    )


def _mask_phone(phone: str | None) -> str | None:
    if not phone or len(phone) < 7:
        return phone
    return phone[:3] + "****" + phone[-4:]


def _demand_to_detail(d, current_user: dict | None = None) -> DemandDetail:
    phone = d.contact_phone
    if phone and current_user:
        is_creator = d.creator_id == current_user["user_id"]
        is_owner = d.owner_id and d.owner_id == current_user["user_id"]
        is_admin = current_user["role"] in ("operator", "super_admin")
        if not (is_creator or is_owner or is_admin):
            phone = _mask_phone(phone)

    return DemandDetail(
        id=d.id,
        title=d.title,
        description=d.description,
        urgency=d.urgency,
        status=d.status,
        convert_status=d.convert_status,
        creator_id=d.creator_id,
        contact_phone=phone,
        attachment_ids=_parse_attachment_ids(d.attachment_ids),
        linked_task_id=d.linked_task_id,
        linked_demand_id=d.linked_demand_id,
        progress=d.progress,
        feedback=d.feedback,
        owner_id=d.owner_id,
        created_at=d.created_at,
        updated_at=d.updated_at,
    )


def _reply_to_out(r) -> DemandReplyOut:
    return DemandReplyOut(
        id=r.id,
        demand_id=r.demand_id,
        thread_id=r.thread_id,
        sender_id=r.sender_id,
        sender_role=r.sender_role,
        content=r.content,
        attachment_ids=_parse_attachment_ids(r.attachment_ids),
        is_revoked=r.is_revoked,
        created_at=r.created_at,
    )


# --- 需求提交与我的需求 ---

@router.post("/demands", response_model=ApiResponse[DemandOut])
async def post_demand(
    body: CreateDemandRequest,
    current_user: dict = Depends(require_permissions("demand:create")),
    db: AsyncSession = Depends(get_db),
):
    demand = await create_demand(
        db,
        creator_id=current_user["user_id"],
        title=body.title,
        description=body.description,
        urgency=body.urgency,
        contact_phone=body.contact_phone,
        attachment_ids=body.attachment_ids,
    )
    return ApiResponse(data=_demand_to_out(demand))


@router.get("/me/demands", response_model=ApiResponse[PaginatedData[DemandOut]])
async def get_my_demands(
    status_filter: str | None = Query(default=None, alias="status"),
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_my_demands(
        db,
        creator_id=current_user["user_id"],
        status=status_filter,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(
        data=PaginatedData(
            items=[_demand_to_out(d) for d in items],
            page=page,
            page_size=page_size,
            total=total,
        )
    )


# ==================== 修改：get_demand 使用统一守卫 ====================
@router.get("/demands/{demand_id}", response_model=ApiResponse[DemandDetail])
async def get_demand(
    demand_id: str,
    current_user: dict = Depends(require_permissions("demand:view")),
    db: AsyncSession = Depends(get_db),
):
    demand = await get_demand_by_id(db, demand_id)
    if not demand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="需求不存在")
    return ApiResponse(data=_demand_to_detail(demand))
# ==================== 修改结束 ====================

# ==================== 修改：get_demand_replies 使用统一守卫 ====================
@router.get("/demands/{demand_id}/replies", response_model=ApiResponse[PaginatedData[DemandReplyOut]])
async def get_demand_replies(
    
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    demand: any = Depends(can_access_demand), # 自动完成鉴权，并拿到 demand 对象
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_replies(db, demand_id=demand.id, page=page, page_size=page_size)
    return ApiResponse(
        data=PaginatedData(
            items=[_reply_to_out(r) for r in items],
            page=page,
            page_size=page_size,
            total=total,
        )
    )
# ==================== 修改结束 ====================


# ==================== 修改：post_reply 使用统一守卫 ====================
@router.post("/demands/{demand_id}/replies", response_model=ApiResponse[DemandReplyOut])
async def post_reply(
    body: ReplyRequest,
    demand: any = Depends(can_access_demand),  # 复用守卫，已包含 PM 校验
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 确定发送者角色
    is_creator = demand.creator_id == current_user["user_id"]
    sender_role = "requester" if is_creator else current_user["role"]
    
    reply = await create_reply(
        db,
        demand_id=demand.id,
        thread_id=body.thread_id,
        sender_id=current_user["user_id"],
        sender_role=sender_role,
        content=body.content,
        attachment_ids=body.attachment_ids,
    )
    return ApiResponse(data=_reply_to_out(reply))
# ==================== 修改结束 ====================



@router.post("/demands/{demand_id}/replies/{reply_id}/revoke", response_model=ApiResponse)
async def post_revoke_reply(
    demand_id: str,
    reply_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    reply = await get_reply_by_id(db, reply_id)
    if not reply or reply.demand_id != demand_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")
    if reply.sender_id != current_user["user_id"] and current_user["role"] != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能撤回自己的消息")
    if reply.is_revoked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="消息已撤回")
    await revoke_reply(db, reply)
    return ApiResponse(message="消息已撤回")


# --- 管理端需求操作 ---

@router.get("/demands", response_model=ApiResponse[PaginatedData[DemandOut]])
async def get_demands_list(
    status_filter: str | None = Query(default=None, alias="status"),
    convert_status: str | None = Query(default=None),
    owner_id: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(require_permissions("demand:view")),
    db: AsyncSession = Depends(get_db),
):
    items, total = await list_demands(
        db,
        status=status_filter,
        convert_status=convert_status,
        owner_id=owner_id,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(
        data=PaginatedData(
            items=[_demand_to_out(d) for d in items],
            page=page,
            page_size=page_size,
            total=total,
        )
    )


@router.patch("/demands/{demand_id}", response_model=ApiResponse[DemandDetail])
async def patch_demand(
    body: DemandUpdateRequest,
    demand_id: str,   
    current_user: dict = Depends(require_permissions("demand:convert")),
    db: AsyncSession = Depends(get_db),
):
    demand = await get_demand_by_id(db, demand_id)
    if not demand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="需求不存在")
    if demand.status in ("closed", "archived"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="已关闭或已归档需求不可编辑")
    updates = body.model_dump(exclude_unset=True)
    demand = await update_demand(db, demand, **updates)
    return ApiResponse(data=_demand_to_detail(demand))


@router.post("/demands/{demand_id}/convert", response_model=ApiResponse)
async def post_convert(
    body: ConvertRequest,
    demand_id: str,    
    current_user: dict = Depends(require_permissions("demand:convert")),
    db: AsyncSession = Depends(get_db),
):
    demand = await get_demand_by_id(db, demand_id)
    if not demand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="需求不存在")
    if demand.status not in ("pending_review", "communicating"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前状态不允许转化")

    from app.services.task import create_task

    user_id = current_user["user_id"]

    # 如果需求还没分配 owner，把当前转化人设为 owner
    if not demand.owner_id:
        demand.owner_id = user_id

    task = await create_task(
        db,
        demand_id=demand.id,
        title=body.title,
        description=demand.description,
        task_type=body.task_type,
        priority=body.priority,
        scope=body.scope,
        acceptance_criteria=body.acceptance_criteria,
        planned_end_time=body.planned_end_time,
        owner_id=demand.owner_id,
        leader_id=user_id,
    )

    import uuid as _uuid
    from app.models.team import TaskMember
    leader_member = TaskMember(
        id=_uuid.uuid4().hex,
        task_id=task.id,
        user_id=user_id,
        role="队长",
        duty="项目管理与协调",
        source="convert",
        status="active",
    )
    db.add(leader_member)
    await db.commit()

    demand = await convert_demand(db, demand, task_id=task.id)
    return ApiResponse(data={
        "demand_id": demand.id,
        "task_id": task.id,
        "demand_status": demand.status,
        "task_status": task.status,
    })


@router.post("/demands/{demand_id}/reject", response_model=ApiResponse)
async def post_reject(
    demand_id: str,
    body: RejectRequest,
    current_user: dict = Depends(require_permissions("demand:reject")),
    db: AsyncSession = Depends(get_db),
):
    demand = await get_demand_by_id(db, demand_id)
    if not demand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="需求不存在")
    if demand.status in ("converted", "linked", "closed", "archived"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前状态不允许驳回")
    await reject_demand(db, demand, reason=body.reason)
    return ApiResponse(message="需求已驳回")


@router.post("/demands/{demand_id}/link-similar", response_model=ApiResponse)
async def post_link_similar(
    demand_id: str,
    body: LinkSimilarRequest,
    current_user: dict = Depends(require_permissions("demand:link")),
    db: AsyncSession = Depends(get_db),
):
    demand = await get_demand_by_id(db, demand_id)
    if not demand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="需求不存在")
    if not body.target_demand_id and not body.target_task_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="需指定关联目标")
    await link_similar(
        db, demand,
        target_demand_id=body.target_demand_id,
        target_task_id=body.target_task_id,
        reason=body.reason,
    )
    return ApiResponse(message="已关联相似需求/任务")


@router.post("/demands/{demand_id}/archive", response_model=ApiResponse)
async def post_archive(
    demand_id: str,
    current_user: dict = Depends(require_permissions("demand:reject")),
    db: AsyncSession = Depends(get_db),
):
    demand = await get_demand_by_id(db, demand_id)
    if not demand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="需求不存在")
    await archive_demand(db, demand)
    return ApiResponse(message="需求已归档")
