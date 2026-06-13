import { api } from './client'
import type { PaginatedData } from './client'

export interface Message {
  id: string
  category: string
  title: string
  summary: string
  content: string
  sender: string
  target_type: string
  target_id: string
  action_text: string
  read_status: number
  created_at: string
}

export const messagesApi = {
  getList(params?: { category?: string; keyword?: string; page?: number; page_size?: number }) {
    return api.get<PaginatedData<Message>>('/messages', params)
  },

  getUnreadCount() {
    return api.get<{ count: number }>('/messages/unread-count')
  },

  getDetail(messageId: string) {
    return api.get<Message>(`/messages/${messageId}`)
  },

  markRead(messageId: string) {
    return api.post(`/messages/${messageId}/read`)
  },

  markAllRead() {
    return api.post('/messages/read-all')
  },

  delete(messageId: string) {
    return api.delete(`/messages/${messageId}`)
  },
}
