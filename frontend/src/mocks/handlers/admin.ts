import { http } from 'msw'
import { faker } from '@faker-js/faker/locale/zh_CN'
import { users, persistUserProfile, getCurrentUser } from '../data/users'
import {
  successResponse,
  errorResponse,
  paginatedResponse,
  parsePageParams,
  paginate,
} from '../utils'

// 与后端 app/core/permissions.py 的 ALL_PERMISSIONS 对齐
const ALL_PERMISSIONS = [
  'demand:create', 'demand:view', 'demand:reply', 'demand:convert',
  'demand:reject', 'demand:link', 'demand:archive',
  'task:view', 'task:join', 'task:update', 'task:manage', 'task:status',
  'member:view', 'member:approve', 'member:invite', 'member:manage',
  'message:view', 'message:manage',
  'file:upload', 'file:delete',
  'admin:user', 'admin:role', 'admin:log',
]

// 各角色的模板权限（与后端 ROLE_PERMISSIONS 对齐）
// builder 刻意不含 task:update：普通任务成员不能提交进度，该权限只由管理员手动授予。
const ROLE_TEMPLATE_PERMISSIONS: Record<string, string[]> = {
  requester: ['demand:create', 'demand:view', 'task:view', 'message:view', 'file:upload'],
  builder: ['demand:create', 'demand:view', 'task:view', 'task:join', 'member:view', 'message:view', 'file:upload'],
  operator: [
    'demand:create', 'demand:view', 'demand:reply', 'demand:convert', 'demand:reject',
    'demand:link', 'demand:archive', 'task:view', 'task:update', 'task:manage', 'task:status',
    'member:view', 'member:approve', 'member:invite', 'member:manage',
    'message:view', 'message:manage', 'file:upload', 'file:delete',
  ],
  super_admin: ALL_PERMISSIONS,
}

const MANUAL_PERMS_KEY = 'mock_manual_permissions'

