import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

const apiSource = readFileSync(new URL('../src/api/messages.ts', import.meta.url), 'utf8')
const viewSource = readFileSync(new URL('../src/views/MessagesView.vue', import.meta.url), 'utf8')
const mockSource = readFileSync(new URL('../src/mocks/handlers/messages.ts', import.meta.url), 'utf8')
const backendSchema = readFileSync(new URL('../../backend/app/schemas/message.py', import.meta.url), 'utf8')

test('B19 unread totals use the backend total and by_category contract', () => {
  assert.match(apiSource, /interface UnreadCount[\s\S]*total: number[\s\S]*by_category: Record<string, number>/)
  assert.doesNotMatch(apiSource, /getUnreadCount\(\)[\s\S]*?\{ count: number \}/)
  assert.match(viewSource, /unreadSummary\.value\.total/)
  assert.match(viewSource, /unreadSummary\.value\.by_category\[cat\.key\]/)
  assert.match(backendSchema, /class UnreadCountOut[\s\S]*total: int[\s\S]*by_category: dict\[str, int\]/)
})

test('B19 mocks expose the same unread structure and actions refresh server totals', () => {
  assert.match(mockSource, /total: unread\.length, by_category: byCategory/)
  assert.doesNotMatch(mockSource, /successResponse\(\{ count \}\)/)
  assert.match(viewSource, /Promise\.all\([\s\S]*messagesApi\.getUnreadCount\(\)/)
  assert.ok(viewSource.match(/messagesApi\.getUnreadCount\(\)/g)?.length >= 5)
})
