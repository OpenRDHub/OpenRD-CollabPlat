<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import TopNavbar from '@/components/TopNavbar.vue'
import { tasksApi } from '@/api/tasks'
import { useToast } from '@/components/ui'

const { show: showToast } = useToast()

type TaskStage = 'pending' | 'doing' | 'done'

interface MyTask {
  id: string
  title: string
  description: string
  status: string
  team_status: string
  progress: number
  created_at: string
  my_role: string
  my_stage: TaskStage
}

const STATUS_LABEL: Record<string, string> = {
  recruiting: '待处理',
  in_progress: '解决中',
  completed: '已完成',
  closed: '已完成',
  reviewing: '解决中',
}

const TEAM_STATUS_LABEL: Record<string, string> = {
  forming: '招募中',
  collaborating: '协作中',
  accepted: '已验收',
  closed: '已关闭',
}

const STAGE_COPY: Record<string, string> = {
  all: '当前展示全部任务，可通过状态 Tab 和筛选器快速定位。',
  pending: '当前仅展示需要我立即响应的任务。',
  doing: '当前仅展示正在推进中的任务。',
  done: '当前仅展示已完成或已验收的任务。',
}

const tasks = ref<MyTask[]>([])
const loading = ref(false)
const searchKeyword = ref('')
const activeTab = ref<'all' | TaskStage>('all')
const currentPage = ref(1)
const PAGE_SIZE = 3

async function loadTasks() {
  loading.value = true
  try {
    const res = await tasksApi.getList({ my: true, page: 1, page_size: 100 })
    tasks.value = (res.data.items as unknown as MyTask[]) ?? []
  } catch {
    showToast({ title: '加载失败', description: '无法获取我的任务列表', variant: 'error' })
  } finally {
    loading.value = false
  }
}

const summaryStats = computed(() => ({
  total: tasks.value.length,
  pending: tasks.value.filter((t) => t.my_stage === 'pending').length,
  doing: tasks.value.filter((t) => t.my_stage === 'doing').length,
  done: tasks.value.filter((t) => t.my_stage === 'done').length,
}))

const filteredTasks = computed(() => {
  let list = tasks.value
  if (activeTab.value !== 'all') list = list.filter((t) => t.my_stage === activeTab.value)
  if (searchKeyword.value.trim()) {
    const kw = searchKeyword.value.trim().toLowerCase()
    list = list.filter(
      (t) =>
        t.title.toLowerCase().includes(kw) ||
        t.description.toLowerCase().includes(kw) ||
        t.my_role.toLowerCase().includes(kw) ||
        t.id.toLowerCase().includes(kw),
    )
  }
  return list
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredTasks.value.length / PAGE_SIZE)))

const pagedTasks = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return filteredTasks.value.slice(start, start + PAGE_SIZE)
})

const paginationStart = computed(() =>
  filteredTasks.value.length === 0 ? 0 : (currentPage.value - 1) * PAGE_SIZE + 1,
)
const paginationEnd = computed(() =>
  Math.min(currentPage.value * PAGE_SIZE, filteredTasks.value.length),
)

function setTab(tab: 'all' | TaskStage) {
  activeTab.value = tab
  currentPage.value = 1
}

function onSearch() {
  currentPage.value = 1
}

function statusClass(status: string) {
  const label = STATUS_LABEL[status] ?? status
  if (label === '待处理') return 'pending'
  if (label === '解决中') return 'doing'
  if (label === '已完成') return 'done'
  return 'doing'
}

function handleEsc(e: KeyboardEvent) {
  if (e.key === 'Escape') searchKeyword.value = ''
}

onMounted(() => {
  loadTasks()
  document.addEventListener('keydown', handleEsc)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEsc)
})
</script>

