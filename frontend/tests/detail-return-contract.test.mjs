import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

const navbarSource = readFileSync(new URL('../src/components/TopNavbar.vue', import.meta.url), 'utf8')

test('B17 detail return uses safe navigation history instead of a fixed workbench link', () => {
  assert.doesNotMatch(navbarSource, /<router-link to="\/workbench" class="ghost-button">\s*返回/)
  assert.match(navbarSource, /window\.history\.state\?\.back/)
  assert.match(navbarSource, /router\.back\(\)/)
  assert.match(navbarSource, /@click="handleReturn"/)
  assert.match(navbarSource, /route\.query\.from/)
  assert.match(navbarSource, /RETURN_PATHS/)
  assert.match(navbarSource, /\^\\\/\(login\|register\|forgot-password\|onboarding\)/)
})

test('B17 list links preserve their source for deterministic return navigation', () => {
  for (const [view, source] of [
    ['DemandManagementView.vue', 'demandManagement'],
    ['MyDemandsView.vue', 'myDemands'],
    ['TaskManagementView.vue', 'taskManagement'],
    ['MyTasksView.vue', 'myTasks'],
    ['HallView.vue', 'hall'],
  ]) {
    const sourceText = readFileSync(new URL(`../src/views/${view}`, import.meta.url), 'utf8')
    assert.match(sourceText, new RegExp(`from: '${source}'`), `${view} must preserve its source`)
  }
})

test('B17 direct detail visits fall back to the correct role-specific list', () => {
  assert.match(navbarSource, /route\.name === 'demand-detail'/)
  assert.match(navbarSource, /'\/admin\/demand-management' : '\/my-demands'/)
  assert.match(navbarSource, /route\.name === 'task-detail'/)
  assert.match(navbarSource, /'\/admin\/task-management' : '\/my-tasks'/)
  assert.match(navbarSource, /route\.name === 'team-detail'/)
  assert.match(navbarSource, /`\/tasks\/\$\{route\.params\.taskId\}`/)
})
