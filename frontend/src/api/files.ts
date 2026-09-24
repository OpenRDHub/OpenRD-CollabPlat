import { api } from './client'

export const filesApi = {
  upload(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return fetch('/api/v1/files', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`,
      },
      body: formData,
    }).then(res => res.json())
  },

  getUrl(fileId: string) {
    return `/api/v1/files/${fileId}`
  },

  // 带鉴权地下载文件，返回原始 Response，由调用方处理为 Blob 触发下载
  download(fileId: string) {
    return fetch(`/api/v1/files/${fileId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token') || ''}`,
      },
    })
  },

  delete(fileId: string) {
    return api.delete(`/files/${fileId}`)
  },
}
