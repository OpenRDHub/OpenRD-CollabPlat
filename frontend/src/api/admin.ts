import { api } from './client'
import type { PaginatedData } from './client'

export interface AdminUser {
  id: string
  platform_id: string
  username: string
  nickname: string
  phone: string
  role: string
  identity: string
  position: string
  province: string
  intro: string
  tags: string[]
  status: string
  created_at: string
  onboarding_completed: number
}

export interface UpdateUserPayload {
  nickname?: string
  platform_id?: string
  role?: string
  identity?: string
  position?: string
  phone?: string
  intro?: string
  new_password?: string
}

export interface SystemLog {
  id: string
  module: string
  action: string
  operator: string
  ip: string
  result: string
  risk_level: string
  created_at: string
  detail: string
}

export interface UserPermissionDetail {
  role: string
  template_permissions: string[]
  manual_permissions: string[]
}

export const adminApi = {
  getUsers(params?: { keyword?: string; role?: string; page?: number; page_size?: number }) {
    return api.get<PaginatedData<AdminUser>>('/admin/users', params)
  },

  getUser(userId: string) {
    return api.get<AdminUser>(`/admin/users/${userId}`)
  },

  updateUser(userId: string, data: UpdateUserPayload) {
    return api.patch(`/admin/users/${userId}`, data)
  },

  lockUser(userId: string) {
    return api.post(`/admin/users/${userId}/lock`)
  },

  unlockUser(userId: string) {
    return api.post(`/admin/users/${userId}/unlock`)
  },

  getRoles() {
    return api.get<{ roles: { id: string; name: string; label: string }[] }>('/admin/roles')
  },

  createRole(data: { name: string; label: string; permissions: string[] }) {
    return api.post('/admin/roles', data)
  },

  updateRole(roleId: string, data: { label?: string; permissions?: string[] }) {
    return api.patch(`/admin/roles/${roleId}`, data)
  },

  getPermissions() {
    return api.get<{ permissions: string[] }>('/admin/permissions')
  },

  getUserPermissions(userId: string) {
    return api.get<UserPermissionDetail>(`/admin/users/${userId}/permissions`)
  },

  setUserPermissions(userId: string, data: { role?: string; manual_permissions?: string[] }) {
    return api.put(`/admin/users/${userId}/permissions`, data)
  },

  getSystemLogs(params?: { keyword?: string; module?: string; risk_level?: string; page?: number; page_size?: number }) {
    return api.get<PaginatedData<SystemLog>>('/admin/system-logs', params)
  },
}
