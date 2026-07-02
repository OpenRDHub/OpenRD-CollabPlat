export const demandStatusDict: Record<string, string> = {
  pending: '待审核',
  pending_review: '待审核',
  reviewing: '审核中',
  approved: '已通过',
  converted: '已转任务',
  rejected: '已驳回',
  archived: '已归档',
  talking: '沟通中',
  linked: '已关联',
  closed: '已关闭',
}

export const convertStatusDict: Record<string, string> = {
  '': '未转化',
  converted: '已转化',
  linked: '已关联',
}

export const urgencyDict: Record<string, string> = {
  low: '低',
  medium: '中',
  high: '高',
}

export const roleDict: Record<string, string> = {
  requester: '需求者',
  builder: '共建者',
  operator: '运营管理员',
  super_admin: '超级管理员',
}

export const demandStageDict: Record<string, string> = {
  pending: '待审核',
  talking: '沟通中',
  converted: '已转任务',
  closed: '已关闭',
}

export function dict(map: Record<string, string>, key: string | undefined | null): string {
  if (!key) return map[''] || '-'
  return map[key] || key
}
