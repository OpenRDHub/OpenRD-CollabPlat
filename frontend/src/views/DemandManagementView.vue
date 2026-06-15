<template>
  <div class="demand-management">
    <!-- 背景装饰元素 -->
    <div class="ambient-ring"></div>
    <div class="ambient-node"></div>

    <!-- Hero 卡片 -->
    <section class="hero-card">
      <div>
        <p class="section-label">Demand Management</p>
        <h1>审核、沟通并转化需求</h1>
        <p class="hero-copy">
          参考用户管理与权限管理布局，帮助运营团队处理全量需求：从待审核、沟通中到已转任务，统一维护转化状态与平台反馈。
        </p>
      </div>
      <OrdButton variant="primary" @click="handleExport">导出需求</OrdButton>
    </section>

    <!-- 统计卡片 -->
    <section class="summary-grid">
      <article class="summary-card" style="--accent: var(--ord-color-blue-600)">
        <strong>{{ stats.total }}</strong>
        <span>总需求</span>
      </article>
      <article class="summary-card" style="--accent: var(--ord-color-yellow-600)">
        <strong>{{ stats.pending }}</strong>
        <span>待审核</span>
      </article>
      <article class="summary-card" style="--accent: var(--ord-color-purple-600)">
        <strong>{{ stats.talking }}</strong>
        <span>沟通中</span>
      </article>
      <article class="summary-card" style="--accent: var(--ord-color-green-600)">
        <strong>{{ stats.converted }}</strong>
        <span>已转任务</span>
      </article>
      <article class="summary-card" style="--accent: var(--ord-color-gray-600)">
        <strong>{{ stats.closed }}</strong>
        <span>已关闭</span>
      </article>
    </section>

    <!-- 需求列表卡片 -->
    <OrdCard class="table-card">
      <!-- 工具栏 -->
      <div class="table-toolbar">
        <div>
          <p class="section-label">Demand List</p>
          <h2>需求列表</h2>
          <p class="toolbar-note">
            可按审核状态、转化状态或关键字筛选。字段用于后续对接真实需求审核流程。
          </p>
        </div>
        <div class="toolbar-actions">
          <OrdSearchBox v-model="keyword" placeholder="搜索需求、发布者、任务编号" width="260px" />
          <OrdSelect
            v-model="reviewFilter"
            :options="reviewFilterOptions"
            placeholder="审核状态"
          />
          <OrdSelect
            v-model="convertFilter"
            :options="convertFilterOptions"
            placeholder="转化状态"
          />
        </div>
      </div>

      <!-- 表格 -->
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
          <OrdTableRow v-for="demand in paginatedDemands" :key="demand.id">
            <OrdTableCell>
              <span class="id-text">{{ demand.id }}</span>
            </OrdTableCell>
            <OrdTableCell>
              <div class="detail-title">{{ demand.title }}</div>
              <div class="detail-sub">{{ demand.description }}</div>
            </OrdTableCell>
            <OrdTableCell>{{ demand.submitted_at }}</OrdTableCell>
            <OrdTableCell>
              <OrdBadge :variant="getReviewVariant(demand.review_status)">
                {{ demand.review_status }}
              </OrdBadge>
            </OrdTableCell>
            <OrdTableCell>
              <OrdBadge :variant="getConvertVariant(demand.convert_status)">
                {{ demand.convert_status }}
              </OrdBadge>
            </OrdTableCell>
            <OrdTableCell>{{ demand.publisher }}</OrdTableCell>
            <OrdTableCell>
              <span class="id-text">{{ demand.task_id || '暂未生成' }}</span>
            </OrdTableCell>
            <OrdTableCell>
              <div class="progress-wrap">
                <OrdProgress :value="demand.progress" />
                <div class="progress-text">{{ demand.progress }}%</div>
              </div>
            </OrdTableCell>
            <OrdTableCell>
              <div class="row-actions">
                <OrdButton
                  variant="outline"
                  size="sm"
                  @click="$router.push(`/demands/${demand.id}`)"
                >
                  详情
                </OrdButton>
                <OrdButton variant="primary" size="sm" @click="openEditModal(demand)">
                  编辑
                </OrdButton>
              </div>
            </OrdTableCell>
          </OrdTableRow>
        </OrdTable>

        <!-- 空状态 -->
        <OrdEmptyState v-if="paginatedDemands.length === 0">
          <template #title>暂无匹配需求</template>
          <template #description>请调整筛选条件</template>
        </OrdEmptyState>
      </div>

      <!-- 分页 -->
      <OrdPagination
        v-model:current-page="currentPage"
        :total="filteredDemands.length"
        :page-size="pageSize"
      />
    </OrdCard>

    <!-- 编辑弹窗 -->
    <OrdDialog v-model:open="isEditModalOpen" title="编辑需求处理信息">
      <template #trigger></template>
      <template #description>
        需求编号、提交时间与发布者为只读信息；运营侧可维护审核、转化、关联任务与反馈。
      </template>

      <form @submit.prevent="handleSubmit" class="edit-form">
        <div class="form-grid">
          <div class="field">
            <label for="demandId">需求编号</label>
            <OrdInput id="demandId" v-model="editForm.id" disabled />
          </div>

          <div class="field">
            <label for="publisher">发布者</label>
            <OrdInput id="publisher" v-model="editForm.publisher" disabled />
          </div>

          <div class="field">
            <label for="submittedAt">提交时间</label>
            <OrdInput id="submittedAt" v-model="editForm.submitted_at" disabled />
          </div>

          <div class="field">
            <label for="taskId">关联任务</label>
            <OrdInput
              id="taskId"
              v-model="editForm.task_id"
              placeholder="如 TASK-1042 或 暂未生成"
            />
          </div>

          <div class="field full">
            <label for="title">需求详情</label>
            <OrdInput id="title" v-model="editForm.title" />
          </div>

          <div class="field">
            <label for="reviewStatus">审核状态</label>
            <OrdSelect
              id="reviewStatus"
              v-model="editForm.review_status"
              :options="reviewStatusOptions"
            />
          </div>

          <div class="field">
            <label for="convertStatus">转化状态</label>
            <OrdSelect
              id="convertStatus"
              v-model="editForm.convert_status"
              :options="convertStatusOptions"
            />
          </div>

          <div class="field">
            <label for="progress">进度</label>
            <OrdInput
              id="progress"
              v-model.number="editForm.progress"
              type="number"
              min="0"
              max="100"
            />
          </div>

          <div class="field full">
            <label for="feedback">平台反馈</label>
            <OrdTextarea
              id="feedback"
              v-model="editForm.feedback"
              placeholder="记录需求审核意见、补充材料或转化结论"
              :rows="4"
            />
          </div>
        </div>
      </form>

      <template #footer>
        <OrdButton type="button" variant="ghost" @click="isEditModalOpen = false">
          取消
        </OrdButton>
        <OrdButton type="submit" variant="primary" :loading="isSubmitting" @click="handleSubmit">
          保存修改
        </OrdButton>
      </template>
    </OrdDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/components/ui/toast/useToast'
