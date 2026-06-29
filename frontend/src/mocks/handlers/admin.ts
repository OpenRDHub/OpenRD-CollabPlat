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

const ALL_PERMISSIONS = [
  'demand:view', 'demand:create', 'demand:reply', 'demand:convert',
  'demand:reject', 'demand:link', 'demand:archive', 'task:view', 'task:join', 'task:update',
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
    return successResponse({ roles: ROLES })
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

  http.put('/api/v1/admin/users/:user_id/permissions', async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const user = users.find((u) => u.id === params.user_id)
    addSystemLog({
      module: '权限管理', action: '修改用户权限',
      target: user ? `${user.nickname} / ${user.platform_id}` : String(params.user_id),
      result: 'success', risk_level: 'high',
      note: `设置权限：${Array.isArray(body.permissions) ? (body.permissions as string[]).join(', ') : '—'}`,
    })

    return successResponse({})
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
