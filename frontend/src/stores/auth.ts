import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import { api } from '@/api/client'
import type { ApiResponse } from '@/api/client'

interface UserInfo {
  id: string
  platform_id: string
  nickname: string
  role: string
  avatar_url: string
  location?: string
  province?: string
  is_onboarded: number
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const user = ref<UserInfo | null>(null)
  const permissions = ref<string[]>([])

  const isLoggedIn = computed(() => !!token.value)
  const userRole = computed(() => user.value?.role || '')

  async function login(username: string, password: string) {
    const res = await authApi.login({ username, password })
    token.value = res.data.access_token
    refreshToken.value = res.data.refresh_token
    localStorage.setItem('access_token', res.data.access_token)
    localStorage.setItem('refresh_token', res.data.refresh_token)
    user.value = res.data.user as UserInfo
    await fetchPermissions()
  }

  function logout() {
    token.value = ''
    refreshToken.value = ''
    user.value = null
    permissions.value = []
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    sessionStorage.removeItem('mock_current_user')
  }

  async function fetchMe() {
    const res = await api.get<UserInfo>('/me')
    user.value = res.data
  }

  async function fetchPermissions() {
    const res = await api.get<string[] | { permissions: string[] }>('/me/permissions')
    permissions.value = Array.isArray(res.data) ? res.data : (res.data.permissions ?? [])
  }

  function hasPermission(perm: string): boolean {
    return permissions.value.includes(perm)
  }

  async function restore() {
    if (!token.value) return false
    try {
      await fetchMe()
      await fetchPermissions()
      return true
    } catch {
      logout()
      return false
    }
  }

  return {
    token,
    refreshToken,
    user,
    permissions,
    isLoggedIn,
    userRole,
    login,
    logout,
    fetchMe,
    fetchPermissions,
    hasPermission,
    restore,
  }
})
