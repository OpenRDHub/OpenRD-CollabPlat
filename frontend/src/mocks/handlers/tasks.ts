import { http } from 'msw'
import { tasks, taskMembers, saveTaskMembers, saveTasks } from '../data/tasks'
import type { MockTask } from '../data/tasks'
import { joinApplications, assignments, teamTimelines } from '../data/teams'
import type { MockJoinApplication } from '../data/teams'
import { users, currentUserId } from '../data/users'
import { demands } from '../data/demands'
import {
  successResponse,
  errorResponse,
  paginatedResponse,
  parsePageParams,
  paginate,
} from '../utils'

const STORAGE_KEY_APPS = 'openrd_team_applications'
const STORAGE_KEY_ASSIGNMENTS = 'openrd_team_assignments'
const STORAGE_KEY_PROGRESS = 'openrd_task_progress'

interface MockTaskProgress {
  id: string
  task_id: string
  user_id: string
  user_name: string
  stage: string
  content: string | null
  next_plan: string | null
  file_ids: string[]
  created_at: string
}

const defaultProgressHistory: MockTaskProgress[] = [
  {
    id: 'progress-1042-1',
    task_id: 'TASK-1042',
    user_id: 'usr-002',
    user_name: '赵明',
    stage: 'develop',
    content: '后端接口与提醒规则已进入联调。',
    next_plan: '完成端到端测试并进入内测。',
    file_ids: [],
    created_at: '2026-06-10T10:00:00+08:00',
  },
]

function loadProgressHistory(): MockTaskProgress[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_PROGRESS)
    return raw ? JSON.parse(raw) as MockTaskProgress[] : [...defaultProgressHistory]
  } catch {
    return [...defaultProgressHistory]
  }
}

const taskProgressHistory = loadProgressHistory()

function persistProgressHistory() {
  localStorage.setItem(STORAGE_KEY_PROGRESS, JSON.stringify(taskProgressHistory))
}

const STAGE_DEMAND_PROGRESS: Record<string, number> = {
  team: 25,
  develop: 50,
  beta: 75,
  opensource: 100,
}

function loadPersistedApps() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_APPS)
    if (!raw) return
    const saved = JSON.parse(raw) as MockJoinApplication[] | Record<string, MockJoinApplication['status']>
    if (Array.isArray(saved)) {
      joinApplications.length = 0
      joinApplications.push(...saved)
      return
    }
    for (const [id, status] of Object.entries(saved)) {
      const app = joinApplications.find((item) => item.id === id)
      if (app) app.status = status
    }
  } catch {}
}

function persistAppStatus(id: string, status: MockJoinApplication['status']) {
  const app = joinApplications.find((item) => item.id === id)
  if (app) app.status = status
  localStorage.setItem(STORAGE_KEY_APPS, JSON.stringify(joinApplications))
}

function loadPersistedAssignments() {
  const raw = localStorage.getItem(STORAGE_KEY_ASSIGNMENTS)
  if (!raw) return
  const saved: Record<string, typeof assignments> = JSON.parse(raw)
  for (const [taskId, items] of Object.entries(saved)) {
    const existing = assignments.filter((a) => a.task_id !== taskId)
    assignments.length = 0
    assignments.push(...existing, ...items)
  }
}

function persistAssignments(taskId: string, items: typeof assignments) {
  const raw = localStorage.getItem(STORAGE_KEY_ASSIGNMENTS)
  const map: Record<string, typeof assignments> = raw ? JSON.parse(raw) : {}
  map[taskId] = items
  localStorage.setItem(STORAGE_KEY_ASSIGNMENTS, JSON.stringify(map))
}

loadPersistedApps()
loadPersistedAssignments()

const MY_STAGE_MAP: Record<string, string> = {
  recruiting: 'pending',
  team_ready: 'pending',
  in_progress: 'doing',
  pending_acceptance: 'doing',
  completed: 'done',
  closed: 'done',
}

const VALID_STATUS_TRANSITIONS: Record<string, string[]> = {
  recruiting: ['team_ready', 'closed'],
  team_ready: ['in_progress', 'closed'],
  in_progress: ['pending_acceptance', 'closed'],
  pending_acceptance: ['completed', 'in_progress', 'closed'],
  completed: [],
  closed: [],
}

