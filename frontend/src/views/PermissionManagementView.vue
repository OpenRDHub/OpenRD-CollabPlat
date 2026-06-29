<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import {
  OrdButton,
  OrdDialog,
  OrdInput,
  OrdNavbar,
  OrdPagination,
  OrdSearchBox,
  OrdSelect,
  OrdTable,
  OrdTableCell,
  OrdTableHeader,
  OrdTableRow,
  useToast,
} from '@/components/ui'
import { adminApi } from '@/api/admin'
import type { AdminUser } from '@/api/admin'
import { useAuthStore } from '@/stores/auth'

type RoleKey = 'requester' | 'builder' | 'operator' | 'super_admin'
type RiskLevel = 'low' | 'medium' | 'high'

interface PermissionItem {
  id: string
  name: string
  group: string
  sensitive?: boolean
}

type PermissionMember = AdminUser & {
  manualPermissions: string[]
  permissionUpdatedAt: string
}

interface StoredPermissionState {
  role?: RoleKey
  manualPermissions: string[]
  updatedAt?: string
}

const router = useRouter()
const auth = useAuthStore()
const { show: showToast } = useToast()

const PAGE_SIZE = 4
const MANUAL_STORAGE_KEY = 'openrd_manual_permissions'

const users = ref<PermissionMember[]>([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const roleFilter = ref('all')
const currentPage = ref(1)
const editOpen = ref(false)
const selectedMemberId = ref('')
const inheritedSearch = ref('')

const editForm = ref({
  id: '',
  platform_id: '',
  nickname: '',
  role: 'requester' as RoleKey,
  position: '',
  manualPermissions: [] as string[],
})

const ROLE_LABEL: Record<RoleKey, string> = {
  requester: '需求者',
  builder: '共建者',
  operator: '运营管理员',
  super_admin: '超级管理员',
}

const ROLE_DESCRIPTION: Record<RoleKey, string> = {
  requester: '提交需求、查看需求进展与相关任务。',
  builder: '参与任务协作、更新任务进度与查看团队成员。',
  operator: '审核需求、推进转化、管理任务与团队协作。',
  super_admin: '拥有平台治理、用户、权限与审计能力。',
}

const ROLE_OPTIONS = [
  { value: 'all', label: '全部身份' },
  { value: 'requester', label: ROLE_LABEL.requester },
  { value: 'builder', label: ROLE_LABEL.builder },
  { value: 'operator', label: ROLE_LABEL.operator },
  { value: 'super_admin', label: ROLE_LABEL.super_admin },
]

const EDIT_ROLE_OPTIONS = ROLE_OPTIONS.filter((item) => item.value !== 'all')

const PERMISSIONS: PermissionItem[] = [
  { id: 'demand:view', name: '查看需求', group: '需求管理' },
  { id: 'demand:create', name: '提交需求', group: '需求管理' },
  { id: 'demand:reply', name: '回复需求', group: '需求管理' },
  { id: 'demand:convert', name: '需求转任务', group: '需求管理' },
  { id: 'demand:reject', name: '驳回需求', group: '需求管理' },
  { id: 'demand:link', name: '关联任务', group: '需求管理' },
  { id: 'demand:archive', name: '归档需求', group: '需求管理', sensitive: true },
  { id: 'task:view', name: '查看任务', group: '任务管理' },
  { id: 'task:join', name: '加入任务', group: '任务管理' },
  { id: 'task:update', name: '更新任务', group: '任务管理' },
  { id: 'task:manage', name: '任务管理', group: '任务管理' },
  { id: 'task:status', name: '调整状态', group: '任务管理', sensitive: true },
  { id: 'member:view', name: '查看成员', group: '成员协作' },
  { id: 'member:approve', name: '审核加入申请', group: '成员协作' },
  { id: 'member:invite', name: '邀请成员', group: '成员协作' },
  { id: 'member:manage', name: '管理成员', group: '成员协作', sensitive: true },
  { id: 'message:view', name: '查看消息', group: '消息通知' },
  { id: 'message:manage', name: '管理消息', group: '消息通知' },
  { id: 'file:upload', name: '上传文件', group: '文件管理' },
  { id: 'file:delete', name: '删除文件', group: '文件管理', sensitive: true },
  { id: 'admin:user', name: '用户管理', group: '平台管理', sensitive: true },
  { id: 'admin:role', name: '权限管理', group: '平台管理', sensitive: true },
  { id: 'admin:log', name: '系统日志', group: '平台管理', sensitive: true },
]

const ROLE_TEMPLATES: Record<RoleKey, string[]> = {
  requester: ['demand:create', 'demand:view', 'task:view', 'message:view', 'file:upload'],
  builder: ['demand:view', 'task:view', 'task:join', 'task:update', 'member:view', 'message:view', 'file:upload'],
  operator: [
    'demand:view',
    'demand:reply',
    'demand:convert',
    'demand:reject',
    'demand:link',
    'demand:archive',
    'task:view',
    'task:manage',
    'task:status',
    'member:view',
    'member:approve',
    'member:invite',
    'member:manage',
    'message:view',
    'message:manage',
    'file:upload',
    'file:delete',
  ],
  super_admin: PERMISSIONS.map((permission) => permission.id),
}

const permissionById = computed(() => Object.fromEntries(PERMISSIONS.map((permission) => [permission.id, permission])))
const canManagePermissions = computed(() => auth.hasPermission('admin:role'))
const roleLabel = computed(() => roleName(auth.userRole))
const selectedTemplateIds = computed(() => getTemplatePermissions(editForm.value.role))
const manualPermissionSet = computed(() => new Set(editForm.value.manualPermissions))
const permissionGroups = computed(() => [...new Set(PERMISSIONS.map((permission) => permission.group))])

const stats = computed(() => {
  const manualTotal = users.value.reduce((sum, user) => sum + user.manualPermissions.length, 0)
  const highRiskTotal = users.value.filter((user) => getRiskLevel(user).level === 'high').length
  return {
    total: total.value,
    roles: Object.keys(ROLE_LABEL).length,
    manual: manualTotal,
    highRisk: highRiskTotal,
  }
})

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))

