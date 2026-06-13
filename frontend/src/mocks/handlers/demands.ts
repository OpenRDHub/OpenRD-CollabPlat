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
      status: 'pending_review',
      convert_status: '',
      creator_id: currentUserId,
      contact_phone: (body.contact_phone as string) || '',
      attachment_ids: (body.attachment_ids as string[]) || [],
      linked_task_id: '',
      linked_demand_id: '',
      progress: 0,
      feedback: '',
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

    return paginatedResponse(paginate(filtered, page, pageSize), page, pageSize, filtered.length)
  }),

  http.get('/api/v1/demands/:demand_id', ({ params }) => {
    const demand = demands.find((d) => d.id === params.demand_id)
    if (!demand) return errorResponse('NOT_FOUND', '需求不存在', 404)
    return successResponse(demand as unknown as Record<string, unknown>)
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
