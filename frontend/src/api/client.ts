const BASE_URL = '/api/v1'

interface ApiResponse<T = unknown> {
  code: string
  message: string
  data: T
}

interface PaginatedData<T> {
  items: T[]
  page: number
  page_size: number
  total: number
}

class ApiClient {
  private getToken(): string | null {
    return localStorage.getItem('access_token')
  }

  private async request<T>(url: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const token = this.getToken()
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers as Record<string, string>,
    }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const response = await fetch(`${BASE_URL}${url}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ code: 'NETWORK_ERROR', message: '网络错误' }))
      throw error
    }

    return response.json()
  }

  get<T>(url: string, params?: Record<string, string | number | undefined>): Promise<ApiResponse<T>> {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          searchParams.set(key, String(value))
        }
      })
    }
    const query = searchParams.toString()
    return this.request<T>(query ? `${url}?${query}` : url)
  }

  post<T>(url: string, body?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>(url, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  patch<T>(url: string, body?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>(url, {
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  put<T>(url: string, body?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>(url, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  delete<T>(url: string): Promise<ApiResponse<T>> {
    return this.request<T>(url, { method: 'DELETE' })
  }
}

export const api = new ApiClient()
export type { ApiResponse, PaginatedData }