function roleName(role?: string) {
  return ROLE_LABEL[role as RoleKey] ?? '平台用户'
}

function getPosition(user: AdminUser) {
  const fallbackUser = user as AdminUser & { occupation?: string; bio?: string }
  return user.position || fallbackUser.occupation || user.identity || '未填写岗位'
}

function getIntro(user: AdminUser) {
  const fallbackUser = user as AdminUser & { bio?: string }
  return user.intro || fallbackUser.bio || ''
}

function getTemplatePermissions(role: string) {
  return ROLE_TEMPLATES[role as RoleKey] ?? []
}

function getEffectivePermissions(member: PermissionMember | typeof editForm.value) {
  return [...new Set([...getTemplatePermissions(member.role), ...member.manualPermissions])]
}

function permissionName(id: string) {
  return permissionById.value[id]?.name ?? id
}

function isSensitive(id: string) {
  return Boolean(permissionById.value[id]?.sensitive)
}

function getRiskLevel(member: PermissionMember | typeof editForm.value): { text: string; level: RiskLevel } {
  const sensitiveCount = getEffectivePermissions(member).filter(isSensitive).length
  if (member.role === 'super_admin' || sensitiveCount >= 3) return { text: '高风险', level: 'high' }
  if (sensitiveCount > 0 || member.manualPermissions.length >= 2) return { text: '中风险', level: 'medium' }
  return { text: '低风险', level: 'low' }
}

function roleBadgeClass(role: string) {
  return `role-badge--${role === 'super_admin' ? 'super-admin' : role}`
}

function dateOnly(value?: string) {
  if (!value) return '-'
  if (value === '刚刚更新') return value
  return value.replace('T', ' ').slice(0, 16)
}

function loadStoredPermissionStates(): Record<string, StoredPermissionState> {
  try {
    const raw = localStorage.getItem(MANUAL_STORAGE_KEY)
    if (!raw) return {}

    const parsed = JSON.parse(raw) as Record<string, string[] | StoredPermissionState>
    return Object.fromEntries(
      Object.entries(parsed).map(([userId, value]) => [
        userId,
        Array.isArray(value) ? { manualPermissions: value } : value,
      ]),
    )
  } catch {
    return {}
  }
}

function persistPermissionState(userId: string, state: StoredPermissionState) {
  try {
    const all = loadStoredPermissionStates()
    all[userId] = state
    localStorage.setItem(MANUAL_STORAGE_KEY, JSON.stringify(all))
  } catch {
    // localStorage may be unavailable in private or restricted environments.
  }
}

function normalizeUser(user: AdminUser, stored: Record<string, StoredPermissionState>): PermissionMember {
  const storedState = stored[user.id]
  return {
    ...user,
    role: storedState?.role ?? user.role,
    position: getPosition(user),
    intro: getIntro(user),
    manualPermissions: storedState?.manualPermissions ?? [],
    permissionUpdatedAt: storedState?.updatedAt ?? user.created_at,
  }
}

function resetPage() {
  currentPage.value = 1
}

