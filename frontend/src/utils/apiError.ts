interface ValidationErrorItem {
  msg?: unknown
}

interface ApiErrorPayload {
  detail?: unknown
  message?: unknown
}

function cleanValidationMessage(message: string): string {
  return message.replace(/^Value error,\s*/i, '').trim()
}

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (!error || typeof error !== 'object') return fallback

  const payload = error as ApiErrorPayload

  if (typeof payload.detail === 'string' && payload.detail.trim()) {
    return payload.detail.trim()
  }

  if (Array.isArray(payload.detail)) {
    const messages = payload.detail
      .map((item: ValidationErrorItem) => (
        typeof item?.msg === 'string' ? cleanValidationMessage(item.msg) : ''
      ))
      .filter(Boolean)

    if (messages.length > 0) return messages.join('；')
  }

  if (typeof payload.message === 'string' && payload.message.trim()) {
    return payload.message.trim()
  }

  return fallback
}
