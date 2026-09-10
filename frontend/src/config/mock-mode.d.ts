export function isMockEnabled(value: string | undefined): boolean

interface UnhandledRequestPrinter {
  error: () => void
}

export function handleUnhandledMockRequest(
  request: Request,
  print: UnhandledRequestPrinter,
): void
