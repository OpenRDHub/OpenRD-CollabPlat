export interface MockDemand {
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
  is_deleted: number
  deleted_at: string
  deleted_by: string
}

export const demands: MockDemand[] = [
  {
    id: 'REQ-2418',
    title: '复诊问题清单与用药提醒',
    description: '希望记录复诊前问题，并支持每日用药提醒。',
    urgency: 'high',
    status: '已转任务',
    convert_status: '已转化',
    creator_id: 'usr-001',
    contact_phone: '15900000001',
    attachment_ids: [],
    linked_task_id: 'TASK-1042',
    linked_demand_id: '',
    progress: 68,
    feedback: '已拆分为用药提醒 API 与复诊清单原型两个方向。',
    created_at: '2026-05-24T09:00:00+08:00',
    updated_at: '2026-06-12T09:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'REQ-2432',
    title: '自然语言病历摘要辅助',
    description: '希望将较长病历内容整理为结构化摘要，方便科研分析。',
    urgency: 'medium',
    status: '沟通中',
    convert_status: '待评估',
    creator_id: 'usr-001',
    contact_phone: '15900000001',
    attachment_ids: ['file-001'],
    linked_task_id: '',
    linked_demand_id: '',
    progress: 36,
    feedback: '平台正在确认数据脱敏边界和可用样例。',
    created_at: '2026-05-25T14:00:00+08:00',
    updated_at: '2026-06-11T11:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'REQ-2440',
    title: '罕见病药物副作用记录模板',
    description: '希望记录用药后的不适反应、发生时间与严重程度。',
    urgency: 'high',
    status: '待审核',
    convert_status: '未转化',
    creator_id: 'usr-001',
    contact_phone: '15900000001',
    attachment_ids: [],
    linked_task_id: '',
    linked_demand_id: '',
    progress: 12,
    feedback: '需求已提交，等待运营管理员初审。',
    created_at: '2026-05-26T10:00:00+08:00',
    updated_at: '2026-05-26T10:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'REQ-2356',
    title: '复诊前问题整理小程序',
    description: '家属希望能在复诊前按分类整理问题并导出。',
    urgency: 'medium',
    status: '已关闭',
    convert_status: '已完成',
    creator_id: 'usr-001',
    contact_phone: '15900000001',
    attachment_ids: ['file-002', 'file-003', 'file-004'],
    linked_task_id: 'TASK-1024',
    linked_demand_id: '',
    progress: 100,
    feedback: '已完成原型验收，需求归档关闭。',
    created_at: '2026-05-08T10:00:00+08:00',
    updated_at: '2026-06-01T16:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'REQ-2380',
    title: '医学影像标注工具体验优化',
    description: '希望标注工具支持快捷键、批量保存和更清晰的标记反馈。',
    urgency: 'medium',
    status: '已转任务',
    convert_status: '开发中',
    creator_id: 'usr-001',
    contact_phone: '15900000001',
    attachment_ids: ['file-005', 'file-006', 'file-007', 'file-008'],
    linked_task_id: 'TASK-1038',
    linked_demand_id: '',
    progress: 42,
    feedback: '已转为 UI 与前端协作任务，正在推进界面优化。',
    created_at: '2026-05-16T08:00:00+08:00',
    updated_at: '2026-06-10T14:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
]
