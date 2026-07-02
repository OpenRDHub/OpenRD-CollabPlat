import { api } from './client'

export interface UserSearchItem {
  platform_id: string
  nickname: string | null
  role: string | null
  avatar_url: string | null
}

export const usersApi = {
  search(keyword: string) {
    return api.get<UserSearchItem[]>('/users/search', { keyword })
  },
}
