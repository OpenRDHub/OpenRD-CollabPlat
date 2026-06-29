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
  OrdProgress,
  OrdSearchBox,
  OrdSelect,
  OrdTable,
  OrdTableCell,
  OrdTableHeader,
  OrdTableRow,
  OrdTextarea,
  useToast,
} from '@/components/ui'
import { tasksApi } from '@/api/tasks'
import type { Task } from '@/api/tasks'
import { useAuthStore } from '@/stores/auth'

type ManagedTask = Task & { leader_name?: string }

interface EditForm {
  id: string
  demand_id: string
  title: string
  status: string
  team_status: string
  leader_name: string
  progress: string
  note: string
}

const router = useRouter()
const auth = useAuthStore()
const { show: showToast } = useToast()

const PAGE_SIZE = 8

const tasks = ref<ManagedTask[]>([])
const loading = ref(false)
const keyword = ref('')
const statusFilter = ref('all')
const teamFilter = ref('all')
const currentPage = ref(1)
const editOpen = ref(false)
const saving = ref(false)

const editForm = ref<EditForm>({
  id: '',
  demand_id: '',
  title: '',
  status: 'recruiting',
  team_status: 'forming',
  leader_name: '',
  progress: '0',
  note: '',
})

const statusOptions = [
  { value: 'recruiting', label: '待处理' },
  { value: 'in_progress', label: '解决中' },
  { value: 'reviewing', label: '评审中' },
  { value: 'completed', label: '已完成' },
  { value: 'closed', label: '已关闭' },
]

const teamStatusOptions = [
  { value: 'forming', label: '招募中' },
  { value: 'formed', label: '招募完成' },
  { value: 'collaborating', label: '协作中' },
  { value: 'accepted', label: '已验收' },
  { value: 'closed', label: '已关闭' },
]

const statusFilterOptions = [{ value: 'all', label: '全部状态' }, ...statusOptions]
const teamStatusFilterOptions = [{ value: 'all', label: '全部团队' }, ...teamStatusOptions]

const STATUS_LABEL = Object.fromEntries(statusOptions.map((item) => [item.value, item.label]))
const TEAM_STATUS_LABEL = Object.fromEntries(teamStatusOptions.map((item) => [item.value, item.label]))

const ROLE_LABEL: Record<string, string> = {
  requester: '需求方',
  builder: '开发者',
  operator: '运营管理员',
  super_admin: '超级管理员',
}

const canManageTasks = computed(() => auth.hasPermission('task:manage'))
const roleLabel = computed(() => ROLE_LABEL[auth.userRole] ?? '平台用户')

const stats = computed(() => ({
  total: tasks.value.length,
  active: tasks.value.filter((task) => ['in_progress', 'reviewing'].includes(task.status)).length,
  pending: tasks.value.filter((task) => task.status === 'recruiting').length,
  done: tasks.value.filter((task) => ['completed', 'closed'].includes(task.status)).length,
}))

const filteredTasks = computed(() => {
  let list = tasks.value

  if (statusFilter.value !== 'all') {
    list = list.filter((task) => task.status === statusFilter.value)
  }

  if (teamFilter.value !== 'all') {
    list = list.filter((task) => task.team_status === teamFilter.value)
  }

  const query = keyword.value.trim().toLowerCase()
  if (query) {
    list = list.filter((task) => {
      const haystack = [
        task.id,
        task.title,
        task.description,
        task.leader_name,
        task.demand_id,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()

      return haystack.includes(query)
    })
  }

  return list
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredTasks.value.length / PAGE_SIZE)))

const pagedTasks = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return filteredTasks.value.slice(start, start + PAGE_SIZE)
})

function dateOnly(value: string) {
  return value ? value.slice(0, 10) : '-'
}

function statusLabel(status: string) {
  return STATUS_LABEL[status] ?? status
}

function teamStatusLabel(status: string) {
  return TEAM_STATUS_LABEL[status] ?? status
}

