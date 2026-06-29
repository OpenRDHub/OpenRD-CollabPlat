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
import { adminDemandsApi } from '@/api/admin-demands'
import type { AdminDemand } from '@/api/admin-demands'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const { show: showToast } = useToast()

const PAGE_SIZE = 8

const demands = ref<AdminDemand[]>([])
const loading = ref(false)
const exportOpen = ref(false)
const keyword = ref('')
const reviewFilter = ref('all')
const convertFilter = ref('all')
const currentPage = ref(1)
const editOpen = ref(false)
const saving = ref(false)

const editForm = ref({
  id: '',
  title: '',
  submitted_at: '',
  publisher: '',
  task_id: '',
  review_status: '待审核' as AdminDemand['review_status'],
  convert_status: '未转化' as AdminDemand['convert_status'],
  progress: '0',
  feedback: '',
})

const reviewFilterOptions = [
  { value: 'all', label: '全部审核' },
  { value: '待审核', label: '待审核' },
  { value: '沟通中', label: '沟通中' },
  { value: '已转任务', label: '已转任务' },
  { value: '已关闭', label: '已关闭' },
]

const convertFilterOptions = [
  { value: 'all', label: '全部转化' },
  { value: '未转化', label: '未转化' },
  { value: '待评估', label: '待评估' },
  { value: '已转化', label: '已转化' },
  { value: '开发中', label: '开发中' },
  { value: '已完成', label: '已完成' },
]

const reviewStatusOptions = [
  { value: '待审核', label: '待审核' },
  { value: '沟通中', label: '沟通中' },
  { value: '已转任务', label: '已转任务' },
  { value: '已关闭', label: '已关闭' },
]

const convertStatusOptions = [
  { value: '未转化', label: '未转化' },
  { value: '待评估', label: '待评估' },
  { value: '已转化', label: '已转化' },
  { value: '开发中', label: '开发中' },
  { value: '已完成', label: '已完成' },
]

const ROLE_LABEL: Record<string, string> = {
  requester: '需求方',
  builder: '开发者',
  operator: '运营管理员',
  super_admin: '超级管理员',
}

const canManageDemands = computed(() => auth.hasPermission('demand:archive'))
const roleLabel = computed(() => ROLE_LABEL[auth.userRole] ?? '平台用户')

const stats = computed(() => ({
  total: demands.value.length,
  pending: demands.value.filter((d) => d.review_status === '待审核').length,
  talking: demands.value.filter((d) => d.review_status === '沟通中').length,
  converted: demands.value.filter((d) => d.review_status === '已转任务').length,
  closed: demands.value.filter((d) => d.review_status === '已关闭').length,
}))

const filteredDemands = computed(() => {
  let list = demands.value

  if (reviewFilter.value !== 'all') {
    list = list.filter((d) => d.review_status === reviewFilter.value)
  }

  if (convertFilter.value !== 'all') {
    list = list.filter((d) => d.convert_status === convertFilter.value)
  }

  const query = keyword.value.trim().toLowerCase()
  if (query) {
    list = list.filter((d) => {
      const haystack = [d.id, d.title, d.description, d.publisher, d.task_id]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
      return haystack.includes(query)
    })
  }

  return list
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredDemands.value.length / PAGE_SIZE)))

const pagedDemands = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return filteredDemands.value.slice(start, start + PAGE_SIZE)
})

function reviewVariant(status: string) {
  if (status === '待审核') return 'orange'
  if (status === '沟通中') return 'purple'
  if (status === '已转任务') return 'green'
  return 'gray'
}

