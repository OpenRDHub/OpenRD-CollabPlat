import { api } from './client'

export interface LoginResult {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: {
    id: string
    platform_id: string
    nickname: string
    role: string
  }
}

export const authApi = {
  register(data: { username: string; password: string; nickname: string; phone: string; sms_code: string; role: string }) {
    return api.post<{ user_id: string; platform_id: string; onboarding_required: number }>('/auth/register', data)
  },

  login(data: { username: string; password: string }) {
    return api.post<LoginResult>('/auth/login', data)
  },

  refresh(refresh_token: string) {
    return api.post<LoginResult>('/auth/refresh', { refresh_token })
  },

  logout(refresh_token: string) {
    return api.post('/auth/logout', { refresh_token })
  },

  sendSmsCode(data: { phone: string; scene: string }) {
    return api.post('/auth/sms-code', data)
  },

  resetPassword(data: { phone: string; sms_code: string; new_password: string }) {
    return api.post('/auth/password/reset', data)
  },

  onboarding(data: { role: string; nickname?: string; province?: string; occupation?: string; bio?: string; tags?: string[] }) {
    return api.post('/auth/onboarding', data)
  },
}
