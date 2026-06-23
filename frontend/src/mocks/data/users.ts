export interface MockUser {
  id: string
  platform_id: string
  username: string
  password: string
  nickname: string
  phone: string
  avatar_url: string
  role: string
  identity: string
  position: string
  province: string
  tags: string[]
  intro: string
  status: string
  created_at: string
  onboarding_completed: number
  is_deleted: number
  deleted_at: string
  deleted_by: string
}

export const users: MockUser[] = [
  {
    id: 'usr-001',
    platform_id: 'requester_chenbei',
    username: 'chenbei',
    password: 'OpenRD#2026',
    nickname: '陈北',
    phone: '15900000001',
    avatar_url: '',
    role: 'requester',
    identity: '患者家属',
    position: '需求者',
    province: '上海',
    tags: ['罕见病政策', '药物信息', '患者社区'],
    intro: '关注罕见病药物信息共享，愿意帮助患者与家属把真实需求转化为可协作的开源任务。',
    status: 'active',
    created_at: '2026-05-10T08:00:00+08:00',
    onboarding_completed: 1,
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'usr-002',
    platform_id: 'builder_linzixuan',
    username: 'linzixuan',
    password: 'OpenRD#2026',
    nickname: '林子轩',
    phone: '15900000002',
    avatar_url: '',
    role: 'builder',
    identity: '志愿开发者',
    position: '全栈工程师',
    province: '浙江',
    tags: ['数据分析', '自然语言处理', '医学影像'],
    intro: '3年 Vue + Python 开发经验，希望参与开源公益项目',
    status: 'active',
    created_at: '2026-05-12T10:30:00+08:00',
    onboarding_completed: 1,
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'usr-003',
    platform_id: 'operator_zhaoming',
    username: 'zhaoming',
    password: 'OpenRD#2026',
    nickname: '赵明',
    phone: '15900000003',
    avatar_url: '',
    role: 'operator',
    identity: '产品经理',
    position: '产品经理',
    province: '北京',
    tags: ['需求分析', '项目管理', '用户研究'],
    intro: '负责需求评审和任务转化，推动平台协作效率提升',
    status: 'active',
    created_at: '2026-04-20T09:00:00+08:00',
    onboarding_completed: 1,
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'usr-004',
    platform_id: 'admin_root',
    username: 'admin',
    password: 'OpenRD#2026',
    nickname: '系统管理员',
    phone: '15900000000',
    avatar_url: '',
    role: 'super_admin',
    identity: '平台治理',
    position: '超级管理员',
    province: '北京',
    tags: ['系统架构', '安全审计', '权限管理'],
    intro: '平台治理与权限管控，确保系统稳定运行',
    status: 'active',
    created_at: '2026-03-01T00:00:00+08:00',
    onboarding_completed: 1,
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
]

const PROFILE_STORAGE_KEY = 'mock_user_profiles'

function loadPersistedProfiles() {
  try {
    const raw = sessionStorage.getItem(PROFILE_STORAGE_KEY)
    if (!raw) return
    const patches: Record<string, Partial<MockUser>> = JSON.parse(raw)
    for (const user of users) {
      if (patches[user.id]) {
        Object.assign(user, patches[user.id])
      }
    }
  } catch { /* ignore */ }
}

function persistUserProfile(user: MockUser) {
  try {
    const raw = sessionStorage.getItem(PROFILE_STORAGE_KEY)
    const patches: Record<string, Partial<MockUser>> = raw ? JSON.parse(raw) : {}
    const { password, ...safeFields } = user
    patches[user.id] = safeFields
    sessionStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(patches))
  } catch { /* ignore */ }
}

loadPersistedProfiles()

export let currentUserId = sessionStorage.getItem('mock_current_user') || 'usr-001'
export function setCurrentUser(id: string) {
  currentUserId = id
  sessionStorage.setItem('mock_current_user', id)
}
export function getCurrentUser() { return users.find(u => u.id === currentUserId)! }
export { persistUserProfile }