function statusVariant(status: string) {
  if (status === 'recruiting') return 'orange'
  if (status === 'in_progress' || status === 'reviewing') return 'blue'
  if (status === 'completed') return 'green'
  return 'gray'
}

function teamVariant(status: string) {
  if (status === 'forming') return 'purple'
  if (status === 'formed') return 'blue'
  if (status === 'collaborating') return 'orange'
  if (status === 'accepted') return 'green'
  return 'gray'
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

async function loadTasks() {
  loading.value = true

  try {
    const res = await tasksApi.getList({ page: 1, page_size: 200 })
    tasks.value = (res.data.items as ManagedTask[]) ?? []
  } catch {
    showToast({
      title: '加载失败',
      description: '无法获取任务列表，请稍后重试。',
      variant: 'error',
    })
  } finally {
    loading.value = false
  }
}

function openEdit(task: ManagedTask) {
  if (!canManageTasks.value) return

  editForm.value = {
    id: task.id,
    demand_id: task.demand_id,
    title: task.title,
    status: task.status,
    team_status: task.team_status,
    leader_name: task.leader_name ?? '',
    progress: String(task.progress),
    note: '',
  }
  editOpen.value = true
}

async function handleSave() {
  if (!canManageTasks.value || !editForm.value.id) return

  saving.value = true
  try {
    const progress = Math.max(0, Math.min(100, Number(editForm.value.progress) || 0))
    const patch = {
      title: editForm.value.title.trim(),
      status: editForm.value.status,
      team_status: editForm.value.team_status,
      leader_name: editForm.value.leader_name.trim(),
      progress,
    }

    await tasksApi.update(editForm.value.id, patch as Partial<Task>)

    const index = tasks.value.findIndex((task) => task.id === editForm.value.id)
    const current = tasks.value[index]
    if (current) {
      tasks.value.splice(index, 1, {
        ...current,
        ...patch,
        title: patch.title || current.title,
        updated_at: new Date().toISOString(),
      })
    }

    editOpen.value = false
    showToast({ title: '任务管理信息已更新', variant: 'success' })
  } catch {
    showToast({
      title: '保存失败',
      description: '请确认当前账号仍具备任务管理权限。',
      variant: 'error',
    })
  } finally {
    saving.value = false
  }
}

function handleExport() {
  if (!canManageTasks.value) return
  showToast({ title: '已生成任务导出预览', variant: 'default' })
}

watch([keyword, statusFilter, teamFilter], resetPage)
watch(totalPages, (pages) => {
  if (currentPage.value > pages) currentPage.value = pages
})

onMounted(loadTasks)
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
                <p>{{ roleLabel }} · {{ canManageTasks ? '可管理全量任务' : '仅可查看任务' }}</p>
              </div>
            </div>
            <div class="profile-meta">
              <div><span>当前角色</span><strong>{{ roleLabel }}</strong></div>
              <div><span>管理权限</span><strong>{{ canManageTasks ? '已授权' : '未授权' }}</strong></div>
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

        <section class="hero-card" aria-label="任务管理概览">
          <div>
            <p class="section-label">Task Management</p>
            <h1>管理平台全量任务</h1>
            <p class="hero-copy">
              面向运营管理员与超级管理员，统一调整任务状态、团队状态、队长与进度，帮助需求转化后的任务持续推进。
            </p>
          </div>
          <OrdButton variant="primary" :disabled="!canManageTasks" @click="handleExport">导出任务</OrdButton>
        </section>

        <section class="summary-grid" aria-label="任务统计">
          <article class="summary-card" style="--accent: var(--ord-color-blue)">
            <strong>{{ stats.total }}</strong>
            <span>总任务</span>
          </article>
          <article class="summary-card" style="--accent: var(--ord-color-orange)">
            <strong>{{ stats.active }}</strong>
            <span>解决中</span>
          </article>
          <article class="summary-card" style="--accent: var(--ord-color-yellow)">
            <strong>{{ stats.pending }}</strong>
            <span>待处理</span>
          </article>
          <article class="summary-card" style="--accent: var(--ord-color-green)">
            <strong>{{ stats.done }}</strong>
            <span>已完成 / 已关闭</span>
          </article>
        </section>

        <section class="table-card" aria-label="任务列表">
          <div class="table-toolbar">
            <div>
              <p class="section-label">Task List</p>
              <h2>任务列表</h2>
              <p class="toolbar-note">可按任务状态、团队状态或关键字快速定位。点击编辑可调整任务管理字段。</p>
            </div>
            <div class="toolbar-actions">
              <OrdSearchBox
                v-model="keyword"
                placeholder="搜索任务、队长、需求编号"
                width="260px"
              />
              <OrdSelect v-model="statusFilter" :options="statusFilterOptions" placeholder="全部状态" />
              <OrdSelect v-model="teamFilter" :options="teamStatusFilterOptions" placeholder="全部团队" />
            </div>
          </div>

          <div class="table-scroll">
            <OrdTable>
              <OrdTableHeader>
                <OrdTableCell header>任务编号</OrdTableCell>
                <OrdTableCell header>任务详情</OrdTableCell>
                <OrdTableCell header>创建时间</OrdTableCell>
                <OrdTableCell header>任务状态</OrdTableCell>
                <OrdTableCell header>团队状态</OrdTableCell>
                <OrdTableCell header>队长</OrdTableCell>
                <OrdTableCell header>关联需求</OrdTableCell>
                <OrdTableCell header>进度</OrdTableCell>
                <OrdTableCell header>操作</OrdTableCell>
              </OrdTableHeader>

              <template v-if="loading">
                <OrdTableRow>
                  <OrdTableCell :colspan="9" class="empty-state">加载中...</OrdTableCell>
                </OrdTableRow>
              </template>
              <template v-else-if="pagedTasks.length === 0">
                <OrdTableRow>
                  <OrdTableCell :colspan="9" class="empty-state">暂无匹配任务，请调整筛选条件。</OrdTableCell>
                </OrdTableRow>
              </template>
              <template v-else>
                <OrdTableRow v-for="task in pagedTasks" :key="task.id">
                  <OrdTableCell><span class="id-text">{{ task.id }}</span></OrdTableCell>
                  <OrdTableCell>
                    <div class="detail-title">{{ task.title }}</div>
                    <div class="detail-sub">{{ task.description }}</div>
                  </OrdTableCell>
                  <OrdTableCell>{{ dateOnly(task.created_at) }}</OrdTableCell>
                  <OrdTableCell>
                    <span class="status-pill" :class="`status-pill--${statusVariant(task.status)}`">
                      {{ statusLabel(task.status) }}
                    </span>
                  </OrdTableCell>
                  <OrdTableCell>
                    <span class="status-pill" :class="`status-pill--${teamVariant(task.team_status)}`">
                      {{ teamStatusLabel(task.team_status) }}
                    </span>
                  </OrdTableCell>
                  <OrdTableCell>{{ task.leader_name || '-' }}</OrdTableCell>
                  <OrdTableCell><span class="id-text">{{ task.demand_id || '-' }}</span></OrdTableCell>
                  <OrdTableCell>
                    <div class="progress-wrap">
                      <div class="progress-meta">
                        <span>进度</span>
                        <strong>{{ task.progress }}%</strong>
                      </div>
                      <OrdProgress :value="task.progress" variant="gradient" />
                    </div>
                  </OrdTableCell>
                  <OrdTableCell>
                    <div class="row-actions">
                      <RouterLink class="detail-btn" :to="`/tasks/${task.id}`">详情</RouterLink>
                      <OrdButton
                        variant="primary"
                        size="sm"
                        :disabled="!canManageTasks"
                        @click="openEdit(task)"
                      >
                        编辑
                      </OrdButton>
                    </div>
                  </OrdTableCell>
                </OrdTableRow>
              </template>
            </OrdTable>
          </div>

          <div v-if="filteredTasks.length > 0" class="pagination" aria-label="分页导航">
            <span class="pagination-summary">共 {{ filteredTasks.length }} 条，第 {{ currentPage }} / {{ totalPages }} 页</span>
            <OrdPagination v-model:current-page="currentPage" :total="filteredTasks.length" :page-size="PAGE_SIZE" />
          </div>
        </section>
      </div>
    </main>

    <OrdDialog
      v-model:open="editOpen"
      title="编辑任务状态"
      description="任务编号与关联需求为系统字段，仅展示；其他管理字段可在此调整。"
    >
      <template #trigger></template>

      <div class="edit-form">
        <div class="form-grid">
          <div class="field">
            <label class="field-label">任务编号</label>
            <OrdInput :model-value="editForm.id" disabled />
          </div>
          <div class="field">
            <label class="field-label">关联需求</label>
            <OrdInput :model-value="editForm.demand_id || '-'" disabled />
          </div>
          <div class="field full">
            <label class="field-label">任务详情</label>
            <OrdInput v-model="editForm.title" />
          </div>
          <div class="field">
            <label class="field-label">任务状态</label>
            <OrdSelect v-model="editForm.status" :options="statusOptions" />
          </div>
          <div class="field">
            <label class="field-label">团队状态</label>
            <OrdSelect v-model="editForm.team_status" :options="teamStatusOptions" />
          </div>
          <div class="field">
            <label class="field-label">队长</label>
            <OrdInput v-model="editForm.leader_name" placeholder="输入队长昵称" />
          </div>
          <div class="field">
            <label class="field-label">进度</label>
            <OrdInput v-model="editForm.progress" type="number" min="0" max="100" />
          </div>
          <div class="field full">
            <label class="field-label">管理备注</label>
            <OrdTextarea
              v-model="editForm.note"
              placeholder="记录运营侧判断、阻塞点或下一步动作"
              :rows="3"
            />
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
.page-root {
  min-height: 100vh;
}

.brand-row {
  display: flex;
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
  flex-shrink: 0;
}

.brand-name {
  color: var(--ord-color-black);
  font-size: 20px;
  font-weight: 600;
  line-height: 1.15;
  letter-spacing: 0;
}

.brand-caption {
  display: block;
  margin-top: 2px;
  color: var(--ord-color-gray-500);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1.2px;
  text-transform: uppercase;
}

.profile-trigger {
  position: relative;
}

.profile-button {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  height: 42px;
  padding: 0 10px;
  color: var(--ord-color-black);
  background: var(--ord-color-white);
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-sm);
  cursor: pointer;
  font: inherit;
  transition: border-color var(--ord-transition-base), color var(--ord-transition-base);
}

