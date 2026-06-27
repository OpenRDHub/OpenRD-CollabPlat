<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import {
  OrdAvatar,
  OrdBadge,
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
  OrdTextarea,
  useToast,
} from '@/components/ui'
import { adminApi } from '@/api/admin'
import type { AdminUser, UpdateUserPayload } from '@/api/admin'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const { show: showToast } = useToast()

const PAGE_SIZE = 8

const users = ref<AdminUser[]>([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const roleFilter = ref('all')
const currentPage = ref(1)
const editOpen = ref(false)
const showPassword = ref(false)

const editForm = ref({
  id: '',
  platform_id: '',
  nickname: '',
  role: 'requester' as string,
  identity: '',
  position: '',
  phone: '',
  intro: '',
  created_at: '',
  new_password: '',
})

const roleFilterOptions = [
  { value: 'all', label: '全部身份' },
  { value: 'requester', label: '需求者' },
  { value: 'builder', label: '共建者' },
  { value: 'operator', label: '运营管理员' },
  { value: 'super_admin', label: '超级管理员' },
]

const roleOptions = [
  { value: 'requester', label: '需求者' },
  { value: 'builder', label: '共建者' },
  { value: 'operator', label: '运营管理员' },
  { value: 'super_admin', label: '超级管理员' },
]

const ROLE_LABEL: Record<string, string> = {
  requester: '需求方',
  builder: '共建方',
  operator: '运营管理员',
  super_admin: '超级管理员',
}

const canManageUsers = computed(() => auth.hasPermission('admin:users'))

const exporting = ref(false)

const ROLE_LABEL_EN: Record<string, string> = {
  requester: '需求方',
  builder: '共建方',
  operator: '运营管理员',
  super_admin: '超级管理员',
}

async function handleExportCSV() {
  if (exporting.value) return
  exporting.value = true
  try {
    const res = await adminApi.getUsers({ page: 1, page_size: 10000 })
    const all: AdminUser[] = (res.data.items as AdminUser[]) ?? []

    const headers = ['用户ID', '平台号', '昵称', '身份角色', '岗位', '手机号', '状态', '注册时间', '个人介绍']
    const rows = all.map((u) => [
      u.id,
      u.platform_id,
      u.nickname,
      ROLE_LABEL_EN[u.role] ?? u.role,
      u.position ?? '',
      u.phone,
      u.status === 'active' ? '正常' : '已锁定',
      u.created_at ? u.created_at.slice(0, 10) : '',
      (u.intro ?? '').replace(/"/g, '""'),
    ])

    const csv = [headers, ...rows]
      .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(','))
      .join('\r\n')

    const bom = '﻿'
    const blob = new Blob([bom + csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `用户列表_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    showToast({ title: `已导出 ${all.length} 位用户`, variant: 'success' })
  } catch {
    showToast({ title: '导出失败', description: '请稍后重试。', variant: 'error' })
  } finally {
    exporting.value = false
  }
}
const roleLabel = computed(() => ROLE_LABEL[auth.userRole] ?? '平台用户')

const stats = computed(() => ({
  total: total.value,
  admins: users.value.filter((u) => u.role === 'operator' || u.role === 'super_admin').length,
  builders: users.value.filter((u) => u.role === 'builder').length,
  requesters: users.value.filter((u) => u.role === 'requester').length,
}))

function roleBadgeVariant(role: string) {
  if (role === 'super_admin') return 'purple'
  if (role === 'operator') return 'orange'
  if (role === 'builder') return 'green'
  return 'blue'
}

function shortId(id: string) {
  return id.length > 14 ? `${id.slice(0, 8)}…${id.slice(-4)}` : id
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
    users.value = (res.data.items as AdminUser[]) ?? []
    total.value = res.data.total ?? 0
  } catch {
    showToast({ title: '加载失败', description: '无法获取用户列表，请稍后重试。', variant: 'error' })
  } finally {
    loading.value = false
  }
}

function openEdit(user: AdminUser) {
  if (!canManageUsers.value) return
  editForm.value = {
    id: user.id,
    platform_id: user.platform_id,
    nickname: user.nickname,
    role: user.role,
    identity: user.identity ?? '',
    position: user.position ?? '',
    phone: user.phone,
    intro: user.intro ?? '',
    created_at: user.created_at ? user.created_at.slice(0, 10) : '',
    new_password: '',
  }
  showPassword.value = false
  editOpen.value = true
}

async function handleSave() {
  if (saving.value) return
  saving.value = true
  try {
    const payload: UpdateUserPayload = {
      platform_id: editForm.value.platform_id,
      nickname: editForm.value.nickname,
      role: editForm.value.role,
      identity: editForm.value.identity,
      position: editForm.value.position,
      phone: editForm.value.phone,
      intro: editForm.value.intro,
    }
    if (editForm.value.new_password.trim()) {
      payload.new_password = editForm.value.new_password.trim()
    }
    await adminApi.updateUser(editForm.value.id, payload)
    showToast({ title: `用户 ${editForm.value.nickname} 信息已更新`, variant: 'success' })
    editOpen.value = false
    await loadUsers()
  } catch {
    showToast({ title: '保存失败', description: '请稍后重试。', variant: 'error' })
  } finally {
    saving.value = false
  }
}

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))

watch([keyword, roleFilter], () => { resetPage(); loadUsers() })
watch(currentPage, loadUsers)

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
        <OrdButton class="nav-height-btn" variant="ghost" size="sm" @click="goBack">返回</OrdButton>
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
                <p>{{ roleLabel }} · {{ canManageUsers ? '可管理全量用户' : '仅可查看' }}</p>
              </div>
            </div>
            <div class="profile-meta">
              <div><span>当前角色</span><strong>{{ roleLabel }}</strong></div>
              <div><span>管理权限</span><strong>{{ canManageUsers ? '已授权' : '未授权' }}</strong></div>
            </div>
            <button class="logout-link" type="button" @click="handleLogout">退出登录</button>
          </section>
        </div>
      </template>
    </OrdNavbar>

    <main class="page-shell">
      <div class="management-frame">
        <div class="ambient-ring" aria-hidden="true"></div>
        <div class="ambient-node" aria-hidden="true"></div>

        <section class="hero-card" aria-label="用户管理概览">
          <div>
            <p class="section-label">User Management</p>
            <h1>管理用户信息与身份</h1>
            <p class="hero-copy">
              查看平台用户资料、身份权限、岗位与参与项目。点击编辑可以在弹窗中修改用户资料，ID 保持不可更改。
            </p>
          </div>
          <OrdButton variant="primary" :disabled="!canManageUsers" :loading="exporting" @click="handleExportCSV">导出 CSV</OrdButton>
        </section>

        <section class="summary-grid" aria-label="用户统计">
          <article class="summary-card" style="--accent: var(--ord-color-blue)">
            <strong>{{ stats.total }}</strong>
            <span>平台用户总数</span>
          </article>
          <article class="summary-card" style="--accent: var(--ord-color-purple)">
            <strong>4</strong>
            <span>身份角色类型</span>
          </article>
          <article class="summary-card" style="--accent: var(--ord-color-yellow)">
            <strong>{{ stats.admins }}</strong>
            <span>管理员账户数</span>
          </article>
          <article class="summary-card" style="--accent: var(--ord-color-green)">
            <strong>{{ stats.builders }}</strong>
            <span>共建者数量</span>
          </article>
        </section>

        <section class="table-card" aria-label="用户列表">
          <div class="table-toolbar">
            <div>
              <p class="section-label">User List</p>
              <h2>用户列表</h2>
              <p class="toolbar-note">字段较多，表格支持横向滚动。可按身份角色或关键字快速定位。</p>
            </div>
            <div class="toolbar-actions">
              <OrdSearchBox v-model="keyword" placeholder="搜索平台号、昵称、手机号" width="260px" />
              <OrdSelect v-model="roleFilter" :options="roleFilterOptions" placeholder="全部身份" />
            </div>
          </div>

          <div class="table-scroll">
            <OrdTable>
              <OrdTableHeader>
                <OrdTableCell header>用户 ID</OrdTableCell>
                <OrdTableCell header>平台号 / 昵称</OrdTableCell>
                <OrdTableCell header>身份</OrdTableCell>
                <OrdTableCell header>岗位</OrdTableCell>
                <OrdTableCell header>手机号</OrdTableCell>
                <OrdTableCell header>注册时间</OrdTableCell>
                <OrdTableCell header>个人介绍</OrdTableCell>
                <OrdTableCell header>操作</OrdTableCell>
              </OrdTableHeader>

              <template v-if="loading">
                <OrdTableRow>
                  <OrdTableCell :colspan="8" class="empty-state">加载中...</OrdTableCell>
                </OrdTableRow>
              </template>
              <template v-else-if="users.length === 0">
                <OrdTableRow>
                  <OrdTableCell :colspan="8" class="empty-state">暂无匹配用户，请调整筛选条件。</OrdTableCell>
                </OrdTableRow>
              </template>
              <template v-else>
                <OrdTableRow v-for="user in users" :key="user.id">
                  <OrdTableCell>
                    <span class="id-text" :title="user.id">{{ shortId(user.id) }}</span>
                  </OrdTableCell>
                  <OrdTableCell>
                    <div class="user-name-cell">
                      <OrdAvatar :name="user.nickname" size="sm" />
                      <div>
                        <div class="primary-text">{{ user.platform_id }}</div>
                        <div class="sub-text">{{ user.nickname }}</div>
                      </div>
                    </div>
                  </OrdTableCell>
                  <OrdTableCell>
                    <OrdBadge :variant="roleBadgeVariant(user.role)">
                      {{ ROLE_LABEL[user.role] ?? user.role }}
                    </OrdBadge>
                  </OrdTableCell>
                  <OrdTableCell>{{ user.position ?? '—' }}</OrdTableCell>
                  <OrdTableCell>{{ user.phone }}</OrdTableCell>
                  <OrdTableCell>{{ user.created_at ? user.created_at.slice(0, 10) : '—' }}</OrdTableCell>
                  <OrdTableCell>
                    <span class="intro-text">{{ user.intro ?? '—' }}</span>
                  </OrdTableCell>
                  <OrdTableCell>
                    <OrdButton
                      variant="primary"
                      size="sm"
                      :disabled="!canManageUsers"
                      @click="openEdit(user)"
                    >编辑</OrdButton>
                  </OrdTableCell>
                </OrdTableRow>
              </template>
            </OrdTable>
          </div>

          <div v-if="total > 0" class="pagination" aria-label="分页导航">
            <span class="pagination-summary">共 {{ total }} 位用户，第 {{ currentPage }} / {{ totalPages }} 页</span>
            <OrdPagination v-model:current-page="currentPage" :total="total" :page-size="PAGE_SIZE" />
          </div>
        </section>
      </div>
    </main>

    <OrdDialog
      v-model:open="editOpen"
      title="编辑用户信息"
      description="用户 ID 与注册时间为系统字段，不可更改。管理员可修改平台号、昵称、身份、岗位、手机号与密码。"
    >
      <template #trigger></template>

      <div class="edit-form">
        <div class="readonly-grid">
          <div class="readonly-box">
            <span>用户 ID</span>
            <strong>{{ editForm.id }}</strong>
          </div>
          <div class="readonly-box">
            <span>注册时间</span>
            <strong>{{ editForm.created_at || '—' }}</strong>
          </div>
        </div>

        <div class="form-grid">
          <div class="field">
            <label class="field-label">平台号</label>
            <OrdInput v-model="editForm.platform_id" placeholder="platform_id" />
          </div>
          <div class="field">
            <label class="field-label">昵称</label>
            <OrdInput v-model="editForm.nickname" placeholder="昵称" />
          </div>
          <div class="field">
            <label class="field-label">身份角色</label>
            <OrdSelect v-model="editForm.role" :options="roleOptions" />
          </div>
          <div class="field">
            <label class="field-label">岗位</label>
            <OrdInput v-model="editForm.position" placeholder="岗位" />
          </div>
          <div class="field">
            <label class="field-label">手机号</label>
            <OrdInput v-model="editForm.phone" type="tel" placeholder="手机号" />
          </div>
          <div class="field">
            <label class="field-label">新密码（留空不修改）</label>
            <div class="password-wrap">
              <OrdInput
                v-model="editForm.new_password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="留空则不修改密码"
              />
              <button
                class="password-toggle"
                type="button"
                @click="showPassword = !showPassword"
              >{{ showPassword ? '隐藏' : '显示' }}</button>
            </div>
          </div>
          <div class="field full">
            <label class="field-label">个人介绍</label>
            <OrdTextarea v-model="editForm.intro" placeholder="个人介绍" :rows="3" />
          </div>
        </div>
      </div>

      <template #footer>
        <OrdButton variant="ghost" @click="editOpen = false">取消</OrdButton>
        <OrdButton variant="primary" :loading="saving" @click="handleSave">保存修改</OrdButton>
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

.brand-caption {
  display: block; margin-top: 2px; color: var(--ord-color-gray-500);
  font-size: 11px; font-weight: 600; letter-spacing: 1.2px; text-transform: uppercase;
}

.nav-height-btn { height: 42px; }

.profile-trigger { position: relative; }

.profile-button {
  display: inline-flex; align-items: center; gap: 10px; height: 42px; padding: 0 10px;
  color: var(--ord-color-black); background: var(--ord-color-white);
  border: 1px solid var(--ord-color-gray-200); border-radius: var(--ord-radius-sm);
  cursor: pointer; font-size: 14px; font-weight: 600; transition: var(--ord-transition-base);
}

.profile-name { font-size: 14px; font-weight: 600; }

.profile-card {
  position: absolute; top: calc(100% + 12px); right: 0; width: 260px; padding: 16px;
  opacity: 0; visibility: hidden; transform: translateY(-4px);
  background: var(--ord-color-white); border: 1px solid var(--ord-color-gray-200);
  border-radius: var(--ord-radius-md); box-shadow: var(--ord-shadow-cascade);
  transition: opacity 160ms ease, transform 160ms ease, visibility 160ms ease; z-index: 30;
}

.profile-trigger:hover .profile-card,
.profile-trigger:focus-within .profile-card {
  opacity: 1; visibility: visible; transform: translateY(0);
}

.profile-card-header { display: flex; align-items: center; gap: 12px; padding-bottom: 14px; border-bottom: 1px solid #ececec; }
.profile-card h3 { margin: 0; font-size: 17px; font-weight: 600; }
.profile-card p { margin: 4px 0 0; color: var(--ord-color-gray-500); font-size: 13px; }

.profile-meta { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 14px; }
.profile-meta div { padding: 10px; background: rgba(20,110,245,0.06); border: 1px solid rgba(20,110,245,0.12); border-radius: var(--ord-radius-sm); }
.profile-meta span { display: block; color: var(--ord-color-gray-500); font-size: 11px; }
.profile-meta strong { display: block; margin-top: 4px; color: var(--ord-color-black); font-size: 15px; font-weight: 600; }

.logout-link {
  display: flex; align-items: center; justify-content: center; min-height: 36px; width: 100%;
  margin-top: 12px; color: #ee1d36; background: rgba(238,29,54,0.08);
  border: 1px solid rgba(238,29,54,0.18); border-radius: var(--ord-radius-sm);
  font-size: 13px; font-weight: 650; cursor: pointer; transition: var(--ord-transition-base);
}
.logout-link:hover { background: rgba(238,29,54,0.12); border-color: rgba(238,29,54,0.34); transform: translateX(6px); }

.page-shell {
  min-height: 100vh; display: flex; justify-content: center; padding: 96px 32px 32px;
  background:
    radial-gradient(circle at 12% 12%, rgba(20,110,245,0.08), transparent 28%),
    radial-gradient(circle at 86% 18%, rgba(122,61,255,0.065), transparent 24%),
    radial-gradient(circle at 80% 86%, rgba(255,174,19,0.055), transparent 28%),
    linear-gradient(135deg, #ffffff 0%, #f7f9ff 100%);
}

.management-frame { position: relative; width: min(1460px, 100%); }

.ambient-ring {
  position: absolute; width: 280px; height: 280px; right: -72px; top: 92px;
  border: 1px solid rgba(20,110,245,0.1); border-radius: 50%; pointer-events: none; z-index: -1;
}

.ambient-node {
  position: absolute; width: 140px; height: 70px; left: -48px; bottom: 84px; pointer-events: none; z-index: -1;
  background:
    radial-gradient(circle at 8px 14px, rgba(20,110,245,0.22) 0 4px, transparent 5px),
    radial-gradient(circle at 72px 38px, rgba(0,215,34,0.18) 0 5px, transparent 6px),
    radial-gradient(circle at 128px 16px, rgba(237,82,203,0.18) 0 4px, transparent 5px);
}

.hero-card {
  display: grid; grid-template-columns: minmax(0,1fr) auto; gap: 22px; align-items: center; padding: 24px;
  background: rgba(255,255,255,0.94); border: 1px solid rgba(216,216,216,0.86);
  border-radius: var(--ord-radius-md); box-shadow: var(--ord-shadow-cascade);
}

.section-label { margin: 0 0 10px; color: var(--ord-color-blue); font-size: 12px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; }

.hero-card h1 { margin: 0; font-size: clamp(40px, 5vw, 58px); font-weight: 600; line-height: 1.04; letter-spacing: -0.8px; }

.hero-copy { max-width: 720px; margin: 14px 0 0; color: var(--ord-color-gray-500); font-size: 16px; line-height: 1.58; }

.summary-grid { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 12px; margin-top: 18px; }

.summary-card {
  min-height: 104px; padding: 16px;
  background: rgba(255,255,255,0.94); border: 1px solid rgba(216,216,216,0.86);
  border-left: 3px solid var(--accent, var(--ord-color-blue));
  border-radius: var(--ord-radius-md);
}
.summary-card strong { display: block; color: var(--ord-color-black); font-size: 32px; font-weight: 600; line-height: 1; letter-spacing: -0.6px; }
.summary-card span { display: block; margin-top: 10px; color: var(--ord-color-gray-500); font-size: 13px; font-weight: 600; }

.table-card {
  margin-top: 18px; overflow: hidden;
  background: rgba(255,255,255,0.94); border: 1px solid rgba(216,216,216,0.86);
  border-radius: var(--ord-radius-md); box-shadow: var(--ord-shadow-cascade);
}

.table-toolbar {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  padding: 18px 20px; border-bottom: 1px solid #ececec;
}
.table-toolbar h2 { margin: 0; font-size: 30px; font-weight: 600; line-height: 1.05; letter-spacing: -0.5px; }
.toolbar-note { margin: 8px 0 0; color: var(--ord-color-gray-500); font-size: 14px; line-height: 1.5; }
.toolbar-actions { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }

.table-scroll { overflow-x: auto; }

.user-name-cell { display: flex; align-items: center; gap: 10px; }
.primary-text { color: var(--ord-color-black); font-size: 14px; font-weight: 700; }
.sub-text { display: block; margin-top: 2px; color: var(--ord-color-gray-500); font-size: 12px; }

.id-text { color: #ababab; font-family: Consolas, 'Inconsolata', monospace; font-size: 11px; letter-spacing: 0.2px; }

.intro-text {
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden; font-size: 13px; color: var(--ord-color-gray-500); max-width: 220px;
}

.empty-state { text-align: center; color: var(--ord-color-gray-500); padding: 40px 0; font-size: 14px; }

.pagination {
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  padding: 14px 18px; border-top: 1px solid #ececec; background: rgba(255,255,255,0.92);
}
.pagination-summary { color: var(--ord-color-gray-500); font-size: 13px; font-weight: 600; }

.edit-form { display: flex; flex-direction: column; gap: 0; }

.readonly-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.readonly-box { padding: 12px; background: rgba(20,110,245,0.045); border: 1px solid rgba(20,110,245,0.14); border-radius: var(--ord-radius-sm); }
.readonly-box span { display: block; margin-bottom: 7px; color: var(--ord-color-gray-500); font-size: 12px; font-weight: 700; letter-spacing: 0.7px; text-transform: uppercase; }
.readonly-box strong { color: var(--ord-color-black); font-size: 14px; font-weight: 600; word-break: break-all; }

.form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-top: 18px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field.full { grid-column: 1 / -1; }
.field-label { color: var(--ord-color-gray-500); font-size: 12px; font-weight: 700; letter-spacing: 0.7px; text-transform: uppercase; }

.password-wrap { position: relative; }
.password-toggle {
  position: absolute; top: 50%; right: 8px; transform: translateY(-50%);
  height: 30px; padding: 0 8px; color: var(--ord-color-gray-500);
  background: transparent; border: none; font-size: 12px; letter-spacing: 0.6px;
  cursor: pointer; transition: color 180ms ease;
}
.password-toggle:hover { color: var(--ord-color-blue); }
</style>
