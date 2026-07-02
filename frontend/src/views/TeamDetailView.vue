<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { tasksApi } from '@/api/tasks'
import { usersApi } from '@/api/users'
import type { UserSearchItem } from '@/api/users'
import type { Assignment, JoinApplication, Task, TaskMember, TeamTimeline } from '@/api/tasks'
import { useAuthStore } from '@/stores/auth'
import OrdAvatar from '@/components/ui/avatar/OrdAvatar.vue'
import OrdBadge from '@/components/ui/badge/OrdBadge.vue'
import OrdButton from '@/components/ui/button/OrdButton.vue'
import OrdCard from '@/components/ui/card/OrdCard.vue'
import OrdDialog from '@/components/ui/dialog/OrdDialog.vue'
import OrdInput from '@/components/ui/input/OrdInput.vue'
import OrdTextarea from '@/components/ui/input/OrdTextarea.vue'
import OrdProgress from '@/components/ui/progress/OrdProgress.vue'
import OrdSelect from '@/components/ui/select/OrdSelect.vue'
import { useToast } from '@/components/ui/toast/useToast'
import TopNavbar from '@/components/TopNavbar.vue'

type ViewMode = 'leader' | 'member' | 'readonly'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const { show: showToast } = useToast()

const taskId = computed(() => (route.params.taskId as string) || (route.query.task as string) || '')
const loading = ref(true)
const task = ref<Task | null>(null)
const members = ref<TaskMember[]>([])
const applications = ref<JoinApplication[]>([])
const assignments = ref<Assignment[]>([])
const timeline = ref<TeamTimeline[]>([])
const leaderId = ref('')
const stage = ref('')
const viewMode = ref<ViewMode>('readonly')

const showInviteModal = ref(false)
const showAssignmentModal = ref(false)
const inviteForm = ref({ name: '', role: '后端开发', platform: '', due: '', reason: '' })
const assignmentNote = ref('')
const assignmentDrafts = ref<Assignment[]>([])

const searchKeyword = ref('')
const searchResults = ref<UserSearchItem[]>([])
const showSearchDropdown = ref(false)
let searchTimer: ReturnType<typeof setTimeout> | null = null

function onSearchInput(val: string) {
  searchKeyword.value = val
  if (searchTimer) clearTimeout(searchTimer)
  if (!val.trim()) {
    searchResults.value = []
    showSearchDropdown.value = false
    return
  }
  searchTimer = setTimeout(async () => {
    try {
      const res = await usersApi.search(val.trim())
      searchResults.value = res.data
      showSearchDropdown.value = res.data.length > 0
    } catch {
      searchResults.value = []
      showSearchDropdown.value = false
    }
  }, 300)
}

function selectUser(user: UserSearchItem) {
  inviteForm.value.name = user.nickname || user.platform_id
  inviteForm.value.platform = user.platform_id
  searchKeyword.value = user.nickname ? `${user.nickname} (${user.platform_id})` : user.platform_id
  showSearchDropdown.value = false
  searchResults.value = []
}
const roleOptions = [
  { value: '后端开发', label: '后端开发' },
  { value: '前端开发', label: '前端开发' },
  { value: '算法工程师', label: '算法工程师' },
  { value: '测试工程师', label: '测试工程师' },
  { value: '医学内容协作', label: '医学内容协作' },
  { value: '运营协调', label: '运营协调' },
]

const taskCopy: Record<string, Partial<Task> & { demandSource?: string }> = {
  'TASK-1042': {
    title: '用药提醒小程序原型优化',
    description: '队伍已基本成型，当前重点是后端接口、消息队列和前端联调说明，同时仍有补充角色申请等待队长审核。',
    task_type: '功能开发',
    demandSource: 'REQ-2418 · 复诊问题清单与用药提醒',
  },
  'TASK-1051': {
    title: '疾病知识库标签整理',
    description: '该任务处于早期拆解阶段，队长需要审核加入申请，并确认模型评估、数据脱敏和前端预览的协作分工。',
    task_type: '数据工程',
    demandSource: 'REQ-2421 · 罕见病知识条目治理',
  },
}

