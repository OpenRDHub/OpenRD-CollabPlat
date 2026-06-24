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
  // system
  { id: 'msg-001', category: 'system', title: '欢迎加入 OpenRD', summary: '您的账号已创建成功，快来探索平台吧', content: '欢迎加入 OpenRD 协作平台！您可以在大厅浏览公开需求、在工作台跟进任务进展，也可以提交您的稀罕病相关需求。祝您使用顺畅。', sender: '系统', target_type: '', target_id: '', action_text: '前往工作台', read_status: 1, created_at: '2026-05-10T08:00:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-009', category: 'system', title: '平台组件库 v1.0 正式上线', summary: '20 个生产就绪组件现已可用', content: 'OpenRD 平台 UI 组件库已完成首个版本搭建，包含按钮、表格、弹窗、标签等 20 个生产就绪组件，欢迎开发者在任务中使用。', sender: '系统', target_type: '', target_id: '', action_text: '', read_status: 0, created_at: '2026-06-12T20:00:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-011', category: 'system', title: '平台维护通知：6 月 20 日凌晨停服 2 小时', summary: '届时将进行数据库升级，请提前保存工作', content: '平台将于 2026-06-20 01:00～03:00 进行数据库升级维护，期间服务不可用。如有正在进行的任务提交，请提前保存草稿。感谢您的理解。', sender: '系统', target_type: '', target_id: '', action_text: '', read_status: 1, created_at: '2026-06-15T10:00:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-012', category: 'system', title: '您的账号已完成实名认证', summary: '身份信息审核通过，协作权限已开放', content: '您提交的实名认证信息已通过审核，协作权限正式开放。您现在可以申请加入任务团队或作为需求者提交正式需求。', sender: '系统', target_type: '', target_id: '', action_text: '查看个人资料', read_status: 0, created_at: '2026-06-18T14:22:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },

  // demand
  { id: 'msg-002', category: 'demand', title: '需求已收到，进入待审核', summary: '复诊问题清单与用药提醒 已进入待审核', content: '您提交的需求「复诊问题清单与用药提醒」已成功提交，正在等待产品经理审核，预计 1～3 个工作日内给出结果。', sender: '系统', target_type: 'demand', target_id: 'REQ-2418', action_text: '查看需求进展', read_status: 1, created_at: '2026-06-01T09:01:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-003', category: 'demand', title: '需求沟通新消息', summary: '赵明 回复了您的需求补充说明', content: '产品经理赵明对您的需求「罕见病药物信息数据库」发送了新消息：请补充目标用户群体和期望的数据更新频率，以便评估开发可行性。', sender: '赵明', target_type: 'demand', target_id: 'REQ-2419', action_text: '查看详情并回复', read_status: 0, created_at: '2026-06-05T11:00:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-004', category: 'demand', title: '需求已转化为协作任务', summary: '患者社区互助交流平台 已转化为 TASK-1042', content: '您的需求「患者社区互助交流平台」已通过审核并转化为任务 TASK-1042，现在可以在任务详情页查看开发进展和团队成员。', sender: '系统', target_type: 'task', target_id: 'TASK-1042', action_text: '查看任务详情', read_status: 1, created_at: '2026-05-25T16:01:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-010', category: 'demand', title: '需求驳回通知', summary: '在线心理咨询预约 已被驳回', content: '您的需求「在线心理咨询预约」已被驳回，原因：超出平台当前服务范围（平台专注稀罕病相关场景）。如您认为有误，可重新提交并补充场景说明。', sender: '赵明', target_type: 'demand', target_id: 'REQ-2422', action_text: '重新提交需求', read_status: 1, created_at: '2026-06-11T09:00:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-013', category: 'demand', title: '需求审核通过，等待资源匹配', summary: '罕见病患者用药记录工具 审核通过', content: '您的需求「罕见病患者用药记录工具」已通过产品审核，目前正在匹配合适的开发团队，预计 3～5 个工作日内开始协作任务创建。', sender: '系统', target_type: 'demand', target_id: 'REQ-2425', action_text: '查看需求状态', read_status: 0, created_at: '2026-06-20T09:30:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },

  // task
  { id: 'msg-005', category: 'task', title: '任务进度更新：45%', summary: 'TASK-1042 患者社区互助平台进度已更新', content: '任务「患者社区互助交流平台」由队长林子轩更新进度至 45%，当前阶段：前端组件开发。您可以在任务详情页查看最新分工和待办事项。', sender: '林子轩', target_type: 'task', target_id: 'TASK-1042', action_text: '查看任务详情', read_status: 0, created_at: '2026-06-10T10:00:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-007', category: 'task', title: '任务提交验收，请确认', summary: 'TASK-1044 平台用户反馈系统 已提交验收', content: '任务「平台用户反馈系统」已由开发团队提交验收申请，请您在 48 小时内确认验收结果。如有问题请在任务详情页的验收反馈区填写说明。', sender: '林子轩', target_type: 'task', target_id: 'TASK-1044', action_text: '前往验收确认', read_status: 0, created_at: '2026-06-12T17:00:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-014', category: 'task', title: '您被指派为任务队长', summary: 'TASK-1051 自然语言病历摘要任务', content: '运营人员已将您指派为任务「自然语言病历摘要」（TASK-1051）的队长。请前往任务详情页完善分工说明，并审核已提交的加入申请。', sender: '系统', target_type: 'task', target_id: 'TASK-1051', action_text: '前往任务管理', read_status: 0, created_at: '2026-06-19T11:15:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-015', category: 'task', title: '任务截止日期提醒', summary: 'TASK-1042 距截止还有 3 天', content: '您参与的任务「患者社区互助交流平台」（TASK-1042）距截止日期仅剩 3 天，请注意推进当前分工进度。如需延期请提前联系队长。', sender: '系统', target_type: 'task', target_id: 'TASK-1042', action_text: '查看我的分工', read_status: 1, created_at: '2026-06-21T09:00:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-016', category: 'task', title: '任务验收通过，已归档', summary: 'TASK-1038 复诊问题清单小程序 验收通过', content: '您参与的任务「复诊问题清单小程序」（TASK-1038）已由需求者确认验收，任务进入归档状态。感谢您的贡献，相关积分已发放至您的账户。', sender: '系统', target_type: 'task', target_id: 'TASK-1038', action_text: '查看验收记录', read_status: 1, created_at: '2026-06-14T15:08:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },

  // team
  { id: 'msg-006', category: 'team', title: '新成员加入申请待审核', summary: '王芳 申请加入 TASK-1042 团队', content: '用户「王芳」申请加入任务「患者社区互助交流平台」（TASK-1042）的协作团队，申请方向：前端开发。请前往任务管理页面完成审核。', sender: '系统', target_type: 'task', target_id: 'TASK-1042', action_text: '审核加入申请', read_status: 0, created_at: '2026-06-11T08:30:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-017', category: 'team', title: '您的加入申请已通过', summary: 'TASK-1051 自然语言病历摘要团队已接受您', content: '您申请加入的任务「自然语言病历摘要」（TASK-1051）团队已通过您的申请，分配方向：数据处理。请前往任务详情查看分工安排。', sender: '系统', target_type: 'task', target_id: 'TASK-1051', action_text: '查看我的分工', read_status: 0, created_at: '2026-06-17T14:20:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-018', category: 'team', title: '成员申请已批量待审核', summary: 'TASK-1051 收到 3 条新申请', content: '您负责的任务「自然语言病历摘要」（TASK-1051）在过去 24 小时内收到 3 条新的成员加入申请，请尽快完成审核，避免申请方长时间等待。', sender: '系统', target_type: 'task', target_id: 'TASK-1051', action_text: '批量审核申请', read_status: 1, created_at: '2026-06-22T08:00:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-019', category: 'team', title: '加入申请被拒绝', summary: 'TASK-1039 的申请未通过', content: '您申请加入任务「罕见病基因数据可视化」（TASK-1039）的请求未被通过，队长备注原因：当前岗位已满。您可以继续浏览大厅中的其他开放任务。', sender: '系统', target_type: 'task', target_id: 'TASK-1039', action_text: '浏览其他任务', read_status: 1, created_at: '2026-06-13T16:45:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },

  // reply
  { id: 'msg-008', category: 'reply', title: '陈北回复了沟通消息', summary: '关于罕见病药物数据库的补充说明', content: '需求者陈北对需求「罕见病药物信息数据库」（REQ-2419）的沟通进行了回复：我们期望数据能覆盖至少 500 种罕见病用药，支持中英文双语检索，更新频率为每季度一次。', sender: '陈北', target_type: 'demand', target_id: 'REQ-2419', action_text: '继续沟通', read_status: 0, created_at: '2026-06-06T09:15:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-020', category: 'reply', title: '易然回复了您的问题', summary: '关于任务分工调整的回复', content: '产品经理易然回复了您在 TASK-1042 中提出的分工调整请求：同意将您的工作范围从"消息推送模块"调整为"用户资料模块"，请在本周内与新模块负责人对接交接事宜。', sender: '易然', target_type: 'task', target_id: 'TASK-1042', action_text: '查看任务分工', read_status: 0, created_at: '2026-06-16T10:30:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-021', category: 'reply', title: '顾星河回复了您的反馈', summary: '关于平台功能建议的官方回复', content: '平台负责人顾星河回复了您提交的功能建议「希望支持任务进度看板视图」：感谢您的建议，已纳入 Q3 功能规划，预计在 8 月版本迭代中上线。', sender: '顾星河', target_type: '', target_id: '', action_text: '', read_status: 1, created_at: '2026-06-09T15:00:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
  { id: 'msg-022', category: 'reply', title: '林子轩 @ 了您', summary: '在 TASK-1042 任务讨论中提到了您', content: '队长林子轩在任务「患者社区互助交流平台」讨论中 @ 了您：请确认一下消息通知模块的接口联调计划，当前前端已基本就绪，等待后端确认时间窗口。', sender: '林子轩', target_type: 'task', target_id: 'TASK-1042', action_text: '查看任务讨论', read_status: 0, created_at: '2026-06-23T11:05:00+08:00', is_deleted: 0, deleted_at: '', deleted_by: '' },
]
