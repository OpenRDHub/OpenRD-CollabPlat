import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import ts from 'typescript'

const source = readFileSync(new URL('../src/utils/projectProgress.ts', import.meta.url), 'utf8')
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext } })
const { projectAvailabilityLabel, taskStageLabel, taskStatusLabels } = await import(
  `data:text/javascript;base64,${Buffer.from(compiled.outputText).toString('base64')}`
)

test('project stages remain independent of task completion or closure', () => {
  for (const status of ['completed', 'closed']) {
    assert.equal(projectAvailabilityLabel({ availability: 'available', status, stage: 'beta' }), '内测')
  }
  assert.deepEqual(['team', 'develop', 'beta', 'opensource'].map(taskStageLabel), ['组队', '开发', '内测', '开源'])
  assert.equal(taskStatusLabels.team_ready, '待处理')
  assert.equal(taskStatusLabels.pending_acceptance, '待验收')
})

test('unavailable project links never display a stale stage', () => {
  assert.equal(projectAvailabilityLabel({ availability: 'deleted', stage: 'develop' }), '关联任务已删除')
  assert.equal(projectAvailabilityLabel({ availability: 'missing', stage: 'beta' }), '关联项目不可用')
  assert.equal(projectAvailabilityLabel({ availability: 'unlinked' }), '暂未关联项目')
  assert.equal(projectAvailabilityLabel(undefined), '暂未关联项目')
  assert.equal(taskStageLabel(null), '阶段未设置')
})
