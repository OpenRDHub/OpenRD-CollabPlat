<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { OrdButton, OrdBadge, OrdProgress } from '@/components/ui'
import TopNavbar from '@/components/TopNavbar.vue'
import { tasksApi } from '@/api/tasks'
import { demandsApi } from '@/api/demands'
import { statsApi } from '@/api/stats'
import type { PlatformStats } from '@/api/stats'

const router = useRouter()

const platformStats = ref<PlatformStats>({
  tasks_total: 0,
  tasks_in_progress: 0,
  tasks_completed: 0,
  tasks_closed: 0,
  users_requester: 0,
  users_builder: 0,
})

// 状态
const activeTab = ref<'tasks' | 'demands'>('tasks')
const searchKeyword = ref('')
const currentPage = ref({ tasks: 1, demands: 1 })
const pageSize = 5

interface HallCard {
  id: string
  title: string
  desc: string
  date: string
  status: string
  statusClass: string
  team: string
  progressLabel: string
  progress: number
}

const tasksHallData = ref<HallCard[]>([])
const demandsHallData = ref<HallCard[]>([])

const TASK_STATUS_MAP: Record<string, { label: string; cls: string; progressLabel: string }> = {
  in_progress: { label: '解决中', cls: 'running', progressLabel: '进行中' },
  recruiting:  { label: '招募中', cls: 'recruiting', progressLabel: '招募中' },
  completed:   { label: '已完成', cls: 'done', progressLabel: '已验收' },
  closed:      { label: '已关闭', cls: 'closed', progressLabel: '已归档' },
  reviewing:   { label: '审核中', cls: 'running', progressLabel: '审核中' },
}

const TEAM_STATUS_MAP: Record<string, string> = {
  forming:       '招募中',
  collaborating: '协作中',
  accepted:      '已完成',
  closed:        '已归档',
}

const DEMAND_STATUS_MAP: Record<string, { cls: string; team: string; progressLabel: string }> = {
  pending:        { cls: 'review',     team: '未转任务',    progressLabel: '审核中' },
  pending_review: { cls: 'review',     team: '未转任务',    progressLabel: '待审核' },
  reviewing:      { cls: 'running',    team: '产品经理跟进', progressLabel: '沟通中' },
  converted:      { cls: 'recruiting', team: '招募中',      progressLabel: '已立项' },
  linked:         { cls: 'recruiting', team: '已关联',      progressLabel: '已关联' },
  rejected:       { cls: 'closed',     team: '已驳回',      progressLabel: '已关闭' },
  archived:       { cls: 'closed',     team: '已完成',      progressLabel: '已关闭' },
}

async function loadTasks() {
  try {
    const res = await tasksApi.getList({ page_size: 50 })
    tasksHallData.value = (res.data?.items ?? []).map((t) => {
      const s = TASK_STATUS_MAP[t.status] ?? { label: '进行中', cls: 'gray', progressLabel: '进行中' }
      return {
        id: t.id,
        title: t.title,
        desc: t.description,
        date: t.created_at.slice(0, 10),
        status: s.label,
        statusClass: s.cls,
        team: TEAM_STATUS_MAP[t.team_status] ?? '组队中',
        progressLabel: s.progressLabel,
        progress: t.progress,
      }
    })
  } catch {}
}

async function loadDemands() {
  try {
    const res = await demandsApi.getList({ page_size: 50 })
    demandsHallData.value = (res.data?.items ?? []).map((d) => {
      const s = DEMAND_STATUS_MAP[d.status] ?? { cls: 'gray', team: '未转任务', progressLabel: '处理中' }
      return {
        id: d.id,
        title: d.title,
        desc: d.description,
        date: d.created_at.slice(0, 10),
        status: s.progressLabel,
        statusClass: s.cls,
        team: s.team,
        progressLabel: s.progressLabel,
        progress: d.progress,
      }
    })
  } catch {}
}

onMounted(() => {
  loadTasks()
  loadDemands()
  statsApi.getPlatformStats().then(res => {
    if (res.data) platformStats.value = res.data
  }).catch(() => {})
})

