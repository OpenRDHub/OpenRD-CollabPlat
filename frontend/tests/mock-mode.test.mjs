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

test('my tasks use the authenticated server endpoint', () => {
  const apiSource = readFileSync(new URL('../src/api/tasks.ts', import.meta.url), 'utf8')
  const viewSource = readFileSync(new URL('../src/views/MyTasksView.vue', import.meta.url), 'utf8')

  assert.match(apiSource, /getMyTasks[\s\S]*['"]\/me\/tasks['"]/)
  assert.match(viewSource, /tasksApi\.getMyTasks\(/)
  assert.doesNotMatch(viewSource, /getList\(\{\s*my:\s*true/)
})

test('joining a task submits an application and never grants local membership', () => {
  const viewSource = readFileSync(new URL('../src/views/TaskDetailView.vue', import.meta.url), 'utf8')

  assert.match(viewSource, /await tasksApi\.applyJoin\(/)
  assert.match(viewSource, /isCurrentUserMember/)
  assert.doesNotMatch(viewSource, /hasJoinedTeam\.value\s*=\s*true/)
})

test('mock approvals persist the member relationship for reloads', () => {
  const dataSource = readFileSync(new URL('../src/mocks/data/tasks.ts', import.meta.url), 'utf8')
  const handlerSource = readFileSync(new URL('../src/mocks/handlers/tasks.ts', import.meta.url), 'utf8')

  assert.match(dataSource, /openrd_task_members/)
  assert.match(dataSource, /export function saveTaskMembers/)
  assert.match(handlerSource, /taskMembers\.push\([\s\S]*saveTaskMembers\(\)/)
  assert.ok(/http\.get\(['"]\/api\/v1\/me\/tasks['"]/.test(handlerSource))
})

test('B12 task management uses backend limits and dedicated mutation endpoints', () => {
  const apiSource = readFileSync(new URL('../src/api/tasks.ts', import.meta.url), 'utf8')
  const viewSource = readFileSync(new URL('../src/views/TaskManagementView.vue', import.meta.url), 'utf8')

  assert.match(viewSource, /tasksApi\.getList\(\{\s*page:\s*1,\s*page_size:\s*100\s*\}\)/)
  assert.doesNotMatch(viewSource, /page_size:\s*200/)
  assert.match(viewSource, /tasksApi\.updateStatus\(/)
  assert.match(viewSource, /tasksApi\.updateProgress\([\s\S]*content:/)
  assert.match(viewSource, /tasksApi\.update\([\s\S]*\{\s*title\s*\}/)
  assert.doesNotMatch(viewSource, /status:\s*'reviewing'/)
  assert.doesNotMatch(viewSource, /value:\s*'formed'/)
  assert.match(apiSource, /updateProgress[\s\S]*expected_updated_at:\s*string \| null/)
  assert.match(viewSource, /expected_updated_at:\s*expectedUpdatedAt/)
})

test('B11 stage progress uses server history and optimistic concurrency tokens', () => {
  const apiSource = readFileSync(new URL('../src/api/tasks.ts', import.meta.url), 'utf8')
  const taskDetailSource = readFileSync(new URL('../src/views/TaskDetailView.vue', import.meta.url), 'utf8')
  const teamDetailSource = readFileSync(new URL('../src/views/TeamDetailView.vue', import.meta.url), 'utf8')

  assert.match(apiSource, /getProgressHistory[\s\S]*\/progress/)
  assert.match(apiSource, /stage:\s*string[\s\S]*next_plan\?: string/)
  assert.match(taskDetailSource, /tasksApi\.getProgressHistory\(/)
  assert.match(taskDetailSource, /tasksApi\.updateProgress\([\s\S]*expected_updated_at:/)
  assert.match(teamDetailSource, /tasksApi\.getProgressHistory\(/)
})

test('B12 my tasks expose explicit loading errors and null-safe fields', () => {
  const viewSource = readFileSync(new URL('../src/views/MyTasksView.vue', import.meta.url), 'utf8')

  assert.match(viewSource, /v-else-if="loadError"/)
  assert.match(viewSource, /description \|\| ''/)
  assert.match(viewSource, /created_at\?\.slice/)
  assert.match(viewSource, /team_ready:\s*'待处理'/)
  assert.match(viewSource, /pending_acceptance:\s*'解决中'/)
})

test('B13 demand management uses the canonical backend contract', () => {
  const apiSource = readFileSync(new URL('../src/api/demands.ts', import.meta.url), 'utf8')
  const viewSource = readFileSync(new URL('../src/views/DemandManagementView.vue', import.meta.url), 'utf8')
  const handlerIndexSource = readFileSync(new URL('../src/mocks/handlers/index.ts', import.meta.url), 'utf8')

  assert.match(viewSource, /demandsApi\.getList\(/)
  assert.doesNotMatch(viewSource, /adminDemandsApi|review_status|submitted_at|publisher_id|\.task_id|task_id\s*:/)
  assert.doesNotMatch(apiSource, /\/admin\/demands/)
  assert.match(apiSource, /getList[\s\S]*['"]\/demands['"]/)
  assert.match(viewSource, /value:\s*'pending_review'/)
  assert.match(viewSource, /value:\s*'communicating'/)
  assert.doesNotMatch(viewSource, /page_size:\s*200/)
  assert.doesNotMatch(handlerIndexSource, /adminDemandsHandlers/)
})

test('B13 demand mocks do not maintain a separate local management model', () => {
  const demandHandlerSource = readFileSync(new URL('../src/mocks/handlers/demands.ts', import.meta.url), 'utf8')

  assert.doesNotMatch(demandHandlerSource, /openrd_mock_admin_demand_patches/)
  assert.doesNotMatch(demandHandlerSource, /\/api\/v1\/admin\/demands/)
  assert.match(demandHandlerSource, /\/api\/v1\/demands/)
})
