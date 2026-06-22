import { demandDetails } from './demand-details'
import type { SimilarCandidate } from './demand-details'

export { demandDetails }
export type { SimilarCandidate }

export const similarCandidates: SimilarCandidate[] = [
  {
    id: 'REQ-2356',
    title: '复诊问题清单小程序原型',
    taskId: 'TASK-1024',
    projectType: '工具开发项目',
    owner: '易然',
    keywords: ['复诊', '问题清单', '提醒', '用药'],
    summary: '已转化为复诊问题清单原型任务，可承接相似复诊整理和提醒需求。',
    linkedDemandIds: ['REQ-2399'],
  },
  {
    id: 'REQ-2291',
    title: '患者随访数据分析看板',
    taskId: 'TASK-1017',
    projectType: '数据分析项目',
    owner: '周桐',
    keywords: ['随访', '数据', '看板', '趋势'],
    summary: '已转化为随访数据看板任务，适合关联相似数据统计与趋势观察需求。',
    linkedDemandIds: [],
  },
  {
    id: 'REQ-2380',
    title: '医学影像标注工具界面优化',
    taskId: 'TASK-1038',
    projectType: '科研辅助项目',
    owner: '莫然',
    keywords: ['影像', '标注', '科研', '工具'],
    summary: '已转化为医学影像标注工具任务，可承接相似科研辅助工具需求。',
    linkedDemandIds: [],
  },
]
