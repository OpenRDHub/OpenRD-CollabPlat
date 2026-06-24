import { http } from 'msw'
import { messages } from '../data/messages'
import {
  successResponse,
  errorResponse,
  paginatedResponse,
  parsePageParams,
  paginate,
} from '../utils'

const STORAGE_KEY = 'openrd_messages_state'

interface PersistedState {
  read_status?: number
  is_deleted?: number
  deleted_at?: string
}

function loadPersistedState() {
  const raw = sessionStorage.getItem(STORAGE_KEY)
  if (!raw) return
  const map: Record<string, PersistedState> = JSON.parse(raw)
  for (const [id, state] of Object.entries(map)) {
    const msg = messages.find((m) => m.id === id)
    if (!msg) continue
    if (state.read_status !== undefined) msg.read_status = state.read_status
    if (state.is_deleted !== undefined) msg.is_deleted = state.is_deleted
    if (state.deleted_at !== undefined) msg.deleted_at = state.deleted_at
  }
}

function persistState(id: string, patch: PersistedState) {
  const raw = sessionStorage.getItem(STORAGE_KEY)
  const map: Record<string, PersistedState> = raw ? JSON.parse(raw) : {}
  map[id] = { ...(map[id] ?? {}), ...patch }
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(map))
}

loadPersistedState()

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
    if (msg) {
      msg.read_status = 1
      persistState(msg.id, { read_status: 1 })
    }
    return successResponse({})
  }),

  http.post('/api/v1/messages/read-all', () => {
    messages.forEach((m) => {
      m.read_status = 1
      persistState(m.id, { read_status: 1 })
    })
    return successResponse({})
  }),

  http.delete('/api/v1/messages/:message_id', ({ params }) => {
    const msg = messages.find((m) => m.id === params.message_id)
    if (msg) {
      msg.is_deleted = 1
      msg.deleted_at = new Date().toISOString()
      persistState(msg.id, { is_deleted: 1, deleted_at: msg.deleted_at })
    }
    return successResponse({})
  }),
]
