import { http } from 'msw'
import { demands } from '../data/demands'
import { currentUserId } from '../data/users'
import {
  successResponse,
  errorResponse,
  paginatedResponse,
  parsePageParams,
  paginate,
} from '../utils'

export const demandHandlers = [
  http.post('/api/v1/demands', async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const newDemand = {
      id: `REQ-${Date.now()}`,
      title: body.title as string,
      description: body.description as string,
      urgency: (body.urgency as string) || 'medium',
      status: '待审核',
      convert_status: '未转化',
      creator_id: currentUserId,
      contact_phone: (body.contact_phone as string) || '',
      attachment_ids: (body.attachment_ids as string[]) || [],
      linked_task_id: '',
      linked_demand_id: '',
      progress: 0,
      feedback: '需求已提交，等待运营管理员初审。',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_deleted: 0,
      deleted_at: '',
      deleted_by: '',
    }
    demands.push(newDemand)
    return successResponse({ id: newDemand.id, status: newDemand.status })
  }),

  http.get('/api/v1/me/demands', ({ request }) => {
    const url = new URL(request.url)
    const { page, pageSize, keyword } = parsePageParams(url)
    const status = url.searchParams.get('status')

    let filtered = demands.filter(
      (d) => d.creator_id === currentUserId && d.is_deleted === 0,
    )
    if (status) filtered = filtered.filter((d) => d.status === status)
    if (keyword)
      filtered = filtered.filter(
        (d) => d.title.includes(keyword) || d.description.includes(keyword),
      )

    // 转换为前端需要的格式
    const transformedData = filtered.map((d) => {
      // 根据状态确定 stage
      let stage: 'pending' | 'talking' | 'converted' | 'closed' = 'pending'
      if (d.status === '待审核') stage = 'pending'
      else if (d.status === '沟通中') stage = 'talking'
      else if (d.status === '已转任务') stage = 'converted'
      else if (d.status === '已关闭') stage = 'closed'

      return {
        id: d.id,
        title: d.title,
        description: d.description,
        submitted_at: d.created_at.split('T')[0],
        status: d.status,
        convert_status: d.convert_status,
        task_id: d.linked_task_id || '暂未生成',
        progress: d.progress,
        contact: d.contact_phone ? '手机号已留存' : '微信已留存',
        attachments: d.attachment_ids.length,
        feedback: d.feedback,
        stage,
      }
    })

    return paginatedResponse(
      paginate(transformedData, page, pageSize),
      page,
      pageSize,
      transformedData.length,
    )
  }),

  http.get('/api/v1/demands/:demand_id', ({ params }) => {
    const demand = demands.find((d) => d.id === params.demand_id)
    if (!demand) return errorResponse('NOT_FOUND', '需求不存在', 404)

    // 扩展需求详情，添加会话和时间线信息
    const detailData = {
      ...demand,
      detail: demand.description,
      desc: demand.title,
      submittedAt: demand.created_at.split('T')[0],
      statusKey: demand.status === '待审核' ? 'pending' :
                  demand.status === '沟通中' ? 'talking' :
                  demand.status === '已转任务' ? 'converted' : 'closed',
      convertStatus: demand.convert_status,
      taskId: demand.linked_task_id || '暂未生成',
      contact: '手机号 159****7824 / 微信已留存',
      privateContact: `手机号 ${demand.contact_phone} / 微信 chenbei_openrd`,
      attachments: demand.attachment_ids.map((id, i) => `附件${i + 1}.pdf`),
      timeline: [
        ['提交需求', '需求发布者提交需求详情和附件。', demand.created_at.split('T')[0], 'done'],
        ['运营审核', '平台产品经理审核需求并沟通。', demand.updated_at.split('T')[0], demand.status === '待审核' ? 'active' : 'done'],
        ['转化评估', demand.feedback, demand.status === '已转任务' ? demand.updated_at.split('T')[0] : '待处理',
         demand.status === '已转任务' ? 'done' : demand.status === '沟通中' ? 'active' : 'pending'],
      ],
      threads: [
        {
          id: 'ops-yiran',
          pmName: '易然',
          pmTitle: '产品经理 · 运管',
          status: demand.status === '已转任务' ? '已转任务' : '信息充分',
          statusKey: demand.status === '已转任务' ? 'converted' : 'ready',
          canConvert: demand.status !== '已转任务',
          taskId: demand.linked_task_id || '',
          summary: demand.feedback,
          scope: '需求范围和功能点待确认',
          messages: [
            { from: 'pm', name: '易然', time: '05-25 10:12', text: '我们已收到你的需求，正在评估可行性。' },
            { from: 'requester', name: '需求者', time: '05-25 11:04', text: '期待能尽快得到反馈，谢谢！' },
          ],
        },
      ],
      convertedBy: demand.status === '已转任务' ? 'ops-yiran' : '',
    }

    return successResponse(detailData as unknown as Record<string, unknown>)
  }),

  http.get('/api/v1/demands', ({ request }) => {
    const url = new URL(request.url)
    const { page, pageSize, keyword } = parsePageParams(url)
    const status = url.searchParams.get('status')

    let filtered = demands.filter((d) => d.is_deleted === 0)
    if (status) filtered = filtered.filter((d) => d.status === status)
    if (keyword)
      filtered = filtered.filter(
        (d) => d.title.includes(keyword) || d.description.includes(keyword),
      )

    return paginatedResponse(paginate(filtered, page, pageSize), page, pageSize, filtered.length)
  }),

  http.post('/api/v1/demands/:demand_id/replies', () => {
    return successResponse({ reply_id: `reply-${Date.now()}` })
  }),

  http.post('/api/v1/demands/:demand_id/replies/:reply_id/revoke', () => {
    return successResponse({})
  }),

  http.post('/api/v1/demands/:demand_id/convert', ({ params }) => {
    const demand = demands.find((d) => d.id === params.demand_id)
    if (demand) {
      demand.status = 'converted'
      demand.convert_status = 'converted'
      demand.linked_task_id = `TASK-${Date.now()}`
    }
    return successResponse({ linked_task_id: demand?.linked_task_id })
  }),

  http.post('/api/v1/demands/:demand_id/reject', ({ params }) => {
    const demand = demands.find((d) => d.id === params.demand_id)
    if (demand) demand.status = 'rejected'
    return successResponse({})
  }),

  http.post('/api/v1/demands/:demand_id/link-similar', ({ params }) => {
    const demand = demands.find((d) => d.id === params.demand_id)
    if (demand) demand.status = 'linked'
    return successResponse({})
  }),

  http.post('/api/v1/demands/:demand_id/archive', ({ params }) => {
    const demand = demands.find((d) => d.id === params.demand_id)
    if (demand) demand.status = 'archived'
    return successResponse({})
  }),
]