import { adminDemandsApi } from '@/api/admin-demands'
import type { AdminDemand } from '@/api/admin-demands'
import {
  OrdButton,
  OrdCard,
  OrdSearchBox,
  OrdSelect,
  OrdTable,
  OrdTableHeader,
  OrdTableRow,
  OrdTableCell,
  OrdBadge,
  OrdProgress,
  OrdEmptyState,
  OrdPagination,
  OrdDialog,
  OrdInput,
  OrdTextarea,
} from '@/components/ui'

const router = useRouter()
const toast = useToast()

// 状态
const demands = ref<AdminDemand[]>([])
const stats = ref({
  total: 0,
  pending: 0,
  talking: 0,
  converted: 0,
  closed: 0,
})
const keyword = ref('')
const reviewFilter = ref('全部')
const convertFilter = ref('全部')
const currentPage = ref(1)
const pageSize = 10
const isEditModalOpen = ref(false)
const isSubmitting = ref(false)
const isLoading = ref(false)

// 编辑表单
const editForm = ref({
  id: '',
  title: '',
  submitted_at: '',
  publisher: '',
  task_id: '',
  review_status: '待审核' as AdminDemand['review_status'],
  convert_status: '未转化' as AdminDemand['convert_status'],
  progress: 0,
  feedback: '',
})

