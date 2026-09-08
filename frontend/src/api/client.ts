import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

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

const instance: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

instance.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

instance.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      const currentPath = window.location.pathname
      if (currentPath !== '/login') {
        window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`
      }
    }
    const data = error.response?.data ?? { code: 'NETWORK_ERROR', message: '网络错误' }
    return Promise.reject(data)
  },
)

class ApiClient {
  async get<T>(url: string, params?: Record<string, string | number | undefined>): Promise<ApiResponse<T>> {
    const cleaned: Record<string, string | number> = {}
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          cleaned[key] = value
        }
      })
    }
    const res = await instance.get<ApiResponse<T>>(url, { params: cleaned })
    return res.data
  }

  async post<T>(url: string, body?: unknown): Promise<ApiResponse<T>> {
    const res = await instance.post<ApiResponse<T>>(url, body)
    return res.data
  }

  async patch<T>(url: string, body?: unknown): Promise<ApiResponse<T>> {
    const res = await instance.patch<ApiResponse<T>>(url, body)
    return res.data
  }

  async put<T>(url: string, body?: unknown): Promise<ApiResponse<T>> {
    const res = await instance.put<ApiResponse<T>>(url, body)
    return res.data
  }

  async delete<T>(url: string): Promise<ApiResponse<T>> {
    const res = await instance.delete<ApiResponse<T>>(url)
    return res.data
  }

  async upload<T>(url: string, formData: FormData, onProgress?: (percent: number) => void): Promise<ApiResponse<T>> {
    const res = await instance.post<ApiResponse<T>>(url, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress(event) {
        if (onProgress && event.total) {
          onProgress(Math.round((event.loaded * 100) / event.total))
        }
      },
    })
    return res.data
  }
}

export const api = new ApiClient()
export { instance as axiosInstance }
export type { ApiResponse, PaginatedData }
