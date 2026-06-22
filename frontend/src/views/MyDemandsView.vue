<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { OrdCard, OrdBadge, OrdTabs, OrdTabsList, OrdTabsTrigger, OrdTabsContent, OrdPagination } from '@/components/ui'
import { demandsApi } from '@/api'
import type { MyDemand } from '@/api/demands'

const demands = ref<MyDemand[]>([])
const isLoading = ref(true)
const activeTab = ref('all')
const searchKeyword = ref('')
const statusFilter = ref('全部')
const currentPage = ref(1)
const pageSize = 3

const stageCopy = {
  all: '当前展示全部需求，可通过生命周期 Tab 和筛选器快速定位。',
  pending: '当前仅展示等待平台审核的需求。',
  talking: '当前仅展示平台正在沟通或补充确认的需求。',
  converted: '当前仅展示已转化为协作任务的需求。',
  closed: '当前仅展示已完成、重复或暂不处理的需求。',
}

const statusClassMap: Record<string, string> = {
  '待审核': 'pending',
  '沟通中': 'talking',
  '已转任务': 'converted',
  '已关闭': 'closed',
}

const summary = computed(() => {
  return {
    total: demands.value.length,
    pending: demands.value.filter(d => d.stage === 'pending').length,
    converted: demands.value.filter(d => d.stage === 'converted').length,
    closed: demands.value.filter(d => d.stage === 'closed').length,
  }
})

const filteredDemands = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  return demands.value.filter(demand => {
    const matchTab = activeTab.value === 'all' || demand.stage === activeTab.value
    const matchStatus = statusFilter.value === '全部' || demand.status === statusFilter.value
    const text = `${demand.id} ${demand.title} ${demand.description} ${demand.feedback} ${demand.task_id} ${demand.contact}`.toLowerCase()
    return matchTab && matchStatus && (!keyword || text.includes(keyword))
  })
})

const paginatedDemands = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredDemands.value.slice(start, start + pageSize)
})

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(filteredDemands.value.length / pageSize))
})

const toolbarNote = computed(() => {
  return stageCopy[activeTab.value as keyof typeof stageCopy]
})

const fetchDemands = async () => {
  isLoading.value = true
  try {
    const response = await demandsApi.getMyDemands()
    demands.value = response.data.items || []
  } catch (error) {
    console.error('Failed to fetch demands:', error)
  } finally {
    isLoading.value = false
  }
}

