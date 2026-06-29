export interface MenuItem {
  label: string
  icon: string
  to: string
}

const MENUS: Record<string, MenuItem[]> = {
  requester: [
    { label: '大厅', icon: '🏛️', to: '/hall' },
    { label: '工作台', icon: '📊', to: '/dashboard' },
    { label: '我的需求', icon: '📋', to: '/my-demands' },
    { label: '消息中心', icon: '🔔', to: '/messages' },
    { label: '个人设置', icon: '⚙️', to: '/settings' },
  ],
  builder: [
    { label: '大厅', icon: '🏛️', to: '/hall' },
    { label: '工作台', icon: '📊', to: '/dashboard' },
    { label: '我的任务', icon: '✅', to: '/my-tasks' },
    { label: '我的需求', icon: '📋', to: '/my-demands' },
    { label: '消息中心', icon: '🔔', to: '/messages' },
    { label: '个人设置', icon: '⚙️', to: '/settings' },
  ],
  operator: [
    { label: '大厅', icon: '🏛️', to: '/hall' },
    { label: '工作台', icon: '📊', to: '/dashboard' },
    { label: '需求管理', icon: '📋', to: '/admin/demand-management' },
    { label: '任务管理', icon: '✅', to: '/admin/task-management' },
    { label: '消息中心', icon: '🔔', to: '/messages' },
    { label: '个人设置', icon: '⚙️', to: '/settings' },
  ],
  super_admin: [
    { label: '大厅', icon: '🏛️', to: '/hall' },
    { label: '工作台', icon: '📊', to: '/dashboard' },
    { label: '需求管理', icon: '📋', to: '/admin/demand-management' },
    { label: '任务管理', icon: '✅', to: '/admin/task-management' },
    { label: '用户管理', icon: '👥', to: '/admin/user-management' },
    { label: '角色权限', icon: '🔐', to: '/admin/permission-management' },
    { label: '系统日志', icon: '📜', to: '/admin/system-logs' },
    { label: '个人设置', icon: '⚙️', to: '/settings' },
  ],
}

export function getMenuByRole(role: string): MenuItem[] {
  return MENUS[role] ?? MENUS.requester ?? []
}