const memberCopy: Record<string, Partial<TaskMember>> = {
  'tm-001': { role: '前端开发', duty: '小程序页面重构', name: '林子轩', platform: 'builder_linzixuan', active: '刚刚活跃' },
  'tm-002': { role: '产品经理', duty: '需求跟进与验收', name: '赵明', platform: 'operator_zhaoming', active: '2 小时前' },
  'tm-003': { role: '后端开发', duty: '提醒规则引擎', name: '陆一', platform: 'backend_luyi', active: '在线' },
  'tm-004': { role: 'UI 设计', duty: '日历组件视觉', name: '许见', platform: 'ux_xujian', active: '在线' },
  'tm-005': { role: '数据工程师', duty: '标签体系设计', name: '林子轩', platform: 'builder_linzixuan', active: '刚刚活跃' },
  'tm-006': { role: '产品经理', duty: '标签规范审核', name: '赵明', platform: 'operator_zhaoming', active: '2 小时前' },
}

const applicationCopy: Record<string, Partial<JoinApplication>> = {
  'app-001': { name: '周南', platform: 'nlp_zhou', role: '算法工程师', skills: ['自然语言处理', '数据脱敏'], reason: '有医疗文本摘要经验，希望负责模型评估。' },
  'app-002': { name: '许见', platform: 'ux_xujian', role: 'UI/UX 设计师', skills: ['原型设计', '可视化'], reason: '可以协助设计摘要结果预览界面。' },
  'app-003': { name: '梁知', platform: 'data_liangzhi', role: '数据标注意愿者', skills: ['医学术语', '样例标注'], reason: '熟悉病历字段整理，可以协助校对脱敏样例。' },
  'app-004': { name: '韩立', platform: 'doc_hanli', role: '文档协作', skills: ['需求整理', '验收文档'], reason: '希望负责字段说明和验收记录整理。' },
  'app-005': { name: '沈越', platform: 'backend_shenyue', role: '后端开发', skills: ['API 设计', '数据结构'], reason: '可以补充摘要结果保存接口和任务数据结构。' },
  'app-006': { name: '顾晓', platform: 'qa_guxiao', role: '测试工程师', skills: ['接口测试', '边界用例'], reason: '可以补充提醒频率、关闭规则和异常消息队列的测试用例。' },
  'app-007': { name: '陆一', platform: 'backend_luyi', role: '后端开发', skills: ['消息队列', '定时任务'], reason: '有提醒服务和异步队列经验，希望协助处理重试策略。' },
  'app-008': { name: '苏棠', platform: 'writer_sutang', role: '医学内容协作', skills: ['用药说明', '用户文案'], reason: '可以协助梳理提醒文案，避免给患者造成压力。' },
}

const assignmentCopy: Record<string, Partial<Assignment>> = {
  'asgn-001': { title: '加入申请审核', owner: '林子轩', deliverable: '确认成员与职责' },
  'asgn-002': { title: '标签体系设计', owner: '林子轩', deliverable: '标签字段清单' },
  'asgn-003': { title: '搜索权重调优方案', owner: '待分配', deliverable: '搜索评估标准' },
  'asgn-004': { title: '接口联调说明', owner: '林子轩', deliverable: '字段与错误码文档' },
  'asgn-005': { title: '提醒配置界面', owner: '赵明', deliverable: '交互稿与组件说明' },
  'asgn-006': { title: '需求者验收', owner: '陈北', deliverable: '验收反馈记录' },
}

const timelineCopy: Record<string, Partial<TeamTimeline>> = {
  'tl-001': { title: '任务创建完成', description: '已拆分为标签体系设计、现有条目重标注、搜索权重调优三个阶段。' },
  'tl-002': { title: '收到加入申请', description: '5 位成员提交加入申请，等待队长审核。' },
  'tl-003': { title: '标签体系评审排期', description: '计划确认标签分类边界与样例要求。' },
  'tl-004': { title: '队伍招募完成', description: '后端、设计、运营协调角色已确认。' },
  'tl-005': { title: '进入接口联调', description: '后端开始补充联调说明。' },
  'tl-006': { title: '收到补充申请', description: '3 位成员申请加入测试、后端队列和医学文案协作。' },
  'tl-007': { title: '准备验收', description: '完成联调后进入需求者验收。' },
}

const currentTask = computed(() => ({ ...task.value, ...taskCopy[task.value?.id || ''] }))
const normalizedMembers = computed(() => members.value.map((item) => ({ ...item, ...memberCopy[item.id] })))
const normalizedApplications = computed(() => applications.value.map((item) => ({ ...item, ...applicationCopy[item.id] })))
const normalizedAssignments = computed(() => assignments.value.map((item) => ({ ...item, ...assignmentCopy[item.id] })))
const normalizedTimeline = computed(() => timeline.value.map((item) => ({ ...item, ...timelineCopy[item.id] })))

