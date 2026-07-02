<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import {
  OrdButton,
  OrdNavbar,
  OrdPagination,
  OrdTabs,
  OrdTabsList,
  OrdTabsTrigger,
  useToast,
} from '@/components/ui'
import { demandsApi } from '@/api'
import type { MyDemand } from '@/api/demands'
import { useAuthStore } from '@/stores/auth'
import { demandStatusDict, convertStatusDict, dict as t } from '@/utils/dict'

const router = useRouter()
const auth = useAuthStore()
const { show: showToast } = useToast()

const ROLE_LABEL: Record<string, string> = {
  requester: '需求者',
  builder: '共建者',
  operator: '运营管理员',
  super_admin: '超级管理员',
}

const PAGE_SIZE = 3

const demands = ref<MyDemand[]>([])
const loading = ref(false)
const activeTab = ref('all')
const searchKeyword = ref('')
const statusFilter = ref('all')
const currentPage = ref(1)

const stageCopy: Record<string, string> = {
  all: '当前展示全部需求，可通过生命周期 Tab 和筛选器快速定位。',
  pending: '当前仅展示等待平台审核的需求。',
  talking: '当前仅展示平台正在沟通或补充确认的需求。',
  converted: '当前仅展示已转化为协作任务的需求。',
  closed: '当前仅展示已完成、重复或暂不处理的需求。',
}

const statusClassMap: Record<string, string> = {
  pending: 'pending',
  reviewing: 'talking',
  approved: 'talking',
  converted: 'converted',
  rejected: 'closed',
  archived: 'closed',
}

const roleLabel = computed(() => ROLE_LABEL[auth.userRole] ?? '平台用户')

const summary = computed(() => ({
  total: demands.value.length,
  pending: demands.value.filter(d => d.stage === 'pending').length,
  converted: demands.value.filter(d => d.stage === 'converted').length,
  closed: demands.value.filter(d => d.stage === 'closed').length,
}))

const filteredDemands = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  return demands.value.filter(demand => {
    const matchTab = activeTab.value === 'all' || demand.stage === activeTab.value
    const matchStatus = statusFilter.value === 'all' || demand.status === statusFilter.value
    const text = `${demand.id} ${demand.title} ${demand.description} ${demand.feedback} ${demand.task_id} ${demand.contact}`.toLowerCase()
    return matchTab && matchStatus && (!keyword || text.includes(keyword))
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredDemands.value.length / PAGE_SIZE)))

const paginatedDemands = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return filteredDemands.value.slice(start, start + PAGE_SIZE)
})

const toolbarNote = computed(() => stageCopy[activeTab.value] || stageCopy.all)