.profile-button:hover {
  color: var(--ord-color-blue);
  border-color: var(--ord-color-blue);
}

.profile-name {
  font-size: 14px;
  font-weight: 600;
}

:deep(.ord-navbar__inner) {
  width: min(1460px, 100%);
  min-height: 76px;
  height: auto;
  margin: 0 auto;
  padding: 16px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  font-size: 16px;
}

:deep(.ord-navbar__actions) {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: nowrap;
  justify-content: flex-end;
}

:deep(.ord-navbar__brand) {
  flex-shrink: 0;
}

:deep(.ord-navbar__center) {
  flex: 1;
  display: flex;
  justify-content: center;
}

:deep(.ord-navbar) {
  position: fixed;
  inset: 0 0 auto;
  z-index: 20;
  height: auto;
  min-height: 76px;
  padding: 0 32px;
  background: rgba(255, 255, 255, 0.94);
  border-bottom: 1px solid rgba(216, 216, 216, 0.86);
  box-shadow: 0 18px 40px rgba(8, 8, 8, 0.08);
  backdrop-filter: blur(16px);
}

.nav-height-btn {
  height: 42px;
  padding: 0 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
}

.profile-card {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  width: 260px;
  padding: 16px;
  background: var(--ord-color-white);
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  opacity: 0;
  visibility: hidden;
  transform: translateY(-4px);
  transition: opacity 160ms ease, transform 160ms ease, visibility 160ms ease;
  z-index: 200;
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
  gap: 10px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--ord-color-border);
}