const isLeader = computed(() => auth.user?.id === leaderId.value || auth.userRole === 'super_admin')
const isMember = computed(() => isLeader.value || normalizedMembers.value.some((item) => item.user_id === auth.user?.id))
const canManage = computed(() => viewMode.value === 'leader' && isLeader.value)
const pendingApplications = computed(() => normalizedApplications.value.filter((item) => item.status === 'pending'))
const leaderName = computed(() => normalizedMembers.value.find((item) => item.user_id === leaderId.value)?.name || '待分配')
const demandSource = computed(() => taskCopy[task.value?.id || '']?.demandSource || (task.value?.demand_id ? `${task.value.demand_id} · 关联需求` : '无关联需求'))

const statusText = computed(() => {
  if (viewMode.value === 'leader') return task.value?.team_status === 'collaborating' ? '解决中 · 协作推进' : '待处理 · 招募中'
  if (viewMode.value === 'member') return '成员协作视角'
  return '只读浏览'
})

function setViewMode(mode: ViewMode) {
  if (mode === 'leader' && !isLeader.value) return
  if (mode === 'member' && !isMember.value) return
  viewMode.value = mode
}

function determineViewMode() {
  if (isLeader.value) viewMode.value = 'leader'
  else if (isMember.value) viewMode.value = 'member'
  else viewMode.value = 'readonly'
}

async function loadData() {
  if (!taskId.value) {
    loading.value = false
    return
  }

  try {
    loading.value = true
    const [taskRes, teamRes] = await Promise.all([
      tasksApi.getDetail(taskId.value),
      tasksApi.getTeam(taskId.value),
    ])

    task.value = taskRes.data
    members.value = (teamRes.data.members || []).map((m: any) => ({
      ...m,
      name: m.name || '',
      platform: m.platform_id || m.platform || '',
    }))
    leaderId.value = teamRes.data.leader_id || taskRes.data.leader_id || ''
    stage.value = taskRes.data.team_status === 'collaborating' ? '接口联调' : '成员确认'
    applications.value = teamRes.data.applications || []
    assignments.value = teamRes.data.assignments || []
    timeline.value = []
    determineViewMode()
  } catch {
    task.value = null
  } finally {
    loading.value = false
  }
}

function openInviteModal() {
  if (!canManage.value) {
    showToast({ title: '只有队长可以邀请成员', variant: 'error' })
    return
  }
  inviteForm.value = {
    name: '',
    role: '后端开发',
    platform: '',
    due: '',
    reason: `邀请加入「${currentTask.value.title}」，优先补齐 ${stage.value} 阶段所需角色。`,
  }
  searchKeyword.value = ''
  searchResults.value = []
  showSearchDropdown.value = false
  showInviteModal.value = true
}

async function handleInvite() {
  const platformId = inviteForm.value.platform.trim()
  if (!platformId) {
    showToast({ title: '请输入被邀请人的平台号', variant: 'error' })
    return
  }
  await tasksApi.inviteMember(taskId.value, {
    platform_id: platformId,
    suggested_role: inviteForm.value.role,
    reason: inviteForm.value.reason || undefined,
    due_time: inviteForm.value.due || undefined,
  })
  showInviteModal.value = false
  showToast({ title: `已向 ${platformId} 发送邀请`, variant: 'success' })
  loadData()
}

function openAssignmentModal() {
  if (!canManage.value) {
    showToast({ title: '只有队长可以调整分工', variant: 'error' })
    return
  }
  assignmentNote.value = `根据 ${stage.value} 阶段进度，调整负责人、交付物和截止时间。`
  assignmentDrafts.value = normalizedAssignments.value.map((item) => ({ ...item }))
  showAssignmentModal.value = true
}

function addAssignmentDraft() {
  assignmentDrafts.value.push({
    id: `draft-${Date.now()}`,
    task_id: taskId.value,
    title: '新增分工事项',
    owner: '待分配',
    deliverable: '待确认交付物',
    due: '2026-06-05',
    status: 'wait',
  })
}

function removeAssignmentDraft(index: number) {
  assignmentDrafts.value.splice(index, 1)
}

async function saveAssignments() {
  const valid = assignmentDrafts.value.filter((item) => item.title.trim())
  await tasksApi.saveAssignments(taskId.value, { assignments: valid })
  assignments.value = valid
  showAssignmentModal.value = false
  showToast({ title: '分工已更新', variant: 'success' })
}

