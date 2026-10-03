import { http } from 'msw'
import { demands } from '../data/demands'
import type { MockDemand } from '../data/demands'
import { currentUserId, getCurrentUser } from '../data/users'
import {
  successResponse,
  errorResponse,
  paginatedResponse,
  parsePageParams,
  paginate,
} from '../utils'

type MutableDemand = MockDemand & { owner_id?: string }

type MockReply = {
  id: string
  demand_id: string
  thread_id: string
  sender_id: string
  sender_role: string
  content: string
  attachment_ids: string[] | null
  is_revoked: number
  created_at: string
}

const repliesByDemand = new Map<string, MockReply[]>()

function findDemand(demandId: string): MutableDemand | undefined {
  return demands.find((d) => d.id === demandId && d.is_deleted === 0)
}

function toDemandOut(demand: MutableDemand) {
  return {
    id: demand.id,
    title: demand.title,
    description: demand.description,
    urgency: demand.urgency,
    status: demand.status,
    convert_status: demand.convert_status || null,
    creator_id: demand.creator_id,
    progress: demand.progress,
    feedback: demand.feedback || null,
    linked_task_id: demand.linked_task_id || null,
    linked_demand_id: demand.linked_demand_id || null,
    owner_id: demand.owner_id || null,
    created_at: demand.created_at,
    updated_at: demand.updated_at,
  }
}

function maskPhone(phone: string | null | undefined) {
  if (!phone || phone.length < 7) return phone || null
  return `${phone.slice(0, 3)}****${phone.slice(-4)}`
}

function toDemandDetail(demand: MutableDemand) {
  const viewer = getCurrentUser()
  const canViewPhone = demand.creator_id === viewer.id || ['operator', 'super_admin'].includes(viewer.role)
  return {
    ...toDemandOut(demand),
    contact_phone: canViewPhone ? demand.contact_phone || null : maskPhone(demand.contact_phone),
    attachment_ids: demand.attachment_ids,
  }
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

    const items = filtered.map(toDemandOut)

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
    return successResponse(toDemandDetail(demand))
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
      paginate(filtered.map(toDemandOut), page, pageSize),
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
    return successResponse(toDemandDetail(demand))
  }),

  http.get('/api/v1/demands/:demand_id/replies', ({ params, request }) => {
    const url = new URL(request.url)
    const { page, pageSize } = parsePageParams(url)
    const items = repliesByDemand.get(params.demand_id as string) || []
    return paginatedResponse(paginate(items, page, pageSize), page, pageSize, items.length)
  }),

  http.post('/api/v1/demands/:demand_id/replies', async ({ params, request }) => {
    const body = (await request.json()) as { thread_id?: string; content?: string; attachment_ids?: string[] }
    const reply: MockReply = {
      id: `reply-${Date.now()}`,
      demand_id: params.demand_id as string,
      thread_id: body.thread_id || 'thread-default',
      sender_id: currentUserId,
      sender_role: getCurrentUser().role === 'requester' ? 'requester' : getCurrentUser().role,
      content: body.content || '',
      attachment_ids: body.attachment_ids || null,
      is_revoked: 0,
      created_at: new Date().toISOString(),
    }
    const items = repliesByDemand.get(reply.demand_id) || []
    items.push(reply)
    repliesByDemand.set(reply.demand_id, items)
    return successResponse(reply)
  }),

  http.post('/api/v1/demands/:demand_id/replies/:reply_id/revoke', ({ params }) => {
    const items = repliesByDemand.get(params.demand_id as string) || []
    const reply = items.find((item) => item.id === params.reply_id)
    if (!reply) return errorResponse('NOT_FOUND', '消息不存在', 404)
    reply.is_revoked = 1
    reply.content = ''
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

  http.post('/api/v1/demands/:demand_id/communicate', ({ params }) => {
    const demand = findDemand(params.demand_id as string)
    if (!demand) return errorResponse('NOT_FOUND', '需求不存在', 404)
    if (demand.status !== 'pending_review') {
      return errorResponse('INVALID_STATUS', '当前状态不允许开始沟通', 400)
    }
    demand.status = 'communicating'
    demand.updated_at = new Date().toISOString()
    return successResponse(toDemandOut(demand))
  }),

  http.post('/api/v1/demands/:demand_id/close', ({ params }) => {
    const demand = findDemand(params.demand_id as string)
    if (!demand) return errorResponse('NOT_FOUND', '需求不存在', 404)
    if (['converted', 'linked', 'archived', 'closed'].includes(demand.status)) {
      return errorResponse('INVALID_STATUS', '当前状态不允许关闭', 400)
    }
    demand.status = 'closed'
    demand.updated_at = new Date().toISOString()
    return successResponse(toDemandOut(demand))
  }),
]
