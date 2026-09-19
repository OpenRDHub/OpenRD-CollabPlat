import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

const viewSource = readFileSync(new URL('../src/views/PermissionManagementView.vue', import.meta.url), 'utf8')
const apiSource = readFileSync(new URL('../src/api/admin.ts', import.meta.url), 'utf8')
const mockSource = readFileSync(new URL('../src/mocks/handlers/admin.ts', import.meta.url), 'utf8')

test('saving authorization uses the single atomic setUserAuthorization call', () => {
  // 必须调用原子授权接口（角色 + 手动权限 + 原因一次提交）
  assert.match(viewSource, /adminApi\.setUserAuthorization\(\s*editForm\.value\.id,\s*\{\s*role:\s*editForm\.value\.role,/)
  // 不允许再出现旧的两步保存（先 updateUser 改角色再 setUserPermissions）
  assert.doesNotMatch(viewSource, /setUserPermissions/)
  assert.doesNotMatch(viewSource, /adminApi\.updateUser\(editForm/)
  assert.doesNotMatch(viewSource, /manual_permissions:\s*effectivePermissions/)
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

test('the save button stays disabled until server permissions are loaded', () => {
  // editReady 只有在服务端权限加载成功后才会置为 true
  assert.match(viewSource, /editReady\.value = false/)
  assert.match(viewSource, /editReady\.value = true/)
  assert.match(viewSource, /:disabled="!editReady"/)
  // handleSave 必须在 editReady 为 false 时直接返回
  assert.match(viewSource, /saving\.value \|\| !editReady\.value\) return/)
})

test('successful saves refresh state from the server response', () => {
  assert.match(viewSource, /const res = await adminApi\.setUserAuthorization\(/)
  assert.match(viewSource, /manual_permission_ids \?\? \[\]/)
  assert.match(viewSource, /role:\s*res\.data\.role/)
})

test('the page never restores authorization state from localStorage', () => {
  assert.doesNotMatch(viewSource, /openrd_manual_permissions/)
  assert.doesNotMatch(viewSource, /persistPermissionState/)
  assert.doesNotMatch(viewSource, /loadStoredPermissionState/)
  assert.doesNotMatch(viewSource, /localStorage/)
})

test('role templates are fetched from the server, not hardcoded', () => {
  // 模板必须来自服务端 getRoles，不允许前端硬编码角色权限数组
  assert.match(viewSource, /adminApi\.getRoles\(\)/)
  assert.doesNotMatch(viewSource, /const ROLE_TEMPLATES:\s*Record<RoleKey,\s*string\[\]>\s*=\s*\{[\s\S]*?demand:create/)
})

test('opening the edit dialog loads permissions from the server', () => {
  assert.match(viewSource, /await adminApi\.getUserPermissions\(/)
})

test('switching a role recalculates template and effective permissions', () => {
  assert.match(viewSource, /getTemplatePermissions\(editForm\.value\.role\)/)
  assert.match(viewSource, /function getEffectivePermissions\(/)
})

test('the api contract uses the atomic authorization payload', () => {
  assert.match(apiSource, /interface SetUserAuthorizationPayload\s*\{[\s\S]*?role:\s*string[\s\S]*?manual_permission_ids:\s*string\[\][\s\S]*?reason:\s*string/)
  assert.match(apiSource, /interface UserPermissionDetail\s*\{[\s\S]*?template_permission_ids[\s\S]*?manual_permission_ids[\s\S]*?effective_permission_ids/)
  // 原子接口端点
  assert.match(apiSource, /\/admin\/users\/\$\{userId\}\/authorization/)
})

test('mocks use the same permission contract as the real backend', () => {
  assert.match(mockSource, /template_permission_ids/)
  assert.match(mockSource, /manual_permission_ids/)
  assert.match(mockSource, /effective_permission_ids/)
  assert.match(mockSource, /reason/)
  assert.match(mockSource, /\/api\/v1\/admin\/users\/:user_id\/authorization/)
})

test('mocks validate reason and permission ids like the real backend', () => {
  assert.match(mockSource, /调整原因不能为空/)
  assert.match(mockSource, /非法权限 ID/)
})

test('mocks enforce the same anti-escalation guards as the backend', () => {
  assert.match(mockSource, /不能修改自己的授权/)
  assert.match(mockSource, /只有超级管理员可以变更角色/)
  assert.match(mockSource, /超出自身权限范围/)
  assert.match(mockSource, /不能降级最后一个超级管理员/)
})