async function handleApprove(app: JoinApplication) {
  await tasksApi.approveJoin(taskId.value, app.id)
  app.status = 'approved'
  showToast({ title: `已通过 ${app.name} 的加入申请`, variant: 'success' })
}

async function handleReject(app: JoinApplication) {
  await tasksApi.rejectJoin(taskId.value, app.id)
  app.status = 'rejected'
  showToast({ title: `已拒绝 ${app.name} 的加入申请`, variant: 'success' })
}

function taskStatusLabel(status?: string) {
  const labels: Record<string, string> = {
    recruiting: '招募中',
    in_progress: '解决中',
    completed: '已完成',
    closed: '已关闭',
  }
  return labels[status || ''] || status || '未设置'
}

function assignmentStatusLabel(status: Assignment['status']) {
  return { done: '已完成', doing: '进行中', wait: '待开始' }[status]
}

onMounted(loadData)
</script>

<template>
  <div class="team-detail-page">
    <TopNavbar />

    <main class="team-frame">
      <OrdCard v-if="loading" class="state-card">
        <p>加载中...</p>
      </OrdCard>

      <OrdCard v-else-if="!task" class="state-card">
        <p class="eyebrow">Team Not Found</p>
        <h1>没有找到该任务队伍</h1>
        <p>当前任务 ID 不存在或暂未创建队伍，请返回工作台重新选择。</p>
        <OrdButton variant="primary" @click="router.push('/workbench')">返回工作台</OrdButton>
      </OrdCard>

      <template v-else>
        <OrdCard class="overview-card" aria-label="队伍概览">
          <div class="hero-card">
            <div>
              <p class="eyebrow">Task-bound Team</p>
              <h1 class="hero-title">{{ currentTask.title }}</h1>
              <p class="hero-copy">{{ currentTask.description }}</p>
              <div class="tag-row">
                <OrdBadge variant="blue">{{ taskStatusLabel(task.status) }}</OrdBadge>
                <OrdBadge variant="purple">{{ demandSource }}</OrdBadge>
                <OrdBadge variant="green">队长：{{ leaderName }}</OrdBadge>
              </div>
            </div>

            <aside class="task-side">
              <span class="task-side__badge">{{ task.id }}</span>
              <strong class="task-side__progress">{{ task.progress }}%</strong>
              <div class="progress-line">
                <OrdProgress :value="task.progress" variant="blue" />
              </div>
              <p>{{ statusText }}</p>
            </aside>
          </div>

          <div class="stat-grid" aria-label="队伍状态概览">
            <article class="stat-card"><p class="stat-label">队长</p><p class="stat-value">{{ leaderName }}</p><p class="stat-desc">当前任务队伍负责人</p></article>
            <article class="stat-card stat-card--green"><p class="stat-label">成员数</p><p class="stat-value">{{ normalizedMembers.length }}</p><p class="stat-desc">已加入正式协作成员</p></article>
            <article class="stat-card stat-card--orange"><p class="stat-label">待审核申请</p><p class="stat-value">{{ pendingApplications.length }}</p><p class="stat-desc">需要队长处理的加入申请</p></article>
            <article class="stat-card stat-card--purple"><p class="stat-label">协作阶段</p><p class="stat-value">{{ stage }}</p><p class="stat-desc">当前队伍推进节点</p></article>
          </div>
        </OrdCard>

        <section class="content-grid">
          <OrdCard class="panel-card" aria-label="成员列表">
            <header class="panel-head">
              <h2 class="panel-title">队伍成员</h2>
              <OrdButton v-if="canManage" variant="ghost" @click="openInviteModal">邀请成员</OrdButton>
            </header>
            <div class="panel-body">
              <div class="member-scroll">
                <div class="member-list">
                  <article v-for="member in normalizedMembers" :key="member.id" class="member-item">
                    <OrdAvatar :name="member.name || member.duty" size="md" />
                    <div>
                      <p class="item-title">{{ member.name || member.duty }} · {{ member.role }}</p>
                      <p class="item-meta">{{ member.platform }} · {{ member.duty }} · {{ member.active || '协作中' }}</p>
                    </div>
                    <OrdBadge :variant="member.status === 'active' ? 'green' : 'gray'">{{ member.status === 'active' ? '协作中' : '离线' }}</OrdBadge>
                  </article>
                </div>
              </div>
            </div>
          </OrdCard>

          <OrdCard class="panel-card" aria-label="加入申请">
            <header class="panel-head">
              <h2 class="panel-title">加入申请</h2>
              <OrdBadge variant="orange">{{ pendingApplications.length }} 待审核</OrdBadge>
            </header>
            <div class="panel-body">
              <div class="member-scroll">
                <div class="application-list">
                  <article v-for="app in pendingApplications" :key="app.id" class="application-item">
                    <div>
                      <p class="item-title">{{ app.name }} · {{ app.role }}</p>
                      <p class="item-meta">{{ app.platform }} · {{ app.reason }}</p>
                      <div class="skill-row">
                        <OrdBadge v-for="skill in app.skills" :key="skill" variant="purple">{{ skill }}</OrdBadge>
                      </div>
                      <p class="item-meta">申请时间：{{ app.time }}</p>
                    </div>
                    <div v-if="canManage" class="action-row">
                      <OrdButton variant="ghost" size="sm" @click="handleApprove(app)">通过</OrdButton>
                      <OrdButton class="danger-button" variant="ghost" size="sm" @click="handleReject(app)">拒绝</OrdButton>
                    </div>
                    <OrdBadge v-else variant="gray">{{ viewMode === 'member' ? '等待队长审核' : '只读' }}</OrdBadge>
                  </article>
                  <p v-if="!pendingApplications.length" class="empty-line">当前没有待审核加入申请。</p>
                </div>
              </div>
            </div>
          </OrdCard>

          <OrdCard class="panel-card" aria-label="分工计划">
            <header class="panel-head">
              <h2 class="panel-title">任务分工</h2>
              <OrdButton v-if="canManage" variant="ghost" @click="openAssignmentModal">调整分工</OrdButton>
            </header>
            <div class="panel-body assignment-list">
              <article v-for="item in normalizedAssignments" :key="item.id" class="assignment-item">
                <div>
                  <p class="item-title">{{ item.title }}</p>
                  <p class="item-meta">负责人：{{ item.owner }} · 交付物：{{ item.deliverable }} · 截止：{{ item.due }}</p>
                </div>
                <span class="status-tag" :class="item.status">{{ assignmentStatusLabel(item.status) }}</span>
              </article>
            </div>
          </OrdCard>

          <OrdCard class="panel-card" aria-label="队伍动态">
            <header class="panel-head">
              <h2 class="panel-title">队伍动态</h2>
              <OrdBadge variant="gray">Timeline</OrdBadge>
            </header>
            <div class="panel-body timeline-list">
              <article v-for="item in normalizedTimeline" :key="item.id" class="timeline-item" :class="`is-${item.state}`">
                <span class="timeline-dot" />
                <div>
                  <p class="item-title">{{ item.title }}</p>
                  <p class="item-meta">{{ item.description }}</p>
                </div>
                <span class="timeline-date">{{ item.date }}</span>
              </article>
            </div>
          </OrdCard>
        </section>
      </template>
    </main>

    <OrdDialog v-model="showInviteModal">
      <header class="modal-header">
        <div>
          <p class="eyebrow">Invite Member</p>
          <h2>邀请成员</h2>
        </div>
        <button class="modal-close" type="button" aria-label="关闭" @click="showInviteModal = false">×</button>
      </header>
      <div class="modal-body">
        <label class="field field--autocomplete">
          <span>邀请对象</span>
          <div class="autocomplete-wrap">
            <OrdInput :model-value="searchKeyword" placeholder="输入昵称或平台号搜索" @update:model-value="onSearchInput" />
            <ul v-if="showSearchDropdown" class="autocomplete-list">
              <li v-for="u in searchResults" :key="u.platform_id" class="autocomplete-item" @mousedown.prevent="selectUser(u)">
                <span class="ac-name">{{ u.nickname || u.platform_id }}</span>
                <span class="ac-pid">{{ u.platform_id }}</span>
              </li>
            </ul>
          </div>
        </label>
        <label class="field"><span>平台 ID</span><OrdInput v-model="inviteForm.platform" placeholder="选择用户后自动填入" readonly /></label>
        <label class="field"><span>建议角色</span><OrdSelect v-model="inviteForm.role" :options="roleOptions" placeholder="选择角色" /></label>
        <label class="field"><span>期望响应时间</span><OrdInput v-model="inviteForm.due" type="date" /></label>
        <label class="field field--full"><span>邀请说明</span><OrdTextarea v-model="inviteForm.reason" :rows="3" /></label>
      </div>
      <footer class="modal-footer">
        <OrdButton variant="ghost" @click="showInviteModal = false">取消</OrdButton>
        <OrdButton variant="primary" @click="handleInvite">发送邀请</OrdButton>
      </footer>
    </OrdDialog>

    <OrdDialog v-model="showAssignmentModal">
      <header class="modal-header">
        <div>
          <p class="eyebrow">Assignments</p>
          <h2>调整分工</h2>
        </div>
        <button class="modal-close" type="button" aria-label="关闭" @click="showAssignmentModal = false">×</button>
      </header>
      <div class="modal-body modal-body--assignment">
        <label class="field field--full"><span>调整说明</span><OrdTextarea v-model="assignmentNote" :rows="2" /></label>
        <section class="assignment-editor-section">
          <div class="assignment-editor-head">
            <p>可新增临时分工，也可删除不再需要的分工项。</p>
            <OrdButton variant="ghost" size="sm" @click="addAssignmentDraft">增加分工</OrdButton>
          </div>
          <article v-for="(draft, index) in assignmentDrafts" :key="draft.id || index" class="assignment-editor-item">
            <label><span>分工事项</span><OrdInput v-model="draft.title" /></label>
            <label><span>负责人</span><OrdInput v-model="draft.owner" /></label>
            <label><span>交付物</span><OrdInput v-model="draft.deliverable" /></label>
            <label><span>截止</span><OrdInput v-model="draft.due" /></label>
            <label><span>状态</span><OrdSelect v-model="draft.status" :options="[{ value: 'done', label: '已完成' }, { value: 'doing', label: '进行中' }, { value: 'wait', label: '待开始' }]" /></label>
            <button class="icon-danger-button" type="button" aria-label="删除分工" @click="removeAssignmentDraft(index)">×</button>
          </article>
          <p v-if="!assignmentDrafts.length" class="empty-line">当前没有分工项，请点击“增加分工”创建。</p>
        </section>
      </div>
      <footer class="modal-footer">
        <OrdButton variant="ghost" @click="showAssignmentModal = false">取消</OrdButton>
        <OrdButton variant="primary" @click="saveAssignments">保存分工</OrdButton>
      </footer>
    </OrdDialog>
  </div>
