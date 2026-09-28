import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

const apiSource = readFileSync(new URL('../src/api/tasks.ts', import.meta.url), 'utf8')
const viewSource = readFileSync(new URL('../src/views/TeamDetailView.vue', import.meta.url), 'utf8')
const mockSource = readFileSync(new URL('../src/mocks/handlers/tasks.ts', import.meta.url), 'utf8')
const backendTeamSource = readFileSync(new URL('../../backend/app/api/v1/team.py', import.meta.url), 'utf8')
const backendTaskSource = readFileSync(new URL('../../backend/app/api/v1/task.py', import.meta.url), 'utf8')

test('B20 team reads use the aggregate endpoint instead of nonexistent GET routes', () => {
  assert.match(apiSource, /getTeam\(taskId: string\)[\s\S]*?get<TeamDetail>\(`\/tasks\/\$\{taskId\}\/team`\)/)
  assert.match(viewSource, /tasksApi\.getTeam\(taskId\.value\)/)
  assert.doesNotMatch(apiSource, /getJoinApplications\(taskId: string\)/)
  assert.doesNotMatch(apiSource, /getAssignments\(taskId: string\)/)
  assert.doesNotMatch(mockSource, /http\.get\('\/api\/v1\/tasks\/:task_id\/join-applications'/)
  assert.doesNotMatch(mockSource, /http\.get\('\/api\/v1\/tasks\/:task_id\/assignments'/)
  assert.match(mockSource, /applications: task\?\.leader_id === currentUserId[\s\S]*: \[\]/)
})

test('B20 keeps only routes implemented by the backend and protects application details', () => {
  assert.match(backendTeamSource, /@router\.get\("\/tasks\/\{task_id\}\/team"/)
  assert.match(backendTeamSource, /@router\.put\("\/tasks\/\{task_id\}\/assignments"/)
  assert.match(backendTaskSource, /@router\.get\("\/tasks\/\{task_id\}\/timeline"/)
  assert.match(backendTeamSource, /can_review_applications[\s\S]*"member:approve"/)
  assert.match(backendTeamSource, /if can_review_applications[\s\S]*else \[\]/)
})
