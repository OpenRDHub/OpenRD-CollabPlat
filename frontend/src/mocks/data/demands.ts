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
    status: 'pending_review',
    convert_status: '',
    creator_id: 'usr-001',
    contact_phone: '15900000001',
    attachment_ids: [],
    linked_task_id: '',
    linked_demand_id: '',
    progress: 0,
    feedback: '',
    created_at: '2026-06-01T09:00:00+08:00',
    updated_at: '2026-06-01T09:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'REQ-2419',
    title: '罕见病药物信息数据库',
    description: '需要一个能检索罕见病对症药物、适应症和副作用的数据库工具。',
    urgency: 'medium',
    status: 'communicating',
    convert_status: '',
    creator_id: 'usr-001',
    contact_phone: '15900000001',
    attachment_ids: ['file-001'],
    linked_task_id: '',
    linked_demand_id: '',
    progress: 30,
    feedback: '已与需求者确认核心功能范围',
    created_at: '2026-05-20T14:00:00+08:00',
    updated_at: '2026-06-05T11:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'REQ-2420',
    title: '患者社区互助交流平台',
    description: '建立病友之间的经验分享和情感支持社区。',
    urgency: 'medium',
    status: 'converted',
    convert_status: 'converted',
    creator_id: 'usr-001',
    contact_phone: '15900000001',
    attachment_ids: [],
    linked_task_id: 'TASK-1042',
    linked_demand_id: '',
    progress: 100,
    feedback: '已转化为任务 TASK-1042',
    created_at: '2026-05-10T10:00:00+08:00',
    updated_at: '2026-05-25T16:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'REQ-2421',
    title: '基因检测报告解读辅助',
    description: '希望有工具能帮助患者理解基因检测报告中的关键指标。',
    urgency: 'low',
    status: 'linked',
    convert_status: 'linked',
    creator_id: 'usr-001',
    contact_phone: '15900000001',
    attachment_ids: ['file-002'],
    linked_task_id: 'TASK-1043',
    linked_demand_id: 'REQ-2420',
    progress: 100,
    feedback: '已关联到相似需求 REQ-2420',
    created_at: '2026-06-08T08:30:00+08:00',
    updated_at: '2026-06-09T14:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'REQ-2422',
    title: '在线心理咨询预约',
    description: '为罕见病患者及家属提供心理咨询预约服务。',
    urgency: 'low',
    status: 'rejected',
    convert_status: '',
    creator_id: 'usr-001',
    contact_phone: '15900000001',
    attachment_ids: [],
    linked_task_id: '',
    linked_demand_id: '',
    progress: 0,
    feedback: '该需求超出平台当前服务范围，建议联系专业心理咨询机构',
    created_at: '2026-06-10T16:00:00+08:00',
    updated_at: '2026-06-11T09:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
]
