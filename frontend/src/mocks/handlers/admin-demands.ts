import { http, HttpResponse } from 'msw'
import type { AdminDemand, DemandStats } from '@/api/admin-demands'

const mockDemands: AdminDemand[] = [
  {
    id: 'REQ-2418',
    title: '复诊问题清单与用药提醒',
    description: '希望在复诊前自动整理问题，并按服药时间提醒家属。',
    submitted_at: '2026-05-20',
    review_status: '已转任务',
    convert_status: '已转化',
    publisher: '陈北',
    publisher_id: 'usr-001',
    task_id: 'TASK-1042',
    progress: 68,
    feedback: '需求已拆分为提醒链路与复诊清单两个任务模块。',
    urgency: 'high',
    contact_phone: '138****1234',
    created_at: '2026-05-20T10:30:00Z',
    updated_at: '2026-06-01T14:20:00Z',
  },
  {
    id: 'REQ-2432',
    title: '自然语言病历摘要辅助',
    description: '帮助科研志愿者快速理解病历材料，降低前期整理压力。',
    submitted_at: '2026-05-24',
    review_status: '沟通中',
    convert_status: '待评估',
    publisher: '科研工作者',
    publisher_id: 'usr-002',
    task_id: null,
    progress: 36,
    feedback: '需要进一步确认脱敏范围与摘要字段。',
    urgency: 'medium',
    contact_phone: '139****5678',
    created_at: '2026-05-24T09:15:00Z',
    updated_at: '2026-05-30T11:45:00Z',
  },
  {
    id: 'REQ-2440',
    title: '罕见病药物副作用记录模板',
    description: '想要结构化记录用药后的不适反应，便于就诊时回溯。',
    submitted_at: '2026-05-25',
    review_status: '待审核',
    convert_status: '未转化',
    publisher: '明明家属',
    publisher_id: 'usr-003',
    task_id: null,
    progress: 12,
    feedback: '待运营确认是否已有相似需求。',
    urgency: 'medium',
    contact_phone: '137****9012',
    created_at: '2026-05-25T16:20:00Z',
    updated_at: '2026-05-25T16:20:00Z',
  },
  {
    id: 'REQ-2356',
    title: '复诊前问题整理小程序',
    description: '将家属零散记录整理为医生可快速查看的问题清单。',
    submitted_at: '2026-05-08',
    review_status: '已关闭',
    convert_status: '已完成',
    publisher: '明明家属',
    publisher_id: 'usr-003',
    task_id: 'TASK-1024',
    progress: 100,
    feedback: '已完成原型交付，需求归档。',
    urgency: 'high',
    contact_phone: '137****9012',
    created_at: '2026-05-08T14:30:00Z',
    updated_at: '2026-06-10T10:00:00Z',
  },
  {
    id: 'REQ-2380',
    title: '医学影像标注工具体验优化',
    description: '标注志愿者希望提升快捷键提示和影像区域操作效率。',
    submitted_at: '2026-05-16',
    review_status: '已转任务',
    convert_status: '开发中',
    publisher: '诺一',
    publisher_id: 'usr-004',
    task_id: 'TASK-1038',
    progress: 42,
    feedback: '已转任务，当前由 UI 与前端协同推进。',
    urgency: 'medium',
    contact_phone: '136****3456',
    created_at: '2026-05-16T11:00:00Z',
    updated_at: '2026-06-05T09:30:00Z',
  },
]

export const adminDemandsHandlers = [
  // 获取需求列表
  http.get('/api/admin/demands', ({ request }) => {
    const url = new URL(request.url)
    const keyword = url.searchParams.get('keyword') || ''
    const reviewStatus = url.searchParams.get('review_status')
    const convertStatus = url.searchParams.get('convert_status')

    let filtered = [...mockDemands]

    if (keyword) {
      const lowerKeyword = keyword.toLowerCase()
      filtered = filtered.filter(
        (d) =>
          d.id.toLowerCase().includes(lowerKeyword) ||
          d.title.toLowerCase().includes(lowerKeyword) ||
          d.publisher.toLowerCase().includes(lowerKeyword) ||
          d.task_id?.toLowerCase().includes(lowerKeyword)
      )
    }

    if (reviewStatus && reviewStatus !== '全部') {
      filtered = filtered.filter((d) => d.review_status === reviewStatus)
    }

    if (convertStatus && convertStatus !== '全部') {
      filtered = filtered.filter((d) => d.convert_status === convertStatus)
    }

    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: {
        items: filtered,
        total: filtered.length,
        page: 1,
        page_size: 1000,
      },
    })
  }),

  // 获取统计数据
  http.get('/api/admin/demands/stats', () => {
    const stats: DemandStats = {
      total: mockDemands.length,
      pending: mockDemands.filter((d) => d.review_status === '待审核').length,
      talking: mockDemands.filter((d) => d.review_status === '沟通中').length,
      converted: mockDemands.filter((d) => d.review_status === '已转任务').length,
      closed: mockDemands.filter((d) => d.review_status === '已关闭').length,
    }

    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: stats,
    })
  }),

  // 获取单个需求详情
  http.get('/api/admin/demands/:id', ({ params }) => {
    const { id } = params
    const demand = mockDemands.find((d) => d.id === id)

    if (!demand) {
      return HttpResponse.json(
        {
          code: 404,
          message: 'Demand not found',
          data: null,
        },
        { status: 404 }
      )
    }

    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: demand,
    })
  }),

  // 更新需求
  http.patch('/api/admin/demands/:id', async ({ params, request }) => {
    const { id } = params
    const body = await request.json() as any
    const demandIndex = mockDemands.findIndex((d) => d.id === id)

    if (demandIndex === -1) {
      return HttpResponse.json(
        {
          code: 404,
          message: 'Demand not found',
          data: null,
        },
        { status: 404 }
      )
    }

    // 更新需求
    mockDemands[demandIndex] = {
      ...mockDemands[demandIndex],
      ...body,
      updated_at: new Date().toISOString(),
    }

    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: mockDemands[demandIndex],
    })
  }),

  // 导出需求
  http.get('/api/admin/demands/export', () => {
    return HttpResponse.json({
      code: 0,
      message: 'success',
      data: {
        url: '/downloads/demands-export.csv',
        filename: 'demands-export.csv',
      },
    })
  }),
]
