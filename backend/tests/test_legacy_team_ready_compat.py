"""兼容期回归：存量 team_ready 历史任务（含未迁移 / 删除后恢复）的行为一致性。

覆盖用户报告的三个场景：
1. 详情页按「解决中」推进到「待验收」——后端不得拒绝。
2. 已删除列表按「解决中」筛选——不得漏掉 team_ready。
3. 加入申请入口——后端允许 team_ready，前端 canApply 需与之一致。
"""

import re
from pathlib import Path

import pytest

from app.dependencies.auth import get_current_user
from app.main import app
from app.models.task import Task

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
    """后端已允许 team_ready 接受加入申请，前端入口需同步放开。"""
    db_session.add(
        Task(id='LEGACY-JOIN', title='Legacy join', status='team_ready',
             team_status='collaborating', owner_id='legacy-owner', is_deleted=0)
    )
    await db_session.commit()

    async def builder():
        return {'user_id': 'legacy-builder', 'role': 'builder', 'jti': 'legacy-join'}

    app.dependency_overrides[get_current_user] = builder
    try:
        response = await client.post(
            '/api/v1/tasks/LEGACY-JOIN/join-applications',
            json={'role': '共建者', 'reason': '申请加入'},
        )
        # 后端不再因 team_ready 而拒绝（非 400「当前任务状态不接受申请」）
        assert response.status_code != 400, response.text
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    source = VIEW.read_text(encoding='utf-8')
    # canApply 不得只认「招募中」，否则 team_ready 入口不可见
    assert not re.search(r"status\s*===\s*'招募中'", source), \
        'canApply 仍只认「招募中」，历史 team_ready 的加入入口不可见'