const handleTabChange = (value: string) => {
  activeTab.value = value
  currentPage.value = 1
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleStatusChange = () => {
  currentPage.value = 1
}

const handlePageChange = (page: number) => {
  currentPage.value = page
}

onMounted(() => {
  fetchDemands()
})
</script>

<template>
  <div class="my-demands-view">
    <section class="hero-section">
      <div class="hero-content">
        <div>
          <p class="eyebrow">My Demands</p>
          <h1>我的需求</h1>
          <p class="hero-copy">
            以提交者视角展示我提交过的需求、审核进度、平台反馈和转化结果，帮助你快速了解需求是否已进入协作流程。
          </p>
        </div>
        <aside class="focus-card" aria-label="当前需求提醒">
          <span>Demand Status</span>
          <strong>{{ summary.pending }} 个待审核</strong>
          <p>需求详情页将在后续开放，本页先聚焦信息总览与状态跟踪。</p>
        </aside>
      </div>
    </section>

    <div class="summary-grid">
      <OrdCard class="summary-card summary-card--total">
        <p class="summary-label">我的需求</p>
        <p class="summary-value">{{ summary.total }}</p>
        <p class="summary-desc">我提交过的需求总数</p>
      </OrdCard>
      <OrdCard class="summary-card summary-card--pending">
        <p class="summary-label">待审核</p>
        <p class="summary-value">{{ summary.pending }}</p>
        <p class="summary-desc">等待产品经理审核</p>
      </OrdCard>
      <OrdCard class="summary-card summary-card--converted">
        <p class="summary-label">已转任务</p>
        <p class="summary-value">{{ summary.converted }}</p>
        <p class="summary-desc">已进入社区协作开发</p>
      </OrdCard>
      <OrdCard class="summary-card summary-card--closed">
        <p class="summary-label">已关闭</p>
        <p class="summary-value">{{ summary.closed }}</p>
        <p class="summary-desc">已完成、重复或暂不处理</p>
      </OrdCard>
    </div>

    <OrdCard class="list-card">
      <div class="list-toolbar">
        <div class="toolbar-top">
          <div>
            <h2 class="toolbar-title">需求列表</h2>
            <p class="toolbar-note">{{ toolbarNote }}</p>
          </div>
          <div class="toolbar-actions">
            <select
              v-model="statusFilter"
              class="status-filter"
              aria-label="按审核状态筛选"
              @change="handleStatusChange"
            >
              <option value="全部">全部状态</option>
              <option value="待审核">待审核</option>
              <option value="沟通中">沟通中</option>
              <option value="已转任务">已转任务</option>
              <option value="已关闭">已关闭</option>
            </select>
            <input
              v-model="searchKeyword"
              class="search-box"
              type="search"
              placeholder="搜索需求、反馈、任务号"
              @input="handleSearch"
            />
          </div>
        </div>

        <OrdTabs :model-value="activeTab" @update:model-value="(value?: string) => handleTabChange(value || 'all')">
          <OrdTabsList class="tab-list">
            <OrdTabsTrigger value="all" class="tab-trigger">全部</OrdTabsTrigger>
            <OrdTabsTrigger value="pending" class="tab-trigger">待审核</OrdTabsTrigger>
            <OrdTabsTrigger value="talking" class="tab-trigger">沟通中</OrdTabsTrigger>
            <OrdTabsTrigger value="converted" class="tab-trigger">已转任务</OrdTabsTrigger>
            <OrdTabsTrigger value="closed" class="tab-trigger">已关闭</OrdTabsTrigger>
          </OrdTabsList>
        </OrdTabs>
      </div>

      <div class="demand-list">
        <div class="demand-header" aria-hidden="true">
          <span>需求详情</span>
          <span>提交时间</span>
          <span>审核状态</span>
          <span>转化状态</span>
          <span>关联任务</span>
          <span>进度</span>
          <span>操作</span>
        </div>

        <div v-if="isLoading" class="loading-state">
          <p>加载中...</p>
        </div>

        <div v-else-if="paginatedDemands.length === 0" class="empty-state">
          <p>没有匹配的需求，试试切换状态或清空搜索。</p>
        </div>

        <article
          v-for="demand in paginatedDemands"
          v-else
          :key="demand.id"
          class="demand-row"
        >
          <div class="demand-info">
            <span class="demand-title">{{ demand.title }}</span>
            <span class="demand-desc">{{ demand.id }} · {{ demand.description }}</span>
            <span class="demand-desc">{{ demand.contact }} · 附件 {{ demand.attachments }} 个</span>
          </div>

          <span class="demand-date">{{ demand.submitted_at }}</span>

          <span class="demand-status">
            <OrdBadge :variant="(statusClassMap[demand.status] as any) || 'gray'">
              {{ demand.status }}
            </OrdBadge>
          </span>

          <span class="demand-convert">
            <span
              class="convert-badge"
              :class="{ 'convert-badge--empty': demand.convert_status === '未转化' }"
            >
              {{ demand.convert_status }}
            </span>
          </span>

          <span class="demand-task">
            <span class="meta-badge">{{ demand.task_id }}</span>
          </span>

          <div class="progress-wrap">
            <div class="progress-line">
              <span :style="{ width: `${demand.progress}%` }" />
            </div>
            <span class="progress-text">{{ demand.progress }}% · {{ demand.feedback }}</span>
          </div>

          <router-link
            :to="`/demands/${demand.id}`"
            class="detail-button"
          >
            查看详情
          </router-link>
        </article>
      </div>

      <div v-if="!isLoading && filteredDemands.length > 0" class="pagination-wrapper">
        <OrdPagination
          v-model:current-page="currentPage"
          :total="filteredDemands.length"
          :page-size="pageSize"
          @update:current-page="handlePageChange"
        />
      </div>
    </OrdCard>
  </div>
</template>

<style scoped>
.my-demands-view {
  width: min(1460px, 100%);
  margin: 0 auto;
  padding: 0;
}

.hero-section {
  margin-bottom: 14px;
}

.hero-content {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.55fr);
  gap: 14px;
  padding: 28px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(216, 216, 216, 0.86);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
}

.eyebrow {
  margin: 0 0 8px;
  color: var(--ord-color-blue);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.5px;
  line-height: 1.3;
  text-transform: uppercase;
}

.hero-content h1 {
  margin: 0 0 14px;
  color: var(--ord-color-black);
  font-size: 42px;
  font-weight: 600;
  line-height: 1.04;
  letter-spacing: -0.7px;
}

