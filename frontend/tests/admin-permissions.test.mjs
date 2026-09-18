import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

const viewSource = readFileSync(new URL('../src/views/PermissionManagementView.vue', import.meta.url), 'utf8')
const apiSource = readFileSync(new URL('../src/api/admin.ts', import.meta.url), 'utf8')
const mockSource = readFileSync(new URL('../src/mocks/handlers/admin.ts', import.meta.url), 'utf8')

test('saving permissions submits only manual_permission_ids and never template permissions', () => {
  assert.match(viewSource, /setUserPermissions\(\s*editForm\.value\.id,\s*\{\s*manual_permission_ids:/)
  assert.doesNotMatch(viewSource, /manual_permissions:\s*effectivePermissions/)
  assert.doesNotMatch(viewSource, /permissions:\s*effectivePermissions/)
})

test('an empty adjustment reason blocks submission before any API call', () => {
  assert.match(viewSource, /const reason = editForm\.value\.reason\.trim\(\)/)
  assert.match(viewSource, /if \(!reason\)\s*\{[\s\S]*?return/)
  // 请求体必须携带 reason 字段
  assert.match(viewSource, /reason,\s*\n\s*\}\)/)
})

test('failed saves never report success or fall back to local persistence', () => {
  assert.doesNotMatch(viewSource, /已在本地保留/)
  assert.doesNotMatch(viewSource, /remotePermissionSaved/)
  // 保存失败的提示必须出现在 catch 分支中
  assert.match(viewSource, /catch\s*\{[\s\S]*?保存失败[\s\S]*?variant:\s*'error'/)
})

test('successful saves refresh state from the server response', () => {
  assert.match(viewSource, /const res = await adminApi\.setUserPermissions\(/)
  assert.match(viewSource, /manual_permission_ids \?\? \[\]/)
  assert.match(viewSource, /role:\s*res\.data\.role/)
})

test('the page never restores authorization state from localStorage', () => {
  assert.doesNotMatch(viewSource, /openrd_manual_permissions/)
  assert.doesNotMatch(viewSource, /persistPermissionState/)
  assert.doesNotMatch(viewSource, /loadStoredPermissionState/)
  assert.doesNotMatch(viewSource, /localStorage/)
})

test('opening the edit dialog loads permissions from the server', () => {
  assert.match(viewSource, /await adminApi\.getUserPermissions\(/)
})

test('switching a role recalculates template and effective permissions', () => {
  assert.match(viewSource, /getTemplatePermissions\(editForm\.value\.role\)/)
  assert.match(viewSource, /function getEffectivePermissions\(/)
})

test('the api contract uses manual_permission_ids and requires a reason', () => {
  assert.match(apiSource, /interface SetUserPermissionsPayload\s*\{[\s\S]*?manual_permission_ids:\s*string\[\][\s\S]*?reason:\s*string/)
  assert.match(apiSource, /interface UserPermissionDetail\s*\{[\s\S]*?template_permission_ids[\s\S]*?manual_permission_ids[\s\S]*?effective_permission_ids/)
})

test('mocks use the same permission contract as the real backend', () => {
  assert.match(mockSource, /template_permission_ids/)
  assert.match(mockSource, /manual_permission_ids/)
  assert.match(mockSource, /effective_permission_ids/)
  assert.match(mockSource, /reason/)
})

test('mocks validate reason and permission ids like the real backend', () => {
  assert.match(mockSource, /调整原因不能为空/)
  assert.match(mockSource, /非法权限 ID/)
})
