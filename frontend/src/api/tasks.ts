import { api } from './client'
import type { PaginatedData } from './client'

export interface Task {
  id: string
  demand_id: string
  title: string
  description: string
  task_type: string
  priority: string
  scope: string
  acceptance_criteria: string
  status: string
  team_status: string
  progress: number
  planned_end_time: string
  owner_id: string
  leader_id: string
  resource_links: { label: string; url: string }[]
  file_ids: string[]
  created_at: string
  updated_at: string
}

export interface TaskMember {
  id: string
  task_id: string
  user_id: string
  role: string
  duty: string
  member_type: string
  status: string
  joined_at: string
  name?: string
  platform?: string
  active?: string
}

export interface JoinApplication {
  id: string
  task_id: string
  user_id: string
  name: string
  platform: string
  role: string
  skills: string[]
  reason: string
  time: string
  status: string
}

export interface Assignment {
  id: string
  task_id: string
  title: string
  owner: string
  deliverable: string
  due: string
  status: 'done' | 'doing' | 'wait'
}

export interface TeamTimeline {
  id: string
  task_id: string
  title: string
  description: string
  date: string
  state: 'done' | 'doing' | 'wait'
}

export interface TeamDetail {
  members: TaskMember[]
  leader_id: string
  stage: string
}

export const tasksApi = {
  getList(params?: { status?: string; keyword?: string; page?: number; page_size?: number }) {
    return api.get<PaginatedData<Task>>('/tasks', params)
  },

  getDetail(taskId: string) {
    return api.get<Task>(`/tasks/${taskId}`)
  },

  update(taskId: string, data: Partial<Task>) {
    return api.patch<Task>(`/tasks/${taskId}`, data)
  },

  updateStatus(taskId: string, data: { status: string }) {
    return api.post(`/tasks/${taskId}/status`, data)
  },

  updateProgress(taskId: string, data: { progress: number; note?: string }) {
    return api.post(`/tasks/${taskId}/progress`, data)
  },

  updateResources(taskId: string, data: { resource_links: { label: string; url: string }[] }) {
    return api.post(`/tasks/${taskId}/resources`, data)
  },

  getTeam(taskId: string) {
    return api.get<TeamDetail>(`/tasks/${taskId}/team`)
  },

  getJoinApplications(taskId: string) {
    return api.get<{ applications: JoinApplication[] }>(`/tasks/${taskId}/join-applications`)
  },

  applyJoin(taskId: string, data: { role: string; message?: string }) {
    return api.post(`/tasks/${taskId}/join-applications`, data)
  },

  approveJoin(taskId: string, applicationId: string) {
    return api.post(`/tasks/${taskId}/join-applications/${applicationId}/approve`)
  },

  rejectJoin(taskId: string, applicationId: string, data?: { reason?: string }) {
    return api.post(`/tasks/${taskId}/join-applications/${applicationId}/reject`, data)
  },

  inviteMember(taskId: string, data: { user_id?: string; name?: string; role: string; platform?: string; due?: string; reason?: string }) {
    return api.post(`/tasks/${taskId}/members/invite`, data)
  },

  updateMemberDuty(taskId: string, memberId: string, data: { duty: string }) {
    return api.patch(`/tasks/${taskId}/members/${memberId}`, data)
  },

  transferLeader(taskId: string, data: { new_leader_id: string }) {
    return api.post(`/tasks/${taskId}/leader/transfer`, data)
  },

  getAssignments(taskId: string) {
    return api.get<{ assignments: Assignment[] }>(`/tasks/${taskId}/assignments`)
  },

  saveAssignments(taskId: string, data: { assignments: Assignment[] }) {
    return api.put(`/tasks/${taskId}/assignments`, data)
  },

  getTimeline(taskId: string) {
    return api.get<{ timeline: TeamTimeline[] }>(`/tasks/${taskId}/timeline`)
  },
}
