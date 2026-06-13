import { HttpResponse } from 'msw'

export function successResponse(data: unknown) {
  return HttpResponse.json({
    code: 'OK',
    message: 'success',
    data,
  })
}

export function paginatedResponse(items: unknown[], page: number, pageSize: number, total: number) {
  return HttpResponse.json({
    code: 'OK',
    message: 'success',
    data: {
      items,
      page,
      page_size: pageSize,
      total,
    },
  })
}

export function errorResponse(code: string, message: string, status: number) {
  return HttpResponse.json(
    { code, message },
    { status },
  )
}

export function paginate<T>(items: T[], page: number, pageSize: number): T[] {
  const start = (page - 1) * pageSize
  return items.slice(start, start + pageSize)
}

export function parsePageParams(url: URL) {
  const page = Number(url.searchParams.get('page')) || 1
  const pageSize = Math.min(Number(url.searchParams.get('page_size')) || 20, 100)
  const keyword = url.searchParams.get('keyword') || ''
  return { page, pageSize, keyword }
}