</template>

<style scoped>
.team-detail-page {
  min-height: 100vh;
  color: var(--ord-color-black);
  background:
    radial-gradient(circle at 12% 12%, rgba(20, 110, 245, 0.08), transparent 28%),
    radial-gradient(circle at 86% 18%, rgba(122, 61, 255, 0.06), transparent 24%),
    radial-gradient(circle at 80% 86%, rgba(255, 174, 19, 0.052), transparent 28%),
    linear-gradient(135deg, #ffffff 0%, #f7f9ff 100%);
}

.team-frame {
  position: relative;
  width: min(1460px, 100%);
  margin: 0 auto;
  padding: 96px 32px 32px;
  display: grid;
  gap: 18px;
}

.team-frame::before,
.team-frame::after {
  content: "";
  position: absolute;
  z-index: 0;
  border: 1px solid rgba(20, 110, 245, 0.2);
  border-radius: 48%;
  pointer-events: none;
}

.team-frame::before { width: 180px; height: 86px; top: 96px; right: 42px; }
.team-frame::after { width: 108px; height: 108px; right: 214px; bottom: 56px; transform: rotate(4deg); }

.state-card {
  min-height: 420px;
  display: grid;
  place-items: center;
  gap: 12px;
  text-align: center;
  padding: 42px 24px;
}

.state-card h1,
.hero-title,
.panel-head h2,
.modal-header h2 {
  margin: 0;
  font-weight: 600;
}

.state-card h1 { font-size: clamp(32px, 4vw, 48px); }
.state-card p { max-width: 560px; margin: 0; color: var(--ord-color-gray-500); line-height: 1.7; }

.overview-card,
.panel-card {
  position: relative;
  z-index: 1;
}

.overview-card {
  padding: 28px;
  display: grid;
  gap: 20px;
}

.hero-card {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 24px;
  padding: 0 0 22px;
  border-bottom: 1px solid #ececec;
}

.eyebrow {
  margin: 0 0 10px;
  color: var(--ord-color-blue);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.4px;
  text-transform: uppercase;
}

.hero-title {
  max-width: 860px;
  font-size: clamp(34px, 4vw, 56px);
  line-height: 1.04;
}

.hero-copy {
  max-width: 760px;
  margin: 16px 0 0;
  color: var(--ord-color-gray-700);
  font-size: 16px;
  line-height: 1.65;
}

.tag-row,
.skill-row,
.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-row { margin-top: 16px; }

.task-side {
  display: grid;
  align-content: center;
  gap: 12px;
  padding: 18px;
  color: var(--ord-color-white);
  background: var(--ord-color-black);
  border-radius: var(--ord-radius-md);
}

.task-side p { margin: 0; color: rgba(255, 255, 255, 0.72); font-size: 13px; line-height: 1.55; }
.task-side__badge { width: max-content; padding: 5px 8px; background: rgba(20, 110, 245, 0.9); border-radius: 4px; font-size: 11px; font-weight: 700; letter-spacing: 1px; }
.task-side__progress { font-size: 34px; font-weight: 600; line-height: 1; }
.progress-line { overflow: hidden; border-radius: 999px; }
.task-side :deep(.ord-progress) { height: 9px; background: rgba(255, 255, 255, 0.16); }

.stat-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.stat-card {
  min-height: 106px;
  padding: 18px;
  background: #fff;
  border: 1px solid rgba(216, 216, 216, 0.82);
  border-left: 4px solid var(--ord-color-blue);
  border-radius: 6px;
}

.stat-card--green { border-left-color: var(--ord-color-green); }
.stat-card--orange { border-left-color: var(--ord-color-orange); }
.stat-card--purple { border-left-color: var(--ord-color-purple); }
.stat-label { margin: 0; color: var(--ord-color-gray-500); font-size: 11px; font-weight: 700; letter-spacing: 1.1px; text-transform: uppercase; }
.stat-value { margin: 12px 0 0; color: var(--ord-color-black); font-size: 34px; font-weight: 600; line-height: 1; }
.stat-desc { margin: 10px 0 0; color: var(--ord-color-gray-500); font-size: 13px; line-height: 1.45; }

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(380px, 0.72fr);
  gap: 18px;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 18px;
  border-bottom: 1px solid #ececec;
}

