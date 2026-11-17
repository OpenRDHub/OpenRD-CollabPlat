import type { LinkedProject } from '@/api/demands'

export const taskStatusLabels: Record<string, string> = {
  recruiting: '招募中',
  team_ready: '待处理',
  in_progress: '解决中',
  pending_acceptance: '待验收',
  completed: '已完成',
  closed: '已关闭',
}

export const teamStatusLabels: Record<string, string> = {
  forming: '招募中',
  collaborating: '协作中',
  accepted: '已验收',
  ended: '已结束',
}

export function taskStageLabel(stage?: string | null) {
  const labels: Record<string, string> = {
    team: '组队', develop: '开发', beta: '内测', opensource: '开源',
  }
  return labels[stage || ''] || stage || '阶段未设置'
}

export function projectAvailabilityLabel(project?: LinkedProject) {
  switch (project?.availability) {
    case 'available': return taskStageLabel(project.stage)
    case 'deleted': return '关联任务已删除'
    case 'missing': return '关联项目不可用'
    default: return '暂未关联项目'
  }
}