// 筛选后的数据
const filteredTasks = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  return tasksHallData.value.filter(item => {
    if (!keyword) return true
    const text = `${item.id} ${item.title} ${item.desc} ${item.status} ${item.team} ${item.progressLabel}`.toLowerCase()
    return text.includes(keyword)
  })
})

const filteredDemands = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  return demandsHallData.value.filter(item => {
    if (!keyword) return true
    const text = `${item.id} ${item.title} ${item.desc} ${item.status} ${item.team} ${item.progressLabel}`.toLowerCase()
    return text.includes(keyword)
  })
})

// 分页数据
const paginatedTasks = computed(() => {
  const start = (currentPage.value.tasks - 1) * pageSize
  return filteredTasks.value.slice(start, start + pageSize)
})

const paginatedDemands = computed(() => {
  const start = (currentPage.value.demands - 1) * pageSize
  return filteredDemands.value.slice(start, start + pageSize)
})

const totalTasksPages = computed(() => Math.max(1, Math.ceil(filteredTasks.value.length / pageSize)))
const totalDemandsPages = computed(() => Math.max(1, Math.ceil(filteredDemands.value.length / pageSize)))

// 方法
const handleTabChange = (tab: 'tasks' | 'demands') => {
  activeTab.value = tab
}

const handleSearchInput = () => {
  currentPage.value.tasks = 1
  currentPage.value.demands = 1
}

const handlePrevPage = () => {
  const key = activeTab.value
  if (currentPage.value[key] > 1) {
    currentPage.value[key]--
  }
}

const handleNextPage = () => {
  const key = activeTab.value
  const maxPages = key === 'tasks' ? totalTasksPages.value : totalDemandsPages.value
  if (currentPage.value[key] < maxPages) {
    currentPage.value[key]++
  }
}

const getBadgeVariant = (statusClass: string): any => {
  const map: Record<string, string> = {
    recruiting: 'blue',
    running: 'orange',
    done: 'green',
    closed: 'red',
    review: 'purple',
  }
  return map[statusClass] || 'gray'
}

const goToDetail = (id: string, type: 'task' | 'demand') => {
  if (type === 'task') {
    router.push(`/tasks/${id}`)
  } else {
    router.push(`/demands/${id}`)
  }
}

const handleDemandSubmitted = (_data: { title: string; description: string }) => {
  loadDemands()
}
</script>

