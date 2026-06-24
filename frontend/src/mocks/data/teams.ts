export interface MockJoinApplication {
  id: string
  task_id: string
  user_id: string
  name: string
  platform: string
  role: string
  skills: string[]
  reason: string
  time: string
  status: 'pending' | 'approved' | 'rejected'
}

export interface MockAssignment {
  id: string
  task_id: string
  title: string
  owner: string
  deliverable: string
  due: string
  status: 'done' | 'doing' | 'wait'
}

export interface MockTeamTimeline {
  id: string
  task_id: string
  title: string
  description: string
  date: string
  state: 'done' | 'doing' | 'wait'
}

export const joinApplications: MockJoinApplication[] = [
  {
    id: 'app-001',
    task_id: 'TASK-1051',
    user_id: '',
    name: '周南',
    platform: 'nlp_zhou',
    role: '算法工程师',
    skills: ['自然语言处理', '数据脱敏'],
    reason: '有医疗文本摘要经验，希望负责模型评估。',
    time: '2026-05-26 11:18',
    status: 'pending',
  },
  {
    id: 'app-002',
    task_id: 'TASK-1051',
    user_id: '',
    name: '许见',
    platform: 'ux_xujian',
    role: 'UI/UX 设计师',
    skills: ['原型设计', '可视化'],
    reason: '可以协助设计摘要结果预览界面。',
    time: '2026-05-26 14:42',
    status: 'pending',
  },
  {
    id: 'app-003',
    task_id: 'TASK-1051',
    user_id: '',
    name: '梁栀',
    platform: 'data_liangzhi',
    role: '数据标注志愿者',
    skills: ['医学术语', '样例标注'],
    reason: '熟悉病历字段整理，可以协助校对脱敏样例。',
    time: '2026-05-26 16:05',
    status: 'pending',
  },
  {
    id: 'app-004',
    task_id: 'TASK-1051',
    user_id: '',
    name: '韩立',
    platform: 'doc_hanli',
    role: '文档协作',
    skills: ['需求整理', '验收文档'],
    reason: '希望负责摘要字段说明和验收记录整理。',
    time: '2026-05-27 09:22',
    status: 'pending',
  },
  {
    id: 'app-005',
    task_id: 'TASK-1051',
    user_id: '',
    name: '沈越',
    platform: 'backend_shenyue',
    role: '后端开发',
    skills: ['API 设计', '数据结构'],
    reason: '可以补充摘要结果保存接口和任务数据结构。',
    time: '2026-05-27 10:36',
    status: 'pending',
  },
  {
    id: 'app-006',
    task_id: 'TASK-1042',
    user_id: '',
    name: '顾晓',
    platform: 'qa_guxiao',
    role: '测试工程师',
    skills: ['接口测试', '边界用例'],
    reason: '可以补充提醒频率、关闭规则和异常消息队列的测试用例。',
    time: '2026-05-27 10:14',
    status: 'pending',
  },
  {
    id: 'app-007',
    task_id: 'TASK-1042',
    user_id: '',
    name: '陆弈',
    platform: 'backend_luyi',
    role: '后端开发',
    skills: ['消息队列', '定时任务'],
    reason: '有提醒服务和异步队列经验，希望协助处理重试策略。',
    time: '2026-05-27 13:26',
    status: 'pending',
  },
  {
    id: 'app-008',
    task_id: 'TASK-1042',
    user_id: '',
    name: '苏棠',
    platform: 'writer_sutang',
    role: '医学内容协作',
    skills: ['用药说明', '用户文案'],
    reason: '可以协助梳理提醒文案，避免给患者造成压力。',
    time: '2026-05-27 15:48',
    status: 'pending',
  },
]

export const assignments: MockAssignment[] = [
  {
    id: 'asgn-001',
    task_id: 'TASK-1051',
    title: '加入申请审核',
    owner: '林子轩',
    deliverable: '确认成员与职责',
    due: '2026-05-27',
    status: 'doing',
  },
  {
    id: 'asgn-002',
    task_id: 'TASK-1051',
    title: '标签体系设计',
    owner: '林子轩',
    deliverable: '标签字段清单',
    due: '2026-05-29',
    status: 'wait',
  },
  {
    id: 'asgn-003',
    task_id: 'TASK-1051',
    title: '搜索权重调优方案',
    owner: '待分配',
    deliverable: '搜索评估标准',
    due: '2026-06-02',
    status: 'wait',
  },
  {
    id: 'asgn-004',
    task_id: 'TASK-1042',
    title: '接口联调说明',
    owner: '林子轩',
    deliverable: '字段与错误码文档',
    due: '2026-05-27',
    status: 'doing',
  },
  {
    id: 'asgn-005',
    task_id: 'TASK-1042',
    title: '提醒配置界面',
    owner: '赵明',
    deliverable: '交互稿与组件说明',
    due: '2026-05-30',
    status: 'doing',
  },
  {
    id: 'asgn-006',
    task_id: 'TASK-1042',
    title: '需求者验收',
    owner: '陈北',
    deliverable: '验收反馈记录',
    due: '2026-06-03',
    status: 'wait',
  },
]

export const teamTimelines: MockTeamTimeline[] = [
  {
    id: 'tl-001',
    task_id: 'TASK-1051',
    title: '任务创建完成',
    description: '已拆分为标签体系设计、条目重标注、搜索权重调优三个阶段。',
    date: '2026-05-19',
    state: 'done',
  },
  {
    id: 'tl-002',
    task_id: 'TASK-1051',
    title: '收到加入申请',
    description: '5 位成员提交加入申请，等待队长审核。',
    date: '2026-05-26',
    state: 'doing',
  },
  {
    id: 'tl-003',
    task_id: 'TASK-1051',
    title: '标签体系评审排期',
    description: '计划确认标签分类边界与样例要求。',
    date: '2026-05-29',
    state: 'wait',
  },
  {
    id: 'tl-004',
    task_id: 'TASK-1042',
    title: '队伍招募完成',
    description: '后端、设计、运营协调角色已确认。',
    date: '2026-05-22',
    state: 'done',
  },
  {
    id: 'tl-005',
    task_id: 'TASK-1042',
    title: '进入接口联调',
    description: '后端开始补充联调说明。',
    date: '2026-05-26',
    state: 'doing',
  },
  {
    id: 'tl-006',
    task_id: 'TASK-1042',
    title: '收到补充申请',
    description: '3 位成员申请加入测试、后端队列和医学文案协作。',
    date: '2026-05-27',
    state: 'doing',
  },
  {
    id: 'tl-007',
    task_id: 'TASK-1042',
    title: '准备验收',
    description: '完成联调后进入需求者验收。',
    date: '2026-06-03',
    state: 'wait',
  },
]