function goBack() {
  router.push('/workbench')
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

async function loadUsers() {
  loading.value = true
  try {
    const params: { keyword?: string; role?: string; page?: number; page_size?: number } = {
      page: currentPage.value,
      page_size: PAGE_SIZE,
    }
    if (keyword.value.trim()) params.keyword = keyword.value.trim()
    if (roleFilter.value !== 'all') params.role = roleFilter.value

    const res = await adminApi.getUsers(params)
    const stored = loadStoredPermissionStates()
    users.value = ((res.data.items as AdminUser[]) ?? []).map((user) => normalizeUser(user, stored))
    total.value = res.data.total ?? 0
  } catch {
    showToast({
      title: '加载失败',
      description: '无法获取成员权限列表，请确认当前账号拥有用户与权限管理授权。',
      variant: 'error',
    })
  } finally {
    loading.value = false
  }
}

function openEdit(user: PermissionMember) {
  if (!canManagePermissions.value) return

  selectedMemberId.value = user.id
  inheritedSearch.value = ''
  editForm.value = {
    id: user.id,
    platform_id: user.platform_id,
    nickname: user.nickname,
    role: (user.role as RoleKey) || 'requester',
    position: getPosition(user),
    manualPermissions: [...user.manualPermissions],
  }
  editOpen.value = true
}

function toggleManualPermission(permissionId: string, checked: boolean) {
  const templateSet = new Set(selectedTemplateIds.value)
  if (templateSet.has(permissionId)) return

  const next = new Set(editForm.value.manualPermissions)
  if (checked) next.add(permissionId)
  else next.delete(permissionId)
  editForm.value.manualPermissions = [...next]
}

function isManualChecked(permissionId: string) {
  return selectedTemplateIds.value.includes(permissionId) || manualPermissionSet.value.has(permissionId)
}

function groupPermissions(groupName: string) {
  const query = inheritedSearch.value.trim().toLowerCase()
  return PERMISSIONS.filter((permission) => {
    const inGroup = permission.group === groupName
    if (!inGroup) return false
    if (!query) return true
    return `${permission.id} ${permission.name} ${permission.group}`.toLowerCase().includes(query)
  })
}

async function handleSave() {
  if (!canManagePermissions.value || !editForm.value.id || saving.value) return

  saving.value = true
  try {
    const templateSet = new Set(selectedTemplateIds.value)
    const manualPermissions = editForm.value.manualPermissions.filter((id) => !templateSet.has(id))
    const effectivePermissions = [...new Set([...selectedTemplateIds.value, ...manualPermissions])]

    await adminApi.updateUser(editForm.value.id, { role: editForm.value.role })

    const updatedAt = '刚刚更新'
    persistPermissionState(editForm.value.id, {
      role: editForm.value.role,
      manualPermissions,
      updatedAt,
    })

    let remotePermissionSaved = true
    try {
      await adminApi.setUserPermissions(editForm.value.id, { permissions: effectivePermissions })
    } catch {
      remotePermissionSaved = false
    }

    const index = users.value.findIndex((user) => user.id === editForm.value.id)
    const currentUser = users.value[index]
    if (currentUser) {
      users.value.splice(index, 1, {
        ...currentUser,
        role: editForm.value.role,
        manualPermissions,
        permissionUpdatedAt: updatedAt,
      })
    }

    editOpen.value = false
    showToast({
      title: `${editForm.value.nickname} 的权限已保存`,
      description: remotePermissionSaved ? '刷新页面后仍会保留当前授权。' : '已在本地保留；后端手动权限接口暂未完成同步。',
      variant: 'success',
    })
  } catch {
    showToast({
      title: '保存失败',
      description: '权限更新未写入，请检查后端是否已开放用户权限保存接口。',
      variant: 'error',
    })
  } finally {
    saving.value = false
  }
}

watch([keyword, roleFilter], () => {
  resetPage()
  loadUsers()
})
watch(currentPage, loadUsers)

onMounted(loadUsers)
</script>

<template>
  <div class="page-root">
    <OrdNavbar>
      <template #brand>
        <RouterLink to="/hall" class="brand-row" aria-label="返回社区大厅">
          <div class="brand-mark">RD</div>
          <div>
            <div class="brand-name">OpenRD 开源社区协作平台</div>
            <span class="brand-caption">Rare Disease Open Collaboration</span>
          </div>
        </RouterLink>
      </template>

      <template #actions>
        <OrdButton class="nav-height-btn" variant="ghost" size="sm" @click="goBack">返回</OrdButton>
        <OrdButton class="nav-height-btn" variant="ghost" size="sm" @click="router.push('/hall')">前往大厅</OrdButton>
        <OrdButton class="nav-height-btn" variant="primary" size="sm" @click="router.push('/hall')">提需求</OrdButton>
        <OrdButton class="nav-height-btn" variant="ghost" size="sm" @click="router.push('/workbench')">工作台</OrdButton>
        <div class="profile-trigger">
          <button class="profile-button" type="button" aria-label="个人信息">
            <span class="profile-name">{{ auth.user?.nickname || '用户' }}</span>
          </button>
          <section class="profile-card" aria-label="个人信息卡片">
            <div class="profile-card-header">
              <div>
                <h3>{{ auth.user?.nickname || '用户' }}</h3>
                <p>{{ roleLabel }} · {{ canManagePermissions ? '可管理角色权限' : '仅可查看授权范围' }}</p>
              </div>
            </div>
            <div class="profile-meta">
              <div><span>当前身份</span><strong>{{ roleLabel }}</strong></div>
              <div><span>权限管理</span><strong>{{ canManagePermissions ? '已授权' : '未授权' }}</strong></div>
            </div>
            <button class="logout-link" type="button" @click="handleLogout">退出登录</button>
          </section>
        </div>
      </template>
    </OrdNavbar>

    <main class="page-shell">
      <section class="permission-frame">
        <section class="hero-card" aria-label="权限管理概览">
          <div>
            <p class="eyebrow">Permission Management</p>
            <h1>角色模板与成员授权</h1>
            <p class="hero-copy">
              按需求者、共建者、运营管理员、超级管理员四类身份展示权限边界；成员先继承身份模板，再按专项协作需要追加个别权限。
            </p>
          </div>
          <aside class="hero-aside" aria-label="权限模板概览">
            <div v-for="role in EDIT_ROLE_OPTIONS" :key="role.value" class="template-pill">
              <span>{{ role.label }}模板</span>
              <strong>{{ getTemplatePermissions(role.value).length }} 项</strong>
            </div>
          </aside>
        </section>

        <section class="summary-grid" aria-label="权限概览">
          <article class="summary-card">
            <p class="summary-label">管理成员</p>
            <p class="summary-value">{{ stats.total }}</p>
            <p class="summary-desc">纳入权限管理的成员账号</p>
          </article>
          <article class="summary-card">
            <p class="summary-label">角色模板</p>
            <p class="summary-value">{{ stats.roles }}</p>
            <p class="summary-desc">需求者 / 共建者 / 运管 / 超管</p>
          </article>
          <article class="summary-card">
            <p class="summary-label">手动授权</p>
            <p class="summary-value">{{ stats.manual }}</p>
            <p class="summary-desc">模板外额外添加的权限项</p>
          </article>
          <article class="summary-card">
            <p class="summary-label">高敏权限</p>
            <p class="summary-value">{{ stats.highRisk }}</p>
            <p class="summary-desc">包含管理、删除、审计等能力</p>
          </article>
        </section>

        <section class="table-card" aria-label="权限成员列表">
          <div class="table-toolbar">
            <div>
              <h2 class="toolbar-title">成员权限列表</h2>
              <p class="toolbar-note">每位成员先继承身份模板，再通过弹窗追加个别权限。</p>
            </div>
            <div class="toolbar-actions">
              <OrdSelect v-model="roleFilter" :options="ROLE_OPTIONS" placeholder="全部身份" />
              <OrdSearchBox v-model="keyword" placeholder="搜索平台号、昵称、岗位" width="260px" />
            </div>
          </div>

          <div class="table-scroll">
            <OrdTable>
              <OrdTableHeader>
                <OrdTableCell header>成员</OrdTableCell>
                <OrdTableCell header>身份模板</OrdTableCell>
                <OrdTableCell header>岗位</OrdTableCell>
                <OrdTableCell header>模板权限</OrdTableCell>
                <OrdTableCell header>手动权限</OrdTableCell>
                <OrdTableCell header>风险等级</OrdTableCell>
                <OrdTableCell header>更新时间</OrdTableCell>
                <OrdTableCell header>操作</OrdTableCell>
              </OrdTableHeader>

              <template v-if="loading">
                <OrdTableRow>
                  <OrdTableCell :colspan="8" class="empty-state">加载中...</OrdTableCell>
                </OrdTableRow>
              </template>
              <template v-else-if="users.length === 0">
                <OrdTableRow>
                  <OrdTableCell :colspan="8" class="empty-state">暂无匹配成员，请调整筛选条件。</OrdTableCell>
                </OrdTableRow>
              </template>
              <template v-else>
                <OrdTableRow v-for="user in users" :key="user.id">
                  <OrdTableCell>
                    <div class="member-cell">
                      <div>
                        <div class="primary-text">{{ user.nickname || '未命名用户' }}</div>
                        <span class="sub-text">{{ user.platform_id || user.id }}</span>
                      </div>
                    </div>
                  </OrdTableCell>
                  <OrdTableCell>
                    <span class="role-badge" :class="roleBadgeClass(user.role)">
                      {{ roleName(user.role) }}
                    </span>
                  </OrdTableCell>
                  <OrdTableCell>{{ getPosition(user) }}</OrdTableCell>
                  <OrdTableCell>
                    <span class="count-badge">{{ getTemplatePermissions(user.role).length }} 项</span>
                  </OrdTableCell>
                  <OrdTableCell>
                    <div class="manual-list">
                      <span v-if="user.manualPermissions.length === 0" class="permission-tag permission-tag--empty">无额外权限</span>
                      <span v-for="permission in user.manualPermissions" v-else :key="permission" class="permission-tag">
                        {{ permissionName(permission) }}
                      </span>
                    </div>
                  </OrdTableCell>
                  <OrdTableCell>
                    <span class="risk-badge" :class="`risk-badge--${getRiskLevel(user).level}`">
                      {{ getRiskLevel(user).text }}
                    </span>
                  </OrdTableCell>
                  <OrdTableCell>{{ dateOnly(user.permissionUpdatedAt || user.created_at) }}</OrdTableCell>
                  <OrdTableCell>
                    <OrdButton
                      variant="primary"
                      size="sm"
                      :disabled="!canManagePermissions"
                      @click="openEdit(user)"
                    >
                      编辑权限
                    </OrdButton>
                  </OrdTableCell>
                </OrdTableRow>
              </template>
            </OrdTable>
          </div>

          <div v-if="total > 0" class="pagination" aria-label="分页导航">
            <span class="pagination-summary">共 {{ total }} 位成员，第 {{ currentPage }} / {{ totalPages }} 页</span>
            <OrdPagination v-model:current-page="currentPage" :total="total" :page-size="PAGE_SIZE" />
          </div>
        </section>
      </section>
    </main>

    <OrdDialog
      v-model:open="editOpen"
      title="编辑成员权限"
      description="角色模板权限会自动继承并锁定，勾选下方权限即可进行个别追加授权。"
    >
      <template #trigger></template>

      <div class="permission-form">
        <div class="form-grid">
          <div class="form-field">
            <label>平台号</label>
            <OrdInput :model-value="editForm.platform_id" disabled />
          </div>
          <div class="form-field">
            <label>昵称</label>
            <OrdInput :model-value="editForm.nickname" disabled />
          </div>
          <div class="form-field">
            <label>角色权限模板</label>
            <OrdSelect v-model="editForm.role" :options="EDIT_ROLE_OPTIONS" />
          </div>
        </div>

        <div class="editor-toolbar">
          <div>
            <strong>{{ ROLE_LABEL[editForm.role] }}</strong>
            <span>{{ ROLE_DESCRIPTION[editForm.role] }}</span>
          </div>
          <OrdInput v-model="inheritedSearch" placeholder="搜索权限项" />
        </div>

        <div class="permission-editor">
          <section class="template-panel" aria-label="模板继承权限">
            <div class="panel-head">
              <h3>模板继承权限</h3>
              <span>{{ selectedTemplateIds.length }} 项</span>
            </div>
            <div class="inherited-list">
              <div v-for="permissionId in selectedTemplateIds" :key="permissionId" class="inherited-item">
                <span>{{ permissionName(permissionId) }}</span>
                <span class="lock-mark">模板锁定</span>
              </div>
            </div>
          </section>

          <section class="manual-panel" aria-label="手动追加权限">
            <div class="panel-head">
              <h3>手动追加权限</h3>
              <span>已追加 {{ editForm.manualPermissions.length }} 项</span>
            </div>
            <div class="permission-groups">
              <section v-for="group in permissionGroups" :key="group" class="group-card">
                <p class="group-title">{{ group }}</p>
                <div class="checkbox-grid">
                  <label
                    v-for="permission in groupPermissions(group)"
                    :key="permission.id"
                    class="permission-check"
                    :class="{ 'is-inherited': selectedTemplateIds.includes(permission.id) }"
                  >
                    <input
                      type="checkbox"
                      :checked="isManualChecked(permission.id)"
                      :disabled="selectedTemplateIds.includes(permission.id)"
                      @change="toggleManualPermission(permission.id, ($event.target as HTMLInputElement).checked)"
                    />
                    <span>{{ permission.name }}</span>
                  </label>
                </div>
              </section>
            </div>
          </section>
        </div>

        <div class="form-message">
          保存后该成员将拥有 {{ getEffectivePermissions(editForm).length }} 项有效权限，当前评估为
          {{ getRiskLevel(editForm).text }}。
        </div>
      </div>

      <template #footer>
        <OrdButton variant="ghost" @click="editOpen = false">取消</OrdButton>
        <OrdButton variant="primary" :loading="saving" @click="handleSave">保存权限</OrdButton>
      </template>
    </OrdDialog>
  </div>
</template>

<style scoped>
.page-root {
  min-height: 100vh;
}

.brand-row {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: inherit;
  text-decoration: none;
}

.brand-mark {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  color: var(--ord-color-white);
  background: var(--ord-color-blue);
  border-radius: var(--ord-radius-sm);
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0;
}

.brand-name {
  color: var(--ord-color-black);
  font-size: 20px;
  font-weight: 600;
  line-height: 1.15;
}

.brand-caption {
  display: block;
  margin-top: 3px;
  color: var(--ord-color-gray-500);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1.2px;
  text-transform: uppercase;
}

:deep(.ord-navbar) {
  position: fixed;
  inset: 0 0 auto;
  z-index: 20;
  min-height: 76px;
  padding: 0 32px;
  background: rgba(255, 255, 255, 0.94);
  border-bottom: 1px solid rgba(216, 216, 216, 0.86);
  box-shadow: 0 18px 40px rgba(8, 8, 8, 0.08);
  backdrop-filter: blur(16px);
}

:deep(.ord-navbar__inner) {
  width: min(1460px, 100%);
  min-height: 76px;
  margin: 0 auto;
  padding: 16px 0;
}

:deep(.ord-navbar__actions) {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-height-btn {
  height: 42px;
}

.profile-trigger {
  position: relative;
}

.profile-button {
  height: 42px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 0 10px;
  color: var(--ord-color-black);
  background: var(--ord-color-white);
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-sm);
  cursor: pointer;
  font: inherit;
}

.profile-name {
  font-size: 14px;
  font-weight: 600;
}

.profile-card {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  z-index: 200;
  width: 260px;
  padding: 16px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-4px);
  background: var(--ord-color-white);
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  transition: opacity 160ms ease, transform 160ms ease, visibility 160ms ease;
}

