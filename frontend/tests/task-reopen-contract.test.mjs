import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import vm from 'node:vm'
import ts from 'typescript'

const source = readFileSync(new URL('../src/views/TaskDetailView.vue', import.meta.url), 'utf8')
const handler = source.slice(source.indexOf('async function handleStatusChange()'), source.indexOf('// 将任务状态映射为阶段索引'))
function context(reason) {
  const requests = [], notices = []
  const state = {
    task: { value: { id: 'TASK-1', status: '解决中', stage: 'beta' } },
    statusSaving: { value: false }, canChangeStatus: { value: true },
    statusForm: { value: { target: '招募中', reason } }, showStatusModal: { value: true },
    CN_TO_STATUS: { '招募中': 'recruiting' },
    statusLabelMap: { recruiting: '招募中' }, teamStatusLabelMap: { forming: '招募中' },
    showToast: (notice) => notices.push(notice),
    tasksApi: { updateStatus: async (...args) => {
      requests.push(args)
      return { data: { status: 'recruiting', team_status: 'forming', updated_at: 'new-version' } }
    } },
  }
  const sandbox = vm.createContext(state)
  vm.runInContext(ts.transpileModule(handler, { compilerOptions: { target: ts.ScriptTarget.ES2022 } }).outputText, sandbox)
  return { sandbox, state, requests, notices }
}
test('reopening blocks empty and overlong reasons before sending a request', async () => {
  for (const reason of ['', ' \t\n ', 'x'.repeat(501)]) {
    const { sandbox, requests, notices } = context(reason)
    await sandbox.handleStatusChange()
    assert.equal(requests.length, 0)
    assert.equal(notices[0].variant, 'error')
  }
})
test('reopening sends the trimmed reason and preserves the displayed stage', async () => {
  const { sandbox, requests, state } = context('  补充成员  ')
  await sandbox.handleStatusChange()
  assert.equal(requests[0][0], 'TASK-1')
  assert.equal(requests[0][1].status, 'recruiting')
  assert.equal(requests[0][1].reason, '补充成员')
  assert.equal(state.task.value.status, '招募中')
  assert.equal(state.task.value.stage, 'beta')
  assert.equal(state.showStatusModal.value, false)
})
test('a rejected reopen keeps the dialog and current state for retry', async () => {
  const { sandbox, state, notices } = context('补充成员')
  state.tasksApi.updateStatus = async () => { throw { detail: '没有权限' } }
  await sandbox.handleStatusChange()
  assert.equal(state.task.value.status, '解决中')
  assert.equal(state.showStatusModal.value, true)
  assert.equal(state.statusSaving.value, false)
  assert.equal(notices[0].variant, 'error')
})
test('status controls follow ownership or effective permission, not membership', () => {
  const start = source.indexOf('const canChangeStatus =')
  const end = source.indexOf('const nextStatusOptionsForUser', start)
  const expression = source.slice(start, end) + '\ncanChangeStatus'
  for (const [leader, owner, permission, expected] of [
    [true, false, false, true], [false, true, false, true],
    [false, false, true, true], [false, false, false, false],
  ]) {
    assert.equal(vm.runInNewContext(expression, {
      computed: (fn) => fn(), isActualLeader: { value: leader }, isOwner: { value: owner },
      auth: { hasPermission: (name) => name === 'task:status' && permission },
    }), expected)
  }
})
