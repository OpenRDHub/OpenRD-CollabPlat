import { http } from 'msw'
import { messages } from '../data/messages'
import {
  successResponse,
  errorResponse,
  paginatedResponse,
  parsePageParams,
  paginate,
} from '../utils'

export const messageHandlers = [
  http.get('/api/v1/messages', ({ request }) => {
    const url = new URL(request.url)
    const { page, pageSize } = parsePageParams(url)
    const category = url.searchParams.get('category')

    let filtered = messages.filter((m) => m.is_deleted === 0)
    if (category) filtered = filtered.filter((m) => m.category === category)

    return paginatedResponse(paginate(filtered, page, pageSize), page, pageSize, filtered.length)
  }),

  http.get('/api/v1/messages/unread-count', () => {
    const count = messages.filter((m) => m.read_status === 0 && m.is_deleted === 0).length
    return successResponse({ count })
  }),

  http.get('/api/v1/messages/:message_id', ({ params }) => {
    const msg = messages.find((m) => m.id === params.message_id)
    if (!msg) return errorResponse('NOT_FOUND', '消息不存在', 404)
    return successResponse(msg as unknown as Record<string, unknown>)
  }),

  http.post('/api/v1/messages/:message_id/read', ({ params }) => {
    const msg = messages.find((m) => m.id === params.message_id)
    if (msg) msg.read_status = 1
    return successResponse({})
  }),

  http.post('/api/v1/messages/read-all', () => {
    messages.forEach((m) => { m.read_status = 1 })
    return successResponse({})
  }),

  http.delete('/api/v1/messages/:message_id', ({ params }) => {
    const msg = messages.find((m) => m.id === params.message_id)
    if (msg) {
      msg.is_deleted = 1
      msg.deleted_at = new Date().toISOString()
    }
    return successResponse({})
  }),
]