<template>
  <div class="page-shell">
    <TopNavbar />

    <main class="content-shell">
      <section class="task-frame" aria-labelledby="pageTitle">
        <!-- Hero -->
        <div class="hero-card">
          <div>
            <p class="eyebrow">My Tasks</p>
            <h1 id="pageTitle">我的任务</h1>
            <p class="hero-copy">
              以参与者视角聚合我负责、参与、待处理和已完成的任务，列表展示方式延续任务大厅，便于快速跳转到独立任务详情页。
            </p>
          </div>
          <aside class="focus-card" aria-label="当前关注事项">
            <span class="focus-label">Focus Today</span>
            <strong class="focus-count">{{ summaryStats.pending }} 项待处理</strong>
            <p>优先处理接口联调、加入申请审核和里程碑确认，保持协作链路清晰。</p>
          </aside>
        </div>

        <!-- Summary -->
        <div class="summary-grid" aria-label="我的任务概览">
          <article class="summary-card">
            <p class="summary-label">全部任务</p>
            <p class="summary-value">{{ summaryStats.total }}</p>
            <p class="summary-desc">我参与或负责的任务总数</p>
          </article>
          <article class="summary-card summary-card--orange">
            <p class="summary-label">待我处理</p>
            <p class="summary-value">{{ summaryStats.pending }}</p>
            <p class="summary-desc">需要我立即响应的事项</p>
          </article>
          <article class="summary-card summary-card--green">
            <p class="summary-label">进行中</p>
            <p class="summary-value">{{ summaryStats.doing }}</p>
            <p class="summary-desc">当前正在推进的协作任务</p>
          </article>
          <article class="summary-card summary-card--purple">
            <p class="summary-label">已完成</p>
            <p class="summary-value">{{ summaryStats.done }}</p>
            <p class="summary-desc">已完成交付或验收的任务</p>
          </article>
        </div>

        <!-- Task List Card -->
        <section class="list-card" aria-label="我的任务列表">
          <div class="list-toolbar">
            <div class="toolbar-top">
              <div>
                <h2 class="toolbar-title">任务列表</h2>
                <p class="toolbar-note">{{ STAGE_COPY[activeTab] }}</p>
              </div>
              <div class="toolbar-actions">
                <div class="select-wrap">
                  <select
                    class="status-filter"
                    v-model="activeTab"
                    @change="currentPage = 1"
                    aria-label="按任务状态筛选"
                  >
                    <option value="all">全部</option>
                    <option value="pending">待我处理</option>
                    <option value="doing">进行中</option>
                    <option value="done">已完成</option>
                  </select>
                  <svg class="select-arrow" viewBox="0 0 12 8" fill="none" aria-hidden="true">
                    <path d="M1 1.5l5 5 5-5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
                <input
                  class="search-box"
                  v-model="searchKeyword"
                  @input="onSearch"
                  type="search"
                  placeholder="搜索任务、角色、待处理动作"
                  aria-label="搜索任务"
                />
              </div>
            </div>
            <div class="tab-list" role="tablist" aria-label="任务状态切换">
              <button
                v-for="tab in (['all', 'pending', 'doing', 'done'] as const)"
                :key="tab"
                class="tab-button"
                :class="{ 'is-active': activeTab === tab }"
                type="button"
                @click="setTab(tab)"
              >
                {{ { all: '全部', pending: '待我处理', doing: '进行中', done: '已完成' }[tab] }}
              </button>
            </div>
          </div>

          <div class="task-list" role="region" aria-label="任务表格">
            <div class="task-header" aria-hidden="true">
              <span>任务详情</span>
              <span>创建时间</span>
              <span>任务状态</span>
              <span>团队状态</span>
              <span>进度</span>
              <span>我的角色</span>
              <span>操作</span>
            </div>

            <div v-if="loading" class="empty-state is-visible">加载中…</div>

            <template v-else>
              <article
                v-for="task in pagedTasks"
                :key="task.id"
                class="task-row"
              >
                <div>
                  <span class="task-title">{{ task.title }}</span>
                  <span class="task-desc">{{ task.id }} · {{ task.description }}</span>
                </div>
                <span>{{ task.created_at.slice(0, 10) }}</span>
                <span>
                  <span class="status-badge" :class="statusClass(task.status)">
                    {{ STATUS_LABEL[task.status] ?? task.status }}
                  </span>
                </span>
                <span>
                  <span class="team-badge">
                    {{ TEAM_STATUS_LABEL[task.team_status] ?? task.team_status }}
                  </span>
                </span>
                <div class="progress-wrap">
                  <div class="progress-line">
                    <span :style="{ width: task.progress + '%' }"></span>
                  </div>
                  <span class="progress-text">{{ task.progress }}%</span>
                </div>
                <span><span class="role-badge">{{ task.my_role }}</span></span>
                <RouterLink class="detail-button" :to="`/tasks/${task.id}`">
                  查看详情
                </RouterLink>
              </article>

              <div
                class="empty-state"
                :class="{ 'is-visible': filteredTasks.length === 0 && !loading }"
              >
                没有匹配的任务，试试切换状态或清空搜索。
              </div>
            </template>
          </div>

          <div class="pagination" aria-label="分页导航" v-if="filteredTasks.length > 0">
            <span class="pagination-summary">
              共 {{ filteredTasks.length }} 条，第 {{ paginationStart }}-{{ paginationEnd }} 条，
              第 {{ currentPage }} / {{ totalPages }} 页
            </span>
            <div class="pagination-actions">
              <button
                class="page-button"
                type="button"
                :disabled="currentPage === 1"
                @click="currentPage--"
              >上一页</button>
              <button class="page-button is-active" type="button" disabled>{{ currentPage }}</button>
              <button
                class="page-button"
                type="button"
                :disabled="currentPage === totalPages"
                @click="currentPage++"
              >下一页</button>
            </div>
          </div>
        </section>
      </section>
    </main>
  </div>
