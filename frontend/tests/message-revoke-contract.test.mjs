import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

const viewSource = readFileSync(new URL('../src/views/DemandDetailView.vue', import.meta.url), 'utf8')
const apiSource = readFileSync(new URL('../src/api/demands.ts', import.meta.url), 'utf8')
const backendSource = readFileSync(new URL('../../backend/app/api/v1/demand.py', import.meta.url), 'utf8')

test('B16 revoke waits for the persistence API before mutating the message', () => {
  assert.match(viewSource, /replyId: r\.id/)
  assert.match(viewSource, /replyId: response\.data\.reply_id/)

  const handler = viewSource.match(/const handleRevokeMessage = async \(\) => \{([\s\S]*?)\n\}/)?.[1]
  assert.ok(handler, 'missing asynchronous revoke handler')
  assert.match(handler, /await demandsApi\.revokeReply\(demandId\.value, msg\.replyId\)/)
  assert.ok(
    handler.indexOf('await demandsApi.revokeReply') < handler.indexOf('msg.revoked = true'),
    'the UI must not report a revoke before the server accepts it',
  )
  assert.match(handler, /catch \(error: any\)[\s\S]*撤回失败/)
})

test('B16 frontend and backend use the same revoke endpoint', () => {
  assert.match(apiSource, /post\(`\/demands\/\$\{demandId\}\/replies\/\$\{replyId\}\/revoke`\)/)
  assert.match(backendSource, /@router\.post\("\/demands\/\{demand_id\}\/replies\/\{reply_id\}\/revoke"/)
  assert.match(backendSource, /await revoke_reply\(db, reply\)/)
})
