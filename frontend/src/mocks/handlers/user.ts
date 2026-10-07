import { http } from 'msw'
import { getCurrentUser, persistUserProfile, users } from '../data/users'
import { demands } from '../data/demands'
import { taskMembers, tasks } from '../data/tasks'
import { successResponse, errorResponse } from '../utils'

const PERMISSION_MAP: Record<string, string[]> = {
  requester: ['demand:view', 'demand:create', 'demand:reply', 'task:view', 'message:view', 'message:manage'],
  // builder 不含 task:update：普通任务成员不能提交进度，该权限只由管理员手动授予。
  builder: ['demand:view', 'task:view', 'task:join', 'member:view', 'message:view', 'message:manage'],
  operator: [
    'demand:view', 'demand:update', 'demand:reply', 'demand:convert', 'demand:reject', 'demand:link',
    'task:view', 'task:manage', 'member:view', 'member:approve', 'member:invite',
    'task:assign', 'message:view', 'message:manage',
    'demand:archive',
  ],
  super_admin: [
    'demand:view', 'demand:create', 'demand:update', 'demand:reply', 'demand:convert', 'demand:reject', 'demand:link',
    'task:view', 'task:join', 'task:update', 'task:manage', 'task:assign',
    'member:view', 'member:approve', 'member:invite',
    'message:view', 'message:manage',
    'admin:user', 'admin:role', 'admin:log', 'demand:archive',
  ],
}

export const userHandlers = [
  http.get('/api/v1/stats', () => {
    const activeTasks = tasks.filter((task) => task.is_deleted === 0)
    return successResponse({
      tasks_total: activeTasks.length,
      tasks_in_progress: activeTasks.filter((task) => task.status === 'in_progress').length,
      tasks_completed: activeTasks.filter((task) => task.status === 'completed').length,
      tasks_closed: activeTasks.filter((task) => task.status === 'closed').length,
      users_requester: users.filter((user) => user.role === 'requester' && user.is_deleted === 0).length,
      users_builder: users.filter((user) => user.role === 'builder' && user.is_deleted === 0).length,
    })
  }),

  http.get('/api/v1/me/stats', () => {
    const user = getCurrentUser()
    if (!user) {
      return errorResponse('UNAUTHORIZED', '未登录', 401)
    }
    return successResponse({
      demand_count: demands.filter((demand) => demand.creator_id === user.id && demand.is_deleted === 0).length,
      task_count: taskMembers.filter((member) => member.user_id === user.id).length,
    })
  }),

  http.get('/api/v1/me', () => {
    const user = getCurrentUser()
    if (!user) {
      return errorResponse('UNAUTHORIZED', '未登录', 401)
    }
    const { password, ...safeUser } = user
    return successResponse(safeUser)
  }),

  http.patch('/api/v1/me/profile', async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const user = getCurrentUser()
    if (!user) {
      return errorResponse('UNAUTHORIZED', '未登录', 401)
    }
    Object.assign(user, body)
    persistUserProfile(user)
    const { password, ...safeUser } = user
    return successResponse(safeUser)
  }),

  http.patch('/api/v1/me/password', () => {
    return successResponse({})
  }),

  http.get('/api/v1/me/permissions', () => {
    const user = getCurrentUser()
    if (!user) {
      return errorResponse('UNAUTHORIZED', '未登录', 401)
    }
    const permissions = PERMISSION_MAP[user.role] || []
    return successResponse({ permissions })
  }),
]
