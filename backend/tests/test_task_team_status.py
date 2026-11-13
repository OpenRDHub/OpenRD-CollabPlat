import pytest

from app.dependencies.auth import get_current_user
from app.main import app
from app.models.task import Task
from scripts.repair_task_team_status import repair


@pytest.mark.parametrize(('initial', 'target', 'expected'), [
    ('recruiting', 'in_progress', 'collaborating'),
    ('team_ready', 'in_progress', 'collaborating'),
    # 存量 team_ready 在界面上即「解决中」，需具备与 in_progress 相同的流转能力
    ('team_ready', 'pending_acceptance', 'collaborating'),
    ('in_progress', 'pending_acceptance', 'collaborating'),
    ('pending_acceptance', 'in_progress', 'collaborating'),
    ('pending_acceptance', 'completed', 'accepted'),
    ('recruiting', 'closed', 'ended'),
    ('pending_acceptance', 'closed', 'ended'),
])
async def test_status_api_persists_team_status(client, db_session, initial, target, expected):
    task = Task(id='SYNC-1', title='Status sync', status=initial, team_status='forming', stage='beta')
    db_session.add(task)
    await db_session.commit()

    async def admin():
        return {'user_id': 'sync-admin', 'role': 'super_admin', 'jti': 'sync-test'}

    app.dependency_overrides[get_current_user] = admin
    try:
        response = await client.post('/api/v1/tasks/SYNC-1/status', json={'status': target})
        assert response.status_code == 200, response.text
        assert response.json()['data']['team_status'] == expected
        detail = await client.get('/api/v1/tasks/SYNC-1')
        assert detail.json()['data']['team_status'] == expected
        assert detail.json()['data']['stage'] == 'beta'
        listing = await client.get('/api/v1/tasks', params={'team_status': expected})
        assert any(item['id'] == 'SYNC-1' for item in listing.json()['data']['items'])
        await db_session.refresh(task)
        assert task.status == target
        assert task.team_status == expected
    finally:
        app.dependency_overrides.pop(get_current_user, None)


async def test_in_progress_filter_includes_legacy_team_ready(client, db_session):
    """按「解决中」筛选时，存量 team_ready 任务不应被漏掉（含已删除任务列表）。"""
    db_session.add_all([
        Task(id='FILTER-PROG', title='Active progress', status='in_progress', team_status='collaborating'),
        Task(id='FILTER-READY', title='Legacy ready', status='team_ready', team_status='collaborating'),
        Task(id='FILTER-REC', title='Recruiting', status='recruiting', team_status='forming'),
        Task(id='FILTER-DEL-READY', title='Deleted legacy ready', status='team_ready',
             team_status='collaborating', is_deleted=1),
    ])
    await db_session.commit()

    async def admin():
        return {'user_id': 'filter-admin', 'role': 'super_admin', 'jti': 'filter-test'}

    app.dependency_overrides[get_current_user] = admin
    try:
        active = await client.get('/api/v1/tasks', params={'status': 'in_progress', 'page_size': 50})
        assert active.status_code == 200, active.text
        active_ids = {item['id'] for item in active.json()['data']['items']}
        assert {'FILTER-PROG', 'FILTER-READY'} <= active_ids
        assert 'FILTER-REC' not in active_ids

        # 已删除任务列表同样需要命中历史 team_ready 任务
        deleted = await client.get(
            '/api/v1/tasks',
            params={'status': 'in_progress', 'deleted': 'true', 'page_size': 50},
        )
        assert deleted.status_code == 200, deleted.text
        deleted_ids = {item['id'] for item in deleted.json()['data']['items']}
        assert 'FILTER-DEL-READY' in deleted_ids
    finally:
        app.dependency_overrides.pop(get_current_user, None)


async def test_repair_is_previewable_idempotent_and_skips_deleted(db_session):
    """终态任务的 status 不变，但不一致的 team_status 仍会被修正——写入范围需如实覆盖。"""
    task = Task(id='REPAIR-1', title='Old completed task', status='completed', team_status='forming', stage='beta')
    # 终态 closed 任务同样会被对齐 team_status（closed/forming -> closed/ended）
    closed = Task(id='REPAIR-3', title='Old closed task', status='closed', team_status='forming', stage='beta')
    deleted = Task(id='REPAIR-2', title='Deleted', status='closed', team_status='forming', is_deleted=1)
    db_session.add_all([task, closed, deleted])
    await db_session.commit()
    assert await repair(db_session) == 2
    await db_session.refresh(task)
    await db_session.refresh(closed)
    assert task.team_status == 'forming'
    assert closed.team_status == 'forming', '预览模式不应写入'
    assert await repair(db_session, apply=True) == 2
    await db_session.refresh(task)
    await db_session.refresh(closed)
    await db_session.refresh(deleted)
    assert task.status == 'completed', '终态任务 status 不变'
    assert task.team_status == 'accepted'
    assert task.stage == 'beta'
    assert closed.status == 'closed', '终态任务 status 不变'
    assert closed.team_status == 'ended'
    assert deleted.team_status == 'forming'
    assert await repair(db_session, apply=True) == 0


async def test_repair_migrates_legacy_team_ready_to_in_progress(db_session):
    """脚本需将已移除的 team_ready 环节历史任务推进为 in_progress，并同步团队状态。"""
    legacy = Task(id='REPAIR-READY', title='Legacy ready', status='team_ready',
                  team_status='forming', stage='develop')
    db_session.add(legacy)
    await db_session.commit()

    assert await repair(db_session) == 1
    await db_session.refresh(legacy)
    assert legacy.status == 'team_ready', '预览模式不应写入'

    assert await repair(db_session, apply=True) == 1
    await db_session.refresh(legacy)
    assert legacy.status == 'in_progress'
    assert legacy.team_status == 'collaborating'
    assert legacy.stage == 'develop', '脚本不应更改项目阶段'

    # 重复运行幂等
    assert await repair(db_session, apply=True) == 0
