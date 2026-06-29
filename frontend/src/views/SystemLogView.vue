<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { adminApi } from '@/api/admin'
import type { SystemLog, LogSummary } from '@/api/admin'
import TopNavbar from '@/components/TopNavbar.vue'
import {
  OrdTable,
  OrdTableHeader,
  OrdTableRow,
  OrdTableCell,
  OrdButton,
  OrdBadge,
  OrdDialog,
  OrdSelect,
  OrdSearchBox,
  OrdPagination,
} from '@/components/ui'

const router = useRouter()
const auth = useAuthStore()

if (!auth.hasPermission('admin:log')) {
  router.replace('/403')
}

const logs = ref<SystemLog[]>([])
const total = ref(0)
const loading = ref(false)
const currentPage = ref(1)
const PAGE_SIZE = 10

const filterModule = ref('all')
const filterRisk = ref('all')
const filterResult = ref('all')
const searchKeyword = ref('')

const selectedLog = ref<SystemLog | null>(null)
const isDetailOpen = ref(false)

const summary = ref<LogSummary>({ today: 0, high_risk: 0, failed: 0, week: 0 })

const moduleOptions = [
  { value: 'all', label: '全部模块' },
  { value: '登录安全', label: '登录安全' },
  { value: '权限管理', label: '权限管理' },
  { value: '用户管理', label: '用户管理' },
  { value: '任务管理', label: '任务管理' },
  { value: '需求管理', label: '需求管理' },
  { value: '系统配置', label: '系统配置' },
]

const riskOptions = [
  { value: 'all', label: '全部风险' },
  { value: 'high', label: '高风险' },
  { value: 'medium', label: '中风险' },
  { value: 'low', label: '低风险' },
]

const resultOptions = [
  { value: 'all', label: '全部结果' },
  { value: 'success', label: '成功' },
  { value: 'failed', label: '失败' },
  { value: 'blocked', label: '拦截' },
]

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))
const pageStart = computed(() => (total.value === 0 ? 0 : (currentPage.value - 1) * PAGE_SIZE + 1))
const pageEnd = computed(() => Math.min(currentPage.value * PAGE_SIZE, total.value))

async function fetchLogs() {
  loading.value = true
  try {
    const res = await adminApi.getSystemLogs({
      keyword: searchKeyword.value || undefined,
      module: filterModule.value === 'all' ? undefined : filterModule.value,
      risk_level: filterRisk.value === 'all' ? undefined : filterRisk.value,
      result: filterResult.value === 'all' ? undefined : filterResult.value,
      page: currentPage.value,
      page_size: PAGE_SIZE,
    })
    logs.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

async function fetchSummary() {
  try {
    const res = await adminApi.getLogSummary()
    summary.value = res.data
  } catch {
    /* summary is non-critical */
  }
}

onMounted(() => {
  fetchLogs()
  fetchSummary()
})

function onFilterChange() {
  currentPage.value = 1
  fetchLogs()
}

let searchTimer: ReturnType<typeof setTimeout> | null = null

watch(searchKeyword, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchLogs()
  }, 300)
})

onUnmounted(() => {
  if (searchTimer) clearTimeout(searchTimer)
})

function onPageChange() {
  fetchLogs()
}

function viewDetail(log: SystemLog) {
  selectedLog.value = log
  isDetailOpen.value = true
}

function formatTime(iso: string) {
  const d = new Date(iso)
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
}

