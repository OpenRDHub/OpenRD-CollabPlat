import { api } from './client'
import type { PaginatedData } from './client'

export interface Demand {
  id: string
  title: string
  description: string
  urgency: string
  status: string
  convert_status: string
  creator_id: string
  contact_phone: string
  attachment_ids: string[]
  linked_task_id: string
  linked_demand_id: string
  progress: number
  feedback: string
  created_at: string
  updated_at: string
}

export interface MyDemand {
  id: string
  title: string
  description: string
  submitted_at: string
  status: string
  convert_status: string
  task_id: string
  progress: number
  contact: string
  attachments: number
  feedback: string
  stage: 'pending' | 'talking' | 'converted' | 'closed'
}

export interface DemandSubmitPayload {
  title: string
  description: string
  contact_phone: string
  wechat_id: string
  attachment_ids: string[]
}

export const demandsApi = {
  submit(data: DemandSubmitPayload) {
    return api.post<{ id: string; status: string }>('/demands', data)
  },

  create(data: { title: string; description: string; urgency: string; contact_phone?: string; attachment_ids?: string[] }) {
    return api.post<{ id: string; status: string }>('/demands', data)
  },

  getMyDemands(params?: { status?: string; keyword?: string; page?: number; page_size?: number }) {
    return api.get<PaginatedData<MyDemand>>('/me/demands', params)
  },

  getDetail(demandId: string) {
    return api.get<Demand>(`/demands/${demandId}`)
  },

  getList(params?: { status?: string; keyword?: string; page?: number; page_size?: number }) {
    return api.get<PaginatedData<Demand>>('/demands', params)
  },

  sendReply(demandId: string, data: { thread_id?: string; content: string; attachment_ids?: string[] }) {
    return api.post(`/demands/${demandId}/replies`, data)
  },

  revokeReply(demandId: string, replyId: string) {
    return api.post(`/demands/${demandId}/replies/${replyId}/revoke`)
  },

  convert(demandId: string, data: { title: string; task_type: string; priority: string; scope?: string; acceptance_criteria?: string }) {
    return api.post(`/demands/${demandId}/convert`, data)
  },

  reject(demandId: string, data: { reason: string }) {
    return api.post(`/demands/${demandId}/reject`, data)
  },

  linkSimilar(demandId: string, data: { linked_demand_id: string }) {
    return api.post(`/demands/${demandId}/link-similar`, data)
  },

  archive(demandId: string) {
    return api.post(`/demands/${demandId}/archive`)
  },

  getSimilarCandidates(demandId: string) {
    return api.get(`/demands/${demandId}/similar-candidates`)
  },
}