function goBack() {
  router.push('/workbench')
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

function handleTabChange(value: string) {
  activeTab.value = value || 'all'
  currentPage.value = 1
}

async function fetchDemands() {
  loading.value = true
  try {
    const response = await demandsApi.getMyDemands()
    demands.value = response.data.items || []
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

watch([searchKeyword, statusFilter], () => {
  currentPage.value = 1
})

onMounted(fetchDemands)
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
                <p>{{ roleLabel }} · {{ auth.user?.province || '未填写' }}</p>
              </div>
            </div>
            <div class="profile-meta">
              <div><span>当前身份</span><strong>{{ roleLabel }}</strong></div>
              <div><span>我的需求</span><strong>{{ summary.total }}</strong></div>
            </div>
            <button class="logout-link" type="button" @click="handleLogout">退出登录</button>
          </section>
        </div>
      </template>
    </OrdNavbar>

    <main class="page-shell">
      <section class="demand-frame">
        <section class="hero-card" aria-label="我的需求概览">
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
        </section>

        <section class="summary-grid" aria-label="我的需求概览">
          <article class="summary-card">
            <p class="summary-label">我的需求</p>
            <p class="summary-value">{{ summary.total }}</p>
            <p class="summary-desc">我提交过的需求总数</p>
          </article>
          <article class="summary-card">
            <p class="summary-label">待审核</p>
            <p class="summary-value">{{ summary.pending }}</p>
            <p class="summary-desc">等待平台运营审核</p>
          </article>
          <article class="summary-card">
            <p class="summary-label">已转任务</p>
            <p class="summary-value">{{ summary.converted }}</p>
            <p class="summary-desc">已进入社区协作开发</p>
          </article>
          <article class="summary-card">
            <p class="summary-label">已关闭</p>
            <p class="summary-value">{{ summary.closed }}</p>
            <p class="summary-desc">已完成、重复或暂不处理</p>
          </article>
        </section>

        <section class="list-card" aria-label="我的需求列表">
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
                >
                  <option value="all">全部状态</option>
                  <option value="pending">待审核</option>
                  <option value="reviewing">沟通中</option>
                  <option value="converted">已转任务</option>
                  <option value="archived">已关闭</option>
                </select>
                <input
                  v-model="searchKeyword"
                  class="search-box"
                  type="search"
                  placeholder="搜索需求、反馈、任务号"
                />
              </div>
            </div>

            <OrdTabs :model-value="activeTab" @update:model-value="(v?: string) => handleTabChange(v || 'all')">
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

            <div v-if="loading" class="empty-state">加载中...</div>
            <div v-else-if="paginatedDemands.length === 0" class="empty-state">
              没有匹配的需求，试试切换状态或清空搜索。
            </div>

            <template v-else>
              <article
                v-for="demand in paginatedDemands"
                :key="demand.id"
                class="demand-row"
              >
                <div>
                  <span class="demand-title">{{ demand.title }}</span>
                  <span class="demand-desc">{{ demand.id }} · {{ demand.description }}</span>
                  <span class="demand-desc">{{ demand.contact }} · 附件 {{ demand.attachments }} 个</span>
                </div>
                <span>{{ demand.submitted_at }}</span>
                <span>
                  <span class="status-badge" :class="statusClassMap[demand.status] || 'pending'">
                    {{ t(demandStatusDict, demand.status) }}
                  </span>
                </span>
                <span>
                  <span class="convert-badge" :class="{ empty: !demand.convert_status }">
                    {{ t(convertStatusDict, demand.convert_status) }}
                  </span>
                </span>
                <span><span class="meta-badge">{{ demand.task_id }}</span></span>
                <div class="progress-wrap">
                  <div class="progress-line"><span :style="{ width: `${demand.progress}%` }" /></div>
                  <span class="progress-text">{{ demand.progress }}% · {{ demand.feedback }}</span>
                </div>
                <RouterLink :to="`/demands/${demand.id}`" class="detail-button">查看详情</RouterLink>
              </article>
            </template>
          </div>

          <div v-if="!loading && filteredDemands.length > 0" class="pagination" aria-label="分页导航">
            <span class="pagination-summary">共 {{ filteredDemands.length }} 条需求，第 {{ currentPage }} / {{ totalPages }} 页</span>
            <OrdPagination v-model:current-page="currentPage" :total="filteredDemands.length" :page-size="PAGE_SIZE" />
          </div>
        </section>
      </section>
    </main>
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

.demand-frame {
  position: relative;
  width: min(1460px, 100%);
  display: grid;
  gap: 18px;
}

.demand-frame::before,
.demand-frame::after {
  content: "";
  position: absolute;
  z-index: 0;
  border: 1px solid rgba(216, 216, 216, 0.7);
  background: rgba(255, 255, 255, 0.45);
  transform: rotate(-2deg);
  pointer-events: none;
}

.demand-frame::before {
  width: 180px;
  height: 86px;
  top: 96px;
  right: 42px;
}

.demand-frame::after {
  width: 108px;
  height: 108px;
  right: 214px;
  bottom: 56px;
  transform: rotate(4deg);
}

.hero-card,
.summary-card,
.list-card {
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
  grid-template-columns: 1fr 300px;
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
}

.summary-card {
  min-height: 106px;
  padding: 18px;
  border-top: 4px solid var(--ord-color-blue);
}

.summary-card:nth-child(2) {
  border-top-color: var(--ord-color-orange);
}

.summary-card:nth-child(3) {
  border-top-color: var(--ord-color-green);
}

.summary-card:nth-child(4) {
  border-top-color: var(--ord-color-purple);
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

.list-card {
  overflow: hidden;
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
  transition: border-color 180ms ease, box-shadow 180ms ease;
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

.demand-title {
  display: block;
  color: var(--ord-color-black);
  font-size: 15px;
  font-weight: 700;
  line-height: 1.35;
}

.demand-desc {
  display: block;
  margin-top: 5px;
  color: var(--ord-color-gray-500);
  font-size: 12px;
  line-height: 1.45;
}

.status-badge,
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

.status-badge.pending {
  color: #b27600;
  background: rgba(255, 174, 19, 0.16);
}

.status-badge.talking {
  color: var(--ord-color-blue);
  background: rgba(20, 110, 245, 0.08);
}

.status-badge.converted {
  color: #009e19;
  background: rgba(0, 215, 34, 0.12);
}

.status-badge.closed {
  color: var(--ord-color-gray-700);
  background: #f4f4f4;
}

.convert-badge {
  color: var(--ord-color-purple);
  background: rgba(122, 61, 255, 0.1);
}

.convert-badge.empty {
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
  transition: transform 180ms ease, background 180ms ease, box-shadow 180ms ease;
}

.detail-button:hover {
  background: var(--ord-color-blue-hover);
  box-shadow: 0 14px 28px rgba(20, 110, 245, 0.22);
  transform: translateX(6px);
}

.empty-state {
  padding: 42px 18px;
  text-align: center;
  color: var(--ord-color-gray-500);
  border-top: 1px solid #ececec;
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

@media (max-width: 992px) {
  .page-shell {
    padding: 96px 20px 32px;
  }

  .hero-card {
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
    padding: 92px 16px 24px;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .tab-list {
    width: 100%;
  }

  .tab-trigger {
    flex: 1;
  }

  .pagination {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
