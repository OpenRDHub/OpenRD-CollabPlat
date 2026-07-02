import { api } from './client'

export interface PlatformStats {
  tasks_total: number
  tasks_in_progress: number
  tasks_completed: number
  tasks_closed: number
  users_requester: number
  users_builder: number
}

export interface MyStats {
  demand_count: number
  task_count: number
}

export const statsApi = {
  getPlatformStats() {
    return api.get<PlatformStats>('/stats')
  },

  getMyStats() {
    return api.get<MyStats>('/me/stats')
  },
}
