import { http } from 'msw'
import { demands } from '../data/demands'
import type { MockDemand } from '../data/demands'
import { currentUserId } from '../data/users'
import { similarCandidates } from '../data/similar-candidates'
import {
  successResponse,
  errorResponse,
  paginatedResponse,
  parsePageParams,
  paginate,
} from '../utils'

type MutableDemand = MockDemand & { owner_id?: string }

function findDemand(demandId: string): MutableDemand | undefined {
  return demands.find((d) => d.id === demandId && d.is_deleted === 0)
}

function demandStage(status: string): 'pending' | 'talking' | 'converted' | 'closed' {
  if (status === 'pending_review') return 'pending'
  if (status === 'communicating') return 'talking'
  if (status === 'converted' || status === 'linked') return 'converted'
  return 'closed'
}

export const demandHandlers = [
  http.post('/api/v1/demands', async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const now = new Date().toISOString()
    const newDemand: MockDemand = {
      id: `REQ-${Date.now()}`,
      title: body.title as string,
      description: body.description as string,
      urgency: (body.urgency as string) || 'medium',
      status: 'pending_review',
      convert_status: '',
      creator_id: currentUserId,
      contact_phone: (body.contact_phone as string) || '',
      attachment_ids: (body.attachment_ids as string[]) || [],
      linked_task_id: '',
      linked_demand_id: '',
      progress: 0,
      feedback: '需求已提交，等待产品经理初审。',
      created_at: now,
      updated_at: now,
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
    if (keyword) {
      filtered = filtered.filter(
        (d) => d.title.includes(keyword) || d.description.includes(keyword),
      )
    }

    const items = filtered.map((d) => ({
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
      stage: demandStage(d.status),
    }))

    return paginatedResponse(
      paginate(items, page, pageSize),
      page,
      pageSize,
      items.length,
    )
  }),

  http.get('/api/v1/demands/:demand_id', ({ params }) => {
    const demand = findDemand(params.demand_id as string)
    if (!demand) return errorResponse('NOT_FOUND', '需求不存在', 404)
    return successResponse(demand)
  }),

  http.get('/api/v1/demands/:demand_id/similar-candidates', () => {
    return successResponse(similarCandidates as unknown as Record<string, unknown>)
  }),

  http.get('/api/v1/demands', ({ request }) => {
    const url = new URL(request.url)
    const { page, pageSize, keyword } = parsePageParams(url)
    const status = url.searchParams.get('status')
    const convertStatus = url.searchParams.get('convert_status')
    const ownerId = url.searchParams.get('owner_id')

    let filtered = demands.filter((d) => d.is_deleted === 0) as MutableDemand[]
    if (status) filtered = filtered.filter((d) => d.status === status)
    if (convertStatus) filtered = filtered.filter((d) => d.convert_status === convertStatus)
    if (ownerId) filtered = filtered.filter((d) => d.owner_id === ownerId)
    if (keyword) {
      filtered = filtered.filter((d) =>
        [d.id, d.title, d.description, d.linked_task_id]
          .some((value) => value.toLowerCase().includes(keyword.toLowerCase())),
      )
    }

    return paginatedResponse(
      paginate(filtered, page, pageSize),
      page,
      pageSize,
      filtered.length,
    )
  }),

  http.patch('/api/v1/demands/:demand_id', async ({ params, request }) => {
    const demand = findDemand(params.demand_id as string)
    if (!demand) return errorResponse('NOT_FOUND', '需求不存在', 404)

    const body = (await request.json()) as Record<string, unknown>
    const allowedFields = new Set(['progress', 'feedback', 'owner_id'])
    if (Object.keys(body).some((key) => !allowedFields.has(key))) {
      return errorResponse('VALIDATION_ERROR', '包含不支持的需求管理字段', 422)
    }
    if (typeof body.progress === 'number') demand.progress = body.progress
    if (typeof body.feedback === 'string') demand.feedback = body.feedback
    if (typeof body.owner_id === 'string') demand.owner_id = body.owner_id
    demand.updated_at = new Date().toISOString()
    return successResponse(demand)
  }),

  http.post('/api/v1/demands/:demand_id/replies', () => {
    return successResponse({ reply_id: `reply-${Date.now()}` })
  }),

  http.post('/api/v1/demands/:demand_id/replies/:reply_id/revoke', () => {
    return successResponse({})
  }),

  http.post('/api/v1/demands/:demand_id/convert', ({ params }) => {
    const demand = findDemand(params.demand_id as string)
    if (!demand) return errorResponse('NOT_FOUND', '需求不存在', 404)
    demand.status = 'converted'
    demand.convert_status = 'converted'
    demand.linked_task_id = `TASK-${Date.now()}`
    demand.updated_at = new Date().toISOString()
    return successResponse({
      demand_id: demand.id,
      task_id: demand.linked_task_id,
      demand_status: demand.status,
      task_status: 'recruiting',
    })
  }),

  http.post('/api/v1/demands/:demand_id/reject', async ({ params, request }) => {
    const demand = findDemand(params.demand_id as string)
    if (!demand) return errorResponse('NOT_FOUND', '需求不存在', 404)
    const body = (await request.json()) as { reason?: string }
    demand.status = 'rejected'
    demand.feedback = body.reason || demand.feedback
    demand.updated_at = new Date().toISOString()
    return successResponse({})
  }),

  http.post('/api/v1/demands/:demand_id/link-similar', async ({ params, request }) => {
    const demand = findDemand(params.demand_id as string)
    if (!demand) return errorResponse('NOT_FOUND', '需求不存在', 404)
    const body = (await request.json()) as {
      target_demand_id?: string
      target_task_id?: string
      reason?: string
    }
    demand.status = 'linked'
    demand.convert_status = 'linked'
    demand.linked_demand_id = body.target_demand_id || demand.linked_demand_id
    demand.linked_task_id = body.target_task_id || demand.linked_task_id
    demand.feedback = body.reason || demand.feedback
    demand.updated_at = new Date().toISOString()
    return successResponse({})
  }),

  http.post('/api/v1/demands/:demand_id/archive', ({ params }) => {
    const demand = findDemand(params.demand_id as string)
    if (!demand) return errorResponse('NOT_FOUND', '需求不存在', 404)
    demand.status = 'archived'
    demand.updated_at = new Date().toISOString()
    return successResponse({})
  }),
]