.hero-copy {
  margin: 0;
  max-width: 560px;
  color: var(--ord-color-gray-500);
  font-size: 15px;
  line-height: 1.6;
}

.focus-card {
  display: grid;
  align-content: center;
  gap: 12px;
  padding: 18px;
  color: var(--ord-color-white);
  background: var(--ord-color-black);
  border-radius: var(--ord-radius-md);
}

.focus-card span {
  width: max-content;
  padding: 5px 8px;
  background: rgba(20, 110, 245, 0.9);
  border-radius: var(--ord-radius-sm);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.focus-card strong {
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
  margin-bottom: 14px;
}

.summary-card {
  min-height: 106px;
  padding: 18px !important;
  border-top: 4px solid var(--ord-color-blue);
}

.summary-card--total {
  border-top-color: var(--ord-color-blue);
}

.summary-card--pending {
  border-top-color: var(--ord-color-orange);
}

.summary-card--converted {
  border-top-color: var(--ord-color-green);
}

.summary-card--closed {
  border-top-color: var(--ord-color-purple);
}

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
  padding: 0 !important;
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
  background: var(--ord-color-white);
  color: var(--ord-color-black);
  font-size: 14px;
  outline: none;
  transition: var(--ord-transition-base);
}

.search-box {
  width: 260px;
  padding: 0 12px;
}

.status-filter {
  width: 150px;
  padding: 0 10px;
}

.search-box:focus,
.status-filter:focus {
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

.tab-trigger {
  min-width: 106px;
  height: 36px;
  padding: 0 14px;
  color: var(--ord-color-gray-700);
  background: transparent;
  border: 0;
  border-radius: var(--ord-radius-sm);
  font-size: 13px;
  white-space: nowrap;
  transition: var(--ord-transition-base);
}

.tab-trigger[data-state='active'] {
  color: var(--ord-color-white);
  background: var(--ord-color-black);
}

.demand-list {
  overflow-x: auto;
}

.demand-header,
.demand-row {
  display: grid;
  grid-template-columns: minmax(300px, 2fr) 130px 122px 122px minmax(170px, 1fr) minmax(150px, 1fr) 112px;
  gap: 14px;
  align-items: center;
  min-width: 1260px;
}

.demand-header {
  padding: 13px 18px;
  color: var(--ord-color-gray-500);
  background: #fafafa;
  border-bottom: 1px solid #ececec;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.8px;
  text-transform: uppercase;
}

.demand-row {
  padding: 16px 18px;
  border-bottom: 1px solid #ececec;
  color: var(--ord-color-gray-700);
  font-size: 13px;
}

.demand-row:last-child {
  border-bottom: 0;
}

.demand-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.demand-title {
  color: var(--ord-color-black);
  font-size: 15px;
  font-weight: 700;
  line-height: 1.35;
}

.demand-desc {
  color: var(--ord-color-gray-500);
  font-size: 12px;
  line-height: 1.45;
}

.demand-date,
.demand-status,
.demand-convert,
.demand-task {
  display: flex;
  align-items: center;
}

.convert-badge,
.meta-badge {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: var(--ord-radius-sm);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.convert-badge {
  color: var(--ord-color-purple);
  background: rgba(122, 61, 255, 0.1);
}

.convert-badge--empty {
  color: var(--ord-color-gray-500);
  background: #f4f4f4;
}

.meta-badge {
  color: var(--ord-color-gray-700);
  background: #f4f4f4;
}

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
  transition: width 300ms ease;
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
  font-weight: 600;
  text-decoration: none;
  transition: var(--ord-transition-base);
}

.detail-button:hover {
  background: var(--ord-color-blue-hover);
  box-shadow: 0 14px 28px rgba(20, 110, 245, 0.22);
  transform: translateX(6px);
}

.loading-state,
.empty-state {
  padding: 42px 18px;
  text-align: center;
  color: var(--ord-color-gray-500);
  border-top: 1px solid #ececec;
}

.pagination-wrapper {
  padding: 14px 18px;
  border-top: 1px solid #ececec;
  background: rgba(255, 255, 255, 0.92);
}

@media (max-width: 992px) {
  .hero-content {
    grid-template-columns: 1fr;
  }

  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .toolbar-top {
    align-items: stretch;
    flex-direction: column;
  }

  .toolbar-actions {
    justify-content: flex-start;
  }

  .search-box {
    width: min(100%, 340px);
  }
}

@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .tab-list {
    width: 100%;
  }

  .tab-trigger {
    flex: 1;
  }
}
</style>
