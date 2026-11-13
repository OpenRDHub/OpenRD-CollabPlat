"""兼容期回归：存量 team_ready 历史任务（含未迁移 / 删除后恢复）的行为一致性。

覆盖用户报告的三个场景：
1. 详情页按「解决中」推进到「待验收」——后端不得拒绝。
2. 已删除列表按「解决中」筛选——不得漏掉 team_ready。
3. 加入申请入口——后端允许 team_ready，前端 canApply 需与之一致。
"""

from pathlib import Path

import pytest
from sqlalchemy import select

from app.dependencies.auth import get_current_user
from app.main import app
from app.models.task import Task
from app.models.team import JoinApplication

VIEW = Path(__file__).resolve().parents[2] / 'frontend/src/views/TaskDetailView.vue'


async def _admin():
    return {'user_id': 'legacy-admin', 'role': 'super_admin', 'jti': 'legacy-test'}


@pytest.mark.parametrize('restore_first', [False, True])
async def test_legacy_team_ready_can_advance_to_pending_acceptance(client, db_session, restore_first):
    """未迁移任务、以及「删除后恢复」的历史任务，都应能推进到「待验收」。

    修复脚本跳过软删除任务，因此删除的历史任务恢复后仍可能是 team_ready；
    这条路径必须与页面「解决中」的展示口径一致，否则用户点「待验收」会被拒。
    """
    task = Task(
        id='LEGACY-ADV', title='Legacy advance', status='team_ready',
        team_status='collaborating', stage='develop',
        is_deleted=1 if restore_first else 0,
    )
    db_session.add(task)
    await db_session.commit()

    app.dependency_overrides[get_current_user] = _admin
    try:
        if restore_first:
            # 走真实恢复接口，模拟「删除后恢复」的运维路径
            restored = await client.post('/api/v1/tasks/LEGACY-ADV/restore')
            assert restored.status_code == 200, restored.text
            await db_session.refresh(task)
            assert task.status == 'team_ready', '恢复不应改变任务状态'

        response = await client.post(
            '/api/v1/tasks/LEGACY-ADV/status', json={'status': 'pending_acceptance'}
        )
        assert response.status_code == 200, response.text
        assert response.json()['data']['team_status'] == 'collaborating'

        await db_session.refresh(task)
        assert task.status == 'pending_acceptance'
        assert task.stage == 'develop'
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.parametrize('is_deleted', [0, 1])
async def test_legacy_team_ready_matched_by_in_progress_filter(client, db_session, is_deleted):
    """按「解决中」筛选时，未迁移与已删除的历史任务都必须命中。"""
    db_session.add_all([
        Task(id='LEGACY-PROG', title='Progress', status='in_progress',
             team_status='collaborating', is_deleted=is_deleted),
        Task(id='LEGACY-READY', title='Legacy ready', status='team_ready',
             team_status='collaborating', is_deleted=is_deleted),
        Task(id='LEGACY-REC', title='Recruiting', status='recruiting',
             team_status='forming', is_deleted=is_deleted),
    ])
    await db_session.commit()

    app.dependency_overrides[get_current_user] = _admin
    try:
        response = await client.get(
            '/api/v1/tasks',
            params={'status': 'in_progress', 'deleted': str(bool(is_deleted)).lower(), 'page_size': 50},
        )
        assert response.status_code == 200, response.text
        ids = {item['id'] for item in response.json()['data']['items']}
        assert 'LEGACY-PROG' in ids
        assert 'LEGACY-READY' in ids, '历史 team_ready 任务被「解决中」筛选漏掉'
        assert 'LEGACY-REC' not in ids
    finally:
        app.dependency_overrides.pop(get_current_user, None)


async def test_join_application_accepts_legacy_team_ready(client, db_session):
    """加入申请与后端状态白名单一致：recruiting/team_ready 提交成功且落库，in_progress 被拒。

    前端 canApply 需用后端原始状态判断（rawStatus），不能用显示标签——
    team_ready 与 in_progress 都显示「解决中」，按显示文字放行会导致 in_progress
    任务的按钮可见但提交必然 400。
    """
    db_session.add_all([
        Task(id='LEGACY-JOIN-RECRUIT', title='Recruiting', status='recruiting',
             team_status='forming', owner_id='legacy-owner', is_deleted=0),
        Task(id='LEGACY-JOIN-READY', title='Legacy ready', status='team_ready',
             team_status='collaborating', owner_id='legacy-owner', is_deleted=0),
        Task(id='LEGACY-JOIN-PROG', title='Normal progress', status='in_progress',
             team_status='collaborating', owner_id='legacy-owner', is_deleted=0),
    ])
    await db_session.commit()

    async def builder():
        return {'user_id': 'legacy-builder', 'role': 'builder', 'jti': 'legacy-join'}

    app.dependency_overrides[get_current_user] = builder
    try:
        async def apply(task_id: str):
            return await client.post(
                f'/api/v1/tasks/{task_id}/join-applications',
                json={'role': '共建者', 'reason': '申请加入'},
            )

        # recruiting：接受且申请落库
        ok_recruit = await apply('LEGACY-JOIN-RECRUIT')
        assert ok_recruit.status_code == 200, ok_recruit.text
        # team_ready（存量「解决中」）：接受且申请落库
        ok_ready = await apply('LEGACY-JOIN-READY')
        assert ok_ready.status_code == 200, ok_ready.text
        # in_progress（普通「解决中」）：必须拒绝，前端按钮也不应可见
        rejected = await apply('LEGACY-JOIN-PROG')
        assert rejected.status_code == 400, rejected.text
        assert '不接受申请' in rejected.json()['detail']

        created = (await db_session.execute(
            select(JoinApplication).where(JoinApplication.task_id == 'LEGACY-JOIN-RECRUIT')
        )).scalars().all()
        assert len(created) == 1
        assert created[0].user_id == 'legacy-builder'
        assert created[0].status == 'pending'

        created_ready = (await db_session.execute(
            select(JoinApplication).where(JoinApplication.task_id == 'LEGACY-JOIN-READY')
        )).scalars().all()
        assert len(created_ready) == 1, 'team_ready 申请应落库'

        not_created = (await db_session.execute(
            select(JoinApplication).where(JoinApplication.task_id == 'LEGACY-JOIN-PROG')
        )).scalars().all()
        assert not_created == [], 'in_progress 的申请不应落库'
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    source = VIEW.read_text(encoding='utf-8')
    # canApply 必须基于后端原始状态（rawStatus），不得按显示标签放行
    assert "APPLY_ALLOWED_RAW_STATUS.includes(task.value.rawStatus)" in source, \
        'canApply 未使用后端原始状态判断，显示标签会把 in_progress 误放行'
    assert "rawStatus: d.status" in source, '任务加载需保留后端原始状态'
