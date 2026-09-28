import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

const menuSource = readFileSync(new URL('../src/router/menus.ts', import.meta.url), 'utf8')
const routerSource = readFileSync(new URL('../src/router/index.ts', import.meta.url), 'utf8')
const appLayoutSource = readFileSync(new URL('../src/layouts/AppLayout.vue', import.meta.url), 'utf8')

test('B18 personal settings menus use the registered profile route for every role', () => {
  for (const role of ['requester', 'builder', 'operator', 'super_admin']) {
    const roleMenu = menuSource.match(new RegExp(`${role}: \\[([\\s\\S]*?)\\n  \\],`))
    assert.ok(roleMenu, `missing menu definition for ${role}`)

    const personalSettings = roleMenu[1].match(/label: '个人设置'[\s\S]*?to: '([^']+)'/)
    assert.ok(personalSettings, `missing personal settings item for ${role}`)
    assert.equal(personalSettings[1], '/profile', `${role} personal settings points to the wrong route`)
  }

  assert.doesNotMatch(menuSource, /to: '\/settings'/)
  assert.doesNotMatch(appLayoutSource, /router\.push\('\/settings'\)/)
  assert.match(appLayoutSource, /个人设置[\s\S]*?router\.push\('\/profile'\)|router\.push\('\/profile'\)[\s\S]*?个人设置/)
  assert.match(
    routerSource,
    /path: '\/profile',[\s\S]*?name: 'profile',[\s\S]*?ProfileView\.vue/,
  )
})
