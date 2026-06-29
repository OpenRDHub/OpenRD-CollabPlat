<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import {
  OrdAvatar,
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

const router = useRouter()
const auth = useAuthStore()
const { show: showToast } = useToast()

const PAGE_SIZE = 8

// ── 权限定义（与后端 ALL_PERMISSIONS 对齐）──────────────────────────
const ALL_PERMISSION_DEFS = [
  { id: 'demand:view',    name: '查看需求',     group: '需求管理' },
  { id: 'demand:create',  name: '提交需求',     group: '需求管理' },
  { id: 'demand:reply',   name: '回复需求',     group: '需求管理' },
  { id: 'demand:convert', name: '需求转工单',   group: '需求管理' },
  { id: 'demand:reject',  name: '拒绝需求',     group: '需求管理' },
  { id: 'demand:link',    name: '关联需求',     group: '需求管理' },
  { id: 'task:view',      name: '查看任务',     group: '任务管理' },
  { id: 'task:join',      name: '加入任务',     group: '任务管理' },
  { id: 'task:update',    name: '更新任务',     group: '任务管理' },
  { id: 'task:manage',    name: '管理任务',     group: '任务管理' },
  { id: 'task:assign',    name: '分配任务',     group: '任务管理' },
  { id: 'member:view',    name: '查看成员',     group: '成员协作' },
  { id: 'member:approve', name: '审核加入申请', group: '成员协作' },
  { id: 'member:invite',  name: '邀请成员',     group: '成员协作' },
  { id: 'message:view',   name: '查看消息',     group: '消息通知' },
  { id: 'message:manage', name: '管理消息',     group: '消息通知' },
  { id: 'admin:demands',  name: '需求管理后台', group: '平台管理', sensitive: true },
  { id: 'admin:tasks',    name: '任务管理后台', group: '平台管理', sensitive: true },
  { id: 'admin:users',    name: '用户管理',     group: '平台管理', sensitive: true },
  { id: 'admin:roles',    name: '权限管理',     group: '平台管理', sensitive: true },
  { id: 'admin:logs',     name: '查看系统日志', group: '平台管理', sensitive: true },
] as const

type PermId = (typeof ALL_PERMISSION_DEFS)[number]['id']

const ROLE_TEMPLATE_PERMISSIONS: Record<string, PermId[]> = {
  requester:   ['demand:create', 'demand:view', 'task:view', 'message:view'],
  builder:     ['demand:view', 'task:view', 'task:join', 'task:update', 'member:view', 'message:view'],
  operator:    [
    'demand:view', 'demand:reply', 'demand:convert', 'demand:reject', 'demand:link',
    'task:view', 'task:manage', 'task:assign', 'member:view', 'member:approve', 'member:invite',
    'message:view', 'message:manage', 'admin:demands', 'admin:tasks',
  ],
  super_admin: ALL_PERMISSION_DEFS.map((p) => p.id) as PermId[],
}

const ROLE_LABEL: Record<string, string> = {
  requester:   '需求者',
  builder:     '共建者',
  operator:    '运营管理员',
  super_admin: '超级管理员',
}

const ROLE_CLASS: Record<string, string> = {
  requester:   'requester',
  builder:     'builder',
  operator:    'operator',
  super_admin: 'superAdmin',
}

const roleFilterOptions = [
  { value: 'all',         label: '全部身份' },
  { value: 'requester',   label: '需求者' },
  { value: 'builder',     label: '共建者' },
  { value: 'operator',    label: '运营管理员' },
  { value: 'super_admin', label: '超级管理员' },
]

const roleEditOptions = [
  { value: 'requester',   label: '需求者' },
  { value: 'builder',     label: '共建者' },
  { value: 'operator',    label: '运营管理员' },
  { value: 'super_admin', label: '超级管理员' },
]

// ── 状态 ─────────────────────────────────────────────────────────────
const users = ref<AdminUser[]>([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const roleFilter = ref('all')
const currentPage = ref(1)
const editOpen = ref(false)

const editUserId    = ref('')
const editPlatformId = ref('')
const editNickname  = ref('')
const editRole      = ref('requester')
const editManual    = ref<string[]>([])

const canManage = computed(() => auth.hasPermission('admin:roles'))

// ── 统计 ─────────────────────────────────────────────────────────────
const templateCounts: Record<string, number> = Object.fromEntries(
  Object.entries(ROLE_TEMPLATE_PERMISSIONS).map(([r, p]) => [r, p.length])
)

type UserWithManual = AdminUser & { manual_permissions: string[] }
const enrichedUsers = ref<UserWithManual[]>([])

const stats = computed(() => {
  const list = enrichedUsers.value
  const manualTotal = list.reduce((s, u) => s + u.manual_permissions.length, 0)
  const sensitiveCount = list.filter((u) => getRiskClass(u) === 'high').length
  return { total: list.length, manualTotal, sensitiveCount }
})

function getTemplatePerms(role: string): PermId[] {
  return (ROLE_TEMPLATE_PERMISSIONS[role] ?? []) as PermId[]
}

function getRiskClass(u: UserWithManual): 'low' | 'medium' | 'high' {
  if (u.role === 'super_admin') return 'high'
  const effective = [...new Set([...getTemplatePerms(u.role), ...u.manual_permissions])]
  const sens = effective.filter((id) => ALL_PERMISSION_DEFS.find((p) => p.id === id && (p as any).sensitive)).length
  if (sens >= 3) return 'high'
  if (sens > 0 || u.manual_permissions.length >= 2) return 'medium'
  return 'low'
}

function getRiskLabel(c: 'low' | 'medium' | 'high') {
  return { low: '低风险', medium: '中风险', high: '高风险' }[c]
}

function getPermName(id: string) {
  return ALL_PERMISSION_DEFS.find((p) => p.id === id)?.name ?? id
}

// ── 分页过滤 ──────────────────────────────────────────────────────────
const filtered = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  const rf = roleFilter.value
  return enrichedUsers.value.filter((u) => {
    const matchRole = rf === 'all' || u.role === rf
    const matchKw = !kw || [u.platform_id, u.nickname, u.position, u.role].join(' ').toLowerCase().includes(kw)
    return matchRole && matchKw
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / PAGE_SIZE)))

const paged = computed(() => {
  const s = (currentPage.value - 1) * PAGE_SIZE
  return filtered.value.slice(s, s + PAGE_SIZE)
})

// ── 弹窗相关 ─────────────────────────────────────────────────────────
const templatePermsForEdit = computed(() => getTemplatePerms(editRole.value))

const permGroups = computed(() => {
  const groups: Record<string, typeof ALL_PERMISSION_DEFS[number][]> = {}
  for (const p of ALL_PERMISSION_DEFS) {
    if (!groups[p.group]) groups[p.group] = []
    groups[p.group].push(p)
  }
  return Object.entries(groups).map(([name, items]) => ({ name, items }))
})

function isInherited(permId: string) {
  return templatePermsForEdit.value.includes(permId as PermId)
}

function isChecked(permId: string) {
  return isInherited(permId) || editManual.value.includes(permId)
}

function toggleManual(permId: string, checked: boolean) {
  if (isInherited(permId)) return
  if (checked) {
    if (!editManual.value.includes(permId)) editManual.value.push(permId)
  } else {
    editManual.value = editManual.value.filter((id) => id !== permId)
  }
}

const manualCountForEdit = computed(() =>
  editManual.value.filter((id) => !isInherited(id)).length
)

const effectiveCountForEdit = computed(() =>
  new Set([...templatePermsForEdit.value, ...editManual.value]).size
)

// 当角色模板变化时，移除已被模板覆盖的手动权限
watch(editRole, () => {
  const tmpl = getTemplatePerms(editRole.value)
  editManual.value = editManual.value.filter((id) => !tmpl.includes(id as PermId))
})

async function openEdit(u: UserWithManual) {
  if (!canManage.value) return
  editUserId.value    = u.id
  editPlatformId.value = u.platform_id
  editNickname.value  = u.nickname
  editRole.value      = u.role
  editManual.value    = [...u.manual_permissions]
  editOpen.value = true
}

async function handleSave() {
  if (!canManage.value) return
  saving.value = true
  try {
    await adminApi.setUserPermissions(editUserId.value, {
      role: editRole.value,
      manual_permissions: editManual.value.filter((id) => !isInherited(id)),
    })
    // 同步本地
    const u = enrichedUsers.value.find((x) => x.id === editUserId.value)
    if (u) {
      u.role = editRole.value
      u.manual_permissions = editManual.value.filter((id) => !getTemplatePerms(editRole.value).includes(id as PermId))
    }
    editOpen.value = false
    showToast({ title: `${editNickname.value} 的权限已更新`, variant: 'success' })
  } catch {
    showToast({ title: '保存失败', description: '请确认当前账号具备权限管理能力。', variant: 'error' })
  } finally {
    saving.value = false
  }
}

// ── 初始化 ───────────────────────────────────────────────────────────
async function loadUsers() {
  loading.value = true
  try {
    const res = await adminApi.getUsers({ page: 1, page_size: 200 })
    const list = (res.data.items ?? []) as AdminUser[]
    // 拉取每个用户的手动权限
    const enriched = await Promise.all(
      list.map(async (u) => {
        try {
          const r = await adminApi.getUserPermissions(u.id)
          return { ...u, manual_permissions: r.data.manual_permissions ?? [] } as UserWithManual
        } catch {
          return { ...u, manual_permissions: [] } as UserWithManual
        }
      })
    )
    enrichedUsers.value = enriched
    total.value = enriched.length
  } catch {
    showToast({ title: '加载失败', description: '无法获取成员列表，请稍后重试。', variant: 'error' })
  } finally {
    loading.value = false
  }
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

watch([keyword, roleFilter], () => { currentPage.value = 1 })
watch(totalPages, (p) => { if (currentPage.value > p) currentPage.value = p })

onMounted(loadUsers)
</script>

<template>
  <div class="page-root">
    <OrdNavbar>
      <template #brand>
        <RouterLink to="/hall" class="brand-row" aria-label="返回社区主页">
          <div class="brand-mark">RD</div>
          <div>
            <div class="brand-name">OpenRD 开源社区协作平台</div>
            <span class="brand-caption">Rare Disease Open Collaboration</span>
          </div>
        </RouterLink>
      </template>
      <template #actions>
        <OrdButton class="nav-height-btn" variant="ghost" size="sm" @click="router.back()">返回</OrdButton>
        <OrdButton class="nav-height-btn" variant="ghost" size="sm" @click="router.push('/hall')">前往大厅</OrdButton>
        <OrdButton class="nav-height-btn" variant="primary" size="sm" @click="router.push('/hall')">提需求</OrdButton>
        <OrdButton class="nav-height-btn" variant="ghost" size="sm" @click="router.push('/workbench')">工作台</OrdButton>
        <div class="profile-trigger">
          <button class="profile-button" type="button" aria-label="个人信息">
            <OrdAvatar :name="auth.user?.nickname || '用户'" size="sm" />
            <span class="profile-name">{{ auth.user?.nickname || '用户' }}</span>
          </button>
          <section class="profile-card" aria-label="个人信息卡片">
            <div class="profile-card-header">
              <OrdAvatar :name="auth.user?.nickname || '用户'" size="sm" />
              <div>
                <h3>{{ auth.user?.nickname || '用户' }}</h3>
                <p>{{ ROLE_LABEL[auth.userRole] ?? '平台用户' }} · {{ canManage ? '可管理权限' : '仅查看' }}</p>
              </div>
            </div>
            <div class="profile-meta">
              <div><span>当前角色</span><strong>{{ ROLE_LABEL[auth.userRole] ?? '-' }}</strong></div>
              <div><span>权限管理</span><strong>{{ canManage ? '已授权' : '未授权' }}</strong></div>
            </div>
            <button class="logout-link" type="button" @click="handleLogout">退出登录</button>
          </section>
        </div>
      </template>
    </OrdNavbar>

    <main class="page-shell">
      <section class="permission-frame" aria-labelledby="pageTitle">
        <div class="deco-rect deco-rect--a" aria-hidden="true"></div>
        <div class="deco-rect deco-rect--b" aria-hidden="true"></div>

        <div class="hero-card">
          <div>
            <p class="eyebrow">Role Template + Manual Grant</p>
            <h1 id="pageTitle">权限管理</h1>
            <p class="hero-copy">在角色权限模板的基础上，针对个别成员手动追加权限，适合临时协作、专项审核、跨角色支援等需要精细化授权的场景。</p>
          </div>
          <aside class="hero-aside" aria-label="权限模板概览">
            <div class="template-pill"><span>需求者模板</span><strong>{{ templateCounts.requester }} 项</strong></div>
            <div class="template-pill"><span>共建者模板</span><strong>{{ templateCounts.builder }} 项</strong></div>
            <div class="template-pill"><span>运营管理员模板</span><strong>{{ templateCounts.operator }} 项</strong></div>
            <div class="template-pill"><span>超级管理员模板</span><strong>{{ templateCounts.super_admin }} 项</strong></div>
          </aside>
        </div>

        <div class="summary-grid" aria-label="权限概览">
          <article class="summary-card" style="--accent: var(--ord-color-blue)">
            <p class="summary-label">管理成员</p>
            <p class="summary-value">{{ stats.total }}</p>
            <p class="summary-desc">纳入权限管理的平台成员</p>
          </article>
          <article class="summary-card" style="--accent: var(--ord-color-green)">
            <p class="summary-label">角色模板</p>
            <p class="summary-value">4</p>
            <p class="summary-desc">需求者 / 共建者 / 运管 / 超管</p>
          </article>
          <article class="summary-card" style="--accent: var(--ord-color-purple)">
            <p class="summary-label">手动授权</p>
            <p class="summary-value">{{ stats.manualTotal }}</p>
            <p class="summary-desc">模板外额外添加的权限项</p>
          </article>
          <article class="summary-card" style="--accent: var(--ord-color-orange)">
            <p class="summary-label">高敏权限</p>
            <p class="summary-value">{{ stats.sensitiveCount }}</p>
            <p class="summary-desc">包含删除、权限、系统配置等能力</p>
          </article>
        </div>

        <section class="table-card" aria-label="权限成员列表">
          <div class="table-toolbar">
            <div>
              <h2 class="toolbar-title">成员权限列表</h2>
              <p class="toolbar-note">每位成员先继承身份模板，再通过弹窗追加个别权限。</p>
            </div>
            <div class="toolbar-actions">
              <OrdSelect v-model="roleFilter" :options="roleFilterOptions" placeholder="全部身份" />
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
              <template v-else-if="paged.length === 0">
                <OrdTableRow>
                  <OrdTableCell :colspan="8" class="empty-state">暂无匹配成员，请调整筛选条件。</OrdTableCell>
                </OrdTableRow>
              </template>
              <template v-else>
                <OrdTableRow v-for="u in paged" :key="u.id">
                  <OrdTableCell>
                    <span class="primary-text">{{ u.nickname }}</span>
                    <span class="sub-text">{{ u.platform_id }}</span>
                  </OrdTableCell>
                  <OrdTableCell>
                    <span class="role-badge" :class="ROLE_CLASS[u.role]">{{ ROLE_LABEL[u.role] ?? u.role }}</span>
                  </OrdTableCell>
                  <OrdTableCell>{{ u.position || '-' }}</OrdTableCell>
                  <OrdTableCell>
                    <span class="count-badge">{{ getTemplatePerms(u.role).length }} 项</span>
                  </OrdTableCell>
                  <OrdTableCell>
                    <div class="manual-list">
                      <template v-if="u.manual_permissions.length === 0">
                        <span class="permission-tag permission-tag--empty">无额外权限</span>
                      </template>
                      <template v-else>
                        <span v-for="pid in u.manual_permissions" :key="pid" class="permission-tag">
                          {{ getPermName(pid) }}
                        </span>
                      </template>
                    </div>
                  </OrdTableCell>
                  <OrdTableCell>
                    <span class="risk-badge" :class="`risk-badge--${getRiskClass(u)}`">
                      {{ getRiskLabel(getRiskClass(u)) }}
                    </span>
                  </OrdTableCell>
                  <OrdTableCell>{{ u.created_at ? u.created_at.slice(0, 10) : '-' }}</OrdTableCell>
                  <OrdTableCell>
                    <OrdButton variant="primary" size="sm" :disabled="!canManage" @click="openEdit(u)">
                      编辑权限
                    </OrdButton>
                  </OrdTableCell>
                </OrdTableRow>
              </template>
            </OrdTable>
          </div>

          <div v-if="filtered.length > 0" class="pagination" aria-label="分页导航">
            <span class="pagination-summary">共 {{ filtered.length }} 条，第 {{ currentPage }} / {{ totalPages }} 页</span>
            <OrdPagination v-model:current-page="currentPage" :total="filtered.length" :page-size="PAGE_SIZE" />
          </div>
        </section>
      </section>
    </main>

    <OrdDialog v-model:open="editOpen" title="编辑成员权限" description="角色模板权限会自动继承并锁定，勾选下方权限即可进行个别追加授权。">
      <template #trigger></template>
      <div class="perm-form">
        <div class="form-grid">
          <div class="field">
            <label class="field-label">平台号</label>
            <OrdInput :model-value="editPlatformId" disabled />
          </div>
          <div class="field">
            <label class="field-label">昵称</label>
            <OrdInput :model-value="editNickname" disabled />
          </div>
          <div class="field">
            <label class="field-label">角色权限模板</label>
            <OrdSelect v-model="editRole" :options="roleEditOptions" :disabled="!canManage" />
          </div>
        </div>
        <div class="permission-editor">
          <section class="panel template-panel" aria-label="模板继承权限">
            <div class="panel-head">
              <h3>模板继承权限</h3>
              <span>{{ templatePermsForEdit.length }} 项</span>
            </div>
            <div class="inherited-list">
              <div v-for="pid in templatePermsForEdit" :key="pid" class="inherited-item">
                <span>{{ getPermName(pid) }}</span>
                <span class="lock-mark">模板锁定</span>
              </div>
            </div>
          </section>
          <section class="panel manual-panel" aria-label="手动追加权限">
            <div class="panel-head">
              <h3>手动追加权限</h3>
              <span>已追加 {{ manualCountForEdit }} 项</span>
            </div>
            <div class="permission-groups">
              <div v-for="group in permGroups" :key="group.name" class="group-card">
                <p class="group-title">{{ group.name }}</p>
                <div class="checkbox-grid">
                  <label
                    v-for="p in group.items"
                    :key="p.id"
                    class="permission-check"
                    :class="{ 'is-inherited': isInherited(p.id) }"
                  >
                    <input
                      type="checkbox"
                      :value="p.id"
                      :checked="isChecked(p.id)"
                      :disabled="isInherited(p.id) || !canManage"
                      @change="toggleManual(p.id, ($event.target as HTMLInputElement).checked)"
                    />
                    <span>{{ p.name }}</span>
                  </label>
                </div>
              </div>
            </div>
            <p class="form-message">保存后该成员将拥有 {{ effectiveCountForEdit }} 项有效权限。</p>
          </section>
        </div>
      </div>
      <template #footer>
        <OrdButton variant="ghost" @click="editOpen = false">取消</OrdButton>
        <OrdButton variant="primary" :loading="saving" :disabled="!canManage" @click="handleSave">保存权限</OrdButton>
      </template>
    </OrdDialog>
  </div>
</template>

<style scoped>
.page-root { min-height: 100vh; }

.brand-row { display: flex; align-items: center; gap: 12px; color: inherit; text-decoration: none; }
.brand-mark {
  width: 40px; height: 40px; display: grid; place-items: center;
  color: var(--ord-color-white); background: var(--ord-color-blue);
  border-radius: var(--ord-radius-sm); font-size: 15px; font-weight: 700; flex-shrink: 0;
}
.brand-name { color: var(--ord-color-black); font-size: 20px; font-weight: 600; line-height: 1.15; }
.brand-caption { display: block; margin-top: 2px; color: var(--ord-color-gray-500); font-size: 11px; font-weight: 600; letter-spacing: 1.2px; text-transform: uppercase; }

:deep(.ord-navbar) {
  position: fixed; inset: 0 0 auto; z-index: 20; height: auto; min-height: 76px;
  padding: 0 32px; background: rgba(255,255,255,0.94);
  border-bottom: 1px solid rgba(216,216,216,0.86);
  box-shadow: 0 18px 40px rgba(8,8,8,0.08); backdrop-filter: blur(16px);
}
:deep(.ord-navbar__inner) {
  width: min(1460px, 100%); min-height: 76px; height: auto; margin: 0 auto;
  padding: 16px 0; display: flex; align-items: center; justify-content: space-between; gap: 20px;
}
:deep(.ord-navbar__actions) { display: flex; align-items: center; gap: 10px; flex-wrap: nowrap; }
:deep(.ord-navbar__brand) { flex-shrink: 0; }

.nav-height-btn {
  height: 42px; padding: 0 16px; display: inline-flex; align-items: center;
  justify-content: center; border-radius: 4px; font-size: 15px; font-weight: 600;
}

.profile-trigger { position: relative; }
.profile-button {
  display: inline-flex; align-items: center; gap: 10px; height: 42px; padding: 0 10px;
  color: var(--ord-color-black); background: var(--ord-color-white);
  border: 1px solid var(--ord-color-border); border-radius: var(--ord-radius-sm);
  cursor: pointer; font: inherit;
  transition: border-color var(--ord-transition-base), color var(--ord-transition-base);
}
.profile-button:hover { color: var(--ord-color-blue); border-color: var(--ord-color-blue); }
.profile-name { font-size: 14px; font-weight: 600; }

.profile-card {
  position: absolute; top: calc(100% + 12px); right: 0; width: 260px; padding: 16px;
  background: var(--ord-color-white); border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-md); box-shadow: var(--ord-shadow-cascade);
  opacity: 0; visibility: hidden; transform: translateY(-4px); z-index: 200;
  transition: opacity 160ms ease, transform 160ms ease, visibility 160ms ease;
}
.profile-trigger:hover .profile-card,
.profile-trigger:focus-within .profile-card { opacity: 1; visibility: visible; transform: translateY(0); }
.profile-card-header { display: flex; align-items: center; gap: 10px; padding-bottom: 12px; border-bottom: 1px solid var(--ord-color-border); }
.profile-card h3 { margin: 0 0 4px; font-size: 16px; }
.profile-card p { margin: 0; color: var(--ord-color-gray-500); font-size: 12px; line-height: 1.5; }
.profile-meta { display: grid; grid-template-columns: repeat(2,1fr); gap: 10px; padding-top: 12px; }
.profile-meta div { padding: 10px; background: #f7f9ff; border: 1px solid rgba(216,216,216,0.7); border-radius: var(--ord-radius-sm); }
.profile-meta span { display: block; color: var(--ord-color-gray-500); font-size: 11px; }
.profile-meta strong { display: block; margin-top: 3px; font-size: 14px; }
.logout-link {
  display: flex; align-items: center; justify-content: center; width: 100%; min-height: 36px;
  margin-top: 12px; color: var(--ord-color-red); background: rgba(238,29,54,0.08);
  border: 1px solid rgba(238,29,54,0.18); border-radius: var(--ord-radius-sm);
  font-size: 13px; font-weight: 650; cursor: pointer;
  transition: background var(--ord-transition-base);
}
.logout-link:hover { background: rgba(238,29,54,0.12); }

/* ── 页面布局 ── */
.page-shell {
  min-height: 100vh; padding: 112px 32px 48px;
  background:
    radial-gradient(circle at 12% 12%, rgba(20,110,245,0.08), transparent 28%),
    radial-gradient(circle at 86% 18%, rgba(122,61,255,0.06), transparent 24%),
    radial-gradient(circle at 80% 86%, rgba(255,174,19,0.052), transparent 28%),
    linear-gradient(135deg, #ffffff 0%, #f7f9ff 100%);
}

.permission-frame {
  position: relative; width: min(1460px, 100%); margin: 0 auto;
  display: grid; gap: 18px;
}

.deco-rect {
  position: absolute; z-index: 0;
  border: 1px solid rgba(216,216,216,0.7); background: rgba(255,255,255,0.45);
  pointer-events: none;
}
.deco-rect--a { width: 180px; height: 86px; top: 96px; right: 42px; transform: rotate(-2deg); }
.deco-rect--b { width: 108px; height: 108px; right: 214px; bottom: 56px; transform: rotate(4deg); }

.hero-card,
.summary-card,
.table-card {
  background: rgba(255,255,255,0.94); border: 1px solid rgba(216,216,216,0.86);
  border-radius: var(--ord-radius-md); box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
}

.hero-card {
  position: relative; overflow: hidden;
  display: grid; grid-template-columns: 1fr auto; gap: 24px; padding: 28px;
}
.hero-card::after {
  content: ""; position: absolute; right: -56px; top: -56px; width: 220px; height: 220px;
  background:
    linear-gradient(90deg, rgba(20,110,245,0.16) 1px, transparent 1px),
    linear-gradient(0deg, rgba(20,110,245,0.16) 1px, transparent 1px);
  background-size: 22px 22px; transform: rotate(8deg); pointer-events: none;
}

.eyebrow { margin: 0 0 10px; color: var(--ord-color-blue); font-size: 12px; font-weight: 700; letter-spacing: 1.4px; text-transform: uppercase; }
h1 { margin: 0; font-size: clamp(34px, 4vw, 56px); font-weight: 600; line-height: 1.04; letter-spacing: -0.6px; }
.hero-copy { max-width: 700px; margin: 16px 0 0; color: var(--ord-color-gray-700); font-size: 16px; line-height: 1.65; }

.hero-aside {
  position: relative; z-index: 1; width: 286px; align-self: stretch;
  display: grid; gap: 10px; padding: 18px;
  background: var(--ord-color-black); border-radius: var(--ord-radius-md); color: var(--ord-color-white);
}
.template-pill {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  min-height: 42px; padding: 0 12px;
  background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.14);
  border-radius: var(--ord-radius-sm); font-size: 13px;
}
.template-pill strong { color: #fff; font-size: 14px; }

.summary-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; }
.summary-card {
  position: relative; overflow: hidden; min-height: 106px; padding: 18px;
  border-top: 4px solid var(--accent, var(--ord-color-blue));
}
.summary-label { margin: 0; color: var(--ord-color-gray-500); font-size: 11px; font-weight: 700; letter-spacing: 1.1px; text-transform: uppercase; }
.summary-value { margin: 12px 0 0; font-size: 34px; font-weight: 600; line-height: 1; }
.summary-desc { margin: 10px 0 0; color: var(--ord-color-gray-500); font-size: 13px; line-height: 1.45; }

.table-card { overflow: hidden; }
.table-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; padding: 18px; border-bottom: 1px solid var(--ord-color-border);
}
.toolbar-title { margin: 0; font-size: 22px; font-weight: 600; line-height: 1.2; }
.toolbar-note { margin: 7px 0 0; color: var(--ord-color-gray-500); font-size: 13px; line-height: 1.45; }
.toolbar-actions { display: flex; align-items: center; gap: 10px; }
.toolbar-actions :deep(.ord-select__trigger) { min-width: 140px; height: 42px; }
.toolbar-actions :deep(.ord-search-box__input) { height: 42px; }

.table-scroll { width: 100%; overflow-x: auto; }
.table-scroll :deep(.ord-table) { border: 0; border-radius: 0; }
.table-scroll :deep(.ord-table__inner) { min-width: 1100px; }
.table-scroll :deep(th), .table-scroll :deep(td) { border-bottom: 1px solid rgba(216,216,216,0.72); vertical-align: middle; }
.table-scroll :deep(th) { background: #fbfcff; }

.primary-text { display: block; color: var(--ord-color-black); font-size: 14px; font-weight: 700; }
.sub-text { display: block; margin-top: 4px; color: var(--ord-color-gray-500); font-size: 12px; }

.role-badge {
  display: inline-flex; align-items: center; min-height: 28px; padding: 0 10px;
  border-radius: var(--ord-radius-sm); font-size: 12px; font-weight: 700; white-space: nowrap;
  color: var(--ord-color-blue); background: rgba(20,110,245,0.08);
}
.role-badge.builder  { color: #009e19; background: rgba(0,215,34,0.12); }
.role-badge.operator { color: #b27600; background: rgba(255,174,19,0.16); }
.role-badge.superAdmin { color: var(--ord-color-purple); background: rgba(122,61,255,0.1); }

.count-badge {
  display: inline-flex; align-items: center; min-height: 28px; padding: 0 10px;
  border-radius: var(--ord-radius-sm); font-size: 12px; font-weight: 700;
  color: var(--ord-color-black); background: #f4f4f4;
}

.manual-list { display: flex; flex-wrap: wrap; gap: 6px; max-width: 280px; }
.permission-tag {
  display: inline-flex; align-items: center; min-height: 24px; padding: 0 8px;
  border-radius: var(--ord-radius-sm); font-size: 11px; font-weight: 700;
  color: var(--ord-color-blue); background: rgba(20,110,245,0.08);
}
.permission-tag--empty { color: var(--ord-color-gray-500); background: #f4f4f4; }

.risk-badge {
  display: inline-flex; align-items: center; min-height: 28px; padding: 0 10px;
  border-radius: var(--ord-radius-sm); font-size: 12px; font-weight: 700; white-space: nowrap;
}
.risk-badge--low    { color: #009e19; background: rgba(0,215,34,0.12); }
.risk-badge--medium { color: #b27600; background: rgba(255,174,19,0.16); }
.risk-badge--high   { color: var(--ord-color-red); background: rgba(238,29,54,0.1); }

.empty-state { padding: 34px; color: var(--ord-color-gray-500); text-align: center; }

.pagination {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; padding: 14px 18px; border-top: 1px solid var(--ord-color-border);
  background: rgba(255,255,255,0.92);
}
.pagination-summary { color: var(--ord-color-gray-500); font-size: 13px; font-weight: 600; }

/* ── 弹窗内部 ── */
.perm-form { padding: 4px 0; }

.form-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 14px; margin-bottom: 18px; }
.field { display: grid; gap: 7px; }
.field-label { color: var(--ord-color-gray-500); font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; }

.permission-editor { display: grid; grid-template-columns: 0.9fr 1.3fr; gap: 16px; }

.panel { border: 1px solid var(--ord-color-border); border-radius: var(--ord-radius-md); background: #fff; overflow: hidden; }
.panel-head {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; padding: 14px; border-bottom: 1px solid #ececec;
}
.panel-head h3 { margin: 0; font-size: 16px; font-weight: 600; }
.panel-head span { color: var(--ord-color-gray-500); font-size: 12px; font-weight: 700; white-space: nowrap; }

.inherited-list { display: grid; gap: 10px; padding: 14px; }
.inherited-item {
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  min-height: 38px; padding: 0 10px;
  color: var(--ord-color-gray-700); background: #f8f8f8;
  border: 1px solid #ededed; border-radius: var(--ord-radius-sm); font-size: 13px;
}
.lock-mark { color: var(--ord-color-gray-300); font-size: 12px; font-weight: 700; }

.permission-groups { display: grid; gap: 10px; padding: 14px; }
.group-card { display: grid; gap: 10px; padding: 12px; border: 1px solid #ededed; border-radius: 6px; }
.group-title { margin: 0; font-size: 13px; font-weight: 700; }
.checkbox-grid { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 8px; }

.permission-check {
  display: flex; align-items: center; gap: 8px; min-height: 34px; padding: 0 9px;
  border: 1px solid var(--ord-color-border); border-radius: var(--ord-radius-sm);
  color: var(--ord-color-gray-700); font-size: 12px; cursor: pointer;
  transition: border-color var(--ord-transition-base), background var(--ord-transition-base);
}
.permission-check:hover:not(.is-inherited) { border-color: var(--ord-color-blue); background: rgba(20,110,245,0.04); }
.permission-check.is-inherited { color: var(--ord-color-gray-300); background: #f8f8f8; cursor: not-allowed; }
.permission-check input { accent-color: var(--ord-color-blue); }

.form-message { margin: 0; padding: 0 14px 14px; color: var(--ord-color-gray-500); font-size: 13px; line-height: 1.45; }

:deep(.ord-dialog__content) { width: min(960px, 96vw); max-height: min(86vh, 800px); overflow: auto; }

/* ── 响应式 ── */
@media (max-width: 992px) {
  .hero-card { grid-template-columns: 1fr; }
  .hero-aside { width: 100%; }
  .summary-grid { grid-template-columns: repeat(2,1fr); }
  .table-toolbar { align-items: stretch; flex-direction: column; }
  .toolbar-actions { flex-wrap: wrap; }
  .permission-editor { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 768px) {
  :deep(.ord-navbar) { padding: 0 16px; }
  .brand-caption, .profile-name { display: none; }
  .page-shell { padding: 96px 16px 24px; }
  .summary-grid, .form-grid { grid-template-columns: 1fr; }
  .pagination { align-items: stretch; flex-direction: column; }
  .checkbox-grid { grid-template-columns: 1fr; }
}
</style>
