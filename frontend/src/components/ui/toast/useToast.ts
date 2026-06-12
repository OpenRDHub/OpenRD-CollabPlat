import { ref } from 'vue'

export interface ToastItem {
  id: number
  title: string
  description?: string
  variant?: 'default' | 'success' | 'error'
  duration?: number
}

const toasts = ref<ToastItem[]>([])
let nextId = 0

export function useToast() {
  function show(options: Omit<ToastItem, 'id'>) {
    const id = nextId++
    const toast: ToastItem = { id, duration: 3000, variant: 'default', ...options }
    toasts.value.push(toast)
    setTimeout(() => dismiss(id), toast.duration)
    return id
  }

  function dismiss(id: number) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  return { toasts, show, dismiss }
}