.profile-card h3 {
  margin: 0 0 4px;
  font-size: 16px;
}

.profile-card p {
  margin: 0;
  color: var(--ord-color-gray-500);
  font-size: 12px;
  line-height: 1.5;
}

.profile-meta {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding-top: 12px;
}

.profile-meta div {
  padding: 10px;
  background: #f7f9ff;
  border: 1px solid rgba(216, 216, 216, 0.7);
  border-radius: var(--ord-radius-sm);
}

.profile-meta span {
  display: block;
  color: var(--ord-color-gray-500);
  font-size: 11px;
}

.profile-meta strong {
  display: block;
  margin-top: 3px;
  font-size: 14px;
}

.logout-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 36px;
  margin-top: 12px;
  color: var(--ord-color-red);
  background: rgba(238, 29, 54, 0.08);
  border: 1px solid rgba(238, 29, 54, 0.18);
  border-radius: var(--ord-radius-sm);
  font-size: 13px;
  font-weight: 650;
}

.logout-link:hover {
  background: rgba(238, 29, 54, 0.12);
}

.page-shell {
  min-height: 100vh;
  padding: 112px 32px 48px;
  background:
    radial-gradient(circle at 7% 14%, rgba(20, 110, 245, 0.08), transparent 28%),
    radial-gradient(circle at 91% 18%, rgba(122, 61, 255, 0.08), transparent 26%),
    linear-gradient(180deg, #ffffff 0%, #f7f9ff 100%);
}

.management-frame {
  position: relative;
  width: min(1460px, 100%);
  margin: 0 auto;
  display: grid;
  gap: 16px;
}

.ambient-ring {
  position: fixed;
  width: 280px;
  height: 280px;
  right: 5%;
  top: 18%;
  border: 1px solid rgba(20, 110, 245, 0.14);
  border-radius: 50%;
  pointer-events: none;
  opacity: 0.45;
}

.ambient-node {
  position: fixed;
  width: 12px;
  height: 12px;
  left: 8%;
  bottom: 16%;
  background: var(--ord-color-green);
  border-radius: 50%;
  box-shadow: 38px -22px 0 rgba(122, 61, 255, 0.32), 70px 20px 0 rgba(255, 174, 19, 0.34);
  pointer-events: none;
  opacity: 0.45;
}

.hero-card,
.summary-card,
.table-card {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(216, 216, 216, 0.9);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
}

.hero-card {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  padding: 32px;
}

.hero-card::after {
  content: "";
  position: absolute;
  width: 190px;
  height: 190px;
  right: -72px;
  top: -94px;
  background: radial-gradient(circle, rgba(20, 110, 245, 0.14), transparent 68%);
  pointer-events: none;
}

.section-label {
  margin: 0 0 10px;
  color: var(--ord-color-blue);
  font-size: 12px;
  font-weight: 650;
  letter-spacing: 1.3px;
  text-transform: uppercase;
}

h1 {
  max-width: 760px;
  margin: 0 0 12px;
  font-size: clamp(34px, 4vw, 56px);
  line-height: 1.04;
  font-weight: 600;
  letter-spacing: 0;
}

.hero-copy {
  max-width: 760px;
  margin: 0;
  color: var(--ord-color-gray-500);
  font-size: 16px;
  line-height: 1.65;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.summary-card {
  position: relative;
  overflow: hidden;
  min-height: 112px;
  padding: 22px;
}

.summary-card::before {
  content: "";
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: var(--accent, var(--ord-color-blue));
}

.summary-card strong {
  display: block;
  margin-bottom: 8px;
  font-size: 32px;
  line-height: 1;
  font-weight: 600;
}

.summary-card span {
  color: var(--ord-color-gray-500);
  font-size: 14px;
  font-weight: 600;
}

.table-card {
  overflow: hidden;
}

.table-toolbar {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  padding: 24px;
  border-bottom: 1px solid var(--ord-color-border);
}

h2 {
  margin: 0 0 6px;
  font-size: 24px;
  line-height: 1.2;
  font-weight: 600;
}

.toolbar-note {
  margin: 0;
  color: var(--ord-color-gray-500);
  font-size: 14px;
  line-height: 1.65;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

.toolbar-actions :deep(.ord-search-box__input),
.toolbar-actions :deep(.ord-select__trigger) {
  height: 42px;
}

.toolbar-actions :deep(.ord-select__trigger) {
  min-width: 150px;
}

.table-scroll {
  width: 100%;
  overflow-x: auto;
}

.table-scroll :deep(.ord-table) {
  border: 0;
  border-radius: 0;
}

.table-scroll :deep(.ord-table__inner) {
  min-width: 1120px;
}

.table-scroll :deep(th),
.table-scroll :deep(td) {
  border-bottom: 1px solid rgba(216, 216, 216, 0.72);
  vertical-align: middle;
}

.table-scroll :deep(th) {
  background: #fbfcff;
}

.id-text {
  color: var(--ord-color-blue);
  font-weight: 650;
  white-space: nowrap;
}

.detail-title {
  margin-bottom: 4px;
  font-weight: 650;
  font-size: 14px;
}

.detail-sub {
  display: -webkit-box;
  overflow: hidden;
  color: var(--ord-color-gray-500);
  font-size: 12px;
  line-height: 1.4;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 8px;
  border-radius: var(--ord-radius-sm);
  font-size: 12px;
  font-weight: 650;
  white-space: nowrap;
}

.status-pill--blue {
  color: var(--ord-color-blue);
  background: rgba(20, 110, 245, 0.1);
}

.status-pill--orange {
  color: #b05a00;
  background: rgba(255, 174, 19, 0.16);
}

.status-pill--green {
  color: #008a15;
  background: rgba(0, 215, 34, 0.12);
}

.status-pill--gray {
  color: var(--ord-color-gray-500);
  background: rgba(90, 90, 90, 0.1);
}

.status-pill--purple {
  color: var(--ord-color-purple);
  background: rgba(122, 61, 255, 0.1);
}

.progress-wrap {
  width: 150px;
}

.progress-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 7px;
  color: var(--ord-color-gray-500);
  font-size: 12px;
  font-weight: 600;
}

.row-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-btn {
  min-width: 64px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 14px;
  color: var(--ord-color-blue);
  background: var(--ord-color-white);
  border: 1px solid var(--ord-color-blue);
  border-radius: var(--ord-radius-sm);
  font-size: 13px;
  font-weight: 650;
  text-decoration: none;
  white-space: nowrap;
  transition: background var(--ord-transition-base), color var(--ord-transition-base), transform var(--ord-transition-base);
}

.detail-btn:hover {
  color: var(--ord-color-white);
  background: var(--ord-color-blue);
  transform: translateX(6px);
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
  border-top: 1px solid var(--ord-color-border);
  background: rgba(255, 255, 255, 0.92);
}

.pagination-summary {
  color: var(--ord-color-gray-500);
  font-size: 13px;
  font-weight: 600;
}

.edit-form {
  padding: 4px 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.field {
  display: grid;
  gap: 7px;
}

.field.full {
  grid-column: 1 / -1;
}

.field-label {
  color: var(--ord-color-gray-700);
  font-size: 12px;
  font-weight: 650;
  letter-spacing: 0.8px;
  text-transform: uppercase;
}

@media (max-width: 992px) {
  .page-shell {
    padding: 112px 20px 32px;
  }

  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .hero-card,
  .table-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .toolbar-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  :deep(.ord-navbar) {
    padding: 0 16px;
  }

  .brand-caption,
  .profile-name {
    display: none;
  }

  .page-shell {
    padding: 96px 16px 32px;
  }

  .summary-grid,
  .form-grid {
    grid-template-columns: 1fr;
  }

  .pagination {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