<template>
  <div class="page-shell">
    <TopNavbar @demand-submitted="handleDemandSubmitted" />

    <main class="hall-main">
      <div class="hall-view">
    <!-- 统计概览 -->
    <section class="summary-grid">
      <!-- 任务概览 -->
      <article class="stat-card">
        <p class="section-label">Task Overview</p>
        <div class="section-heading">
          <h1>全部任务</h1>
          <p>展示平台当前任务流转情况，帮助共建者快速判断哪里需要支援。</p>
        </div>
        <div class="task-stat-grid">
          <div class="metric-tile total">
            <span class="metric-number">{{ platformStats.tasks_total }}</span>
            <span class="metric-name">总任务</span>
            <span class="metric-note">平台累计</span>
          </div>
          <div class="metric-tile solving">
            <span class="metric-number">{{ platformStats.tasks_in_progress }}</span>
            <span class="metric-name">解决中</span>
            <span class="metric-note">正在进行</span>
          </div>
          <div class="metric-tile done">
            <span class="metric-number">{{ platformStats.tasks_completed }}</span>
            <span class="metric-name">已完成</span>
            <span class="metric-note">已通过验收</span>
          </div>
          <div class="metric-tile closed">
            <span class="metric-number">{{ platformStats.tasks_closed }}</span>
            <span class="metric-name">已关闭</span>
            <span class="metric-note">含重复与归档</span>
          </div>
        </div>
      </article>

      <!-- 注册用户 -->
      <article class="stat-card">
        <p class="section-label">Registered Users</p>
        <div class="section-heading">
          <h2>注册用户</h2>
        </div>
        <div class="user-card-body">
          <div class="user-tile">
            <div>
              <span>患者 / 家属人数</span>
              <strong>{{ platformStats.users_requester }}</strong>
            </div>
            <div class="user-icon patient">P</div>
          </div>
          <div class="user-tile">
            <div>
              <span>志愿者人数</span>
              <strong>{{ platformStats.users_builder }}</strong>
            </div>
            <div class="user-icon volunteer">V</div>
          </div>
        </div>
      </article>
    </section>

    <!-- 大厅卡片 -->
    <section class="hall-card">
      <div class="hall-tabs">
        <div>
          <p class="section-label">Community Hall</p>
          <div class="tab-buttons" role="tablist">
            <button
              class="tab-button"
              :class="{ 'is-active': activeTab === 'tasks' }"
              type="button"
              @click="handleTabChange('tasks')"
            >
              任务大厅
            </button>
            <button
              class="tab-button"
              :class="{ 'is-active': activeTab === 'demands' }"
              type="button"
              @click="handleTabChange('demands')"
            >
              需求大厅
            </button>
          </div>
        </div>
        <div class="hall-summary">
          <input
            v-model="searchKeyword"
            class="hall-search"
            type="search"
            placeholder="搜索任务、需求、状态、团队"
            @input="handleSearchInput"
          />
        </div>
      </div>

      <div class="hall-content">
        <!-- 表头 -->
        <div class="list-header">
          <span>{{ activeTab === 'tasks' ? '任务' : '需求' }}详情</span>
          <span>创建时间</span>
          <span>{{ activeTab === 'tasks' ? '任务' : '需求' }}状态</span>
          <span>团队状态</span>
          <span>进度</span>
          <span>操作</span>
        </div>

        <!-- 任务列表 -->
        <div v-if="activeTab === 'tasks'" class="tab-panel">
          <article
            v-for="item in paginatedTasks"
            :key="item.id"
            class="list-row"
          >
            <div>
              <h3 class="item-title">{{ item.title }}</h3>
              <p class="item-desc">{{ item.id }} · {{ item.desc }}</p>
            </div>
            <span class="date-text">{{ item.date }}</span>
            <span>
              <OrdBadge :variant="getBadgeVariant(item.statusClass)">
                {{ item.status }}
              </OrdBadge>
            </span>
            <span class="team-text">{{ item.team }}</span>
            <div class="progress-cell">
              <div class="progress-meta">
                <span>{{ item.progressLabel }}</span>
                <b>{{ item.progress }}%</b>
              </div>
              <OrdProgress :value="item.progress" variant="gradient" />
            </div>
            <OrdButton variant="primary" size="sm" @click="goToDetail(item.id, 'task')">
              详情
            </OrdButton>
          </article>

          <div v-if="filteredTasks.length === 0" class="hall-empty">
            没有匹配的任务，试试更换关键词。
          </div>
        </div>

        <!-- 需求列表 -->
        <div v-if="activeTab === 'demands'" class="tab-panel">
          <article
            v-for="item in paginatedDemands"
            :key="item.id"
            class="list-row"
          >
            <div>
              <h3 class="item-title">{{ item.title }}</h3>
              <p class="item-desc">{{ item.id }} · {{ item.desc }}</p>
            </div>
            <span class="date-text">{{ item.date }}</span>
            <span>
              <OrdBadge :variant="getBadgeVariant(item.statusClass)">
                {{ item.status }}
              </OrdBadge>
            </span>
            <span class="team-text">{{ item.team }}</span>
            <div class="progress-cell">
              <div class="progress-meta">
                <span>{{ item.progressLabel }}</span>
                <b>{{ item.progress }}%</b>
              </div>
              <OrdProgress :value="item.progress" variant="gradient" />
            </div>
            <OrdButton variant="primary" size="sm" @click="goToDetail(item.id, 'demand')">
              详情
            </OrdButton>
          </article>

          <div v-if="filteredDemands.length === 0" class="hall-empty">
            没有匹配的需求，试试更换关键词。
          </div>
        </div>

        <!-- 分页 -->
        <div class="pagination">
          <span class="pagination-summary">
            共 {{ activeTab === 'tasks' ? filteredTasks.length : filteredDemands.length }} 条，
            当前第 {{ activeTab === 'tasks' ? currentPage.tasks : currentPage.demands }} /
            {{ activeTab === 'tasks' ? totalTasksPages : totalDemandsPages }} 页
          </span>
          <div class="pagination-actions">
            <button
              class="page-button"
              type="button"
              :disabled="(activeTab === 'tasks' ? currentPage.tasks : currentPage.demands) === 1"
              @click="handlePrevPage"
            >
              上一页
            </button>
            <button class="page-button is-active" type="button" disabled>
              {{ activeTab === 'tasks' ? currentPage.tasks : currentPage.demands }}
            </button>
            <button
              class="page-button"
              type="button"
              :disabled="(activeTab === 'tasks' ? currentPage.tasks : currentPage.demands) >= (activeTab === 'tasks' ? totalTasksPages : totalDemandsPages)"
              @click="handleNextPage"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