.panel-head h2 { margin: 0; font-size: 22px; font-weight: 600; line-height: 1.2; }

.panel-body {
  padding: 18px;
  display: grid;
  gap: 14px;
}

.member-scroll {
  position: relative;
  overflow: hidden;
  padding: 10px;
  background: linear-gradient(180deg, #ffffff, #f8fbff);
  border: 1px solid rgba(20, 110, 245, 0.14);
  border-radius: 8px;
}

.member-scroll::after {
  content: "";
  position: absolute;
  left: 10px;
  right: 10px;
  bottom: 10px;
  height: 42px;
  pointer-events: none;
  background: linear-gradient(180deg, rgba(248, 251, 255, 0), rgba(248, 251, 255, 0.98));
}

.member-list,
.application-list {
  max-height: 322px;
  overflow-y: auto;
  padding: 0 8px 56px 0;
  scroll-padding-bottom: 56px;
  display: grid;
  gap: 10px;
}

.member-list::-webkit-scrollbar,
.application-list::-webkit-scrollbar { width: 6px; }
.member-list::-webkit-scrollbar-thumb,
.application-list::-webkit-scrollbar-thumb { background: rgba(20, 110, 245, 0.22); border-radius: 999px; }

.assignment-list,
.timeline-list {
  display: grid;
  gap: 10px;
}

.member-item,
.application-item,
.assignment-item,
.timeline-item {
  display: grid;
  gap: 12px;
  padding: 13px;
  background: #fff;
  border: 1px solid #ececec;
  border-radius: 6px;
}

.member-item { grid-template-columns: auto minmax(0, 1fr) auto; align-items: center; }
.application-item { grid-template-columns: minmax(0, 1fr) auto; align-items: start; }
.assignment-item { grid-template-columns: minmax(0, 1fr) max-content; align-items: center; }
.timeline-item { grid-template-columns: 18px minmax(0, 1fr) auto; align-items: start; }

.item-title { margin: 0; font-size: 14px; font-weight: 700; line-height: 1.35; }
.item-meta { margin: 5px 0 0; color: var(--ord-color-gray-500); font-size: 12px; line-height: 1.45; }
.empty-line { margin: 0; padding: 16px; color: var(--ord-color-gray-500); text-align: center; }
.danger-button { color: var(--ord-color-red) !important; border-color: var(--ord-color-red) !important; }

.status-tag {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.status-tag.done { color: #009e19; background: rgba(0, 215, 34, 0.12); }
.status-tag.doing { color: var(--ord-color-blue); background: rgba(20, 110, 245, 0.08); }
.status-tag.wait { color: #b27600; background: rgba(255, 174, 19, 0.16); }

.timeline-dot { width: 10px; height: 10px; margin-top: 5px; background: var(--ord-color-blue); border-radius: 50%; }
.timeline-item.is-done .timeline-dot { background: var(--ord-color-green); }
.timeline-item.is-wait .timeline-dot { background: var(--ord-color-gray-300); }
.timeline-date { color: var(--ord-color-gray-500); font-size: 12px; white-space: nowrap; }

.modal-header,
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 20px;
  border-bottom: 1px solid #ececec;
}

.modal-footer {
  justify-content: flex-end;
  border-top: 1px solid #ececec;
  border-bottom: 0;
}

.modal-header h2 { font-size: 24px; }

.modal-body {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  max-height: min(580px, calc(100vh - 190px));
  overflow: auto;
  padding: 20px;
  background: linear-gradient(180deg, #fff 0%, #f8faff 100%);
}

.modal-body--assignment {
  grid-template-columns: 1fr;
  padding: 0;
}

.field--full {
  grid-column: 1 / -1;
}

.field,
.assignment-editor-item label {
  display: grid;
  gap: 7px;
}

.field span,
.assignment-editor-item span {
  color: var(--ord-color-gray-500);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.assignment-editor-section { display: grid; gap: 12px; grid-column: 1 / -1; }
.assignment-editor-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 0 0 4px; }
.assignment-editor-head p { margin: 0; color: var(--ord-color-gray-500); font-size: 12px; line-height: 1.45; }
.assignment-editor-item {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(110px, 0.68fr) minmax(150px, 0.9fr) 116px 110px auto;
  gap: 10px;
  align-items: end;
  padding: 12px;
  background: #fff;
  border: 1px solid #ececec;
  border-radius: 6px;
}

.icon-danger-button {
  width: 42px;
  height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--ord-color-red);
  background: rgba(238, 29, 54, 0.08);
  border: 1px solid rgba(238, 29, 54, 0.18);
  border-radius: 4px;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  transition: transform 180ms ease, background 180ms ease, border-color 180ms ease;
}

.icon-danger-button:hover {
  background: rgba(238, 29, 54, 0.12);
  border-color: rgba(238, 29, 54, 0.34);
  transform: translateX(6px);
}

:deep(.ord-dialog__content) { padding: 0; width: min(1200px, calc(100vw - 48px)); }
:deep(.ord-dialog__title),
:deep(.ord-dialog__description),
:deep(.ord-dialog__footer) { display: none; }

.modal-close {
  width: 38px;
  height: 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--ord-color-black);
  background: #fff;
  border: 1px solid var(--ord-color-border);
  border-radius: 4px;
  cursor: pointer;
  font-size: 22px;
  line-height: 1;
  transition: border-color 180ms ease;
}

.modal-close:hover {
  border-color: var(--ord-color-blue);
  color: var(--ord-color-blue);
}

@media (max-width: 992px) {
  .hero-card,
  .content-grid {
    grid-template-columns: 1fr;
  }
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .team-frame {
    padding: 92px 16px 24px;
  }
  .stat-grid,
  .member-item,
  .application-item,
  .assignment-item,
  .timeline-item,
  .modal-body,
  .assignment-editor-item {
    grid-template-columns: 1fr;
  }
  .modal-footer {
    align-items: stretch;
    flex-direction: column-reverse;
  }
}

.field--autocomplete {
  position: relative;
}

.autocomplete-wrap {
  position: relative;
}

.autocomplete-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 100;
  margin: 4px 0 0;
  padding: 4px 0;
  list-style: none;
  background: #fff;
  border-radius: var(--ord-radius-md, 8px);
  box-shadow: rgba(0, 0, 0, 0.08) 0px 0px 0px 1px, rgba(0, 0, 0, 0.06) 0px 4px 12px;
  max-height: 200px;
  overflow-y: auto;
}

.autocomplete-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  cursor: pointer;
  transition: background 120ms ease;
}

.autocomplete-item:hover {
  background: var(--ord-color-gray-50, #fafafa);
}

.ac-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--ord-color-black, #171717);
}

.ac-pid {
  font-size: 12px;
  color: var(--ord-color-gray-500, #666);
  font-family: var(--ord-font-mono, monospace);
}
</style>
