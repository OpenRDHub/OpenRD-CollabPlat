import { http } from 'msw'
import { tasks, taskMembers } from '../data/tasks'
import {
  successResponse,
  errorResponse,
  paginatedResponse,
  parsePageParams,
  paginate,
} from '../utils'

export const taskHandlers = [
  http.get('/api/v1/tasks', ({ request }) => {
    const url = new URL(request.url)
    const { page, pageSize, keyword } = parsePageParams(url)
    const status = url.searchParams.get('status')

    let filtered = tasks.filter((t) => t.is_deleted === 0)
    if (status) filtered = filtered.filter((t) => t.status === status)
    if (keyword)
      filtered = filtered.filter(
        (t) => t.title.includes(keyword) || t.description.includes(keyword),
      )

    return paginatedResponse(paginate(filtered, page, pageSize), page, pageSize, filtered.length)
  }),

  http.get('/api/v1/tasks/:task_id', ({ params }) => {
    const task = tasks.find((t) => t.id === params.task_id)
    if (!task) return errorResponse('NOT_FOUND', '任务不存在', 404)
    return successResponse(task as unknown as Record<string, unknown>)
  }),

  http.patch('/api/v1/tasks/:task_id', async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const task = tasks.find((t) => t.id === params.task_id)
    if (!task) return errorResponse('NOT_FOUND', '任务不存在', 404)
    Object.assign(task, body, { updated_at: new Date().toISOString() })
    return successResponse(task as unknown as Record<string, unknown>)
  }),

  http.post('/api/v1/tasks/:task_id/status', async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const task = tasks.find((t) => t.id === params.task_id)
    if (!task) return errorResponse('NOT_FOUND', '任务不存在', 404)
    task.status = body.status as string
    task.updated_at = new Date().toISOString()
    return successResponse({})
  }),

  http.post('/api/v1/tasks/:task_id/progress', async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const task = tasks.find((t) => t.id === params.task_id)
    if (!task) return errorResponse('NOT_FOUND', '任务不存在', 404)
    task.progress = body.progress as number
    task.updated_at = new Date().toISOString()
    return successResponse({})
  }),

  http.post('/api/v1/tasks/:task_id/resources', async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const task = tasks.find((t) => t.id === params.task_id)
    if (!task) return errorResponse('NOT_FOUND', '任务不存在', 404)
    task.resource_links = body.resource_links as { label: string; url: string }[]
    task.updated_at = new Date().toISOString()
    return successResponse({})
  }),

  http.get('/api/v1/tasks/:task_id/team', ({ params }) => {
    const members = taskMembers.filter((m) => m.task_id === params.task_id)
    return successResponse({ members } as unknown as Record<string, unknown>)
  }),

  http.post('/api/v1/tasks/:task_id/join-applications', () => {
    return successResponse({})
  }),

  http.post('/api/v1/tasks/:task_id/join-applications/:application_id/approve', () => {
    return successResponse({})
  }),

  http.post('/api/v1/tasks/:task_id/join-applications/:application_id/reject', () => {
    return successResponse({})
  }),

  http.post('/api/v1/tasks/:task_id/members/invite', () => {
    return successResponse({})
  }),

  http.patch('/api/v1/tasks/:task_id/members/:member_id', async ({ params, request }) => {
    const body = (await request.json()) as Record<string, unknown>
    const member = taskMembers.find((m) => m.id === params.member_id)
    if (member) Object.assign(member, body)
    return successResponse({})
  }),

  http.post('/api/v1/tasks/:task_id/leader/transfer', () => {
    return successResponse({})
  }),

  http.put('/api/v1/tasks/:task_id/assignments', () => {
    return successResponse({})
  }),
]
