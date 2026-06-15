import { api } from './client'
import type { PaginatedData } from './client'

export interface AdminDemand {
  id: string
  title: string
  description: string
  submitted_at: string
  review_status: '待审核' | '沟通中' | '已转任务' | '已关闭'
  convert_status: '未转化' | '待评估' | '已转化' | '开发中' | '已完成'
  publisher: string
  publisher_id: string
  task_id: string | null
  progress: number
  feedback: string
  urgency: string
  contact_phone: string
  created_at: string
  updated_at: string
}

export interface DemandStats {
  total: number
  pending: number
  talking: number
  converted: number
  closed: number
}

export interface UpdateDemandPayload {
  review_status?: '待审核' | '沟通中' | '已转任务' | '已关闭'
  convert_status?: '未转化' | '待评估' | '已转化' | '开发中' | '已完成'
  task_id?: string
  progress?: number
  feedback?: string
  title?: string
}

export const adminDemandsApi = {
  getList(params?: {
    keyword?: string
    review_status?: string
    convert_status?: string
    page?: number
    page_size?: number
  }) {
    return api.get<PaginatedData<AdminDemand>>('/admin/demands', params)
  },

  getStats() {
    return api.get<DemandStats>('/admin/demands/stats')
  },

  getDemand(demandId: string) {
    return api.get<AdminDemand>(`/admin/demands/${demandId}`)
  },

  updateDemand(demandId: string, data: UpdateDemandPayload) {
    return api.patch(`/admin/demands/${demandId}`, data)
  },

  exportDemands(params?: {
    review_status?: string
    convert_status?: string
    keyword?: string
  }) {
    return api.get('/admin/demands/export', params)
  },
}