.profile-trigger:hover .profile-card,
.profile-trigger:focus-within .profile-card {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.profile-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 14px;
  border-bottom: 1px solid #ececec;
}

.profile-card h3 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
}

.profile-card p {
  margin: 4px 0 0;
  color: var(--ord-color-gray-500);
  font-size: 13px;
}

.profile-meta {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-top: 14px;
}

.profile-meta div {
  padding: 10px;
  background: rgba(20, 110, 245, 0.06);
  border: 1px solid rgba(20, 110, 245, 0.12);
  border-radius: var(--ord-radius-sm);
}

.profile-meta span {
  display: block;
  color: var(--ord-color-gray-500);
  font-size: 11px;
}

.profile-meta strong {
  display: block;
  margin-top: 4px;
  color: var(--ord-color-black);
  font-size: 15px;
  font-weight: 600;
}

.logout-link {
  width: 100%;
  min-height: 36px;
  margin-top: 12px;
  color: var(--ord-color-red);
  background: rgba(238, 29, 54, 0.08);
  border: 1px solid rgba(238, 29, 54, 0.18);
  border-radius: var(--ord-radius-sm);
  font-size: 13px;
  font-weight: 650;
  cursor: pointer;
}

.page-shell {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 96px 32px 32px;
  background:
    radial-gradient(circle at 12% 12%, rgba(20, 110, 245, 0.08), transparent 28%),
    radial-gradient(circle at 86% 18%, rgba(122, 61, 255, 0.06), transparent 24%),
    radial-gradient(circle at 80% 86%, rgba(255, 174, 19, 0.052), transparent 28%),
    linear-gradient(135deg, #ffffff 0%, #f7f9ff 100%);
}

.permission-frame {
  position: relative;
  width: min(1460px, 100%);
  display: grid;
  gap: 18px;
}

.permission-frame::before,
.permission-frame::after {
  content: "";
  position: absolute;
  z-index: 0;
  border: 1px solid rgba(216, 216, 216, 0.7);
  background: rgba(255, 255, 255, 0.45);
  transform: rotate(-2deg);
  pointer-events: none;
}

.permission-frame::before {
  width: 180px;
  height: 86px;
  top: 96px;
  right: 42px;
}

.permission-frame::after {
  width: 108px;
  height: 108px;
  right: 214px;
  bottom: 56px;
  transform: rotate(4deg);
}

.hero-card,
.summary-card,
.table-card {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(216, 216, 216, 0.86);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
}

.hero-card {
  overflow: hidden;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 24px;
  padding: 28px;
}

.hero-card::after {
  content: "";
  position: absolute;
  right: -56px;
  top: -56px;
  width: 220px;
  height: 220px;
  background:
    linear-gradient(90deg, rgba(20, 110, 245, 0.16) 1px, transparent 1px),
    linear-gradient(0deg, rgba(20, 110, 245, 0.16) 1px, transparent 1px);
  background-size: 22px 22px;
  transform: rotate(8deg);
  pointer-events: none;
}

.eyebrow,
.summary-label {
  margin: 0;
  color: var(--ord-color-blue);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.4px;
  text-transform: uppercase;
}

h1 {
  margin: 10px 0 0;
  color: var(--ord-color-black);
  font-size: clamp(34px, 4vw, 56px);
  font-weight: 600;
  line-height: 1.04;
}

.hero-copy {
  max-width: 700px;
  margin: 16px 0 0;
  color: var(--ord-color-gray-700);
  font-size: 16px;
  line-height: 1.65;
}

.hero-aside {
  position: relative;
  z-index: 1;
  width: 286px;
  align-self: stretch;
  display: grid;
  gap: 10px;
  padding: 18px;
  color: var(--ord-color-white);
  background: var(--ord-color-black);
  border-radius: var(--ord-radius-md);
}

.template-pill {
  min-height: 42px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 0 12px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: var(--ord-radius-sm);
  font-size: 13px;
}

.template-pill strong {
  font-size: 14px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.summary-card {
  min-height: 106px;
  padding: 18px;
  border-top: 4px solid var(--ord-color-blue);
}

.summary-card:nth-child(2) {
  border-top-color: var(--ord-color-green);
}

.summary-card:nth-child(3) {
  border-top-color: var(--ord-color-purple);
}

.summary-card:nth-child(4) {
  border-top-color: var(--ord-color-orange);
}

.summary-label {
  color: var(--ord-color-gray-500);
}

.summary-value {
  margin: 12px 0 0;
  color: var(--ord-color-black);
  font-size: 34px;
  font-weight: 600;
  line-height: 1;
}

.summary-desc {
  margin: 10px 0 0;
  color: var(--ord-color-gray-500);
  font-size: 13px;
  line-height: 1.45;
}

.table-card {
  overflow: hidden;
}

.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px;
  border-bottom: 1px solid #ececec;
}

.toolbar-title {
  margin: 0;
  color: var(--ord-color-black);
  font-size: 22px;
  font-weight: 600;
  line-height: 1.2;
}

.toolbar-note {
  margin: 7px 0 0;
  color: var(--ord-color-gray-500);
  font-size: 13px;
  line-height: 1.45;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-scroll {
  overflow-x: auto;
}

.table-scroll :deep(.ord-table) {
  border: 0;
  border-radius: 0;
}

.table-scroll :deep(.ord-table__inner) {
  min-width: 1220px;
}

.table-scroll :deep(th),
.table-scroll :deep(td) {
  padding: 14px 12px;
  border-bottom: 1px solid #ececec;
  vertical-align: middle;
}

.member-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.primary-text {
  color: var(--ord-color-black);
  font-size: 14px;
  font-weight: 700;
}

.sub-text {
  display: block;
  margin-top: 4px;
  color: var(--ord-color-gray-500);
  font-size: 12px;
}

.role-badge,
.count-badge,
.risk-badge,
.permission-tag {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: var(--ord-radius-sm);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.role-badge {
  color: var(--ord-color-blue);
  background: rgba(20, 110, 245, 0.08);
}

.role-badge--builder {
  color: #009e19;
  background: rgba(0, 215, 34, 0.12);
}

.role-badge--operator {
  color: #b27600;
  background: rgba(255, 174, 19, 0.16);
}

.role-badge--super-admin {
  color: var(--ord-color-purple);
  background: rgba(122, 61, 255, 0.1);
}

.count-badge {
  color: var(--ord-color-black);
  background: #f4f4f4;
}

.manual-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-width: 280px;
}

.permission-tag {
  min-height: 24px;
  padding: 0 8px;
  color: var(--ord-color-blue);
  background: rgba(20, 110, 245, 0.08);
  font-size: 11px;
}

.permission-tag--empty {
  color: var(--ord-color-gray-500);
  background: #f4f4f4;
}

.risk-badge--low {
  color: #009e19;
  background: rgba(0, 215, 34, 0.12);
}

.risk-badge--medium {
  color: #b27600;
  background: rgba(255, 174, 19, 0.16);
}

.risk-badge--high {
  color: var(--ord-color-red);
  background: rgba(238, 29, 54, 0.1);
}

.empty-state {
  padding: 34px;
  color: var(--ord-color-gray-500);
  text-align: center;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 18px;
  border-top: 1px solid #ececec;
  background: rgba(255, 255, 255, 0.92);
}

.pagination-summary {
  color: var(--ord-color-gray-500);
  font-size: 13px;
  font-weight: 600;
}

:global(.ord-dialog__content) {
  width: min(960px, calc(100vw - 48px));
  padding: 0;
}

:global(.ord-dialog__title) {
  padding: 22px 24px 0;
  font-size: 26px;
}

:global(.ord-dialog__description) {
  padding: 0 24px;
  margin-bottom: 0;
}

:global(.ord-dialog__footer) {
  padding: 0 24px 24px;
}

.permission-form {
  padding: 22px 24px 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  margin-bottom: 18px;
}

.form-field label {
  display: block;
  margin-bottom: 7px;
  color: var(--ord-color-gray-500);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
  padding: 12px;
  background: rgba(20, 110, 245, 0.045);
  border: 1px solid rgba(20, 110, 245, 0.14);
  border-radius: var(--ord-radius-sm);
}

.editor-toolbar strong {
  display: block;
  margin-bottom: 4px;
  color: var(--ord-color-black);
  font-size: 15px;
}

.editor-toolbar span {
  color: var(--ord-color-gray-500);
  font-size: 13px;
}

.editor-toolbar :deep(.ord-input) {
  width: 240px;
}

.permission-editor {
  display: grid;
  grid-template-columns: 0.9fr 1.3fr;
  gap: 16px;
}

.template-panel,
.manual-panel {
  overflow: hidden;
  background: var(--ord-color-white);
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-md);
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px;
  border-bottom: 1px solid #ececec;
}

.panel-head h3 {
  margin: 0;
  color: var(--ord-color-black);
  font-size: 16px;
  font-weight: 600;
}

.panel-head span {
  color: var(--ord-color-gray-500);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.inherited-list,
.permission-groups {
  display: grid;
  gap: 10px;
  max-height: 360px;
  overflow: auto;
  padding: 14px;
}

.inherited-item {
  min-height: 38px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 0 10px;
  color: var(--ord-color-gray-700);
  background: #f8f8f8;
  border: 1px solid #ededed;
  border-radius: var(--ord-radius-sm);
  font-size: 13px;
}

.lock-mark {
  color: var(--ord-color-gray-300);
  font-size: 12px;
  font-weight: 700;
}

.group-card {
  display: grid;
  gap: 10px;
  padding: 12px;
  border: 1px solid #ededed;
  border-radius: 6px;
}

.group-title {
  margin: 0;
  color: var(--ord-color-black);
  font-size: 13px;
  font-weight: 700;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.permission-check {
  min-height: 36px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 10px;
  color: var(--ord-color-gray-700);
  background: #ffffff;
  border: 1px solid #ececec;
  border-radius: var(--ord-radius-sm);
  font-size: 13px;
  cursor: pointer;
}

.permission-check.is-inherited {
  color: var(--ord-color-gray-500);
  background: #f7f7f7;
  cursor: not-allowed;
}

.permission-check input {
  width: 15px;
  height: 15px;
  accent-color: var(--ord-color-blue);
}

.form-message {
  margin: 16px 0 0;
  padding: 12px 0 0;
  color: var(--ord-color-gray-500);
  border-top: 1px solid #ececec;
  font-size: 13px;
  line-height: 1.5;
}

@media (max-width: 992px) {
  .page-shell {
    padding: 96px 20px 32px;
  }

  .hero-card,
  .table-toolbar,
  .editor-toolbar {
    grid-template-columns: 1fr;
    align-items: stretch;
    flex-direction: column;
  }

  .hero-aside,
  .editor-toolbar :deep(.ord-input) {
    width: 100%;
  }

  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .permission-editor,
  .form-grid {
    grid-template-columns: 1fr;
  }

  .toolbar-actions {
    flex-wrap: wrap;
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  :deep(.ord-navbar) {
    padding: 0 16px;
  }

  :deep(.ord-navbar__actions) {
    gap: 6px;
  }

  .brand-caption {
    display: none;
  }

  .page-shell {
    padding: 96px 16px 32px;
  }

  .summary-grid,
  .checkbox-grid {
    grid-template-columns: 1fr;
  }

  .pagination {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
