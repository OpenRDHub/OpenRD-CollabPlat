import { http } from 'msw'
import { getCurrentUser, persistUserProfile } from '../data/users'
import { successResponse, errorResponse } from '../utils'

const PERMISSION_MAP: Record<string, string[]> = {
  requester: ['demand:view', 'demand:create', 'demand:reply', 'task:view', 'message:view', 'message:manage'],
  builder: ['demand:view', 'task:view', 'task:join', 'task:update', 'member:view', 'message:view', 'message:manage'],
  operator: [
    'demand:view', 'demand:reply', 'demand:convert', 'demand:reject', 'demand:link',
    'task:view', 'task:manage', 'member:view', 'member:approve', 'member:invite',
    'task:assign', 'message:view', 'message:manage',
    'demand:archive',
  ],
  super_admin: [
    'demand:view', 'demand:create', 'demand:reply', 'demand:convert', 'demand:reject', 'demand:link',
    'task:view', 'task:join', 'task:update', 'task:manage', 'task:assign',
    'member:view', 'member:approve', 'member:invite',
    'message:view', 'message:manage',
    'admin:user', 'admin:role', 'admin:log', 'demand:archive',
  ],
}

export const userHandlers = [
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
