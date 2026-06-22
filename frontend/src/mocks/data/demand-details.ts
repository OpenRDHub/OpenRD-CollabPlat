export interface DemandDetailThread {
  id: string
  pmName: string
  pmTitle: string
  status: string
  taskId: string
  summary: string
  scope: string
  messages: {
    from: 'pm' | 'requester' | 'system'
    name: string
    time: string
    text: string
    attachment?: string
    revoked?: boolean
  }[]
}

export interface DemandDetail {
  id: string
  title: string
  desc: string
  detail: string
  submittedAt: string
  status: string
  statusKey: 'pending' | 'talking' | 'converted' | 'closed'
  convertStatus: string
  taskId: string
  convertedBy: string
  progress: number
  contact: string
  privateContact: string
  attachments: string[]
  feedback: string
  timeline: [string, string, string, string][]
  demandMarkStatus: 'pending' | 'needs_supplement' | 'info_sufficient'
  lastMarkedBy: string
  threads: DemandDetailThread[]
}

export interface SimilarCandidate {
  id: string
  title: string
  taskId: string
  projectType: string
  owner: string
  keywords: string[]
  summary: string
  linkedDemandIds: string[]
}

export const demandDetails: Record<string, DemandDetail> = {
  'REQ-2418': {
    id: 'REQ-2418',
    title: '复诊问题清单与用药提醒',
    desc: '希望在复诊前整理问题，并在用药周期中得到提醒。',
    detail: '患者家属希望能够在复诊前按主题整理要问医生的问题，同时在用药期间收到温和提醒，避免遗漏服药和复查事项。',
    submittedAt: '2026-05-24',
    status: '沟通中',
    statusKey: 'talking',
    convertStatus: '待转化',
    taskId: '暂未生成',
    convertedBy: '',
    progress: 46,
    contact: '手机号 159****7824 / 微信已留存',
    privateContact: '手机号 15912347824 / 微信 chenbei_openrd',
    attachments: ['复诊问题草稿.docx', '用药周期截图.png'],
    feedback: '易然已确认提醒频率、关闭规则和复诊前问题清单范围，可作为演示直接转化为任务工单。',
    timeline: [
      ['提交需求', '需求发布者提交需求详情和附件。', '2026-05-24', 'done'],
      ['多方沟通', '易然与莫然分别确认提醒频率和复诊清单分组。', '2026-05-25', 'done'],
      ['转化评估', '易然认为需求边界已明确，可在产品视角转化任务。', '待转化', 'active'],
    ],
    demandMarkStatus: 'info_sufficient',
    lastMarkedBy: 'ops-yiran',
    threads: [
      {
        id: 'ops-yiran',
        pmName: '赵明',
        pmTitle: '产品经理 · 运管',
        status: '信息充分',
        taskId: 'TASK-1042',
        summary: '提醒频率、关闭规则和复诊前提醒已确认，可以转为任务。',
        scope: '用药提醒 API、复诊前问题清单和用户可关闭提醒的配置能力。',
        messages: [
          { from: 'pm', name: '赵明', time: '05-25 10:12', text: '我们已收到你的需求，请确认提醒频率是否需要按每日/每周分别设置。' },
          { from: 'requester', name: '陈北', time: '05-25 11:04', text: '每日提醒和复诊前一周提醒都需要，最好可以自己关闭。', attachment: '补充说明.md' },
          { from: 'pm', name: '赵明', time: '05-26 16:18', text: '这些信息已经足够，我可以把它转成任务工单，进入共建任务流程。' },
        ],
      },
      {
        id: 'ops-moran',
        pmName: '莫然',
        pmTitle: '产品经理 · 医疗内容',
        status: '信息充分',
        taskId: '',
        summary: '复诊问题清单的主题分组已确认，结论可合并进准备转化的任务。',
        scope: '复诊问题按症状、用药和检查结果分组，后续允许需求者自行新增问题。',
        messages: [
          { from: 'pm', name: '莫然', time: '05-25 15:20', text: '复诊问题清单是否需要按症状、用药、检查结果三个主题分组？' },
          { from: 'requester', name: '陈北', time: '05-25 17:40', text: '可以先按这三个主题分组，我也希望可以自己新增问题。' },
        ],
      },
    ],
  },
  'REQ-2432': {
    id: 'REQ-2432',
    title: '自然语言病历摘要辅助',
    desc: '希望将较长病历内容整理为结构化摘要，方便科研分析。',
    detail: '科研工作者希望将较长病历文本整理为结构化摘要，便于后续研究分析，但需要先确认数据脱敏边界和模型评估标准。',
    submittedAt: '2026-05-25',
    status: '沟通中',
    statusKey: 'talking',
    convertStatus: '待评估',
    taskId: '暂未生成',
    convertedBy: '',
    progress: 36,
    contact: '微信已留存',
    privateContact: '微信 chenbei_lab / 手机号 13822660931',
    attachments: ['病历摘要需求说明.pdf'],
    feedback: '平台正在确认数据脱敏边界和可用样例。',
    timeline: [
      ['提交需求', '需求发布者提交病历摘要需求。', '2026-05-25', 'done'],
      ['产品沟通', '两位产品经理分别确认脱敏样例和字段结构。', '2026-05-26', 'active'],
      ['转化评估', '任一产品经理确认可以承接后，可直接转化任务。', '待定', 'pending'],
    ],
    demandMarkStatus: 'needs_supplement',
    lastMarkedBy: 'ops-qinghe',
    threads: [
      {
        id: 'ops-yiran',
        pmName: '赵明',
        pmTitle: '产品经理 · 数据协作',
        status: '信息充分',
        taskId: 'TASK-1051',
        summary: '脱敏样例和摘要边界已基本确认，认为可以转为小型任务。',
        scope: '确认病历脱敏边界，输出摘要字段清单和两条脱敏样例的结构化结果。',
        messages: [
          { from: 'pm', name: '赵明', time: '05-26 09:30', text: '是否有可脱敏的样例文本？我们需要判断摘要字段和隐私边界。' },
          { from: 'requester', name: '陈北', time: '05-26 10:02', text: '可以提供 2 条脱敏样例，稍后补充附件。' },
          { from: 'pm', name: '赵明', time: '05-26 10:28', text: '如果能补充样例，我认为可以先转为一个小型任务，目标是确认脱敏边界和摘要字段。' },
        ],
      },
      {
        id: 'ops-qinghe',
        pmName: '青禾',
        pmTitle: '产品经理 · 科研场景',
        status: '待回复',
        taskId: 'TASK-1051',
        summary: '科研字段范围仍需确认，暂不建议由该会话直接转化。',
        scope: '诊断、用药、检查、随访四类字段的必要性确认。',
        messages: [
          { from: 'pm', name: '青禾', time: '05-26 14:25', text: '摘要结果是否需要区分诊断、用药、检查、随访四类字段？' },
          { from: 'system', name: '系统', time: '05-26 14:26', text: '等待需求发布者补充科研分析所需字段。' },
        ],
      },
    ],
  },
}