function convertVariant(status: string) {
  if (status === '未转化') return 'gray'
  if (status === '待评估') return 'orange'
  if (status === '已转化') return 'blue'
  if (status === '开发中') return 'orange'
  if (status === '已完成') return 'green'
  return 'blue'
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

async function loadDemands() {
  loading.value = true
  try {
    const res = await adminDemandsApi.getList({ page: 1, page_size: 200 })
    demands.value = (res.data.items as AdminDemand[]) ?? []
  } catch {
    showToast({
      title: '加载失败',
      description: '无法获取需求列表，请稍后重试。',
      variant: 'error',
    })
  } finally {
    loading.value = false
  }
}

function openEdit(demand: AdminDemand) {
  if (!canManageDemands.value) return

  editForm.value = {
    id: demand.id,
    title: demand.title,
    submitted_at: demand.submitted_at,
    publisher: demand.publisher,
    task_id: demand.task_id || '',
    review_status: demand.review_status,
    convert_status: demand.convert_status,
    progress: String(demand.progress),
    feedback: demand.feedback,
  }
  editOpen.value = true
}

async function handleSave() {
  if (!canManageDemands.value || !editForm.value.id) return

  saving.value = true
  try {
    const progress = Math.max(0, Math.min(100, Number(editForm.value.progress) || 0))
    const patch = {
      title: editForm.value.title.trim(),
      task_id: editForm.value.task_id.trim() || undefined,
      review_status: editForm.value.review_status,
      convert_status: editForm.value.convert_status,
      progress,
      feedback: editForm.value.feedback.trim(),
    }

    await adminDemandsApi.updateDemand(editForm.value.id, patch)

    const index = demands.value.findIndex((d) => d.id === editForm.value.id)
    const current = demands.value[index]
    if (current) {
      demands.value.splice(index, 1, {
        ...current,
        ...patch,
        task_id: patch.task_id ?? null,
        title: patch.title || current.title,
        updated_at: new Date().toISOString(),
      })
    }

    editOpen.value = false
    showToast({ title: '需求管理信息已更新', variant: 'success' })
  } catch {
    showToast({
      title: '保存失败',
      description: '请确认当前账号仍具备需求管理权限。',
      variant: 'error',
    })
  } finally {
    saving.value = false
  }
}

function handleExport() {
  if (!canManageDemands.value) return
  exportOpen.value = true
}

function downloadCsv() {
  const items = filteredDemands.value
  const headers = ['需求编号', '标题', '发布者', '提交日期', '审核状态', '转化状态', '关联任务', '进度', '紧急程度', '反馈']
  const rows = items.map((d) => [
    d.id,
    d.title,
    d.publisher,
    d.submitted_at,
    d.review_status,
    d.convert_status,
    d.task_id ?? '',
    d.progress,
    d.urgency ?? '',
    d.feedback ?? '',
  ])
  const csvContent =
    '﻿' +
    [headers, ...rows]
      .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(','))
      .join('\r\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, '')
  const a = document.createElement('a')
  a.href = url
  a.download = `demands_${date}.csv`
  a.click()
  URL.revokeObjectURL(url)

  exportOpen.value = false
  showToast({ title: `已导出 ${items.length} 条需求`, variant: 'success' })
}

watch([keyword, reviewFilter, convertFilter], resetPage)
watch(totalPages, (pages) => {
  if (currentPage.value > pages) currentPage.value = pages
})

onMounted(loadDemands)
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
                <p>{{ roleLabel }} · {{ canManageDemands ? '可管理全量需求' : '仅可查看需求' }}</p>
              </div>
            </div>
            <div class="profile-meta">
              <div><span>当前角色</span><strong>{{ roleLabel }}</strong></div>
              <div><span>管理权限</span><strong>{{ canManageDemands ? '已授权' : '未授权' }}</strong></div>
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

        <section class="hero-card" aria-label="需求管理概览">
          <div>
            <p class="section-label">Demand Management</p>
            <h1>审核、沟通并转化需求</h1>
            <p class="hero-copy">
              面向运营管理员与超级管理员，统一处理全量需求：从待审核、沟通中到已转任务，维护转化状态与平台反馈。
            </p>
          </div>
          <OrdButton variant="primary" :disabled="!canManageDemands" @click="handleExport">导出需求</OrdButton>
        </section>

        <section class="summary-grid" aria-label="需求统计">
          <article class="summary-card" style="--accent: var(--ord-color-blue)">
            <strong>{{ stats.total }}</strong>
            <span>总需求</span>
          </article>
          <article class="summary-card" style="--accent: var(--ord-color-yellow)">
            <strong>{{ stats.pending }}</strong>
            <span>待审核</span>
          </article>
          <article class="summary-card" style="--accent: var(--ord-color-purple)">
            <strong>{{ stats.talking }}</strong>
            <span>沟通中</span>
          </article>
          <article class="summary-card" style="--accent: var(--ord-color-green)">
            <strong>{{ stats.converted }}</strong>
            <span>已转任务</span>
          </article>
          <article class="summary-card" style="--accent: var(--ord-color-gray-500)">
            <strong>{{ stats.closed }}</strong>
            <span>已关闭</span>
          </article>
        </section>

        <section class="table-card" aria-label="需求列表">
          <div class="table-toolbar">
            <div>
              <p class="section-label">Demand List</p>
              <h2>需求列表</h2>
              <p class="toolbar-note">可按审核状态、转化状态或关键字快速定位。点击编辑可调整需求管理字段。</p>
            </div>
            <div class="toolbar-actions">
              <OrdSearchBox
                v-model="keyword"
                placeholder="搜索需求、发布者、任务编号"
                width="260px"
              />
              <OrdSelect v-model="reviewFilter" :options="reviewFilterOptions" placeholder="全部审核" />
              <OrdSelect v-model="convertFilter" :options="convertFilterOptions" placeholder="全部转化" />
            </div>
          </div>

          <div class="table-scroll">
            <OrdTable>
              <OrdTableHeader>
                <OrdTableCell header>需求编号</OrdTableCell>
                <OrdTableCell header>需求详情</OrdTableCell>
                <OrdTableCell header>提交时间</OrdTableCell>
                <OrdTableCell header>审核状态</OrdTableCell>
                <OrdTableCell header>转化状态</OrdTableCell>
                <OrdTableCell header>发布者</OrdTableCell>
                <OrdTableCell header>关联任务</OrdTableCell>
                <OrdTableCell header>进度</OrdTableCell>
                <OrdTableCell header>操作</OrdTableCell>
              </OrdTableHeader>

              <template v-if="loading">
                <OrdTableRow>
                  <OrdTableCell :colspan="9" class="empty-state">加载中...</OrdTableCell>
                </OrdTableRow>
              </template>
              <template v-else-if="pagedDemands.length === 0">
                <OrdTableRow>
                  <OrdTableCell :colspan="9" class="empty-state">暂无匹配需求，请调整筛选条件。</OrdTableCell>
                </OrdTableRow>
              </template>
              <template v-else>
                <OrdTableRow v-for="demand in pagedDemands" :key="demand.id">
                  <OrdTableCell><span class="id-text">{{ demand.id }}</span></OrdTableCell>
                  <OrdTableCell>
                    <div class="detail-title">{{ demand.title }}</div>
                    <div class="detail-sub">{{ demand.description }}</div>
                  </OrdTableCell>
                  <OrdTableCell>{{ demand.submitted_at }}</OrdTableCell>
                  <OrdTableCell>
                    <span class="status-pill" :class="`status-pill--${reviewVariant(demand.review_status)}`">
                      {{ demand.review_status }}
                    </span>
                  </OrdTableCell>
                  <OrdTableCell>
                    <span class="status-pill" :class="`status-pill--${convertVariant(demand.convert_status)}`">
                      {{ demand.convert_status }}
                    </span>
                  </OrdTableCell>
                  <OrdTableCell>{{ demand.publisher }}</OrdTableCell>
                  <OrdTableCell>
                    <span class="id-text">{{ demand.task_id || '暂未生成' }}</span>
                  </OrdTableCell>
                  <OrdTableCell>
                    <div class="progress-wrap">
                      <div class="progress-meta">
                        <span>进度</span>
                        <strong>{{ demand.progress }}%</strong>
                      </div>
                      <OrdProgress :value="demand.progress" variant="gradient" />
                    </div>
                  </OrdTableCell>
                  <OrdTableCell>
                    <div class="row-actions">
                      <RouterLink class="detail-btn" :to="`/demands/${demand.id}`">详情</RouterLink>
                      <OrdButton
                        variant="primary"
                        size="sm"
                        :disabled="!canManageDemands"
                        @click="openEdit(demand)"
                      >
                        编辑
                      </OrdButton>
                    </div>
                  </OrdTableCell>
                </OrdTableRow>
              </template>
            </OrdTable>
          </div>

          <div v-if="filteredDemands.length > 0" class="pagination" aria-label="分页导航">
            <span class="pagination-summary">共 {{ filteredDemands.length }} 条，第 {{ currentPage }} / {{ totalPages }} 页</span>
            <OrdPagination v-model:current-page="currentPage" :total="filteredDemands.length" :page-size="PAGE_SIZE" />
          </div>
        </section>
      </div>
    </main>

    <OrdDialog
      v-model:open="editOpen"
      title="编辑需求处理信息"
      description="需求编号、提交时间与发布者为只读信息；运营侧可维护审核、转化、关联任务与反馈。"
    >
      <template #trigger></template>

      <div class="edit-form">
        <div class="form-grid">
          <div class="field">
            <label class="field-label">需求编号</label>
            <OrdInput :model-value="editForm.id" disabled />
          </div>
          <div class="field">
            <label class="field-label">发布者</label>
            <OrdInput :model-value="editForm.publisher" disabled />
          </div>
          <div class="field">
            <label class="field-label">提交时间</label>
            <OrdInput :model-value="editForm.submitted_at" disabled />
          </div>
          <div class="field">
            <label class="field-label">关联任务</label>
            <OrdInput v-model="editForm.task_id" placeholder="如 TASK-1042 或留空" />
          </div>
          <div class="field full">
            <label class="field-label">需求详情</label>
            <OrdInput v-model="editForm.title" />
          </div>
          <div class="field">
            <label class="field-label">审核状态</label>
            <OrdSelect v-model="editForm.review_status" :options="reviewStatusOptions" />
          </div>
          <div class="field">
            <label class="field-label">转化状态</label>
            <OrdSelect v-model="editForm.convert_status" :options="convertStatusOptions" />
          </div>
          <div class="field">
            <label class="field-label">进度</label>
            <OrdInput v-model="editForm.progress" type="number" min="0" max="100" />
          </div>
          <div class="field full">
            <label class="field-label">平台反馈</label>
            <OrdTextarea
              v-model="editForm.feedback"
              placeholder="记录需求审核意见、补充材料或转化结论"
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

    <OrdDialog
      v-model:open="exportOpen"
      title="导出需求预览"
      :description="`共 ${filteredDemands.length} 条需求将被导出，内容与当前筛选条件一致。`"
    >
      <template #trigger></template>

      <div class="export-preview">
        <div class="export-preview-scroll">
          <OrdTable>
            <OrdTableHeader>
              <OrdTableCell header>需求编号</OrdTableCell>
              <OrdTableCell header>标题</OrdTableCell>
              <OrdTableCell header>发布者</OrdTableCell>
              <OrdTableCell header>提交日期</OrdTableCell>
              <OrdTableCell header>审核状态</OrdTableCell>
              <OrdTableCell header>转化状态</OrdTableCell>
              <OrdTableCell header>关联任务</OrdTableCell>
            </OrdTableHeader>
            <template v-if="filteredDemands.length === 0">
              <OrdTableRow>
                <OrdTableCell :colspan="7" class="empty-state">当前筛选条件下无可导出数据。</OrdTableCell>
              </OrdTableRow>
            </template>
            <template v-else>
              <OrdTableRow v-for="d in filteredDemands" :key="d.id">
                <OrdTableCell><span class="id-text">{{ d.id }}</span></OrdTableCell>
                <OrdTableCell>{{ d.title }}</OrdTableCell>
                <OrdTableCell>{{ d.publisher }}</OrdTableCell>
                <OrdTableCell>{{ d.submitted_at }}</OrdTableCell>
                <OrdTableCell>
                  <span class="status-pill" :class="`status-pill--${reviewVariant(d.review_status)}`">
                    {{ d.review_status }}
                  </span>
                </OrdTableCell>
                <OrdTableCell>
                  <span class="status-pill" :class="`status-pill--${convertVariant(d.convert_status)}`">
                    {{ d.convert_status }}
                  </span>
                </OrdTableCell>
                <OrdTableCell><span class="id-text">{{ d.task_id || '—' }}</span></OrdTableCell>
              </OrdTableRow>
            </template>
          </OrdTable>
        </div>
      </div>

      <template #footer>
        <OrdButton variant="ghost" @click="exportOpen = false">取消</OrdButton>
        <OrdButton variant="primary" :disabled="filteredDemands.length === 0" @click="downloadCsv">下载 CSV</OrdButton>
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
  flex-shrink: 0;
}

