import { http, HttpResponse } from 'msw'
import { successResponse, errorResponse } from '../utils'

export const fileHandlers = [
  http.post('/api/v1/files', () => {
    return successResponse({ file_id: `file-${Date.now()}` })
  }),

  http.get('/api/v1/files/:file_id', () => {
    return new HttpResponse(null, { status: 204 })
  }),

  http.delete('/api/v1/files/:file_id', () => {
    return successResponse({})
  }),
]
