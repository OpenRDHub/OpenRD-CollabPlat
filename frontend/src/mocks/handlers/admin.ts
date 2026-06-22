import { http } from 'msw'
import { faker } from '@faker-js/faker/locale/zh_CN'
import { users } from '../data/users'
import {
  successResponse,
  errorResponse,
  paginatedResponse,
  parsePageParams,
  paginate,
} from '../utils'

const ALL_PERMISSIONS = [
  'demand:view', 'demand:create', 'demand:reply', 'demand:convert',
  'demand:reject', 'demand:link', 'task:view', 'task:join', 'task:update',
  'task:manage', 'task:assign', 'member:view', 'member:approve',
  'member:invite', 'message:view', 'message:manage',
  'admin:users', 'admin:roles', 'admin:logs',
]

const ROLES = [
  { id: 'role-requester', name: 'requester', label: '需求方', description: '提交和跟踪需求' },
  { id: 'role-builder', name: 'builder', label: '共建方', description: '参与任务协作开发' },
  { id: 'role-operator', name: 'operator', label: '产品经理', description: '审核需求、管理任务' },
  { id: 'role-super_admin', name: 'super_admin', label: '超级管理员', description: '平台全局管理' },
]

export const adminHandlers = [
  http.get('/api/v1/admin/users', ({ request }) => {
    const url = new URL(request.url)
    const { page, pageSize } = parsePageParams(url)
    const filtered = users.filter((u) => u.is_deleted === 0)
    return paginatedResponse(
      paginate(filtered, page, pageSize).map(({ password, ...u }) => u),
      page,
      pageSize,
      filtered.length,
    )
  }),

  http.get('/api/v1/admin/users/:user_id', ({ params }) => {
    const user = users.find((u) => u.id === params.user_id)
    if (!user) return errorResponse('NOT_FOUND', '用户不存在', 404)
    const { password, ...safeUser } = user
    return successResponse(safeUser)
  }),

  http.patch('/api/v1/admin/users/:user_id', async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const user = users.find((u) => u.id === params.user_id)
    if (!user) return errorResponse('NOT_FOUND', '用户不存在', 404)
    Object.assign(user, body)
    return successResponse({})
  }),

  http.post('/api/v1/admin/users/:user_id/lock', ({ params }) => {
    const user = users.find((u) => u.id === params.user_id)
    if (user) user.status = 'locked'
    return successResponse({})
  }),

  http.post('/api/v1/admin/users/:user_id/unlock', ({ params }) => {
    const user = users.find((u) => u.id === params.user_id)
    if (user) user.status = 'active'
    return successResponse({})
  }),

  http.get('/api/v1/admin/roles', () => {
    return successResponse({ roles: ROLES })
  }),

  http.post('/api/v1/admin/roles', () => {
    return successResponse({})
  }),

  http.patch('/api/v1/admin/roles/:role_id', () => {
    return successResponse({})
  }),

  http.get('/api/v1/admin/permissions', () => {
    return successResponse({ permissions: ALL_PERMISSIONS })
  }),

  http.put('/api/v1/admin/users/:user_id/permissions', () => {
    return successResponse({})
  }),

  http.get('/api/v1/admin/system-logs', () => {
    const logs = Array.from({ length: 10 }, (_, i) => ({
      id: `log-${i + 1}`,
      operator: faker.person.fullName(),
      action: faker.helpers.arrayElement(['用户登录', '需求审核', '任务创建', '角色变更', '权限修改']),
      target: faker.helpers.arrayElement(['用户管理', '需求管理', '任务管理', '系统设置']),
      detail: faker.lorem.sentence(),
      ip: faker.internet.ipv4(),
      created_at: faker.date.recent({ days: 7 }).toISOString(),
    }))
    return successResponse({ logs })
  }),
]