// 筛选选项
const reviewFilterOptions = [
  { value: '全部', label: '全部审核' },
  { value: '待审核', label: '待审核' },
  { value: '沟通中', label: '沟通中' },
  { value: '已转任务', label: '已转任务' },
  { value: '已关闭', label: '已关闭' },
]

const convertFilterOptions = [
  { value: '全部', label: '全部转化' },
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

// 计算属性
const filteredDemands = computed(() => {
  return demands.value.filter((demand) => {
    const matchKeyword =
      !keyword.value ||
      demand.id.toLowerCase().includes(keyword.value.toLowerCase()) ||
      demand.title.toLowerCase().includes(keyword.value.toLowerCase()) ||
      demand.publisher.toLowerCase().includes(keyword.value.toLowerCase()) ||
      demand.task_id?.toLowerCase().includes(keyword.value.toLowerCase())

    const matchReview = reviewFilter.value === '全部' || demand.review_status === reviewFilter.value
    const matchConvert =
      convertFilter.value === '全部' || demand.convert_status === convertFilter.value

    return matchKeyword && matchReview && matchConvert
  })
})

const paginatedDemands = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredDemands.value.slice(start, end)
})

// 方法
function getReviewVariant(status: string) {
  const map: Record<string, any> = {
    待审核: 'orange',
    沟通中: 'purple',
    已转任务: 'green',
    已关闭: 'gray',
  }
  return map[status] || 'blue'
}

function getConvertVariant(status: string) {
  const map: Record<string, any> = {
    未转化: 'gray',
    待评估: 'orange',
    已转化: 'blue',
    开发中: 'orange',
    已完成: 'green',
  }
  return map[status] || 'blue'
}

function openEditModal(demand: AdminDemand) {
  editForm.value = {
    id: demand.id,
    title: demand.title,
    submitted_at: demand.submitted_at,
    publisher: demand.publisher,
    task_id: demand.task_id || '',
    review_status: demand.review_status,
    convert_status: demand.convert_status,
    progress: demand.progress,
    feedback: demand.feedback,
  }
  isEditModalOpen.value = true
}

async function handleSubmit() {
  isSubmitting.value = true
  try {
    await adminDemandsApi.updateDemand(editForm.value.id, {
      title: editForm.value.title,
      task_id: editForm.value.task_id || undefined,
      review_status: editForm.value.review_status,
      convert_status: editForm.value.convert_status,
      progress: editForm.value.progress,
      feedback: editForm.value.feedback,
    })

    // 更新本地数据
    const index = demands.value.findIndex((d) => d.id === editForm.value.id)
    if (index !== -1) {
      demands.value[index] = {
        ...demands.value[index],
        title: editForm.value.title,
        task_id: editForm.value.task_id || null,
        review_status: editForm.value.review_status,
        convert_status: editForm.value.convert_status,
        progress: editForm.value.progress,
        feedback: editForm.value.feedback,
      }
    }

    await fetchStats()
    isEditModalOpen.value = false
    toast.show({
      title: '保存成功',
      description: '需求管理信息已更新',
      variant: 'success',
    })
  } catch (error) {
    toast.show({
      title: '保存失败',
      description: '请稍后重试',
      variant: 'error',
    })
  } finally {
    isSubmitting.value = false
  }
}

async function handleExport() {
  try {
    await adminDemandsApi.exportDemands({
      review_status: reviewFilter.value === '全部' ? undefined : reviewFilter.value,
      convert_status: convertFilter.value === '全部' ? undefined : convertFilter.value,
      keyword: keyword.value || undefined,
    })
    toast.show({
      title: '导出成功',
      description: '已生成需求导出预览',
      variant: 'success',
    })
  } catch (error) {
    toast.show({
      title: '导出失败',
      description: '请稍后重试',
      variant: 'error',
    })
  }
}