</template>

<style scoped>
.page-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at 12% 12%, rgba(20, 110, 245, 0.08), transparent 28%),
    radial-gradient(circle at 86% 18%, rgba(122, 61, 255, 0.06), transparent 24%),
    radial-gradient(circle at 80% 86%, rgba(255, 174, 19, 0.052), transparent 28%),
    linear-gradient(135deg, #ffffff 0%, #f7f9ff 100%);
}

.content-shell {
  display: flex;
  justify-content: center;
  min-height: 100vh;
  padding: 96px 32px 32px;
}

.task-frame {
  position: relative;
  display: grid;
  gap: 18px;
  width: min(1460px, 100%);
  align-content: start;
}

.task-frame::before,
.task-frame::after {
  content: "";
  position: absolute;
  z-index: 0;
  border: 1px solid rgba(216, 216, 216, 0.7);
  background: rgba(255, 255, 255, 0.45);
}

.task-frame::before {
  width: 180px;
  height: 86px;
  top: 96px;
  right: 42px;
  transform: rotate(-2deg);
}

.task-frame::after {
  width: 108px;
  height: 108px;
  right: 214px;
  bottom: 56px;
  transform: rotate(4deg);
}

.hero-card {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 24px;
  padding: 28px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(216, 216, 216, 0.86);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
  z-index: 1;
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

.eyebrow {
  margin: 0 0 10px;
  color: var(--ord-color-blue);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.4px;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  color: var(--ord-color-black);
  font-size: clamp(34px, 4vw, 56px);
  font-weight: 600;
  line-height: 1.04;
  letter-spacing: -0.6px;
}

.hero-copy {
  max-width: 720px;
  margin: 16px 0 0;
  color: var(--ord-color-gray-700);
  font-size: 16px;
  line-height: 1.65;
}

.focus-card {
  position: relative;
  z-index: 1;
  display: grid;
  align-content: center;
  gap: 12px;
  padding: 18px;
  color: var(--ord-color-white);
  background: var(--ord-color-black);
  border-radius: var(--ord-radius-md);
}

.focus-label {
  width: max-content;
  padding: 5px 8px;
  background: rgba(20, 110, 245, 0.9);
  border-radius: var(--ord-radius-sm);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.focus-count {
  font-size: 26px;
  font-weight: 600;
  line-height: 1.1;
}

.focus-card p {
  margin: 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  line-height: 1.55;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  z-index: 1;
}

.summary-card {
  min-height: 106px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(216, 216, 216, 0.86);
  border-top: 4px solid var(--ord-color-blue);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
}

.summary-card--orange { border-top-color: var(--ord-color-orange); }
.summary-card--green { border-top-color: var(--ord-color-green); }
.summary-card--purple { border-top-color: var(--ord-color-purple); }

.summary-label {
  margin: 0;
  color: var(--ord-color-gray-500);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.1px;
  text-transform: uppercase;
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

.list-card {
  overflow: hidden;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(216, 216, 216, 0.86);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
  z-index: 1;
}

.list-toolbar {
  display: grid;
  gap: 16px;
  padding: 18px;
  border-bottom: 1px solid #ececec;
}

.toolbar-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
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
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 10px;
}

.search-box,
.status-filter {
  height: 42px;
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-sm);
  background: #fff;
  color: var(--ord-color-black);
  font-size: 14px;
  font-family: inherit;
  font-weight: 500;
  outline: none;
  transition: border-color var(--ord-transition-base), box-shadow var(--ord-transition-base);
}

.search-box {
  width: 260px;
  padding: 0 12px;
}

.select-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.select-wrap .select-arrow {
  position: absolute;
  right: 12px;
  width: 12px;
  height: 8px;
  color: var(--ord-color-gray-500);
  pointer-events: none;
  transition: color var(--ord-transition-base);
}

.select-wrap:focus-within .select-arrow {
  color: var(--ord-color-blue);
}

.status-filter {
  width: 140px;
  padding: 0 34px 0 12px;
  appearance: none;
  -webkit-appearance: none;
  cursor: pointer;
}

.search-box:focus,
.status-filter:focus {
  border-color: var(--ord-color-blue);
  box-shadow: 0 0 0 4px rgba(20, 110, 245, 0.12);
}

.select-wrap:focus-within .status-filter {
  border-color: var(--ord-color-blue);
  box-shadow: 0 0 0 4px rgba(20, 110, 245, 0.12);
}

.tab-list {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px;
  width: max-content;
  max-width: 100%;
  overflow-x: auto;
  background: #f5f5f5;
  border: 1px solid #ececec;
  border-radius: var(--ord-radius-md);
}

.tab-button {
  min-width: 106px;
  height: 36px;
  padding: 0 14px;
  color: var(--ord-color-gray-700);
  background: transparent;
  border: 0;
  border-radius: var(--ord-radius-sm);
  font-size: 13px;
  font-family: inherit;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
  transition: background var(--ord-transition-base), color var(--ord-transition-base);
}

.tab-button.is-active {
  color: var(--ord-color-white);
  background: var(--ord-color-black);
}

.task-header,
.task-row {
  display: grid;
  grid-template-columns: minmax(280px, 2fr) 130px 120px 120px minmax(150px, 1fr) 150px 112px;
  gap: 14px;
  align-items: center;
  min-width: 1240px;
}

.task-header {
  padding: 13px 18px;
  color: var(--ord-color-gray-500);
  background: #fafafa;
  border-bottom: 1px solid #ececec;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.8px;
  text-transform: uppercase;
}

.task-list {
  overflow-x: auto;
}

.task-row {
  padding: 16px 18px;
  border-bottom: 1px solid #ececec;
  color: var(--ord-color-gray-700);
  font-size: 13px;
}

.task-row:last-child {
  border-bottom: 0;
}

.task-title {
  display: block;
  color: var(--ord-color-black);
  font-size: 15px;
  font-weight: 700;
  line-height: 1.35;
}

.task-desc {
  display: block;
  margin-top: 5px;
  color: var(--ord-color-gray-500);
  font-size: 12px;
  line-height: 1.45;
}

.status-badge,
.team-badge,
.role-badge {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: var(--ord-radius-sm);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.status-badge.pending { color: #b27600; background: rgba(255, 174, 19, 0.16); }
.status-badge.doing { color: var(--ord-color-blue); background: rgba(20, 110, 245, 0.08); }
.status-badge.done { color: #009e19; background: rgba(0, 215, 34, 0.12); }
.team-badge { color: var(--ord-color-purple); background: rgba(122, 61, 255, 0.1); }
.role-badge { color: var(--ord-color-gray-700); background: #f4f4f4; }

.progress-wrap {
  display: grid;
  gap: 7px;
}

.progress-line {
  height: 8px;
  overflow: hidden;
  background: #ededed;
  border-radius: 999px;
}

.progress-line span {
  display: block;
  height: 100%;
  background: var(--ord-color-blue);
  border-radius: inherit;
}

.progress-text {
  color: var(--ord-color-gray-500);
  font-size: 12px;
}

.detail-button {
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 88px;
  padding: 0 14px;
  color: var(--ord-color-white);
  background: var(--ord-color-blue);
  border: 1px solid var(--ord-color-blue);
  border-radius: var(--ord-radius-sm);
  font-size: 13px;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: background var(--ord-transition-base), box-shadow var(--ord-transition-base), transform var(--ord-transition-base);
}

.detail-button:hover {
  background: var(--ord-color-blue-hover);
  border-color: var(--ord-color-blue-hover);
  box-shadow: 0 14px 28px rgba(20, 110, 245, 0.22);
  transform: translateX(6px);
}

.empty-state {
  display: none;
  padding: 42px 18px;
  text-align: center;
  color: var(--ord-color-gray-500);
  border-top: 1px solid #ececec;
}

.empty-state.is-visible {
  display: block;
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
  line-height: 1.45;
}

.pagination-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-button {
  min-width: 34px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 12px;
  color: var(--ord-color-black);
  background: var(--ord-color-white);
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-sm);
  cursor: pointer;
  font-size: 13px;
  font-family: inherit;
  font-weight: 650;
  transition: transform var(--ord-transition-base), border-color var(--ord-transition-base),
    color var(--ord-transition-base), background var(--ord-transition-base);
}

.page-button:hover:not(:disabled) {
  color: var(--ord-color-blue);
  border-color: var(--ord-color-blue);
  transform: translateX(6px);
}

.page-button.is-active {
  color: var(--ord-color-white);
  background: var(--ord-color-blue);
  border-color: var(--ord-color-blue);
}

.page-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

@media (max-width: 992px) {
  .hero-card { grid-template-columns: 1fr; }
  .summary-grid { grid-template-columns: repeat(2, 1fr); }
  .toolbar-top { align-items: stretch; flex-direction: column; }
  .toolbar-actions { justify-content: flex-start; }
  .search-box { width: min(100%, 340px); }
}

@media (max-width: 768px) {
  .content-shell { padding: 92px 16px 24px; }
  .summary-grid { grid-template-columns: 1fr; }
  .tab-list { width: 100%; }
  .tab-button { flex: 1; }
  .pagination { align-items: stretch; flex-direction: column; }
  .pagination-actions { justify-content: space-between; }
  .page-button { flex: 1; }
}
</style>