.page-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at 12% 10%, rgba(20, 110, 245, 0.08), transparent 28%),
    radial-gradient(circle at 84% 16%, rgba(122, 61, 255, 0.065), transparent 24%),
    radial-gradient(circle at 82% 86%, rgba(255, 174, 19, 0.06), transparent 26%),
    linear-gradient(135deg, #ffffff 0%, #f7f9ff 100%);
}

.hall-main {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 94px 32px 32px;
}

.hall-view {
  position: relative;
  width: min(1460px, 100%);
  margin: 0 auto;
  padding: 0 32px;
}

.stat-card,
.hall-card {
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(216, 216, 216, 0.86);
  border-radius: 8px;
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
}

.summary-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.55fr);
  gap: 14px;
  margin-top: 14px;
}

.stat-card {
  padding: 18px;
}

.section-label {
  margin: 0 0 10px;
  color: var(--ord-color-blue);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.5px;
  line-height: 1.3;
  text-transform: uppercase;
}

.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.section-heading h1,
.section-heading h2 {
  margin: 0;
  color: var(--ord-color-black);
  font-size: 32px;
  font-weight: 600;
  line-height: 1.04;
  letter-spacing: -0.5px;
}

.section-heading p {
  max-width: 420px;
  margin: 0;
  color: var(--ord-color-gray-500);
  font-size: 14px;
  line-height: 1.55;
  text-align: right;
}

/* __CONTINUE_HERE__ */

.task-stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.metric-tile {
  position: relative;
  min-height: 92px;
  padding: 14px;
  overflow: hidden;
  background: #fff;
  border: 1px solid var(--ord-color-border);
  border-radius: 8px;
}

.metric-tile::after {
  content: "";
  position: absolute;
  width: 90px;
  height: 90px;
  right: -38px;
  top: -42px;
  border-radius: 50%;
  background: rgba(20, 110, 245, 0.08);
}

.metric-tile.total::after { background: rgba(20, 110, 245, 0.1); }
.metric-tile.solving::after { background: rgba(255, 174, 19, 0.16); }
.metric-tile.done::after { background: rgba(0, 215, 34, 0.12); }
.metric-tile.closed::after { background: rgba(238, 29, 54, 0.1); }

.metric-number {
  display: block;
  color: var(--ord-color-black);
  font-size: 32px;
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.6px;
}

.metric-name {
  display: block;
  margin-top: 8px;
  color: var(--ord-color-gray-500);
  font-size: 14px;
  font-weight: 600;
}

.metric-note {
  display: block;
  margin-top: 8px;
  color: var(--ord-color-gray-300);
  font-size: 12px;
  line-height: 1.4;
}

.user-card-body {
  display: grid;
  gap: 10px;
}

.user-tile {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 62px;
  padding: 12px;
  background: #fff;
  border: 1px solid var(--ord-color-border);
  border-radius: 8px;
}

.user-tile span {
  color: var(--ord-color-gray-500);
  font-size: 14px;
  font-weight: 600;
}

.user-tile strong {
  color: var(--ord-color-black);
  font-size: 30px;
  font-weight: 600;
  line-height: 1;
}

.user-icon {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 4px;
  font-size: 18px;
  font-weight: 700;
}

.user-icon.patient {
  color: var(--ord-color-pink);
  background: rgba(237, 82, 203, 0.1);
}

