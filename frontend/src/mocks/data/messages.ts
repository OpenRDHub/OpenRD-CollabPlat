export interface MockMessage {
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
  is_deleted: number
  deleted_at: string
  deleted_by: string
}

export const messages: MockMessage[] = [
  { id: 'msg-001', category: 'system', title: '欢迎加入 OpenRD', summary: '您的账号已创建成功', content: '欢迎加入 OpenRD 协作平台，您可以开始提交需求或浏览任务。', sender: '系统', target_type: '', target_id: '', action_text: '查看工作台', read_status: 1, created_at: '2026-05-10T08:00:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-002', category: 'demand', title: '您的需求已收到', summary: '复诊问题清单与用药提醒 已进入待审核', content: '您提交的需求「复诊问题清单与用药提醒」已成功提交，正在等待产品经理审核。', sender: '系统', target_type: 'demand', target_id: 'REQ-2418', action_text: '查看需求', read_status: 1, created_at: '2026-06-01T09:01:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-003', category: 'demand', title: '需求沟通更新', summary: '赵明 回复了您的需求', content: '产品经理赵明对您的需求「罕见病药物信息数据库」发送了新消息。', sender: '赵明', target_type: 'demand', target_id: 'REQ-2419', action_text: '查看详情', read_status: 0, created_at: '2026-06-05T11:00:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-004', category: 'demand', title: '需求已转化为任务', summary: '患者社区互助交流平台 已转化', content: '您的需求「患者社区互助交流平台」已转化为任务 TASK-1042。', sender: '系统', target_type: 'task', target_id: 'TASK-1042', action_text: '查看任务', read_status: 1, created_at: '2026-05-25T16:01:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-005', category: 'task', title: '任务进度更新', summary: 'TASK-1042 进度已更新至 45%', content: '任务「患者社区互助交流平台」进度已更新至 45%。', sender: '林子轩', target_type: 'task', target_id: 'TASK-1042', action_text: '查看任务', read_status: 0, created_at: '2026-06-10T10:00:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-006', category: 'team', title: '新成员加入申请', summary: '有人申请加入 TASK-1042', content: '用户「王芳」申请加入任务「患者社区互助交流平台」的协作团队。', sender: '系统', target_type: 'task', target_id: 'TASK-1042', action_text: '审核申请', read_status: 0, created_at: '2026-06-11T08:30:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-007', category: 'task', title: '任务待验收', summary: 'TASK-1044 已提交验收', content: '任务「平台用户反馈系统」已提交验收，请及时确认。', sender: '林子轩', target_type: 'task', target_id: 'TASK-1044', action_text: '查看任务', read_status: 0, created_at: '2026-06-12T17:00:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-008', category: 'reply', title: '回复通知', summary: '陈北 回复了沟通消息', content: '需求者陈北对需求「罕见病药物信息数据库」的沟通进行了回复。', sender: '陈北', target_type: 'demand', target_id: 'REQ-2419', action_text: '查看详情', read_status: 0, created_at: '2026-06-06T09:15:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-009', category: 'system', title: '平台更新通知', summary: '组件库 v1.0 已上线', content: 'OpenRD 平台组件库已完成首个版本搭建，包含 20 个生产就绪组件。', sender: '系统', target_type: '', target_id: '', action_text: '', read_status: 0, created_at: '2026-06-12T20:00:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-010', category: 'demand', title: '需求已驳回', summary: '在线心理咨询预约 已驳回', content: '您的需求「在线心理咨询预约」已被驳回，原因：超出平台当前服务范围。', sender: '赵明', target_type: 'demand', target_id: 'REQ-2422', action_text: '查看详情', read_status: 1, created_at: '2026-06-11T09:00:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
]
