import assert from 'node:assert/strict'
import { randomUUID } from 'node:crypto'
import { fileURLToPath } from 'node:url'
import test from 'node:test'
import { createServer } from 'vite'

function memoryStorage() {
  const values = new Map()
  return {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, String(value)),
    removeItem: (key) => values.delete(key),
    clear: () => values.clear(),
  }
}

test('real mock approvals keep recruitment open below, at, and above four members', async (t) => {
  const previous = new Map()
  for (const name of ['localStorage', 'sessionStorage']) {
    previous.set(name, Object.getOwnPropertyDescriptor(globalThis, name))
    Object.defineProperty(globalThis, name, { value: memoryStorage(), configurable: true })
  }
  t.after(() => {
    for (const [name, descriptor] of previous) {
      if (descriptor) Object.defineProperty(globalThis, name, descriptor)
      else delete globalThis[name]
    }
  })
  const vite = await createServer({
    configFile: false,
    optimizeDeps: { noDiscovery: true, include: [] },
    root: fileURLToPath(new URL('..', import.meta.url)),
    server: { middlewareMode: true },
    appType: 'custom',
  })
  t.after(() => vite.close())
  const { taskHandlers } = await vite.ssrLoadModule('/src/mocks/handlers/tasks.ts')
  const { tasks, taskMembers } = await vite.ssrLoadModule('/src/mocks/data/tasks.ts')
  const { joinApplications } = await vite.ssrLoadModule('/src/mocks/data/teams.ts')
  const { setCurrentUser } = await vite.ssrLoadModule('/src/mocks/data/users.ts')
  setCurrentUser('usr-002')
  const origin = 'http://localhost'
  async function call(method, route, path, body) {
    const handler = taskHandlers.find((item) => item.info.method === method && item.info.path === route)
    assert.ok(handler, `Missing actual handler: ${method} ${route}`)
    const result = await handler.run({
      request: new Request(origin + path, {
        method, headers: { 'Content-Type': 'application/json' },
        ...(body === undefined ? {} : { body: JSON.stringify(body) }),
      }),
      requestId: randomUUID(), resolutionContext: { baseUrl: origin },
    })
    assert.equal(result?.response?.status, 200)
    return result.response.json()
  }

  for (const initialCount of [0, 3, 5]) {
    await t.test(`starting with ${initialCount} active members`, async () => {
      const id = `RECRUIT-${initialCount}`
      const task = { ...tasks[0], id, status: 'recruiting', team_status: 'forming', stage: 'beta' }
      tasks.push(task)
      for (let i = 0; i < initialCount; i++) {
        taskMembers.push({ id: `${id}-member-${i}`, task_id: id, user_id: `${id}-user-${i}`,
          role: 'dev', status: 'active', member_type: 'member' })
      }
      for (let i = 0; i < 2; i++) {
        const application = { id: `${id}-app-${i}`, task_id: id, user_id: `${id}-new-${i}`,
          platform: `${id}-new-${i}`, role: 'dev', status: 'pending' }
        joinApplications.push(application)
        await call('POST', '/api/v1/tasks/:task_id/join-applications/:application_id/approve',
          `/api/v1/tasks/${id}/join-applications/${application.id}/approve`)
        assert.equal(application.status, 'approved')
        assert.equal(JSON.parse(localStorage.getItem('openrd_team_applications'))
          .find((item) => item.id === application.id).status, 'approved')
        assert.equal(taskMembers.filter((m) => m.task_id === id && m.status === 'active').length,
          initialCount + i + 1)
        const detail = await call('GET', '/api/v1/tasks/:task_id', `/api/v1/tasks/${id}`)
        assert.equal(detail.data.status, 'recruiting')
        assert.equal(detail.data.team_status, 'forming')
        assert.equal(detail.data.stage, 'beta')
        const persisted = JSON.parse(localStorage.getItem('openrd_mock_tasks')).find((x) => x.id === id)
        assert.equal(persisted.status, 'recruiting')
        assert.equal(persisted.team_status, 'forming')
        assert.equal(JSON.parse(localStorage.getItem('openrd_task_members'))
          .filter((m) => m.task_id === id && m.status === 'active').length, initialCount + i + 1)
      }
      const submitted = await call('POST', '/api/v1/tasks/:task_id/join-applications',
        `/api/v1/tasks/${id}/join-applications`, { role: 'dev', reason: 'Continue recruiting' })
      assert.equal(submitted.data.status, 'pending')
      assert.equal(task.status, 'recruiting')
    })
  }
})
