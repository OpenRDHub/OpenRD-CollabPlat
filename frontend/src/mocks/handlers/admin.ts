import { http } from 'msw'
import { faker } from '@faker-js/faker/locale/zh_CN'
import { users, persistUserProfile } from '../data/users'
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
  'admin:demands', 'admin:tasks',
  'admin:users', 'admin:roles', 'admin:logs',
]

const ROLES = [
  { id: 'role-requester', name: 'requester', label: '需求方', description: '提交和跟踪需求' },
  { id: 'role-builder', name: 'builder', label: '共建方', description: '参与任务协作开发' },
  { id: 'role-operator', name: 'operator', label: '产品经理', description: '审核需求、管理任务' },
  { id: 'role-super_admin', name: 'super_admin', label: '超级管理员', description: '平台全局管理' },
]

// 各角色的模板权限（与后端 ROLE_PERMISSIONS 对齐）
const ROLE_TEMPLATE_PERMISSIONS: Record<string, string[]> = {
  requester: ['demand:create', 'demand:view', 'task:view', 'message:view'],
  builder: ['demand:view', 'task:view', 'task:join', 'task:update', 'member:view', 'message:view'],
  operator: [
    'demand:view', 'demand:reply', 'demand:convert', 'demand:reject', 'demand:link',
    'task:view', 'task:manage', 'task:assign', 'member:view', 'member:approve', 'member:invite',
    'message:view', 'message:manage', 'admin:demands', 'admin:tasks',
  ],
  super_admin: ALL_PERMISSIONS,
}

const MANUAL_PERMS_KEY = 'mock_manual_permissions'

const MANUAL_PERMS_DEFAULTS: Record<string, string[]> = {
  'usr-001': [],
  'usr-002': ['member:approve', 'task:assign'],
  'usr-003': ['admin:users'],
  'usr-004': [],
}

function loadManualPermissions(): Record<string, string[]> {
  try {
    const raw = localStorage.getItem(MANUAL_PERMS_KEY)
    if (raw) return { ...MANUAL_PERMS_DEFAULTS, ...JSON.parse(raw) }
  } catch { /* ignore */ }
  return { ...MANUAL_PERMS_DEFAULTS }
}

function saveManualPermissions(store: Record<string, string[]>) {
  try {
    localStorage.setItem(MANUAL_PERMS_KEY, JSON.stringify(store))
  } catch { /* ignore */ }
}

const manualPermissionsStore: Record<string, string[]> = loadManualPermissions()

export const adminHandlers = [
  http.get('/api/v1/admin/users', ({ request }) => {
    const url = new URL(request.url)
    const { page, pageSize } = parsePageParams(url)
    const keyword = url.searchParams.get('keyword')?.toLowerCase() || ''
    const role = url.searchParams.get('role') || ''

    let filtered = users.filter((u) => u.is_deleted === 0)

    if (keyword) {
      filtered = filtered.filter((u) =>
        u.platform_id.toLowerCase().includes(keyword) ||
        u.nickname.toLowerCase().includes(keyword) ||
        u.phone.includes(keyword)
      )
    }

    if (role && role !== 'all') {
      filtered = filtered.filter((u) => u.role === role)
    }

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
    const { new_password, ...rest } = body
    Object.assign(user, rest)
    if (new_password && typeof new_password === 'string') {
      user.password = new_password
    }
    persistUserProfile(user)
    return successResponse({})
  }),

  http.post('/api/v1/admin/users/:user_id/lock', ({ params }) => {
    const user = users.find((u) => u.id === params.user_id)
    if (user) { user.status = 'locked'; persistUserProfile(user) }
    return successResponse({})
  }),

  http.post('/api/v1/admin/users/:user_id/unlock', ({ params }) => {
    const user = users.find((u) => u.id === params.user_id)
    if (user) { user.status = 'active'; persistUserProfile(user) }
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

  http.get('/api/v1/admin/users/:user_id/permissions', ({ params }) => {
    const userId = params.user_id as string
    const user = users.find((u) => u.id === userId)
    if (!user) return errorResponse('NOT_FOUND', '用户不存在', 404)
    const manual = manualPermissionsStore[userId] ?? []
    const template = ROLE_TEMPLATE_PERMISSIONS[user.role] ?? []
    return successResponse({
      role: user.role,
      template_permissions: template,
      manual_permissions: manual,
    })
  }),

  http.put('/api/v1/admin/users/:user_id/permissions', async ({ params, request }) => {
    const userId = params.user_id as string
    const body = (await request.json()) as { role?: string; manual_permissions?: string[] }
    const user = users.find((u) => u.id === userId)
    if (!user) return errorResponse('NOT_FOUND', '用户不存在', 404)
    if (body.role) {
      user.role = body.role
      persistUserProfile(user)
    }
    manualPermissionsStore[userId] = body.manual_permissions ?? []
    saveManualPermissions(manualPermissionsStore)
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