function formatDate(iso: string) {
  const d = new Date(iso)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function formatDateTime(iso: string) {
  return `${formatDate(iso)} ${formatTime(iso)}`
}

function riskVariant(risk: string): 'red' | 'orange' | 'green' {
  if (risk === 'high') return 'red'
  if (risk === 'medium') return 'orange'
  return 'green'
}

function riskLabel(risk: string) {
  return risk === 'high' ? '高' : risk === 'medium' ? '中' : '低'
}

function resultVariant(result: string): 'green' | 'red' | 'orange' {
  if (result === 'success') return 'green'
  if (result === 'failed') return 'red'
  return 'orange'
}

function resultLabel(result: string) {
  return result === 'success' ? '成功' : result === 'failed' ? '失败' : '拦截'
}

function roleLabel(role: string) {
  const map: Record<string, string> = {
    super_admin: '超级管理员',
    operator: '运营管理员',
    builder: '共建者',
    requester: '需求者',
  }
  return map[role] || role || '未认证'
}
</script>

<template>
  <div class="system-log-page">
    <TopNavbar />

    <main class="page-shell">
      <section class="log-frame">
        <!-- Hero Card -->
        <div class="hero-card">
          <div class="hero-left">
            <p class="eyebrow">System Audit Log</p>
            <h1>系统日志</h1>
            <p class="hero-copy">
              面向超级管理员的综合审计界面，用来追踪登录安全、权限变更、用户管理、任务需求与系统配置等关键操作。
            </p>
          </div>
          <aside class="super-admin-card">
            <span class="sa-tag">Super Admin Only</span>
            <strong class="sa-title">仅超级管理员可见</strong>
            <p class="sa-desc">该页面用于审计敏感操作和异常行为，普通成员与运营管理员不展示此入口。</p>
          </aside>
        </div>

        <!-- Summary Grid -->
        <div class="summary-grid">
          <article class="summary-card summary--blue">
            <p class="summary-label">今日日志</p>
            <p class="summary-value">{{ summary.today }}</p>
            <p class="summary-desc">今天产生的关键审计记录</p>
          </article>
          <article class="summary-card summary--red">
            <p class="summary-label">高风险操作</p>
            <p class="summary-value">{{ summary.high_risk }}</p>
            <p class="summary-desc">权限、删除、系统配置等敏感操作</p>
          </article>
          <article class="summary-card summary--orange">
            <p class="summary-label">失败 / 拦截</p>
            <p class="summary-value">{{ summary.failed }}</p>
            <p class="summary-desc">异常登录、权限不足和风控拦截</p>
          </article>
          <article class="summary-card summary--purple">
            <p class="summary-label">近 7 日审计</p>
            <p class="summary-value">{{ summary.week }}</p>
            <p class="summary-desc">平台近 7 日审计记录总数</p>
          </article>
        </div>

        <!-- Table Card -->
        <section class="table-card">
          <div class="table-toolbar">
            <div class="toolbar-info">
              <h2 class="toolbar-title">综合审计日志</h2>
              <p class="toolbar-note">支持按关键词、模块、风险等级和结果状态筛选，点击详情查看审计上下文。</p>
            </div>
            <div class="toolbar-actions">
              <OrdSelect
                v-model="filterModule"
                :options="moduleOptions"
                placeholder="全部模块"
                @update:model-value="onFilterChange"
              />
              <OrdSelect
                v-model="filterRisk"
                :options="riskOptions"
                placeholder="全部风险"
                @update:model-value="onFilterChange"
              />
              <OrdSelect
                v-model="filterResult"
                :options="resultOptions"
                placeholder="全部结果"
                @update:model-value="onFilterChange"
              />
              <OrdSearchBox
                v-model="searchKeyword"
                placeholder="搜索操作者、对象、IP"
                width="260px"
              />
            </div>
          </div>

          <div class="table-scroll">
            <OrdTable>
              <OrdTableHeader>
                <OrdTableCell header>时间</OrdTableCell>
                <OrdTableCell header>操作者</OrdTableCell>
                <OrdTableCell header>角色</OrdTableCell>
                <OrdTableCell header>模块</OrdTableCell>
                <OrdTableCell header>操作类型</OrdTableCell>
                <OrdTableCell header>操作对象</OrdTableCell>
                <OrdTableCell header>结果</OrdTableCell>
                <OrdTableCell header>风险</OrdTableCell>
                <OrdTableCell header>IP 地址</OrdTableCell>
                <OrdTableCell header>操作</OrdTableCell>
              </OrdTableHeader>
              <tbody>
                <OrdTableRow v-for="log in logs" :key="log.id">
                  <OrdTableCell>
                    <span class="cell-primary">{{ formatTime(log.created_at) }}</span>
                    <span class="cell-sub">{{ formatDate(log.created_at) }}</span>
                  </OrdTableCell>
                  <OrdTableCell>
                    <span class="cell-primary">{{ log.operator }}</span>
                    <span class="cell-sub">{{ log.operator_account }}</span>
                  </OrdTableCell>
                  <OrdTableCell>{{ roleLabel(log.operator_role) }}</OrdTableCell>
                  <OrdTableCell>
                    <OrdBadge variant="blue">{{ log.module }}</OrdBadge>
                  </OrdTableCell>
                  <OrdTableCell>{{ log.action }}</OrdTableCell>
                  <OrdTableCell class="target-cell">{{ log.target }}</OrdTableCell>
                  <OrdTableCell>
                    <span class="result-badge" :class="'result--' + resultVariant(log.result)">
                      {{ resultLabel(log.result) }}
                    </span>
                  </OrdTableCell>
                  <OrdTableCell>
                    <span class="risk-badge" :class="'risk--' + riskVariant(log.risk_level)">
                      {{ riskLabel(log.risk_level) }}风险
                    </span>
                  </OrdTableCell>
                  <OrdTableCell class="ip-cell">{{ log.ip }}</OrdTableCell>
                  <OrdTableCell>
                    <OrdButton variant="primary" size="sm" @click="viewDetail(log)">详情</OrdButton>
                  </OrdTableCell>
                </OrdTableRow>
              </tbody>
            </OrdTable>
          </div>

          <div class="pagination-bar">
            <span class="pagination-summary">
              共 {{ total }} 条记录 · 第 {{ pageStart }}–{{ pageEnd }} 条 · 第 {{ currentPage }} / {{ totalPages }} 页
            </span>
            <OrdPagination
              v-model:current-page="currentPage"
              :total="total"
              :page-size="PAGE_SIZE"
              @update:current-page="onPageChange"
            />
          </div>
        </section>
      </section>
    </main>

    <!-- Detail Dialog -->
    <OrdDialog v-model:open="isDetailOpen">
      <div class="modal-top">
        <div>
          <p class="eyebrow">Audit Detail</p>
          <h2 class="modal-title">日志详情</h2>
          <p class="modal-subtitle">展示单条日志的完整审计上下文，便于超级管理员追踪异常或回溯操作。</p>
        </div>
        <button class="close-btn" type="button" @click="isDetailOpen = false" aria-label="关闭弹窗">×</button>
      </div>

      <div v-if="selectedLog" class="detail-grid">
        <div class="detail-item">
          <p class="detail-label">日志 ID</p>
          <p class="detail-value mono">{{ selectedLog.id }}</p>
        </div>
        <div class="detail-item">
          <p class="detail-label">追踪 ID</p>
          <p class="detail-value mono">{{ selectedLog.trace_id }}</p>
        </div>
        <div class="detail-item">
          <p class="detail-label">操作时间</p>
          <p class="detail-value">{{ formatDateTime(selectedLog.created_at) }}</p>
        </div>
        <div class="detail-item">
          <p class="detail-label">操作者</p>
          <p class="detail-value">{{ selectedLog.operator }}（{{ selectedLog.operator_account }} / {{ roleLabel(selectedLog.operator_role) }}）</p>
        </div>
        <div class="detail-item">
          <p class="detail-label">模块与动作</p>
          <p class="detail-value">{{ selectedLog.module }} / {{ selectedLog.action }}</p>
        </div>
        <div class="detail-item">
          <p class="detail-label">结果与风险</p>
          <p class="detail-value">{{ resultLabel(selectedLog.result) }} / {{ riskLabel(selectedLog.risk_level) }}风险</p>
        </div>
        <div class="detail-item detail-full">
          <p class="detail-label">IP 与设备</p>
          <p class="detail-value">{{ selectedLog.ip }} · {{ selectedLog.device }}</p>
        </div>
        <div class="detail-item detail-full">
          <p class="detail-label">影响对象</p>
          <p class="detail-value">{{ selectedLog.target }}</p>
        </div>
        <div class="detail-item detail-full">
          <p class="detail-label">审计备注</p>
          <p class="detail-value">{{ selectedLog.note || '—' }}</p>
        </div>
      </div>
    </OrdDialog>
  </div>
</template>

<style scoped>
/* ───── Page Shell ───── */
.system-log-page {
  min-height: 100vh;
}

.page-shell {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 96px 32px 32px;
}

.log-frame {
  position: relative;
  width: min(1460px, 100%);
  display: grid;
  gap: 18px;
}

.log-frame::before,
.log-frame::after {
  content: "";
  position: absolute;
  z-index: -1;
  border: 1px solid rgba(216, 216, 216, 0.7);
  background: rgba(255, 255, 255, 0.45);
  transform: rotate(-2deg);
}

.log-frame::before {
  width: 180px;
  height: 86px;
  top: 96px;
  right: 42px;
}

.log-frame::after {
  width: 108px;
  height: 108px;
  right: 214px;
  bottom: 56px;
  transform: rotate(4deg);
}

/* ───── Hero Card ───── */
.hero-card {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: 1fr 306px;
  gap: 24px;
  padding: 28px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(216, 216, 216, 0.86);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
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

.super-admin-card {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 12px;
  align-content: center;
  min-height: 160px;
  padding: 18px;
  color: var(--ord-color-white);
  background: var(--ord-color-black);
  border-radius: var(--ord-radius-md);
}

.sa-tag {
  width: max-content;
  padding: 5px 8px;
  color: #fff;
  background: rgba(20, 110, 245, 0.9);
  border-radius: var(--ord-radius-sm);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.sa-title {
  font-size: 26px;
  font-weight: 600;
  line-height: 1.1;
}

.sa-desc {
  margin: 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  line-height: 1.55;
}

/* ───── Summary Grid ───── */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
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

.summary--blue  { border-top-color: var(--ord-color-blue); }
.summary--red   { border-top-color: var(--ord-color-red); }
.summary--orange { border-top-color: var(--ord-color-orange); }
.summary--purple { border-top-color: var(--ord-color-purple); }

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

/* ───── Table Card ───── */
.table-card {
  overflow: hidden;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(216, 216, 216, 0.86);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
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
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 10px;
}

.toolbar-actions :deep(.ord-select__trigger) {
  min-width: 132px;
  height: 42px;
  font-size: 14px;
}

.table-scroll {
  overflow-x: auto;
}

.table-scroll :deep(.ord-table) {
  border: none;
  border-radius: 0;
}

.table-scroll :deep(.ord-table__inner) {
  min-width: 1320px;
}

.table-scroll :deep(.ord-table-cell) {
  padding: 14px 12px;
  font-size: 13px;
  line-height: 1.42;
  color: var(--ord-color-gray-700);
  vertical-align: middle;
}

.table-scroll :deep(.ord-table-header) {
  background: transparent;
}

.table-scroll :deep(.ord-table-header th) {
  color: var(--ord-color-gray-500);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  border-bottom: 1px solid #ececec;
}

.table-scroll :deep(.ord-table-row) {
  border-bottom: 1px solid #ececec;
}

.table-scroll :deep(.ord-table-row:last-child) {
  border-bottom: 1px solid #ececec;
}

.cell-primary {
  display: block;
  color: var(--ord-color-black);
  font-size: 14px;
  font-weight: 700;
}

.cell-sub {
  display: block;
  margin-top: 4px;
  color: var(--ord-color-gray-500);
  font-size: 12px;
}

.target-cell {
  max-width: 160px;
}

.target-cell :deep(.ord-table-cell) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ip-cell :deep(.ord-table-cell) {
  font-family: monospace;
  white-space: nowrap;
}

/* Custom result / risk badges matching demo exactly */
.result-badge,
.risk-badge {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: var(--ord-radius-sm);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.result--green { color: #009e19; background: rgba(0, 215, 34, 0.12); }
.result--red   { color: var(--ord-color-red); background: rgba(238, 29, 54, 0.1); }
.result--orange { color: #b27600; background: rgba(255, 174, 19, 0.16); }

.risk--green  { color: #009e19; background: rgba(0, 215, 34, 0.12); }
.risk--orange { color: #b27600; background: rgba(255, 174, 19, 0.16); }
.risk--red    { color: var(--ord-color-red); background: rgba(238, 29, 54, 0.1); }

/* Detail button override */
.table-scroll :deep(.ord-button--primary.ord-button--sm) {
  min-height: 34px;
  min-width: 76px;
  padding: 0 14px;
  font-size: 13px;
  border-radius: var(--ord-radius-sm);
}

/* ───── Pagination Bar ───── */
.pagination-bar {
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

/* ───── Dialog Overrides ───── */
:deep(.ord-dialog__content) {
  width: min(860px, 100%) !important;
  max-height: min(86vh, 720px);
  padding: 0 !important;
}

:deep(.ord-dialog__title),
:deep(.ord-dialog__description) {
  display: none;
}

.modal-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 22px 24px;
  border-bottom: 1px solid #ececec;
}

.modal-title {
  margin: 0;
  color: var(--ord-color-black);
  font-size: 26px;
  font-weight: 600;
  line-height: 1.18;
}

.modal-subtitle {
  margin: 8px 0 0;
  color: var(--ord-color-gray-500);
  font-size: 13px;
  line-height: 1.5;
}

.close-btn {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  color: var(--ord-color-black);
  background: #fff;
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-sm);
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  transition: transform var(--ord-transition-base), border-color var(--ord-transition-base), color var(--ord-transition-base);
}

.close-btn:hover {
  color: var(--ord-color-blue);
  border-color: var(--ord-color-blue);
}

/* ───── Detail Grid ───── */
.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 22px 24px 24px;
}

.detail-item {
  min-height: 74px;
  padding: 13px;
  border: 1px solid #ececec;
  border-radius: 6px;
  background: #fff;
}

.detail-full {
  grid-column: 1 / -1;
}

.detail-label {
  margin: 0 0 7px;
  color: var(--ord-color-gray-500);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.detail-value {
  margin: 0;
  color: var(--ord-color-black);
  font-size: 14px;
  line-height: 1.55;
  word-break: break-word;
}

.detail-value.mono {
  font-family: var(--ord-font-mono);
  font-size: 13px;
}

/* ───── Responsive ───── */
@media (max-width: 992px) {
  .hero-card {
    grid-template-columns: 1fr;
  }
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .table-toolbar {
    align-items: stretch;
    flex-direction: column;
  }
  .toolbar-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .page-shell {
    padding: 92px 16px 24px;
  }
  .summary-grid,
  .detail-grid {
    grid-template-columns: 1fr;
  }
  .detail-full {
    grid-column: auto;
  }
  .pagination-bar {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
