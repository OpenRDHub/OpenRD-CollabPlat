/**
 * MSW is an explicit opt-in development tool. Missing or malformed values
 * must keep requests on the real backend path.
 *
 * @param {string | undefined} value
 */
export function isMockEnabled(value) {
  return value === 'true'
}

/**
 * In explicit Mock mode, missing API handlers are contract errors. Non-API
 * resources continue normally so Vite assets are not affected.
 *
 * @param {Request} request
 * @param {{ error: () => void }} print
 */
export function handleUnhandledMockRequest(request, print) {
  const pathname = new URL(request.url).pathname
  if (pathname.startsWith('/api/v1/')) {
    print.error()
  }
}