export const taskHandlers = [
  http.get('/api/v1/me/tasks', ({ request }) => {
    const url = new URL(request.url)
    const { page, pageSize, keyword } = parsePageParams(url)
    const status = url.searchParams.get('status')
    const uid = currentUserId
    const myMemberMap = new Map(
      taskMembers
        .filter((member) => member.user_id === uid && member.status === 'active')
        .map((member) => [member.task_id, member.role]),
    )
    let filtered = tasks
      .filter((task) => task.is_deleted === 0 && (myMemberMap.has(task.id) || task.leader_id === uid || task.owner_id === uid))
      .map((task) => ({
        ...task,
        my_role: myMemberMap.get(task.id) ?? (task.leader_id === uid ? '任务队长' : '需求方'),
        my_stage: MY_STAGE_MAP[task.status] ?? 'doing',
      }))
    if (status) filtered = filtered.filter((task) => task.status === status)
    if (keyword) filtered = filtered.filter((task) => task.title.includes(keyword) || (task.description || '').includes(keyword) || task.id.includes(keyword))
    return paginatedResponse(paginate(filtered, page, pageSize), page, pageSize, filtered.length)
  }),

  http.get('/api/v1/tasks', ({ request }) => {
    const url = new URL(request.url)
    const { page, pageSize, keyword } = parsePageParams(url)
    const status = url.searchParams.get('status')
    const teamStatus = url.searchParams.get('team_status')
    let filtered: Array<MockTask & { leader_name?: string }> =
      tasks.filter((t) => t.is_deleted === 0)
    filtered = filtered.map((t) => {
      const leader = users.find((u) => u.id === t.leader_id)
      return { ...t, leader_name: leader?.nickname ?? '' }
    })

    if (status) filtered = filtered.filter((t) => t.status === status)
    if (teamStatus) filtered = filtered.filter((t) => t.team_status === teamStatus)
    if (keyword)
      filtered = filtered.filter(
        (t) => t.title.includes(keyword) || (t.description || '').includes(keyword) || t.leader_name?.includes(keyword) || (t.demand_id || '').includes(keyword),
      )

    return paginatedResponse(paginate(filtered, page, pageSize), page, pageSize, filtered.length)
  }),

  http.get('/api/v1/tasks/:task_id', ({ params }) => {
    const task = tasks.find((t) => t.id === params.task_id)
    if (!task) return errorResponse('NOT_FOUND', '任务不存在', 404)
    const fileIds: string[] = task.file_ids || []
    const withFiles = {
      ...task,
      files: fileIds.map((id) => ({
        id,
        filename: id,
        size: 0,
        url: `/api/v1/files/${id}`,
      })),
    }
    return successResponse(withFiles as unknown as Record<string, unknown>)
  }),

  http.patch('/api/v1/tasks/:task_id', async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const task = tasks.find((t) => t.id === params.task_id)
    if (!task) return errorResponse('NOT_FOUND', '任务不存在', 404)
    if (['completed', 'closed'].includes(task.status)) {
      return errorResponse('TASK_NOT_EDITABLE', '已完成或已关闭的任务不可编辑', 400)
    }
    const editableFields = [
      'title',
      'description',
      'task_type',
      'priority',
      'scope',
      'acceptance_criteria',
      'planned_end_time',
      'leader_id',
      'resource_links',
      'file_ids',
    ] as const
    for (const field of editableFields) {
      if (field in body) Object.assign(task, { [field]: body[field] })
    }
    task.updated_at = new Date().toISOString()
    saveTasks()
    return successResponse(task as unknown as Record<string, unknown>)
  }),

  http.post('/api/v1/tasks/:task_id/status', async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const task = tasks.find((t) => t.id === params.task_id)
    if (!task) return errorResponse('NOT_FOUND', '任务不存在', 404)
    const nextStatus = body.status as string
    if (!(VALID_STATUS_TRANSITIONS[task.status] || []).includes(nextStatus)) {
      return errorResponse('INVALID_STATUS_TRANSITION', `不允许从 ${task.status} 变更到 ${nextStatus}`, 400)
    }
    task.status = nextStatus
    task.updated_at = new Date().toISOString()
    saveTasks()
    return successResponse(task as unknown as Record<string, unknown>)
  }),

  http.post('/api/v1/tasks/:task_id/progress', async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const task = tasks.find((t) => t.id === params.task_id)
    if (!task) return errorResponse('NOT_FOUND', '任务不存在', 404)
    if (!['in_progress', 'pending_acceptance'].includes(task.status)) {
      return errorResponse('INVALID_TASK_STATUS', '当前状态不允许提交进度', 400)
    }
    if (!('expected_updated_at' in body)) {
      return errorResponse('VALIDATION_ERROR', 'expected_updated_at 为必填字段', 422)
    }
    if ((body.expected_updated_at ?? null) !== (task.updated_at ?? null)) {
      return errorResponse('PROGRESS_CONFLICT', '进度已被其他人更新', 409)
    }
    if (body.base_stage && body.base_stage !== task.stage) {
      return errorResponse('PROGRESS_CONFLICT', '进度已被其他人更新', 409)
    }
    const stage = body.stage as string
    if (!['team', 'develop', 'beta', 'opensource'].includes(stage)) {
      return errorResponse('VALIDATION_ERROR', '阶段必须是 team/develop/beta/opensource 之一', 422)
    }
    const now = new Date().toISOString()
    const entry: MockTaskProgress = {
      id: `progress-${Date.now()}`,
      task_id: task.id,
      user_id: currentUserId,
      user_name: users.find((user) => user.id === currentUserId)?.nickname || currentUserId,
      stage,
      content: typeof body.content === 'string' ? body.content : null,
      next_plan: typeof body.next_plan === 'string' ? body.next_plan : null,
      file_ids: Array.isArray(body.file_ids) ? body.file_ids as string[] : [],
      created_at: now,
    }
    taskProgressHistory.unshift(entry)
    task.stage = stage
    task.updated_at = now
    demands
      .filter((demand) => demand.linked_task_id === task.id && demand.is_deleted === 0)
      .forEach((demand) => {
        demand.progress = STAGE_DEMAND_PROGRESS[stage] ?? demand.progress
        demand.updated_at = now
      })
    saveTasks()
    persistProgressHistory()
    return successResponse(entry as unknown as Record<string, unknown>)
  }),

  http.get('/api/v1/tasks/:task_id/progress', ({ params, request }) => {
    const task = tasks.find((t) => t.id === params.task_id)
    if (!task) return errorResponse('NOT_FOUND', '任务不存在', 404)
    const url = new URL(request.url)
    const { page, pageSize } = parsePageParams(url)
    const items = taskProgressHistory
      .filter((entry) => entry.task_id === params.task_id)
      .sort((a, b) => b.created_at.localeCompare(a.created_at))
    return paginatedResponse(paginate(items, page, pageSize), page, pageSize, items.length)
  }),

  http.post('/api/v1/tasks/:task_id/resources', async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const task = tasks.find((t) => t.id === params.task_id)
    if (!task) return errorResponse('NOT_FOUND', '任务不存在', 404)
    task.resource_links = body.resource_links as { label: string; url: string }[]
    task.updated_at = new Date().toISOString()
    saveTasks()
    return successResponse({})
  }),

  http.get('/api/v1/tasks/:task_id/team', ({ params }) => {
    const taskId = params.task_id as string
    const task = tasks.find((t) => t.id === taskId)
    const members = taskMembers.filter((m) => m.task_id === taskId)
    const enrichedMembers = members.map((m) => {
      const u = users.find((usr) => usr.id === m.user_id)
      return {
        ...m,
        name: u?.nickname || m.duty,
        platform: u?.platform_id || '',
        active: m.status === 'active' ? '在线' : '离线',
      }
    })
    return successResponse({
      members: enrichedMembers,
      leader_id: task?.leader_id || '',
      applications: joinApplications.filter((a) => a.task_id === taskId),
      assignments: assignments.filter((a) => a.task_id === taskId),
      stage: task?.team_status === 'collaborating' ? '接口联调' : task?.team_status === 'forming' ? '成员确认' : '已完成',
    } as unknown as Record<string, unknown>)
  }),

  http.get('/api/v1/tasks/:task_id/join-applications', ({ params }) => {
    const apps = joinApplications.filter((a) => a.task_id === params.task_id && a.status === 'pending')
    return successResponse({ applications: apps } as unknown as Record<string, unknown>)
  }),

  http.post('/api/v1/tasks/:task_id/join-applications', async ({ params, request }) => {
    const taskId = params.task_id as string
    const body = (await request.json()) as { role: string; skills?: string[]; reason?: string; message?: string }
    if (taskMembers.some((member) => member.task_id === taskId && member.user_id === currentUserId && member.status === 'active')) {
      return errorResponse('ALREADY_MEMBER', '已是任务成员', 409)
    }
    if (joinApplications.some((app) => app.task_id === taskId && app.user_id === currentUserId && app.status === 'pending')) {
      return errorResponse('DUPLICATE_APPLICATION', '已有待审核的申请', 409)
    }
    const user = users.find((item) => item.id === currentUserId)
    const app: MockJoinApplication = {
      id: `app-${Date.now()}`,
      task_id: taskId,
      user_id: currentUserId,
      name: user?.nickname || user?.username || currentUserId,
      platform: user?.platform_id || '',
      role: body.role,
      skills: body.skills || [],
      reason: body.reason || body.message || '',
      time: new Date().toISOString(),
      status: 'pending',
    }
    joinApplications.push(app)
    localStorage.setItem(STORAGE_KEY_APPS, JSON.stringify(joinApplications))
    return successResponse(app as unknown as Record<string, unknown>)
  }),

  http.post('/api/v1/tasks/:task_id/join-applications/:application_id/approve', ({ params }) => {
    const app = joinApplications.find((a) => a.id === params.application_id)
    const taskId = params.task_id as string
    if (app) {
      app.status = 'approved'
      persistAppStatus(app.id, 'approved')
      if (!taskMembers.some((m) => m.task_id === taskId && m.user_id === app.user_id && m.role === app.role)) {
        taskMembers.push({
          id: `tm-${Date.now()}`,
          task_id: taskId,
          user_id: app.user_id || app.platform,
          role: app.role,
          duty: app.role,
          member_type: 'member',
          status: 'active',
          joined_at: new Date().toISOString(),
        })
        saveTaskMembers()
      }
      const task = tasks.find((t) => t.id === taskId)
      if (task) {
        const activeCount = taskMembers.filter((m) => m.task_id === taskId && m.status === 'active').length
        const recruitingProgress = Math.min(activeCount * 25, 100)
        if (recruitingProgress >= 100 && task.status === 'recruiting') {
          task.status = 'team_ready'
          task.team_status = 'collaborating'
        }
        task.updated_at = new Date().toISOString()
        saveTasks()
      }
    }
    return successResponse({})
  }),

  http.post('/api/v1/tasks/:task_id/join-applications/:application_id/reject', ({ params }) => {
    const app = joinApplications.find((a) => a.id === params.application_id)
    if (app) {
      app.status = 'rejected'
      persistAppStatus(app.id, 'rejected')
    }
    return successResponse({})
  }),

  http.post('/api/v1/tasks/:task_id/members/invite', () => {
    return successResponse({})
  }),

  http.patch('/api/v1/tasks/:task_id/members/:member_id', async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const member = taskMembers.find((m) => m.id === params.member_id)
    if (member) Object.assign(member, body)
    return successResponse({})
  }),

  http.post('/api/v1/tasks/:task_id/leader/transfer', () => {
    return successResponse({})
  }),

  http.get('/api/v1/tasks/:task_id/assignments', ({ params }) => {
    const items = assignments.filter((a) => a.task_id === params.task_id)
    return successResponse({ assignments: items } as unknown as Record<string, unknown>)
  }),

  http.put('/api/v1/tasks/:task_id/assignments', async ({ params, request }) => {
    const body = (await request.json()) as { assignments: typeof assignments }
    const taskId = params.task_id as string
    const existing = assignments.filter((a) => a.task_id !== taskId)
    const newItems = body.assignments.map((a, i) => ({ ...a, id: a.id || `asgn-new-${i}`, task_id: taskId }))
    assignments.length = 0
    assignments.push(...existing, ...newItems)
    persistAssignments(taskId, newItems)
    return successResponse({})
  }),

  http.get('/api/v1/tasks/:task_id/timeline', ({ params }) => {
    const items = teamTimelines.filter((t) => t.task_id === params.task_id)
    return successResponse({ timeline: items } as unknown as Record<string, unknown>)
  }),
]
