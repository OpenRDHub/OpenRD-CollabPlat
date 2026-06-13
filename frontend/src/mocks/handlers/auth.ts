import { http } from 'msw'
import { users, setCurrentUser } from '../data/users'
import { successResponse, errorResponse } from '../utils'

export const authHandlers = [
  http.post('/api/v1/auth/register', async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>
    return successResponse({
      user_id: `usr-${Date.now()}`,
      platform_id: `platform_${body.username}`,
    })
  }),

  http.post('/api/v1/auth/login', async ({ request }) => {
    const body = (await request.json()) as Record<string, string>
    const user = users.find(
      (u) => u.username === body.username && u.password === body.password,
    )
    if (!user) {
      return errorResponse('UNAUTHORIZED', '用户名或密码错误', 401)
    }
    setCurrentUser(user.id)
    return successResponse({
      access_token: `mock-access-token-${user.id}`,
      refresh_token: `mock-refresh-token-${user.id}`,
      user: {
        id: user.id,
        username: user.username,
        nickname: user.nickname,
        role: user.role,
        avatar_url: user.avatar_url,
      },
    })
  }),

  http.post('/api/v1/auth/refresh', () => {
    return successResponse({
      access_token: `mock-access-token-refreshed-${Date.now()}`,
      refresh_token: `mock-refresh-token-refreshed-${Date.now()}`,
    })
  }),

  http.post('/api/v1/auth/logout', () => {
    return successResponse({})
  }),

  http.post('/api/v1/auth/sms-code', () => {
    return successResponse({ message: '验证码已发送' })
  }),

  http.post('/api/v1/auth/password/reset', () => {
    return successResponse({})
  }),

  http.post('/api/v1/auth/onboarding', () => {
    return successResponse({})
  }),
]
