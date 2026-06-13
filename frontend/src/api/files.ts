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

  delete(fileId: string) {
    return api.delete(`/files/${fileId}`)
  },
}