.brand-name {
  color: var(--ord-color-black);
  font-size: 20px;
  font-weight: 600;
  line-height: 1.15;
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
  cursor: pointer;
  font: inherit;
  transition: background var(--ord-transition-base);
}

.logout-link:hover {
  background: rgba(238, 29, 54, 0.12);
}

.page-shell {
  min-height: 100vh;
  padding: 112px 32px 48px;
  background:
    radial-gradient(circle at 8% 16%, rgba(255, 174, 19, 0.12), transparent 27%),
    radial-gradient(circle at 92% 14%, rgba(20, 110, 245, 0.08), transparent 26%),
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
  border: 1px solid rgba(255, 174, 19, 0.18);
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
  background: var(--ord-color-blue);
  border-radius: 50%;
  box-shadow: 38px -22px 0 rgba(237, 82, 203, 0.26), 70px 20px 0 rgba(0, 215, 34, 0.3);
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
  background: radial-gradient(circle, rgba(255, 174, 19, 0.18), transparent 68%);
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
  grid-template-columns: repeat(5, 1fr);
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

@media (max-width: 1180px) {
  .summary-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 992px) {
  .page-shell {
    padding: 112px 20px 32px;
  }

  .summary-grid {
    grid-template-columns: repeat(3, 1fr);
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

.export-preview {
  margin-top: var(--ord-space-2);
}

.export-preview-scroll {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid var(--ord-color-gray-200);
  border-radius: var(--ord-radius-sm);
}
</style>