const MANUAL_PERMS_DEFAULTS: Record<string, string[]> = {
  'usr-001': [],
  'usr-002': ['member:approve', 'task:manage'],
  'usr-003': ['admin:user'],
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

function hoursAgo(h: number) {
  return new Date(Date.now() - h * 3600_000).toISOString()
}

function fmtDate(iso: string) {
  return iso.slice(0, 10).replace(/-/g, '')
}

const SEED_LOGS = [
  { id: `LOG-${fmtDate(hoursAgo(1))}-001`, module: '权限管理', action: '修改角色权限', target: '角色模板 operator', operator: '系统管理员', operator_account: 'admin_root', operator_role: 'super_admin', ip: '192.168.1.102', device: 'Chrome 126 / Windows 11', result: 'success', risk_level: 'high', trace_id: 'TRC-A1B2C3', note: '批量修改了 operator 角色的需求管理权限', created_at: hoursAgo(1) },
  { id: `LOG-${fmtDate(hoursAgo(2))}-002`, module: '用户管理', action: '封禁用户', target: '用户 usr-089', operator: '系统管理员', operator_account: 'admin_root', operator_role: 'super_admin', ip: '192.168.1.102', device: 'Chrome 126 / Windows 11', result: 'success', risk_level: 'medium', trace_id: 'TRC-D4E5F6', note: '因违规操作被临时封禁', created_at: hoursAgo(2) },
  { id: `LOG-${fmtDate(hoursAgo(3))}-003`, module: '登录安全', action: '登录失败', target: '账户 builder_linzixuan', operator: '林子轩', operator_account: 'builder_linzixuan', operator_role: 'builder', ip: '203.205.17.88', device: 'Firefox 126 / macOS 14', result: 'failed', risk_level: 'medium', trace_id: 'TRC-G7H8I9', note: '连续 5 次密码错误，触发风控', created_at: hoursAgo(3) },
  { id: `LOG-${fmtDate(hoursAgo(5))}-004`, module: '系统配置', action: '修改平台参数', target: '注册审核开关', operator: '系统管理员', operator_account: 'admin_root', operator_role: 'super_admin', ip: '192.168.1.102', device: 'Chrome 126 / Windows 11', result: 'success', risk_level: 'high', trace_id: 'TRC-J1K2L3', note: '关闭了新用户注册审核流程', created_at: hoursAgo(5) },
  { id: `LOG-${fmtDate(hoursAgo(8))}-005`, module: '需求管理', action: '强制关闭需求', target: '需求 #DEM-0098', operator: '赵明', operator_account: 'operator_zhaoming', operator_role: 'operator', ip: '10.0.0.55', device: 'Edge 126 / Windows 10', result: 'blocked', risk_level: 'high', trace_id: 'TRC-M4N5O6', note: '操作被风控拦截，该需求已有关联任务', created_at: hoursAgo(8) },
  { id: `LOG-${fmtDate(hoursAgo(26))}-006`, module: '任务管理', action: '删除任务', target: '任务 #TSK-0215', operator: '系统管理员', operator_account: 'admin_root', operator_role: 'super_admin', ip: '192.168.1.102', device: 'Chrome 126 / Windows 11', result: 'success', risk_level: 'medium', trace_id: 'TRC-P7Q8R9', note: '清理已完成超过 180 天的归档任务', created_at: hoursAgo(26) },
  { id: `LOG-${fmtDate(hoursAgo(30))}-007`, module: '权限管理', action: '手动授权', target: '用户 林子轩 / builder_linzixuan', operator: '系统管理员', operator_account: 'admin_root', operator_role: 'super_admin', ip: '192.168.1.102', device: 'Chrome 126 / Windows 11', result: 'success', risk_level: 'medium', trace_id: 'TRC-S1T2U3', note: '为林子轩临时增加 task:assign 权限', created_at: hoursAgo(30) },
  { id: `LOG-${fmtDate(hoursAgo(38))}-008`, module: '登录安全', action: '用户登录', target: '账户 admin_root', operator: '系统管理员', operator_account: 'admin_root', operator_role: 'super_admin', ip: '192.168.1.102', device: 'Chrome 126 / Windows 11', result: 'success', risk_level: 'low', trace_id: 'TRC-V4W5X6', note: '', created_at: hoursAgo(38) },
  { id: `LOG-${fmtDate(hoursAgo(50))}-009`, module: '用户管理', action: '重置密码', target: '用户 陈北 / requester_chenbei', operator: '系统管理员', operator_account: 'admin_root', operator_role: 'super_admin', ip: '192.168.1.102', device: 'Chrome 126 / Windows 11', result: 'success', risk_level: 'medium', trace_id: 'TRC-Y7Z8A9', note: '用户申请管理员协助重置密码', created_at: hoursAgo(50) },
  { id: `LOG-${fmtDate(hoursAgo(55))}-010`, module: '系统配置', action: '导出数据', target: '用户列表全量数据', operator: '系统管理员', operator_account: 'admin_root', operator_role: 'super_admin', ip: '192.168.1.102', device: 'Chrome 126 / Windows 11', result: 'success', risk_level: 'high', trace_id: 'TRC-B1C2D3', note: '合规审计需求，导出包含个人信息字段', created_at: hoursAgo(55) },
  { id: `LOG-${fmtDate(hoursAgo(68))}-011`, module: '登录安全', action: '登录拦截', target: '账户 unknown_user', operator: '未知用户', operator_account: 'unknown_user', operator_role: '', ip: '45.33.32.156', device: 'Unknown / Linux', result: 'blocked', risk_level: 'high', trace_id: 'TRC-E4F5G6', note: '异常 IP 登录尝试，已触发封锁', created_at: hoursAgo(68) },
  { id: `LOG-${fmtDate(hoursAgo(80))}-012`, module: '需求管理', action: '提交需求', target: '需求 #DEM-0120 / 复诊问题清单', operator: '陈北', operator_account: 'requester_chenbei', operator_role: 'requester', ip: '120.244.66.82', device: 'Chrome 126 / Android', result: 'success', risk_level: 'low', trace_id: 'TRC-H7I8J9', note: '需求者提交新需求，进入待审核池', created_at: hoursAgo(80) },
  { id: `LOG-${fmtDate(hoursAgo(90))}-013`, module: '任务管理', action: '申请加入任务', target: '任务 #TSK-0188 / 用药提醒 API', operator: '林子轩', operator_account: 'builder_linzixuan', operator_role: 'builder', ip: '223.104.41.18', device: 'Safari 17 / macOS', result: 'success', risk_level: 'low', trace_id: 'TRC-K3L4M5', note: '普通协作行为，等待队长审核', created_at: hoursAgo(90) },
  { id: `LOG-${fmtDate(hoursAgo(105))}-014`, module: '需求管理', action: '需求转工单', target: '需求 #DEM-0098 / 症状记录功能', operator: '赵明', operator_account: 'operator_zhaoming', operator_role: 'operator', ip: '10.0.0.55', device: 'Edge 126 / Windows 10', result: 'success', risk_level: 'medium', trace_id: 'TRC-N6O7P8', note: '需求审核通过并创建关联工单，记录转化链路', created_at: hoursAgo(105) },
  { id: `LOG-${fmtDate(hoursAgo(115))}-015`, module: '权限管理', action: '删除角色模板', target: '角色模板 guest', operator: '系统管理员', operator_account: 'admin_root', operator_role: 'super_admin', ip: '192.168.1.102', device: 'Chrome 126 / Windows 11', result: 'success', risk_level: 'medium', trace_id: 'TRC-Q9R1S2', note: '废弃的访客角色已无用户关联，安全清除', created_at: hoursAgo(115) },
]

// ── localStorage 持久化 ──
const LOG_STORAGE_KEY = 'mock_system_logs'

interface LogEntry {
  id: string; module: string; action: string; target: string
  operator: string; operator_account: string; operator_role: string
  ip: string; device: string; result: string; risk_level: string
  trace_id: string; note: string; created_at: string
}

const systemLogs: LogEntry[] = [...SEED_LOGS]

function loadPersistedLogs() {
  try {
    const raw = localStorage.getItem(LOG_STORAGE_KEY)
    if (!raw) return
    const persisted: LogEntry[] = JSON.parse(raw)
    systemLogs.unshift(...persisted)
  } catch { /* ignore */ }
}

function persistLogs() {
  try {
    const seedIds = new Set(SEED_LOGS.map(l => l.id))
    const userLogs = systemLogs.filter(l => !seedIds.has(l.id))
    localStorage.setItem(LOG_STORAGE_KEY, JSON.stringify(userLogs))
  } catch { /* ignore */ }
}

let logCounter = 100

function addSystemLog(fields: {
  module: string; action: string; target: string
  result: string; risk_level: string; note: string
}) {
  const now = new Date()
  const user = getCurrentUser()
  const log: LogEntry = {
    id: `LOG-${fmtDate(now.toISOString())}-${String(++logCounter).padStart(3, '0')}`,
    module: fields.module,
    action: fields.action,
    target: fields.target,
    operator: user.nickname,
    operator_account: user.platform_id,
    operator_role: user.role,
    ip: '127.0.0.1',
    device: navigator.userAgent.slice(0, 40),
    result: fields.result,
    risk_level: fields.risk_level,
    trace_id: `TRC-${Math.random().toString(36).slice(2, 8).toUpperCase()}`,
    note: fields.note,
    created_at: now.toISOString(),
  }
  systemLogs.unshift(log)
  persistLogs()
}

loadPersistedLogs()

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
    const currentUser = getCurrentUser()

    // 角色变更守卫：只有超级管理员可以变更角色，且不能改自己的角色
    if (typeof body.role === 'string' && body.role !== user.role) {
      if (currentUser.role !== 'super_admin') {
        return errorResponse('FORBIDDEN', '只有超级管理员可以变更角色', 403)
      }
      if (currentUser.id === user.id) {
        return errorResponse('FORBIDDEN', '不能修改自己的角色', 403)
      }
    }

    const { new_password, ...rest } = body
    const changedFields = Object.keys(rest).join('、') || (new_password ? '密码' : '')
    Object.assign(user, rest)
    if (new_password && typeof new_password === 'string') {
      user.password = new_password
    }
    persistUserProfile(user)
    addSystemLog({
      module: '用户管理', action: '修改用户信息',
      target: `${user.nickname} / ${user.platform_id}`,
      result: 'success', risk_level: rest.role ? 'high' : 'medium',
      note: `修改字段：${changedFields || '密码'}`,
    })
    return successResponse({})
  }),

  http.post('/api/v1/admin/users/:user_id/lock', ({ params }) => {
    const user = users.find((u) => u.id === params.user_id)
    const currentUser = getCurrentUser()

    // 锁定守卫：不能锁定自己；超管只能被超管锁定
    if (user) {
      if (currentUser.id === user.id) {
        return errorResponse('FORBIDDEN', '不能锁定自己的账号', 403)
      }
      if (user.role === 'super_admin' && currentUser.role !== 'super_admin') {
        return errorResponse('FORBIDDEN', '只有超级管理员可以锁定超级管理员', 403)
      }
    }

    if (user) { user.status = 'locked'; persistUserProfile(user) }
    addSystemLog({
      module: '用户管理', action: '封禁用户',
      target: user ? `${user.nickname} / ${user.platform_id}` : String(params.user_id),
      result: 'success', risk_level: 'high',
      note: '管理员手动封禁用户账号',
    })
    return successResponse({})
  }),

  http.post('/api/v1/admin/users/:user_id/unlock', ({ params }) => {
    const user = users.find((u) => u.id === params.user_id)
    const currentUser = getCurrentUser()

    // 解锁守卫：与锁定接口对称，超管只能被超管解锁
    if (user && user.role === 'super_admin' && currentUser.role !== 'super_admin') {
      return errorResponse('FORBIDDEN', '只有超级管理员可以解锁超级管理员', 403)
    }

    if (user) { user.status = 'active'; persistUserProfile(user) }
    addSystemLog({
      module: '用户管理', action: '解封用户',
      target: user ? `${user.nickname} / ${user.platform_id}` : String(params.user_id),
      result: 'success', risk_level: 'medium',
      note: '管理员手动解除账号封禁',
    })
    return successResponse({})
  }),

  http.get('/api/v1/admin/roles', () => {
    // 与后端 GET /admin/roles 契约对齐：返回 [{name, code, permissions}]
    const roles = Object.entries(ROLE_TEMPLATE_PERMISSIONS).map(([code, permissions]) => ({
      name: code,
      code,
      permissions: [...permissions].sort(),
    }))
    return successResponse(roles)
  }),

  http.post('/api/v1/admin/roles', () => {
    return successResponse({})
  }),

  http.patch('/api/v1/admin/roles/:role_id', async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>
    addSystemLog({
      module: '权限管理', action: '修改角色权限',
      target: `角色 ${String(params.role_id)}`,
      result: 'success', risk_level: 'high',
      note: body.permissions ? '修改角色权限列表' : '修改角色信息',
    })
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
    const effective = [...new Set([...template, ...manual])]
    return successResponse({
      role: user.role,
      template_permission_ids: template,
      manual_permission_ids: manual,
      effective_permission_ids: effective,
    })
  }),

  http.put('/api/v1/admin/users/:user_id/authorization', async ({ params, request }) => {
    const userId = params.user_id as string
    const body = (await request.json()) as {
      role?: string
      manual_permission_ids?: string[]
      reason?: string
    }
    const user = users.find((u) => u.id === userId)
    if (!user) return errorResponse('NOT_FOUND', '用户不存在', 404)

    const currentUser = getCurrentUser()

    // 守卫 1：不能修改自己的授权
    if (currentUser.id === userId) {
      return errorResponse('FORBIDDEN', '不能修改自己的授权', 403)
    }

    const role = body.role ?? user.role
    const actorIsSuper = currentUser.role === 'super_admin'

    // 守卫 2/3：只有超级管理员可以变更角色 / 调整超级管理员
    if (role !== user.role && !actorIsSuper) {
      return errorResponse('FORBIDDEN', '只有超级管理员可以变更角色', 403)
    }
    if ((user.role === 'super_admin' || role === 'super_admin') && !actorIsSuper) {
      return errorResponse('FORBIDDEN', '只有超级管理员可以调整超级管理员的授权', 403)
    }
    if (!ROLE_TEMPLATE_PERMISSIONS[role]) {
      return errorResponse('BAD_REQUEST', '非法角色', 400)
    }

    // reason 必填且不可为纯空格，用于权限审计
    const reason = (body.reason ?? '').trim()
    if (!reason) return errorResponse('VALIDATION_ERROR', '调整原因不能为空', 422)

    // 权限 ID 必须属于 ALL_PERMISSIONS
    const requested = body.manual_permission_ids ?? []
    const invalid = requested.filter((id) => !ALL_PERMISSIONS.includes(id))
    if (invalid.length > 0) {
      return errorResponse('BAD_REQUEST', `非法权限 ID: ${invalid.join(', ')}`, 400)
    }

    // 守卫 4：非超级管理员不能授予超出自身最终权限的权限
    if (!actorIsSuper) {
      const actorTemplate = ROLE_TEMPLATE_PERMISSIONS[currentUser.role] ?? []
      const actorManual = manualPermissionsStore[currentUser.id] ?? []
      const actorEffective = new Set([...actorTemplate, ...actorManual])
      const beyond = requested.filter((id) => !actorEffective.has(id))
      if (beyond.length > 0) {
        return errorResponse('FORBIDDEN', `不能授予超出自身权限范围的权限: ${beyond.join(', ')}`, 403)
      }
    }

    // 守卫 5：不能降级最后一个超级管理员
    if (user.role === 'super_admin' && role !== 'super_admin') {
      const superCount = users.filter((u) => u.role === 'super_admin').length
      if (superCount <= 1) {
        return errorResponse('BAD_REQUEST', '不能降级最后一个超级管理员', 400)
      }
    }

    const previous = manualPermissionsStore[userId] ?? []
    const next = [...new Set(requested)]
    manualPermissionsStore[userId] = next
    saveManualPermissions(manualPermissionsStore)

    // 必须在修改 user.role 之前取旧角色，否则 role !== user.role 恒为 false，
    // 角色变更会被错误记录成「修改用户权限」。
    const previousRole = user.role
    if (role !== previousRole) {
      user.role = role
      persistUserProfile(user)
    }

    const added = next.filter((id) => !previous.includes(id))
    const removed = previous.filter((id) => !next.includes(id))

    addSystemLog({
      module: '权限管理',
      action: role !== previousRole ? '调整用户授权（角色+权限）' : '修改用户权限',
      target: `${user.nickname} / ${user.platform_id}`,
      result: 'success',
      risk_level: 'high',
      note: `调整原因：${reason}；新增 ${added.join(', ') || '无'}；移除 ${removed.join(', ') || '无'}`,
    })

    const template = ROLE_TEMPLATE_PERMISSIONS[user.role] ?? []
    return successResponse({
      role: user.role,
      template_permission_ids: template,
      manual_permission_ids: next,
      effective_permission_ids: [...new Set([...template, ...next])],
    })
  }),

  http.get('/api/v1/admin/system-logs/summary', () => {
    const today = new Date().toISOString().slice(0, 10)
    const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
    return successResponse({
      today: systemLogs.filter(l => l.created_at.startsWith(today)).length,
      high_risk: systemLogs.filter(l => l.risk_level === 'high').length,
      failed: systemLogs.filter(l => l.result !== 'success').length,
      week: systemLogs.filter(l => l.created_at >= weekAgo).length,
    })
  }),

  http.get('/api/v1/admin/system-logs', ({ request }) => {
    const url = new URL(request.url)
    const { page, pageSize } = parsePageParams(url)
    const keyword = url.searchParams.get('keyword')?.toLowerCase() || ''
    const moduleFilter = url.searchParams.get('module') || ''
    const riskFilter = url.searchParams.get('risk_level') || ''
    const resultFilter = url.searchParams.get('result') || ''

    let filtered = [...systemLogs]
    if (keyword) {
      filtered = filtered.filter(l =>
        l.operator.includes(keyword) ||
        l.operator_account.includes(keyword) ||
        l.target.toLowerCase().includes(keyword) ||
        l.ip.includes(keyword)
      )
    }
    if (moduleFilter) filtered = filtered.filter(l => l.module === moduleFilter)
    if (riskFilter) filtered = filtered.filter(l => l.risk_level === riskFilter)
    if (resultFilter) filtered = filtered.filter(l => l.result === resultFilter)

    return paginatedResponse(paginate(filtered, page, pageSize), page, pageSize, filtered.length)
  }),
]