async function fetchDemands() {
  isLoading.value = true
  try {
    const res = await adminDemandsApi.getList({
      page: 1,
      page_size: 1000, // 客户端分页
    })
    demands.value = res.data.items
  } catch (error) {
    toast.show({
      title: '加载失败',
      description: '无法加载需求列表',
      variant: 'error',
    })
  } finally {
    isLoading.value = false
  }
}

async function fetchStats() {
  try {
    const res = await adminDemandsApi.getStats()
    stats.value = res.data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

// 监听筛选变化，重置页码
watch([keyword, reviewFilter, convertFilter], () => {
  currentPage.value = 1
})

onMounted(() => {
  fetchDemands()
  fetchStats()
})
</script>

<style scoped>
.demand-management {
  position: relative;
  width: min(1460px, 100%);
  margin: 0 auto;
  display: grid;
  gap: 16px;
}

/* 背景装饰 */
.ambient-ring,
.ambient-node {
  position: fixed;
  pointer-events: none;
  opacity: 0.45;
}

.ambient-ring {
  width: 280px;
  height: 280px;
  right: 5%;
  top: 18%;
  border: 1px solid rgba(255, 174, 19, 0.18);
  border-radius: 50%;
}

.ambient-node {
  width: 12px;
  height: 12px;
  left: 8%;
  bottom: 16%;
  background: var(--ord-color-blue-600);
  border-radius: 50%;
  box-shadow: 38px -22px 0 rgba(237, 82, 203, 0.26), 70px 20px 0 rgba(0, 215, 34, 0.3);
}

/* Hero 卡片 */
.hero-card {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  padding: 32px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(216, 216, 216, 0.9);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
}

.hero-card::after {
  content: '';
  position: absolute;
  width: 190px;
  height: 190px;
  right: -72px;
  top: -94px;
  background: radial-gradient(circle, rgba(255, 174, 19, 0.18), transparent 68%);
}

.section-label {
  margin: 0 0 10px;
  color: var(--ord-color-blue-600);
  font-size: 12px;
  font-weight: 650;
  letter-spacing: 1.3px;
  text-transform: uppercase;
}

h1 {
  margin: 0 0 12px;
  max-width: 760px;
  font-size: clamp(34px, 4vw, 56px);
  line-height: 1.04;
  font-weight: 600;
  letter-spacing: -0.7px;
}

.hero-copy {
  margin: 0;
  max-width: 760px;
  color: var(--ord-color-gray-600);
  font-size: 16px;
  line-height: 1.65;
}

/* 统计卡片 */
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
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(216, 216, 216, 0.9);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
}

.summary-card::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: var(--accent, var(--ord-color-blue-600));
}

.summary-card strong {
  display: block;
  margin-bottom: 8px;
  font-size: 32px;
  line-height: 1;
  font-weight: 600;
}

.summary-card span {
  color: var(--ord-color-gray-600);
  font-size: 14px;
  font-weight: 600;
}

/* 表格卡片 */
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
  color: var(--ord-color-gray-600);
  font-size: 16px;
  line-height: 1.65;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.table-scroll {
  width: 100%;
  overflow-x: auto;
}

.id-text {
  color: var(--ord-color-blue-600);
  font-weight: 650;
  white-space: nowrap;
}

.detail-title {
  margin-bottom: 4px;
  font-weight: 650;
}

.detail-sub {
  color: var(--ord-color-gray-600);
  font-size: 12px;
}

.progress-wrap {
  width: 150px;
}

.progress-text {
  margin-top: 4px;
  color: var(--ord-color-gray-600);
  font-size: 12px;
  font-weight: 600;
  text-align: center;
}

.row-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* 编辑表单 */
.edit-form {
  display: grid;
  gap: 24px;
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

.field label {
  color: var(--ord-color-gray-700);
  font-size: 12px;
  font-weight: 650;
  letter-spacing: 0.8px;
  text-transform: uppercase;
}

/* 响应式 */
@media (max-width: 1180px) {
  .summary-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 992px) {
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
  .summary-grid,
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
