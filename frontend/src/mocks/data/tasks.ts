export interface MockTask {
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
  is_deleted: number
  deleted_at: string
  deleted_by: string
}

export interface MockTaskMember {
  id: string
  task_id: string
  user_id: string
  role: string
  duty: string
  member_type: string
  status: string
  joined_at: string
}

export const tasks: MockTask[] = [
  {
    id: 'TASK-1042',
    demand_id: 'REQ-2420',
    title: '患者社区互助交流平台',
    description: '搭建病友社区，支持经验分享、话题讨论和情感互助。',
    task_type: '功能开发',
    priority: 'high',
    scope: '含前端社区页面、后端话题/帖子/评论 API、消息通知',
    acceptance_criteria: '支持发帖、评论、点赞、话题分类，消息通知正常',
    status: 'in_progress',
    team_status: 'collaborating',
    progress: 45,
    planned_end_time: '2026-07-15T00:00:00+08:00',
    owner_id: 'usr-003',
    leader_id: 'usr-002',
    resource_links: [
      { label: '代码仓库', url: 'https://github.com/OpenRDHub/community' },
      { label: '设计稿', url: 'https://figma.com/file/xxx' },
    ],
    file_ids: [],
    created_at: '2026-05-25T16:00:00+08:00',
    updated_at: '2026-06-10T10:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'TASK-1043',
    demand_id: 'REQ-2421',
    title: '罕见病知识图谱构建',
    description: '构建罕见病药物-基因-症状关联知识图谱。',
    task_type: '数据工程',
    priority: 'medium',
    scope: '数据采集、清洗、图谱构建、查询接口',
    acceptance_criteria: '覆盖 100+ 罕见病条目，支持关联查询',
    status: 'recruiting',
    team_status: 'forming',
    progress: 0,
    planned_end_time: '2026-08-30T00:00:00+08:00',
    owner_id: 'usr-003',
    leader_id: '',
    resource_links: [],
    file_ids: ['file-003'],
    created_at: '2026-06-09T14:00:00+08:00',
    updated_at: '2026-06-09T14:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'TASK-1044',
    demand_id: '',
    title: '平台用户反馈系统',
    description: '建立用户使用反馈收集与处理闭环。',
    task_type: '功能开发',
    priority: 'low',
    scope: '反馈提交表单、管理后台、统计面板',
    acceptance_criteria: '支持提交、分类、回复、统计',
    status: 'pending_acceptance',
    team_status: 'accepted',
    progress: 95,
    planned_end_time: '2026-06-20T00:00:00+08:00',
    owner_id: 'usr-003',
    leader_id: 'usr-002',
    resource_links: [
      { label: '测试环境', url: 'https://staging.openrd.org/feedback' },
    ],
    file_ids: [],
    created_at: '2026-04-15T09:00:00+08:00',
    updated_at: '2026-06-12T17:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'TASK-1045',
    demand_id: '',
    title: '无障碍辅助阅读模式',
    description: '为视障用户提供高对比度和屏幕朗读优化。',
    task_type: '无障碍优化',
    priority: 'medium',
    scope: '全站无障碍改造、ARIA 标注、键盘导航',
    acceptance_criteria: 'WCAG 2.1 AA 等级合规',
    status: 'completed',
    team_status: 'accepted',
    progress: 100,
    planned_end_time: '2026-05-30T00:00:00+08:00',
    owner_id: 'usr-003',
    leader_id: 'usr-002',
    resource_links: [],
    file_ids: [],
    created_at: '2026-03-20T10:00:00+08:00',
    updated_at: '2026-05-28T15:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
]

export const taskMembers: MockTaskMember[] = [
  { id: 'tm-001', task_id: 'TASK-1042', user_id: 'usr-002', role: '前端开发', duty: '社区页面开发', member_type: 'leader', status: 'active', joined_at: '2026-05-26T09:00:00+08:00' },
  { id: 'tm-002', task_id: 'TASK-1042', user_id: 'usr-003', role: '产品经理', duty: '需求跟进与验收', member_type: 'operator', status: 'active', joined_at: '2026-05-25T16:00:00+08:00' },
  { id: 'tm-003', task_id: 'TASK-1044', user_id: 'usr-002', role: '全栈开发', duty: '反馈系统开发', member_type: 'leader', status: 'active', joined_at: '2026-04-16T10:00:00+08:00' },
]
