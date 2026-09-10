import { http } from 'msw'
import { tasks, taskMembers, saveTaskMembers, saveTasks } from '../data/tasks'
import type { MockTask } from '../data/tasks'
import { joinApplications, assignments, teamTimelines } from '../data/teams'
import type { MockJoinApplication } from '../data/teams'
import { users, currentUserId } from '../data/users'
import {
  successResponse,
  errorResponse,
  paginatedResponse,
  parsePageParams,
  paginate,
} from '../utils'

const STORAGE_KEY_APPS = 'openrd_team_applications'
const STORAGE_KEY_ASSIGNMENTS = 'openrd_team_assignments'

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
  reviewing: 'doing',
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
    if (keyword) filtered = filtered.filter((task) => task.title.includes(keyword) || task.description.includes(keyword) || task.id.includes(keyword))
    return paginatedResponse(paginate(filtered, page, pageSize), page, pageSize, filtered.length)
  }),

  http.get('/api/v1/tasks', ({ request }) => {
    const url = new URL(request.url)
    const { page, pageSize, keyword } = parsePageParams(url)
    const status = url.searchParams.get('status')
    const teamStatus = url.searchParams.get('team_status')
    const my = url.searchParams.get('my') === 'true'

    let filtered: Array<MockTask & { leader_name?: string; my_role?: string; my_stage?: string }> =
      tasks.filter((t) => t.is_deleted === 0)

    if (my) {
      const uid = currentUserId
      const myMemberMap = new Map(
        taskMembers.filter((m) => m.user_id === uid).map((m) => [m.task_id, m.role]),
      )
      filtered = filtered
        .filter((t) => myMemberMap.has(t.id) || t.leader_id === uid || t.owner_id === uid)
        .map((t) => {
          const myRole = myMemberMap.get(t.id) ?? (t.leader_id === uid ? '任务队长' : '需求方')
          return { ...t, my_role: myRole, my_stage: MY_STAGE_MAP[t.status] ?? 'doing' }
        })
    } else {
      filtered = filtered.map((t) => {
        const leader = users.find((u) => u.id === t.leader_id)
        return { ...t, leader_name: leader?.nickname ?? '' }
      })
    }

    if (status) filtered = filtered.filter((t) => t.status === status)
    if (teamStatus) filtered = filtered.filter((t) => t.team_status === teamStatus)
    if (keyword)
      filtered = filtered.filter(
        (t) => t.title.includes(keyword) || t.description.includes(keyword) || t.leader_name?.includes(keyword) || t.demand_id.includes(keyword),
      )

    return paginatedResponse(paginate(filtered, page, pageSize), page, pageSize, filtered.length)
  }),

  http.get('/api/v1/tasks/:task_id', ({ params }) => {
    const task = tasks.find((t) => t.id === params.task_id)
    if (!task) return errorResponse('NOT_FOUND', '任务不存在', 404)
    return successResponse(task as unknown as Record<string, unknown>)
  }),

  http.patch('/api/v1/tasks/:task_id', async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const task = tasks.find((t) => t.id === params.task_id)
    if (!task) return errorResponse('NOT_FOUND', '任务不存在', 404)
    Object.assign(task, body, { updated_at: new Date().toISOString() })
    saveTasks()
    return successResponse(task as unknown as Record<string, unknown>)
  }),

  http.post('/api/v1/tasks/:task_id/status', async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const task = tasks.find((t) => t.id === params.task_id)
    if (!task) return errorResponse('NOT_FOUND', '任务不存在', 404)
    task.status = body.status as string
    task.updated_at = new Date().toISOString()
    saveTasks()
    return successResponse({})
  }),

  http.post('/api/v1/tasks/:task_id/progress', async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const task = tasks.find((t) => t.id === params.task_id)
    if (!task) return errorResponse('NOT_FOUND', '任务不存在', 404)
    task.progress = body.progress as number
    task.updated_at = new Date().toISOString()
    saveTasks()
    return successResponse({})
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
        task.progress = Math.max(task.progress || 0, recruitingProgress)
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
