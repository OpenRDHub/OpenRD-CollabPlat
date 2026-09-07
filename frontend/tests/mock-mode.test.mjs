import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

import { handleUnhandledMockRequest, isMockEnabled } from '../src/config/mock-mode.js'

test('MSW is disabled when the environment variable is missing', () => {
  assert.equal(isMockEnabled(undefined), false)
})

test('MSW is disabled for false and malformed values', () => {
  for (const value of ['false', 'TRUE', '1', '']) {
    assert.equal(isMockEnabled(value), false)
  }
})

test('MSW is enabled only by an explicit true value', () => {
  assert.equal(isMockEnabled('true'), true)
})

test('unhandled API requests fail instead of silently reaching the backend', () => {
  let errorCount = 0
  const print = { error: () => { errorCount += 1 } }

  handleUnhandledMockRequest(new Request('http://127.0.0.1:5173/api/v1/tasks'), print)
  handleUnhandledMockRequest(new Request('http://127.0.0.1:5173/assets/index.js'), print)

  assert.equal(errorCount, 1)
})

test('the application bootstrap uses the tested mock-mode contract', () => {
  const source = readFileSync(new URL('../src/main.ts', import.meta.url), 'utf8')

  assert.match(
    source,
    /import\.meta\.env\.DEV\s*&&\s*isMockEnabled\(import\.meta\.env\.VITE_ENABLE_MOCK\)/,
  )
  assert.doesNotMatch(
    source,
    /VITE_ENABLE_MOCK\s*!==\s*['"]false['"]/,
  )
})
