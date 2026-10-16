import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

const apiSource = readFileSync(new URL('../src/api/tasks.ts', import.meta.url), 'utf8')
const taskDetailSource = readFileSync(new URL('../src/views/TaskDetailView.vue', import.meta.url), 'utf8')
const teamDetailSource = readFileSync(new URL('../src/views/TeamDetailView.vue', import.meta.url), 'utf8')

test('task API exposes leave application workflow', () => {
  assert.match(apiSource, /applyLeave\(/)
  assert.match(apiSource, /leave-applications/)
  assert.match(apiSource, /approveLeave\(/)
  assert.match(apiSource, /rejectLeave\(/)
})

test('members can request leave and leaders can review it', () => {
  assert.match(taskDetailSource, /申请退出队伍/)
  assert.match(taskDetailSource, /hasPendingLeaveApplication/)
  assert.match(teamDetailSource, /退出申请/)
  assert.match(teamDetailSource, /handleApproveLeave/)
})

test('super admins receive the join application entry', () => {
  assert.match(taskDetailSource, /\['builder', 'super_admin'\]\.includes\(auth\.userRole\)/)
})
