import { api } from './client'

export interface PlatformStats {
  tasks_total: number
  tasks_in_progress: number
  tasks_completed: number
  tasks_closed: number
  users_requester: number
  users_builder: number
  users_total: number
  demands_total: number
  tasks_recruiting: number
  pending_demands: number
  conversion_rate: number | null
  dau_today: number
  demands_7d: number
  tasks_7d: number
}

export interface MyStats {
  demand_count: number
  task_count: number
  converted_demands: number
  led_tasks: number
  pending_applications: number
}

export const statsApi = {
  getPlatformStats() {
    return api.get<PlatformStats>('/stats')
  },

  getMyStats() {
    return api.get<MyStats>('/me/stats')
  },
}
