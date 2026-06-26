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

const TASKS_STORAGE_KEY = 'openrd_mock_tasks'

const defaultTasks: MockTask[] = [
  {
    id: 'TASK-1042',
    demand_id: 'REQ-2418',
    title: '用药提醒小程序原型优化',
    description: '优化服药日历、提醒规则与家属同步流程。',
    task_type: '功能开发',
    priority: 'high',
    scope: '服药日历 UI 重构、提醒规则引擎、家属同步通知',
    acceptance_criteria: '日历展示正确，提醒按规则触发，家属端可同步查看',
    status: 'in_progress',
    team_status: 'collaborating',
    progress: 68,
    planned_end_time: '2026-07-15T00:00:00+08:00',
    owner_id: 'usr-003',
    leader_id: 'usr-002',
    resource_links: [
      { label: '代码仓库', url: 'https://github.com/OpenRDHub/med-reminder' },
      { label: '设计稿', url: 'https://figma.com/file/med-reminder' },
    ],
    file_ids: ['file-001', 'file-002'],
    created_at: '2026-05-21T10:00:00+08:00',
    updated_at: '2026-06-10T10:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'TASK-1051',
    demand_id: 'REQ-2421',
    title: '疾病知识库标签整理',
    description: '整理罕见病知识条目标签，提升搜索与推荐准确度。',
    task_type: '数据工程',
    priority: 'medium',
    scope: '标签体系设计、现有条目重标注、搜索权重调优',
    acceptance_criteria: '标签覆盖率 ≥90%，搜索准确率提升 15%',
    status: 'recruiting',
    team_status: 'forming',
    progress: 24,
    planned_end_time: '2026-08-01T00:00:00+08:00',
    owner_id: 'usr-003',
    leader_id: 'usr-002',
    resource_links: [
      { label: '标签规范文档', url: 'https://docs.openrd.org/tag-spec' },
    ],
    file_ids: [],
    created_at: '2026-05-19T09:00:00+08:00',
    updated_at: '2026-06-05T14:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'TASK-1024',
    demand_id: '',
    title: '患者随访表单无障碍改造',
    description: '改进移动端填写体验，增加大字号与语义提示。',
    task_type: '无障碍优化',
    priority: 'high',
    scope: '表单控件大字号适配、ARIA 标注、语义化错误提示',
    acceptance_criteria: 'WCAG 2.1 AA 合规，大字号模式可用',
    status: 'completed',
    team_status: 'accepted',
    progress: 100,
    planned_end_time: '2026-06-10T00:00:00+08:00',
    owner_id: 'usr-003',
    leader_id: 'usr-002',
    resource_links: [],
    file_ids: ['file-003'],
    created_at: '2026-05-16T08:00:00+08:00',
    updated_at: '2026-06-08T17:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'TASK-1017',
    demand_id: '',
    title: '多病种需求模板合并',
    description: '将重复需求模板归并，减少患者提交时的信息负担。',
    task_type: '产品优化',
    priority: 'low',
    scope: '模板梳理、合并策略、迁移脚本',
    acceptance_criteria: '模板数量减少 40%，患者提交时间缩短',
    status: 'closed',
    team_status: 'accepted',
    progress: 100,
    planned_end_time: '2026-05-30T00:00:00+08:00',
    owner_id: 'usr-003',
    leader_id: '',
    resource_links: [],
    file_ids: [],
    created_at: '2026-05-12T10:00:00+08:00',
    updated_at: '2026-05-28T11:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'TASK-1064',
    demand_id: 'REQ-2440',
    title: '复诊问题清单导出功能',
    description: '支持患者将症状、用药和提问导出为医生可读的 PDF。',
    task_type: '功能开发',
    priority: 'medium',
    scope: 'PDF 生成模板、数据聚合接口、导出按钮交互',
    acceptance_criteria: '支持导出包含症状、用药、提问的 PDF，格式清晰',
    status: 'recruiting',
    team_status: 'forming',
    progress: 18,
    planned_end_time: '2026-08-15T00:00:00+08:00',
    owner_id: 'usr-003',
    leader_id: '',
    resource_links: [],
    file_ids: [],
    created_at: '2026-05-27T14:00:00+08:00',
    updated_at: '2026-06-01T09:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'TASK-1068',
    demand_id: '',
    title: '病历摘要结构化字段设计',
    description: '为自然语言病历摘要建立字段字典和脱敏展示规则。',
    task_type: '数据工程',
    priority: 'high',
    scope: '字段字典定义、NLP 抽取规则、脱敏策略、展示组件',
    acceptance_criteria: '字段覆盖核心病历要素，脱敏规则通过安全审计',
    status: 'in_progress',
    team_status: 'collaborating',
    progress: 52,
    planned_end_time: '2026-07-20T00:00:00+08:00',
    owner_id: 'usr-003',
    leader_id: 'usr-002',
    resource_links: [
      { label: '字段字典', url: 'https://docs.openrd.org/medical-fields' },
      { label: '脱敏规范', url: 'https://docs.openrd.org/desensitization' },
    ],
    file_ids: ['file-004'],
    created_at: '2026-05-28T10:00:00+08:00',
    updated_at: '2026-06-15T16:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'TASK-1072',
    demand_id: '',
    title: '任务详情子任务原型',
    description: '补充父任务拆分、认领、验收和 Review 的子任务交互。',
    task_type: '功能开发',
    priority: 'medium',
    scope: '子任务 CRUD、认领流程、验收流程、Review 机制',
    acceptance_criteria: '支持子任务创建、认领、完成、Review 全流程',
    status: 'in_progress',
    team_status: 'collaborating',
    progress: 41,
    planned_end_time: '2026-07-30T00:00:00+08:00',
    owner_id: 'usr-003',
    leader_id: 'usr-002',
    resource_links: [
      { label: '原型稿', url: 'https://figma.com/file/subtask-proto' },
    ],
    file_ids: [],
    created_at: '2026-05-29T09:00:00+08:00',
    updated_at: '2026-06-12T11:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'TASK-1076',
    demand_id: '',
    title: '患者联系方式查看审计',
    description: '为产品经理和超级管理员查看联系方式增加审计记录。',
    task_type: '安全合规',
    priority: 'medium',
    scope: '审计日志表、查看行为拦截、后台审计面板',
    acceptance_criteria: '每次查看生成审计记录，后台可查询导出',
    status: 'recruiting',
    team_status: 'forming',
    progress: 16,
    planned_end_time: '2026-08-10T00:00:00+08:00',
    owner_id: 'usr-003',
    leader_id: '',
    resource_links: [],
    file_ids: [],
    created_at: '2026-05-30T11:00:00+08:00',
    updated_at: '2026-06-02T15:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'TASK-1081',
    demand_id: '',
    title: '附件上传限制提示优化',
    description: '在需求提交与沟通区明确附件数量、大小和错误提示。',
    task_type: '体验优化',
    priority: 'low',
    scope: '上传组件提示文案、校验逻辑、错误反馈 UI',
    acceptance_criteria: '超限时有明确提示，错误信息可定位原因',
    status: 'completed',
    team_status: 'accepted',
    progress: 100,
    planned_end_time: '2026-06-15T00:00:00+08:00',
    owner_id: 'usr-003',
    leader_id: 'usr-002',
    resource_links: [],
    file_ids: [],
    created_at: '2026-06-01T09:00:00+08:00',
    updated_at: '2026-06-14T18:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'TASK-1086',
    demand_id: '',
    title: '队伍成员贡献看板',
    description: '展示成员认领任务、提交记录、Review 通过率和协作状态。',
    task_type: '功能开发',
    priority: 'medium',
    scope: '贡献数据聚合、看板 UI、筛选与排序',
    acceptance_criteria: '展示认领/提交/Review 数据，支持按时间筛选',
    status: 'in_progress',
    team_status: 'collaborating',
    progress: 37,
    planned_end_time: '2026-08-01T00:00:00+08:00',
    owner_id: 'usr-003',
    leader_id: 'usr-002',
    resource_links: [
      { label: '看板原型', url: 'https://figma.com/file/contribution-board' },
    ],
    file_ids: [],
    created_at: '2026-06-03T10:00:00+08:00',
    updated_at: '2026-06-18T14:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'TASK-1038',
    demand_id: 'REQ-2380',
    title: '医学影像标注工具体验优化',
    description: '实现快捷键支持、批量保存和更清晰的标记反馈，提升标注效率。',
    task_type: '体验优化',
    priority: 'medium',
    scope: '快捷键映射、批量保存接口、标记反馈 UI',
    acceptance_criteria: '常用快捷键覆盖率 ≥80%，保存成功率 100%，标记反馈延迟 <200ms',
    status: 'in_progress',
    team_status: 'collaborating',
    progress: 42,
    planned_end_time: '2026-07-25T00:00:00+08:00',
    owner_id: 'usr-003',
    leader_id: 'usr-002',
    resource_links: [
      { label: '设计稿', url: 'https://figma.com/file/annotation-tool' },
    ],
    file_ids: [],
    created_at: '2026-05-17T10:00:00+08:00',
    updated_at: '2026-06-10T14:00:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
  {
    id: 'TASK-1055',
    demand_id: 'REQ-2489',
    title: '任务验收流程通知优化',
    description: '在验收环节增加即时站内通知，缩短开发者等待反馈的周期。',
    task_type: '功能开发',
    priority: 'high',
    scope: '站内通知模块、验收状态推送、通知中心 UI',
    acceptance_criteria: '验收操作后 5 秒内触发通知，通知中心可读可清除',
    status: 'in_progress',
    team_status: 'collaborating',
    progress: 55,
    planned_end_time: '2026-07-20T00:00:00+08:00',
    owner_id: 'usr-003',
    leader_id: 'usr-002',
    resource_links: [],
    file_ids: ['file-009'],
    created_at: '2026-06-09T09:00:00+08:00',
    updated_at: '2026-06-20T11:30:00+08:00',
    is_deleted: 0,
    deleted_at: '',
    deleted_by: '',
  },
]

function loadTasks(): MockTask[] {
  try {
    const raw = localStorage.getItem(TASKS_STORAGE_KEY)
    if (raw) return JSON.parse(raw) as MockTask[]
  } catch {}
  return defaultTasks.map((t) => ({ ...t }))
}

export function saveTasks() {
  try {
    localStorage.setItem(TASKS_STORAGE_KEY, JSON.stringify(tasks))
  } catch {}
}

export const tasks: MockTask[] = loadTasks()

export const taskMembers: MockTaskMember[] = [
  { id: 'tm-001', task_id: 'TASK-1042', user_id: 'usr-002', role: '前端开发', duty: '小程序页面重构', member_type: 'builder', status: 'active', joined_at: '2026-05-21T10:00:00+08:00' },
  { id: 'tm-002', task_id: 'TASK-1042', user_id: 'usr-003', role: '产品经理', duty: '需求跟进与验收', member_type: 'operator', status: 'active', joined_at: '2026-05-21T10:00:00+08:00' },
  { id: 'tm-003', task_id: 'TASK-1042', user_id: 'usr-004', role: '后端开发', duty: '提醒规则引擎', member_type: 'builder', status: 'active', joined_at: '2026-05-22T09:00:00+08:00' },
  { id: 'tm-004', task_id: 'TASK-1042', user_id: 'usr-005', role: 'UI 设计', duty: '日历组件视觉', member_type: 'builder', status: 'active', joined_at: '2026-05-23T14:00:00+08:00' },
  { id: 'tm-005', task_id: 'TASK-1051', user_id: 'usr-002', role: '数据工程师', duty: '标签体系设计', member_type: 'builder', status: 'active', joined_at: '2026-05-19T09:00:00+08:00' },
  { id: 'tm-006', task_id: 'TASK-1051', user_id: 'usr-003', role: '产品经理', duty: '标签规范审核', member_type: 'operator', status: 'active', joined_at: '2026-05-19T09:00:00+08:00' },
  { id: 'tm-007', task_id: 'TASK-1024', user_id: 'usr-002', role: '前端开发', duty: '无障碍改造', member_type: 'builder', status: 'active', joined_at: '2026-05-16T08:00:00+08:00' },
  { id: 'tm-008', task_id: 'TASK-1024', user_id: 'usr-004', role: '测试', duty: '无障碍测试', member_type: 'builder', status: 'active', joined_at: '2026-05-17T10:00:00+08:00' },
  { id: 'tm-009', task_id: 'TASK-1068', user_id: 'usr-002', role: '数据架构', duty: '字段字典与脱敏规则', member_type: 'builder', status: 'active', joined_at: '2026-05-28T10:00:00+08:00' },
  { id: 'tm-010', task_id: 'TASK-1068', user_id: 'usr-003', role: '产品经理', duty: '需求对接', member_type: 'operator', status: 'active', joined_at: '2026-05-28T10:00:00+08:00' },
  { id: 'tm-011', task_id: 'TASK-1072', user_id: 'usr-002', role: '全栈开发', duty: '子任务系统开发', member_type: 'builder', status: 'active', joined_at: '2026-05-29T09:00:00+08:00' },
  { id: 'tm-012', task_id: 'TASK-1072', user_id: 'usr-004', role: '前端开发', duty: '子任务 UI', member_type: 'builder', status: 'active', joined_at: '2026-05-30T10:00:00+08:00' },
  { id: 'tm-013', task_id: 'TASK-1081', user_id: 'usr-002', role: '前端开发', duty: '上传组件优化', member_type: 'builder', status: 'active', joined_at: '2026-06-01T09:00:00+08:00' },
  { id: 'tm-014', task_id: 'TASK-1086', user_id: 'usr-002', role: '全栈开发', duty: '贡献数据聚合', member_type: 'builder', status: 'active', joined_at: '2026-06-03T10:00:00+08:00' },
  { id: 'tm-015', task_id: 'TASK-1086', user_id: 'usr-003', role: '产品经理', duty: '看板需求定义', member_type: 'operator', status: 'active', joined_at: '2026-06-03T10:00:00+08:00' },
  { id: 'tm-016', task_id: 'TASK-1086', user_id: 'usr-004', role: '前端开发', duty: '看板 UI 开发', member_type: 'builder', status: 'active', joined_at: '2026-06-04T09:00:00+08:00' },
  { id: 'tm-017', task_id: 'TASK-1086', user_id: 'usr-005', role: 'UI 设计', duty: '看板视觉设计', member_type: 'builder', status: 'active', joined_at: '2026-06-04T14:00:00+08:00' },
  { id: 'tm-018', task_id: 'TASK-1038', user_id: 'usr-002', role: '前端开发', duty: '快捷键与标注 UI', member_type: 'builder', status: 'active', joined_at: '2026-05-17T10:00:00+08:00' },
  { id: 'tm-019', task_id: 'TASK-1038', user_id: 'usr-004', role: '后端开发', duty: '批量保存接口', member_type: 'builder', status: 'active', joined_at: '2026-05-18T09:00:00+08:00' },
  { id: 'tm-020', task_id: 'TASK-1055', user_id: 'usr-002', role: '全栈开发', duty: '通知模块开发', member_type: 'builder', status: 'active', joined_at: '2026-06-09T09:00:00+08:00' },
  { id: 'tm-021', task_id: 'TASK-1055', user_id: 'usr-004', role: '前端开发', duty: '通知中心 UI', member_type: 'builder', status: 'active', joined_at: '2026-06-10T10:00:00+08:00' },
]