.user-icon.volunteer {
  color: var(--ord-color-green);
  background: rgba(0, 215, 34, 0.1);
}

.hall-card {
  margin-top: 14px;
  overflow: hidden;
}

.hall-tabs {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 20px;
  border-bottom: 1px solid #ececec;
}

.tab-buttons {
  display: inline-flex;
  padding: 4px;
  background: #f3f6ff;
  border: 1px solid rgba(20, 110, 245, 0.12);
  border-radius: 8px;
}

.tab-button {
  height: 38px;
  padding: 0 18px;
  color: var(--ord-color-gray-500);
  background: transparent;
  border: 0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: var(--ord-transition-base);
}

.tab-button.is-active {
  color: var(--ord-color-white);
  background: var(--ord-color-blue);
  box-shadow: 0 10px 20px rgba(20, 110, 245, 0.18);
}

.hall-search {
  width: min(360px, 100%);
  height: 42px;
  padding: 0 12px;
  color: var(--ord-color-black);
  background: #fff;
  border: 1px solid var(--ord-color-border);
  border-radius: 4px;
  outline: none;
  font-size: 14px;
  font-weight: 500;
  transition: var(--ord-transition-base);
}

.hall-search:focus {
  border-color: var(--ord-color-blue);
  box-shadow: 0 0 0 4px rgba(20, 110, 245, 0.12);
}

.hall-content {
  padding: 0 20px 20px;
}

.list-header,
.list-row {
  display: grid;
  grid-template-columns: minmax(260px, 1.55fr) 150px 120px 120px 160px 96px;
  gap: 16px;
  align-items: center;
}

.list-header {
  min-height: 48px;
  color: var(--ord-color-gray-500);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.8px;
  text-transform: uppercase;
}

.list-row {
  min-height: 82px;
  padding: 14px 0;
  border-top: 1px solid #ececec;
}

.item-title {
  margin: 0;
  color: var(--ord-color-black);
  font-size: 16px;
  font-weight: 600;
  line-height: 1.35;
}

.item-desc {
  margin: 6px 0 0;
  color: var(--ord-color-gray-500);
  font-size: 13px;
  line-height: 1.45;
}

.date-text,
.team-text {
  color: var(--ord-color-gray-700);
  font-size: 14px;
  line-height: 1.4;
}

.progress-cell {
  display: grid;
  gap: 8px;
}

.progress-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--ord-color-gray-500);
  font-size: 12px;
  font-weight: 600;
}

.hall-empty {
  padding: 34px 0 20px;
  color: var(--ord-color-gray-500);
  text-align: center;
  border-top: 1px solid #ececec;
  font-size: 14px;
  font-weight: 600;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 0 0;
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
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 650;
  transition: var(--ord-transition-base);
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

@media (max-width: 1100px) {
  .summary-grid,
  .task-stat-grid {
    grid-template-columns: 1fr 1fr;
  }

  .list-header,
  .list-row {
    grid-template-columns: minmax(240px, 1.4fr) 120px 110px 110px 140px;
  }
}

@media (max-width: 900px) {
  .hall-view {
    padding: 0;
  }

  .stat-card,
  .hall-card {
    border-radius: 0;
    box-shadow: none;
  }

  .summary-grid,
  .task-stat-grid {
    grid-template-columns: 1fr;
  }

  .section-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .section-heading p {
    text-align: left;
  }

  .hall-card,
  .summary-grid {
    margin-top: 12px;
  }

  .hall-tabs {
    align-items: flex-start;
    flex-direction: column;
  }

  .hall-content {
    overflow-x: auto;
  }

  .list-header,
  .list-row {
    min-width: 820px;
  }
}

@media (max-width: 520px) {
  .hall-search {
    width: 100%;
  }

  .pagination {
    align-items: stretch;
    flex-direction: column;
  }

  .pagination-actions {
    justify-content: space-between;
  }

  .page-button {
    flex: 1;
  }

  .stat-card,
  .hall-tabs,
  .hall-content {
    padding-left: 16px;
    padding-right: 16px;
  }

  .tab-buttons {
    width: 100%;
  }

  .tab-button {
    flex: 1;
  }
}
</style>





