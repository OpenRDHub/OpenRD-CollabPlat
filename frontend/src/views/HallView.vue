<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { OrdButton, OrdBadge, OrdProgress } from '@/components/ui'
import TopNavbar from '@/components/TopNavbar.vue'

const router = useRouter()

// 状态
const activeTab = ref<'tasks' | 'demands'>('tasks')
const searchKeyword = ref('')
const currentPage = ref({ tasks: 1, demands: 1 })
const pageSize = 5

// 任务大厅数据
const tasksHallData = ref([
  { id: 'TASK-1042', title: '用药提醒小程序原型优化', desc: '优化服药日历、提醒规则与家属同步流程。', date: '2026-05-21', status: '解决中', statusClass: 'running', team: '4/5 已组队', progressLabel: '进行中', progress: 68 },
  { id: 'TASK-1051', title: '疾病知识库标签整理', desc: '整理罕见病知识条目标签，提升搜索与推荐准确度。', date: '2026-05-19', status: '招募中', statusClass: 'recruiting', team: '2/4 招募中', progressLabel: '准备中', progress: 24 },
  { id: 'TASK-1024', title: '患者随访表单无障碍改造', desc: '改进移动端填写体验，增加大字号与语义提示。', date: '2026-05-16', status: '已完成', statusClass: 'done', team: '3/3 已完成', progressLabel: '已验收', progress: 100 },
  { id: 'TASK-1017', title: '多病种需求模板合并', desc: '将重复需求模板归并，减少患者提交时的信息负担。', date: '2026-05-12', status: '已关闭', statusClass: 'closed', team: '无需组队', progressLabel: '已归档', progress: 100 },
  { id: 'TASK-1064', title: '复诊问题清单导出功能', desc: '支持患者将症状、用药和提问导出为医生可读的 PDF。', date: '2026-05-27', status: '招募中', statusClass: 'recruiting', team: '1/3 招募中', progressLabel: '待开发', progress: 18 },
  { id: 'TASK-1068', title: '病历摘要结构化字段设计', desc: '为自然语言病历摘要建立字段字典和脱敏展示规则。', date: '2026-05-28', status: '解决中', statusClass: 'running', team: '5/5 已组队', progressLabel: '联调中', progress: 52 },
  { id: 'TASK-1072', title: '任务详情子任务原型', desc: '补充父任务拆分、认领、验收和 Review 的子任务交互。', date: '2026-05-29', status: '解决中', statusClass: 'running', team: '3/4 协作中', progressLabel: '设计中', progress: 41 },
  { id: 'TASK-1076', title: '患者联系方式查看审计', desc: '为产品经理和超级管理员查看联系方式增加审计记录。', date: '2026-05-30', status: '招募中', statusClass: 'recruiting', team: '2/3 招募中', progressLabel: '待排期', progress: 16 },
  { id: 'TASK-1081', title: '附件上传限制提示优化', desc: '在需求提交与沟通区明确附件数量、大小和错误提示。', date: '2026-06-01', status: '已完成', statusClass: 'done', team: '2/2 已完成', progressLabel: '已验收', progress: 100 },
  { id: 'TASK-1086', title: '队伍成员贡献看板', desc: '展示成员认领任务、提交记录、Review 通过率和协作状态。', date: '2026-06-03', status: '解决中', statusClass: 'running', team: '4/6 协作中', progressLabel: '开发中', progress: 37 },
])

// 需求大厅数据
const demandsHallData = ref([
  { id: 'REQ-2440', title: '希望记录复诊前的问题清单', desc: '患者家属希望将近期症状和疑问整理成复诊前摘要。', date: '2026-05-22', status: '待审核', statusClass: 'review', team: '未转任务', progressLabel: '审核中', progress: 12 },
  { id: 'REQ-2418', title: '罕见病资料一键分享给医生', desc: '需要将检查结果、用药历史、症状记录整合为可分享页面。', date: '2026-05-20', status: '已转任务', statusClass: 'recruiting', team: '招募中', progressLabel: '已立项', progress: 32 },
  { id: 'REQ-2432', title: '用药副作用记录提醒', desc: '希望每日快速记录副作用，并在异常时提醒家属查看。', date: '2026-05-18', status: '评估中', statusClass: 'running', team: '运营跟进', progressLabel: '沟通中', progress: 45 },
  { id: 'REQ-2380', title: '患者社群常见问题整理', desc: '将社群中重复出现的问题整理成知识卡片。', date: '2026-05-14', status: '已转化', statusClass: 'done', team: '内容协作', progressLabel: '完成整理', progress: 100 },
  { id: 'REQ-2451', title: '儿童患者用药打卡提醒', desc: '家属希望按儿童作息配置多次提醒，并记录漏服原因。', date: '2026-05-26', status: '待审核', statusClass: 'review', team: '未转任务', progressLabel: '初审中', progress: 8 },
  { id: 'REQ-2457', title: '检查报告指标趋势对比', desc: '希望自动汇总多次检查指标变化，辅助复诊沟通。', date: '2026-05-27', status: '评估中', statusClass: 'running', team: '产品评估', progressLabel: '确认边界', progress: 28 },
  { id: 'REQ-2463', title: '公益项目志愿者教学材料', desc: '需要面向新人共建者的项目背景、开发规范和任务认领说明。', date: '2026-05-29', status: '已转任务', statusClass: 'recruiting', team: '教学中枢', progressLabel: '已拆分', progress: 36 },
  { id: 'REQ-2470', title: '线下义诊信息订阅提醒', desc: '患者希望订阅病种相关义诊、讲座和招募信息。', date: '2026-05-31', status: '待审核', statusClass: 'review', team: '未转任务', progressLabel: '等待审核', progress: 10 },
  { id: 'REQ-2476', title: '病友互助经验卡片模板', desc: '将病友经验整理为可审核、可标签化的知识卡片。', date: '2026-06-02', status: '评估中', statusClass: 'running', team: '运营沟通', progressLabel: '补充材料', progress: 34 },
  { id: 'REQ-2482', title: '任务进度自动通知需求方', desc: '当需求转任务后，自动向需求发布者同步关键进度节点。', date: '2026-06-04', status: '已转任务', statusClass: 'recruiting', team: '平台开发', progressLabel: '排期中', progress: 22 },
])

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
</script>

<template>
  <div class="page-shell">
    <TopNavbar />

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
            <span class="metric-number">128</span>
            <span class="metric-name">总任务</span>
            <span class="metric-note">较上周 +18</span>
          </div>
          <div class="metric-tile solving">
            <span class="metric-number">36</span>
            <span class="metric-name">解决中</span>
            <span class="metric-note">12 个队伍招募中</span>
          </div>
          <div class="metric-tile done">
            <span class="metric-number">74</span>
            <span class="metric-name">已完成</span>
            <span class="metric-note">本月完成 9 个</span>
          </div>
          <div class="metric-tile closed">
            <span class="metric-number">18</span>
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
              <strong>268</strong>
            </div>
            <div class="user-icon patient">P</div>
          </div>
          <div class="user-tile">
            <div>
              <span>志愿者人数</span>
              <strong>412</strong>
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





