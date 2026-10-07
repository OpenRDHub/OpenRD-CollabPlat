import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

const root = path.resolve(import.meta.dirname, '..')

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8')
}

test('global responsive tokens cover mobile spacing, touch targets, viewport and safe area', () => {
  const tokens = read('src/styles/tokens.css')
  const base = read('src/styles/base.css')

  assert.match(tokens, /--ord-page-padding/)
  assert.match(tokens, /--ord-touch-target:\s*44px/)
  assert.match(tokens, /safe-area-inset-bottom/)
  assert.match(base, /100dvh/)
  assert.match(base, /overflow-x:\s*hidden/)
})

test('shared navigation and overlay components expose mobile interaction rules', () => {
  const appLayout = read('src/layouts/AppLayout.vue')
  const topNavbar = read('src/components/TopNavbar.vue')
  const dialog = read('src/components/ui/dialog/OrdDialog.vue')

  assert.match(appLayout, /app-layout__sidebar--open/)
  assert.match(appLayout, /ord-sidebar-open/)
  assert.match(topNavbar, /mobile-menu-toggle/)
  assert.match(topNavbar, /profile-trigger--open/)
  assert.match(dialog, /ord-slide-up/)
  assert.match(dialog, /safe-area-inset-bottom|ord-mobile-bottom-space/)
})

test('core mobile pages keep a single-column interaction path', () => {
  const hall = read('src/views/HallView.vue')
  const task = read('src/views/TaskDetailView.vue')
  const demand = read('src/views/DemandDetailView.vue')
  const team = read('src/views/TeamDetailView.vue')

  for (const source of [hall, task, demand, team]) {
    assert.match(source, /@media \(max-width: 768px\)|@media \(max-width: 767px\)/)
  }

  assert.match(hall, /\.list-row\s*\{[\s\S]*?min-width: 0;/)
  assert.match(task, /calc\(var\(--ord-nav-height\) \+ var\(--ord-page-padding\)\)/)
  assert.match(demand, /max-height: 46dvh/)
  assert.match(team, /var\(--ord-mobile-bottom-space\)/)
})

test('second-batch user pages switch dense content to touch-friendly mobile layouts', () => {
  const tasks = read('src/views/MyTasksView.vue')
  const demands = read('src/views/MyDemandsView.vue')
  const messages = read('src/views/MessagesView.vue')
  const profile = read('src/views/ProfileView.vue')

  assert.match(tasks, /\.task-header\s*\{\s*display:\s*none/)
  assert.match(tasks, /\.task-row\s*\{[\s\S]*?min-width:\s*0/)
  assert.match(demands, /\.demand-header\s*\{\s*display:\s*none/)
  assert.match(demands, /\.demand-row\s*\{[\s\S]*?min-width:\s*0/)
  assert.match(messages, /height:\s*100dvh/)
  assert.match(messages, /ord-message-drawer-open/)
  assert.match(profile, /\.modal-footer\s*\{[\s\S]*?position:\s*sticky/)
})

test('authentication pages account for dynamic viewport and bottom safe area', () => {
  for (const file of ['LoginView.vue', 'RegisterView.vue', 'ForgotPasswordView.vue']) {
    const source = read(`src/views/${file}`)
    assert.match(source, /100dvh/)
    assert.match(source, /safe-area-inset-bottom/)
  }
})
