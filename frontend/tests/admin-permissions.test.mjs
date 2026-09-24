import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

const viewSource = readFileSync(new URL('../src/views/PermissionManagementView.vue', import.meta.url), 'utf8')
const apiSource = readFileSync(new URL('../src/api/admin.ts', import.meta.url), 'utf8')
const mockSource = readFileSync(new URL('../src/mocks/handlers/admin.ts', import.meta.url), 'utf8')
const userMockSource = readFileSync(new URL('../src/mocks/handlers/user.ts', import.meta.url), 'utf8')

// 抓取形如 `builder: ['a', 'b']` 的角色权限数组字面量
function roleTemplate(source, role) {
  const match = source.match(new RegExp(`${role}:\\s*\\[[^\\]]*\\]`))
  return match ? match[0] : ''
}

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
  assert.match(mockSource, /只有超级管理员可以解锁超级管理员/)
})

test('mock logs role changes using the role captured before mutation', () => {
  // 先保存旧角色，再做变更判断：否则 role !== user.role 恒为 false
  const captureIndex = mockSource.indexOf('const previousRole = user.role')
  const mutateIndex = mockSource.indexOf('user.role = role')
  assert.ok(captureIndex >= 0, '必须先保存 previousRole')
  assert.ok(mutateIndex > captureIndex, 'previousRole 必须在 user.role 赋值之前捕获')
  assert.match(mockSource, /action:\s*role !== previousRole \?/)
})

test('the builder role template no longer inherits task:update', () => {
  // builder 模板不含 task:update：普通任务成员不能提交进度，模板里暴露它只会
  // 让 /me/permissions 出现一个调用即 403 的权限
  const adminBuilder = roleTemplate(mockSource, 'builder')
  assert.ok(adminBuilder, '未在权限管理 mock 中找到 builder 模板')
  assert.doesNotMatch(adminBuilder, /task:update/)

  // 变更范围最小化：operator 的平台级能力不受影响
  assert.match(roleTemplate(mockSource, 'operator'), /task:manage/)

  // /me/permissions 的 mock 权限表必须同步
  const userBuilder = roleTemplate(userMockSource, 'builder')
  assert.ok(userBuilder, '未在 user mock 中找到 builder 权限表')
  assert.doesNotMatch(userBuilder, /task:update/)
})

test('task:update stays in the permission catalogue so it can still be granted', () => {
  // 模板里移除不等于权限下线：它必须仍在权限全集里，否则授权接口会判为非法权限 ID
  const catalogue = mockSource.match(/const ALL_PERMISSIONS = \[[\s\S]*?\]/)?.[0] ?? ''
  assert.ok(catalogue, '未找到 ALL_PERMISSIONS')
  assert.match(catalogue, /'task:update'/)
})

test('the task:update checkbox is operable and saved as a manual permission', () => {
  // 复选框只因「模板继承」被锁定；builder 模板已不含 task:update ⇒ 可勾选
  assert.match(viewSource, /:disabled="selectedTemplateIds\.includes\(permission\.id\)"/)
  assert.match(viewSource, /:checked="isManualChecked\(permission\.id\)"/)
  // 取消锁定后仍会写入 editForm.manualPermissions（toggle 内部对模板项直接 return）
  assert.match(viewSource, /function toggleManualPermission\(permissionId: string, checked: boolean\)/)
  assert.match(viewSource, /if \(templateSet\.has\(permissionId\)\) return/)
  assert.match(viewSource, /editForm\.value\.manualPermissions = \[\.\.\.next\]/)
  // 保存时按「非模板项」提交，task:update 会出现在 manual_permission_ids 中
  assert.match(viewSource, /filter\(\(id\) => !templateSet\.has\(id\)\)/)
  assert.match(viewSource, /manual_permission_ids:\s*manualPermissionIds,/)
})

test('reopening the dialog restores the manual task:update grant from the server', () => {
  // 打开弹窗时以服务端 manual_permission_ids 为事实来源
  assert.match(viewSource, /editForm\.value\.manualPermissions = \[\.\.\.\(res\.data\.manual_permission_ids \?\? \[\]\)\]/)
  assert.match(viewSource, /applyPermissionDetail\(user, res\.data\)/)
  // mock 侧同样持久化手动授权，保证重新打开后读到的仍是已授权状态（而非模板继承）
  assert.match(mockSource, /manualPermissionsStore\[userId\] = next/)
  assert.match(mockSource, /saveManualPermissions\(manualPermissionsStore\)/)
  assert.match(mockSource, /manual_permission_ids: manual,/)
})
