<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { tasksApi } from '@/api/tasks'
import type { Task, TaskMember } from '@/api/tasks'
import { useAuthStore } from '@/stores/auth'
import OrdButton from '@/components/ui/button/OrdButton.vue'
import OrdBadge from '@/components/ui/badge/OrdBadge.vue'
import OrdCard from '@/components/ui/card/OrdCard.vue'
import OrdProgress from '@/components/ui/progress/OrdProgress.vue'
import OrdTimeline from '@/components/ui/timeline/OrdTimeline.vue'
import OrdDialog from '@/components/ui/dialog/OrdDialog.vue'
import OrdInput from '@/components/ui/input/OrdInput.vue'
import OrdTextarea from '@/components/ui/input/OrdTextarea.vue'
import { useToast } from '@/components/ui/toast/useToast'
import TopNavbar from '@/components/TopNavbar.vue'

type ViewMode = 'leader' | 'builder' | 'readonly'

interface MilestoneItem {
  title: string
  description: string
  date: string
  state: 'done' | 'doing' | 'wait'
}

interface ResourceLink {
  label: string
  url: string
}

interface TaskDetail {
  id: string
  title: string
  desc: string
  brief: string
  createdAt: string
  status: string
  teamStatus: string
  progress: number
  myRole: string
  action: string
  demandId: string
  isCurrentUserLeader: boolean
  isCurrentUserMember: boolean
  taskInfo: {
    sourceDemand: string
    productManager: string
    taskType: string
    priority: string
    scope: string
    acceptance: string
  }
  members: { name: string; role: string; isMe: boolean }[]
  milestones: MilestoneItem[]
  files: string[]
  resources: ResourceLink[]
  actions: string[]
}

const route = useRoute()
const router = useRouter()
const { show: showToast } = useToast()
const auth = useAuthStore()

const taskId = ref(route.params.id as string)
const loading = ref(true)
const task = ref<TaskDetail | null>(null)
const viewMode = ref<ViewMode>('readonly')
const hasJoinedTeam = ref(false)
const showEditModal = ref(false)
const saving = ref(false)

const editForm = ref({
  productManager: '',
  taskType: '',
  priority: '',
  scope: '',
  acceptance: '',
  resources: [] as ResourceLink[],
  files: [] as string[],
  actions: [] as string[],
})

const PRIORITY_TO_API: Record<string, string> = { '高': 'high', '中': 'medium', '低': 'low' }

const isLeader = computed(() => {
  if (!task.value) return false
  if (auth.userRole === 'super_admin') return true
  return task.value.isCurrentUserLeader
})

const isBuilder = computed(() => {
  if (!task.value) return false
  return task.value.isCurrentUserMember && !task.value.isCurrentUserLeader
})

const canEdit = computed(() => {
  if (auth.userRole === 'super_admin') return true
  if (isLeader.value) return true
  if (hasJoinedTeam.value) return true
  return false
})

const currentRoleLabel = computed(() => {
  if (auth.userRole === 'super_admin') return '超级管理员'
  if (isLeader.value) return '队长'
  if (viewMode.value === 'builder' || hasJoinedTeam.value) return '共建者'
  if (auth.userRole === 'requester') return '需求者'
  return '只读'
})

const currentActionLabel = computed(() => {
  if (!task.value) return ''
  if (canEdit.value) return task.value.action
  return '仅查看任务进展'
})

const statusLabelMap: Record<string, string> = {
  in_progress: '解决中',
  recruiting: '招募中',
  pending_acceptance: '待验收',
  completed: '已完成',
  pending: '待处理',
  closed: '已关闭',
}

const teamStatusLabelMap: Record<string, string> = {
  collaborating: '协作中',
  forming: '招募中',
  accepted: '已验收',
}

const statusBadgeVariant = computed(() => {
  if (!task.value) return 'blue'
  const map: Record<string, string> = {
    in_progress: 'blue',
    recruiting: 'orange',
    pending_acceptance: 'purple',
    completed: 'green',
    pending: 'orange',
    '待处理': 'orange',
    '解决中': 'blue',
    '已完成': 'green',
  }
  return (map[task.value.status] || 'blue') as any
})

const timelineItems = computed(() => {
  if (!task.value) return []
  return task.value.milestones.map((m) => ({
    title: m.title,
    description: m.description,
    date: m.date,
    status: m.state === 'done' ? 'done' : m.state === 'doing' ? 'active' : 'pending',
  })) as { title: string; description: string; date: string; status: 'done' | 'active' | 'pending' }[]
})

function handleActionClick() {
  if (!canEdit.value) {
    showToast({ title: '请先加入队伍或联系队长获取编辑权限', variant: 'error' })
    return
  }
  showToast({
    title: `已记录操作：${task.value?.action}`,
    variant: 'success',
  })
}

function handleJoinTeam() {
  hasJoinedTeam.value = true
  showToast({ title: '已加入队伍，现在可以编辑和提交进度', variant: 'success' })
}

function openEditModal() {
  if (!canEdit.value) {
    showToast({ title: '请先加入队伍或联系队长获取编辑权限', variant: 'error' })
    return
  }
  if (!task.value) return
  editForm.value = {
    productManager: task.value.taskInfo.productManager,
    taskType: task.value.taskInfo.taskType,
    priority: task.value.taskInfo.priority,
    scope: task.value.taskInfo.scope,
    acceptance: task.value.taskInfo.acceptance,
    resources: [...task.value.resources],
    files: [...task.value.files],
    actions: [...task.value.actions],
  }
  showEditModal.value = true
}

async function handleEditSave() {
  if (!task.value || saving.value) return
  saving.value = true
  try {
    const priority = PRIORITY_TO_API[editForm.value.priority] || editForm.value.priority
    await tasksApi.update(taskId.value, {
      task_type: editForm.value.taskType,
      priority,
      scope: editForm.value.scope,
      acceptance_criteria: editForm.value.acceptance,
      leader_id: editForm.value.productManager,
      resource_links: editForm.value.resources,
      file_ids: editForm.value.files,
    })
    try {
      localStorage.setItem(`openrd_task_actions_${taskId.value}`, JSON.stringify(editForm.value.actions))
    } catch {}

    task.value.taskInfo.productManager = editForm.value.productManager
    task.value.taskInfo.taskType = editForm.value.taskType
    task.value.taskInfo.priority = editForm.value.priority
    task.value.taskInfo.scope = editForm.value.scope
    task.value.taskInfo.acceptance = editForm.value.acceptance
    task.value.resources = [...editForm.value.resources]
    task.value.files = [...editForm.value.files]
    task.value.actions = [...editForm.value.actions]
    showEditModal.value = false
    showToast({ title: '任务信息已更新', variant: 'success' })
  } catch {
    showToast({ title: '保存失败', description: '请稍后重试。', variant: 'error' })
  } finally {
    saving.value = false
  }
}

function addResource() {
  editForm.value.resources.push({ label: '', url: '' })
}

function removeResource(idx: number) {
  editForm.value.resources.splice(idx, 1)
}

function addFile() {
  editForm.value.files.push('')
}

function removeFile(idx: number) {
  editForm.value.files.splice(idx, 1)
}

function addAction() {
  editForm.value.actions.push('')
}

function removeAction(idx: number) {
  editForm.value.actions.splice(idx, 1)
}

async function loadTaskDetail() {
  try {
    loading.value = true
    const res = await tasksApi.getDetail(taskId.value)
    const d = res.data
    const teamRes = await tasksApi.getTeam(taskId.value)
    const rawMembers = Array.isArray(teamRes.data) ? teamRes.data : (teamRes.data as any).members || []
    const members = rawMembers.map((m: TaskMember) => ({
      name: m.duty || m.role,
      role: m.role,
      isMe: m.user_id === auth.user?.id,
      memberType: m.member_type,
    }))

    task.value = {
      id: d.id,
      title: d.title,
      desc: d.description,
      brief: d.scope || d.description,
      createdAt: d.created_at?.slice(0, 10) || '',
      status: statusLabelMap[d.status] || d.status,
      teamStatus: teamStatusLabelMap[d.team_status] || d.team_status || '招募中',
      progress: d.progress || 0,
      myRole: members.find((m: any) => m.isMe)?.role || '只读',
      action: '提交更新',
      demandId: d.demand_id || '',
      taskInfo: {
        sourceDemand: d.demand_id ? `${d.demand_id} · 关联需求` : '无关联需求',
        productManager: d.leader_id || '待分配',
        taskType: d.task_type || '',
        priority: d.priority === 'high' ? '高' : d.priority === 'medium' ? '中' : d.priority === 'low' ? '低' : d.priority || '中',
        scope: d.scope || '',
        acceptance: d.acceptance_criteria || '',
      },
      members,
      isCurrentUserLeader: members.some((m: any) => m.isMe && (m.memberType === 'leader' || m.role === '产品经理')),
      isCurrentUserMember: members.some((m: any) => m.isMe),
      milestones: [],
      files: (d.file_ids || []).map((f: string) => f),
      resources: d.resource_links || [],
      actions: (() => {
        try { return JSON.parse(localStorage.getItem(`openrd_task_actions_${d.id}`) || '[]') } catch { return [] }
      })(),
    }

    if (auth.userRole === 'super_admin') {
      viewMode.value = 'leader'
    } else if (task.value.isCurrentUserLeader) {
      viewMode.value = 'leader'
    } else if (auth.userRole === 'builder' || task.value.isCurrentUserMember) {
      viewMode.value = 'builder'
    } else {
      viewMode.value = 'readonly'
    }
  } catch {
    task.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTaskDetail()
})
</script>

<template>
  <div class="task-detail-page">
    <TopNavbar />

    <div v-if="loading" class="task-detail-view">
      <OrdCard class="loading-card">
        <p>加载中...</p>
      </OrdCard>
    </div>

    <div v-else-if="!task" class="task-detail-view">
      <OrdCard class="empty-card">
        <p class="eyebrow">Task Not Found</p>
        <h1>没有找到该任务</h1>
        <p class="empty-desc">当前任务 ID 不存在或已被移除，请返回我的任务列表重新选择。</p>
        <OrdButton variant="primary" @click="router.push('/workbench')">返回工作台</OrdButton>
      </OrdCard>
    </div>

    <div v-else class="task-detail-view">
      <OrdCard class="overview-card">
        <div class="hero-card">
          <div class="hero-left">
            <div class="breadcrumb">
              <router-link to="/workbench">工作台</router-link>
              <span>/</span>
              <span>{{ task.id }}</span>
            </div>
            <p class="eyebrow">Task Detail</p>
            <h1 class="hero-title">{{ task.title }}</h1>
            <p class="hero-copy">{{ task.desc }}</p>
          </div>
          <aside class="side-status">
            <span class="side-status__badge">{{ task.status }}</span>
            <strong class="side-status__progress">{{ task.progress }}%</strong>
            <OrdProgress :value="task.progress" variant="blue" />
            <p class="side-status__action">{{ currentActionLabel }}</p>
            <OrdButton
              v-if="viewMode === 'builder' && !hasJoinedTeam"
              variant="primary"
              @click="handleJoinTeam"
            >加入队伍</OrdButton>
          </aside>
        </div>

        <div class="info-grid">
          <article class="info-card">
            <p class="info-label">任务编号</p>
            <p class="info-value">{{ task.id }}</p>
            <p class="info-desc">其他入口可通过该编号进入详情页</p>
          </article>
          <article class="info-card info-card--orange">
            <p class="info-label">我的角色</p>
            <p class="info-value">{{ currentRoleLabel }}</p>
            <p class="info-desc">当前账号在该任务中的职责</p>
          </article>
          <article class="info-card info-card--green">
            <p class="info-label">团队状态</p>
            <p class="info-value">{{ task.teamStatus }}</p>
            <p class="info-desc">成员招募与协作推进情况</p>
          </article>
          <article class="info-card info-card--purple">
            <p class="info-label">创建时间</p>
            <p class="info-value">{{ task.createdAt }}</p>
            <p class="info-desc">任务进入协作大厅的时间</p>
          </article>
        </div>
      </OrdCard>

      <div class="content-grid">
        <!-- 任务信息与项目资源 (wide card) -->
        <OrdCard class="panel-card wide-card">
          <div class="panel-head">
            <h2 class="panel-title">任务信息与项目资源</h2>
            <div class="panel-actions">
              <OrdButton variant="ghost" @click="router.push(`/demands/${task.demandId}`)">需求详情</OrdButton>
              <OrdButton v-if="canEdit" variant="primary" @click="openEditModal">编辑</OrdButton>
            </div>
          </div>
          <div class="panel-body">
            <div class="resource-layout">
              <section class="resource-section">
                <h3 class="resource-section-title">任务信息</h3>
                <div class="task-info-list">
                  <div class="task-info-item">
                    <span class="task-info-label">来源需求</span>
                    <span class="task-info-value">{{ task.taskInfo.sourceDemand }}</span>
                  </div>
                  <div class="task-info-item">
                    <span class="task-info-label">转化产品经理</span>
                    <span class="task-info-value">{{ task.taskInfo.productManager }}</span>
                  </div>
                  <div class="task-info-item">
                    <span class="task-info-label">任务类型</span>
                    <span class="task-info-value">{{ task.taskInfo.taskType }}</span>
                  </div>
                  <div class="task-info-item">
                    <span class="task-info-label">优先级</span>
                    <span class="task-info-value">{{ task.taskInfo.priority }}</span>
                  </div>
                  <div class="task-info-item task-info-item--wide">
                    <span class="task-info-label">工单范围</span>
                    <span class="task-info-value">{{ task.taskInfo.scope }}</span>
                  </div>
                  <div class="task-info-item task-info-item--wide">
                    <span class="task-info-label">验收标准</span>
                    <span class="task-info-value task-info-value--pre">{{ task.taskInfo.acceptance }}</span>
                  </div>
                </div>
              </section>
              <section class="resource-section">
                <h3 class="resource-section-title">项目资源</h3>
                <div class="resource-list">
                  <a
                    v-for="(res, idx) in task.resources"
                    :key="idx"
                    class="resource-item"
                    :href="res.url"
                    target="_blank"
                    rel="noreferrer"
                  >
                    <div>
                      <span class="resource-name">{{ res.label }}</span>
                      <span class="resource-meta">{{ res.url }}</span>
                    </div>
                    <OrdBadge variant="gray">资源</OrdBadge>
                  </a>
                </div>
              </section>
              <section class="resource-section">
                <h3 class="resource-section-title">项目附件</h3>
                <div class="file-list">
                  <div v-for="(file, idx) in task.files" :key="idx" class="file-item">
                    <div>
                      <span class="file-name">{{ file }}</span>
                      <span class="file-meta">任务相关附件</span>
                    </div>
                    <OrdBadge variant="blue">附件</OrdBadge>
                  </div>
                  <div v-if="!task.files.length" class="list-empty">
                    <span class="list-empty__text">暂无附件</span>
                    <button v-if="canEdit" class="list-empty__action" type="button" @click="openEditModal">去添加</button>
                  </div>
                </div>
              </section>
              <section class="resource-section">
                <h3 class="resource-section-title">协作动作</h3>
                <div class="action-list">
                  <div v-for="(action, idx) in task.actions" :key="idx" class="action-item">
                    <div>
                      <span class="action-name">{{ action }}</span>
                      <span class="action-meta">{{ idx === 0 ? '当前优先事项' : '后续协作事项' }}</span>
                    </div>
                    <OrdBadge variant="gray">{{ idx + 1 }}</OrdBadge>
                  </div>
                  <div v-if="!task.actions.length" class="list-empty">
                    <span class="list-empty__text">暂无协作动作</span>
                    <button v-if="canEdit" class="list-empty__action" type="button" @click="openEditModal">去添加</button>
                  </div>
                </div>
              </section>
            </div>
          </div>
        </OrdCard>

        <!-- 项目进度 -->
        <OrdCard class="panel-card progress-card">
          <div class="panel-head">
            <h2 class="panel-title">项目进度</h2>
            <div class="panel-actions">
              <OrdBadge :variant="statusBadgeVariant">{{ task.status }}</OrdBadge>
              <OrdButton v-if="canEdit" variant="primary" @click="handleActionClick">提交更新</OrdButton>
            </div>
          </div>
          <div class="panel-body">
            <p class="section-copy">{{ task.brief }}</p>
            <div class="timeline-scroll">
              <OrdTimeline :items="timelineItems" />
            </div>
          </div>
        </OrdCard>

        <!-- 团队成员 -->
        <OrdCard class="panel-card team-card">
          <div class="panel-head">
            <h2 class="panel-title">团队成员</h2>
            <div class="panel-actions">
              <OrdBadge variant="purple">{{ task.teamStatus }}</OrdBadge>
              <OrdButton variant="ghost" @click="router.push(`/teams?task=${task.id}`)">队伍详情</OrdButton>
            </div>
          </div>
          <div class="panel-body">
            <div class="member-list">
              <div v-for="(member, idx) in task.members" :key="idx" class="member-item">
                <div>
                  <span class="member-name">{{ member.name }}</span>
                  <span class="member-meta">{{ member.role }}</span>
                </div>
                <OrdBadge v-if="member.isMe" variant="gray">我</OrdBadge>
              </div>
            </div>
          </div>
        </OrdCard>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <OrdDialog v-model="showEditModal">
      <div class="modal-header">
        <div>
          <p class="eyebrow">Edit Task Info</p>
          <h2 class="modal-title">编辑任务信息与项目资源</h2>
        </div>
      </div>
      <div class="modal-body">
        <div class="field">
          <label class="field-label">来源需求（只读）</label>
          <OrdInput :model-value="task?.taskInfo.sourceDemand || ''" disabled />
        </div>
        <div class="field">
          <label class="field-label">转化产品经理</label>
          <OrdInput v-model="editForm.productManager" placeholder="产品经理 / 负责人" />
        </div>
        <div class="field">
          <label class="field-label">任务类型</label>
          <OrdInput v-model="editForm.taskType" placeholder="如：工具开发 / 后端接口" />
        </div>
        <div class="field">
          <label class="field-label">优先级</label>
          <OrdInput v-model="editForm.priority" placeholder="高 / 中 / 低" />
        </div>
        <div class="field field--full">
          <label class="field-label">工单范围</label>
          <OrdTextarea v-model="editForm.scope" placeholder="本次任务工单覆盖的功能范围" :rows="3" />
        </div>
        <div class="field field--full">
          <label class="field-label">验收标准</label>
          <OrdTextarea v-model="editForm.acceptance" placeholder="可逐条填写验收标准" :rows="3" />
        </div>
        <div class="field field--full">
          <label class="field-label">项目资源</label>
          <div class="edit-list">
            <div v-for="(res, idx) in editForm.resources" :key="idx" class="edit-row">
              <OrdInput v-model="res.label" placeholder="资源名称" />
              <OrdInput v-model="res.url" placeholder="资源地址" type="url" />
              <button class="edit-row__remove" type="button" @click="removeResource(idx)" aria-label="删除资源">&times;</button>
            </div>
            <button class="edit-list__add" type="button" @click="addResource">+ 添加资源</button>
          </div>
        </div>
        <div class="field field--full">
          <label class="field-label">项目附件</label>
          <div class="edit-list">
            <div v-for="(file, idx) in editForm.files" :key="idx" class="edit-row edit-row--single">
              <OrdInput :model-value="file" placeholder="附件名称" @update:model-value="editForm.files[idx] = $event" />
              <button class="edit-row__remove" type="button" @click="removeFile(idx)" aria-label="删除附件">&times;</button>
            </div>
            <button class="edit-list__add" type="button" @click="addFile">+ 添加附件</button>
          </div>
        </div>
        <div class="field field--full">
          <label class="field-label">协作动作</label>
          <div class="edit-list">
            <div v-for="(action, idx) in editForm.actions" :key="idx" class="edit-row edit-row--single">
              <OrdInput :model-value="action" placeholder="协作动作" @update:model-value="editForm.actions[idx] = $event" />
              <button class="edit-row__remove" type="button" @click="removeAction(idx)" aria-label="删除动作">&times;</button>
            </div>
            <button class="edit-list__add" type="button" @click="addAction">+ 添加动作</button>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <OrdButton variant="ghost" @click="showEditModal = false">取消</OrdButton>
        <OrdButton variant="primary" :loading="saving" @click="handleEditSave">保存修改</OrdButton>
      </div>
    </OrdDialog>
  </div>
</template>

<style scoped>
.task-detail-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at 12% 12%, rgba(20, 110, 245, 0.08), transparent 28%),
    radial-gradient(circle at 86% 18%, rgba(122, 61, 255, 0.06), transparent 24%),
    radial-gradient(circle at 80% 86%, rgba(255, 174, 19, 0.052), transparent 28%),
    linear-gradient(135deg, #ffffff 0%, #f7f9ff 100%);
}

.task-detail-view {
  width: min(var(--ord-content-max-width), 100%);
  margin: 0 auto;
  padding: 96px 32px 32px;
  display: grid;
  gap: 26px;
}

.loading-card,
.empty-card {
  min-height: 420px;
  display: grid;
  place-items: center;
  text-align: center;
  padding: 42px 24px;
}

.empty-card h1 {
  margin: 0;
  font-size: clamp(32px, 4vw, 48px);
  font-weight: 600;
  color: var(--ord-color-black);
}

.empty-desc {
  max-width: 540px;
  margin: 14px auto 22px;
  color: var(--ord-color-gray-500);
  font-size: 15px;
  line-height: 1.7;
}

.eyebrow {
  margin: 0 0 10px;
  color: var(--ord-color-blue);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.4px;
  text-transform: uppercase;
}

.overview-card {
  position: relative;
  overflow: hidden;
}

.overview-card::after {
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

.hero-card {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  padding: 28px 28px 22px;
  border-bottom: 1px solid #ececec;
}

.breadcrumb {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
  color: var(--ord-color-gray-500);
  font-size: 13px;
}

.breadcrumb a {
  color: var(--ord-color-gray-500);
  text-decoration: none;
  transition: color var(--ord-transition-base);
}

.breadcrumb a:hover {
  color: var(--ord-color-blue);
}

.hero-title {
  margin: 0;
  font-size: clamp(34px, 4vw, 54px);
  font-weight: 600;
  line-height: 1.04;
  letter-spacing: -0.6px;
  color: var(--ord-color-black);
}

.hero-copy {
  max-width: 760px;
  margin: 16px 0 0;
  color: var(--ord-color-gray-700);
  font-size: 16px;
  line-height: 1.65;
}

.side-status {
  position: relative;
  z-index: 1;
  display: grid;
  align-content: center;
  gap: 14px;
  padding: 18px;
  color: var(--ord-color-white);
  background: var(--ord-color-black);
  border-radius: var(--ord-radius-md);
}

.side-status__badge {
  width: max-content;
  padding: 5px 8px;
  background: rgba(20, 110, 245, 0.9);
  border-radius: var(--ord-radius-sm);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.side-status__progress {
  font-size: 34px;
  font-weight: 600;
  line-height: 1;
}

.side-status__action {
  margin: 0;
  color: rgba(255, 255, 255, 0.72);
  font-size: 13px;
  line-height: 1.55;
}

.side-status :deep(.ord-progress) {
  height: 9px;
  background: rgba(255, 255, 255, 0.16);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  padding: 20px 28px 28px;
}

.info-card {
  min-height: 104px;
  padding: 16px;
  background: #fff;
  border: 1px solid rgba(216, 216, 216, 0.82);
  border-left: 4px solid var(--ord-color-blue);
  border-radius: 6px;
}

.info-card--orange { border-left-color: var(--ord-color-orange); }
.info-card--green { border-left-color: var(--ord-color-green); }
.info-card--purple { border-left-color: var(--ord-color-purple); }

.info-label {
  margin: 0;
  color: var(--ord-color-gray-500);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.1px;
  text-transform: uppercase;
}

.info-value {
  margin: 12px 0 0;
  color: var(--ord-color-black);
  font-size: 21px;
  font-weight: 600;
  line-height: 1.25;
}

.info-desc {
  margin: 9px 0 0;
  color: var(--ord-color-gray-500);
  font-size: 13px;
  line-height: 1.45;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(360px, 0.75fr);
  align-items: stretch;
  gap: 18px;
}

.panel-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.progress-card,
.team-card {
  min-height: 540px;
}

.wide-card {
  grid-column: 1 / -1;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 18px;
  border-bottom: 1px solid #ececec;
}

.panel-actions {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.panel-title {
  margin: 0;
  color: var(--ord-color-black);
  font-size: 22px;
  font-weight: 600;
  line-height: 1.2;
}

.panel-body {
  display: grid;
  gap: 14px;
  flex: 1;
  padding: 18px;
}

.section-copy {
  margin: 0;
  color: var(--ord-color-gray-700);
  font-size: 15px;
  line-height: 1.7;
}

.timeline-scroll {
  position: relative;
  overflow: hidden;
  padding: 10px;
  background: linear-gradient(180deg, #ffffff, #f8fbff);
  border: 1px solid rgba(20, 110, 245, 0.14);
  border-radius: var(--ord-radius-md);
  max-height: 380px;
  overflow-y: auto;
}

.timeline-scroll::-webkit-scrollbar {
  width: 6px;
}

.timeline-scroll::-webkit-scrollbar-thumb {
  background: rgba(20, 110, 245, 0.22);
  border-radius: var(--ord-radius-full);
}

.resource-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr);
  gap: 16px;
}

.resource-section {
  display: grid;
  gap: 10px;
  padding: 14px;
  background: #fff;
  border: 1px solid #ececec;
  border-radius: 6px;
}

.resource-section-title {
  margin: 0;
  color: var(--ord-color-black);
  font-size: 15px;
  font-weight: 700;
}

.task-info-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.task-info-item {
  min-height: 74px;
  padding: 12px;
  background: #f8fbff;
  border: 1px solid rgba(20, 110, 245, 0.12);
  border-radius: 6px;
}

.task-info-item--wide {
  grid-column: 1 / -1;
}

.task-info-label {
  display: block;
  color: var(--ord-color-gray-500);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.8px;
  text-transform: uppercase;
}

.task-info-value {
  display: block;
  margin-top: 6px;
  color: var(--ord-color-black);
  font-size: 14px;
  font-weight: 700;
  line-height: 1.5;
}

.task-info-value--pre {
  white-space: pre-line;
}

.resource-list,
.file-list,
.action-list,
.member-list {
  display: grid;
  gap: 10px;
}

.team-card .member-list {
  max-height: 430px;
  overflow-y: auto;
  padding-right: 4px;
}

.member-list::-webkit-scrollbar {
  width: 6px;
}

.member-list::-webkit-scrollbar-thumb {
  background: rgba(20, 110, 245, 0.22);
  border-radius: var(--ord-radius-full);
}

.resource-item,
.file-item,
.action-item,
.member-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 54px;
  padding: 12px;
  border: 1px solid #ececec;
  border-radius: 6px;
  background: #fff;
}

.resource-item {
  color: inherit;
  text-decoration: none;
  transition: transform var(--ord-transition-base), border-color var(--ord-transition-base), box-shadow var(--ord-transition-base);
}

.resource-item:hover {
  border-color: var(--ord-color-blue);
  box-shadow: 0 12px 24px rgba(20, 110, 245, 0.1);
  transform: translateX(6px);
}

.resource-name,
.file-name,
.action-name,
.member-name {
  display: block;
  color: var(--ord-color-black);
  font-size: 14px;
  font-weight: 700;
}

.resource-meta,
.file-meta,
.action-meta,
.member-meta {
  display: block;
  margin-top: 4px;
  color: var(--ord-color-gray-500);
  font-size: 12px;
  line-height: 1.45;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 20px;
  border-bottom: 1px solid #ececec;
}

.modal-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--ord-color-black);
}

.modal-body {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
  max-height: 60vh;
  overflow-y: auto;
  padding: 20px;
}

.modal-body::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: rgba(20, 110, 245, 0.22);
  border-radius: var(--ord-radius-full);
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 14px;
  padding: 20px;
  border-top: 1px solid #ececec;
}

.field {
  display: grid;
  gap: 7px;
}

.field--full {
  grid-column: 1 / -1;
}

.field-label {
  color: var(--ord-color-gray-700);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.8px;
  text-transform: uppercase;
}

.edit-list {
  display: grid;
  gap: 10px;
}

.edit-row {
  display: grid;
  grid-template-columns: minmax(150px, 0.38fr) minmax(0, 0.62fr) 32px;
  gap: 10px;
  align-items: center;
  padding: 10px;
  background: #f8fbff;
  border: 1px solid rgba(20, 110, 245, 0.12);
  border-radius: 6px;
}

.edit-row--single {
  grid-template-columns: 1fr 32px;
}

.edit-row__remove {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  padding: 0;
  color: var(--ord-color-gray-500);
  background: transparent;
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-sm);
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  transition: color var(--ord-transition-base), border-color var(--ord-transition-base), background var(--ord-transition-base);
}

.edit-row__remove:hover {
  color: var(--ord-color-red);
  border-color: var(--ord-color-red);
  background: rgba(238, 29, 54, 0.06);
}

.edit-list__add {
  width: 100%;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--ord-color-blue);
  background: transparent;
  border: 1px dashed rgba(20, 110, 245, 0.4);
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
  transition: background var(--ord-transition-base), border-color var(--ord-transition-base);
}

.edit-list__add:hover {
  background: rgba(20, 110, 245, 0.04);
  border-color: var(--ord-color-blue);
}

.list-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 72px;
  padding: 16px;
  background: #f8fbff;
  border: 1px dashed rgba(20, 110, 245, 0.2);
  border-radius: 6px;
}

.list-empty__text {
  color: var(--ord-color-gray-300);
  font-size: 13px;
  font-weight: 600;
}

.list-empty__action {
  padding: 4px 10px;
  color: var(--ord-color-blue);
  background: transparent;
  border: 1px solid rgba(20, 110, 245, 0.3);
  border-radius: var(--ord-radius-sm);
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
  transition: background var(--ord-transition-base), border-color var(--ord-transition-base);
}

.list-empty__action:hover {
  background: rgba(20, 110, 245, 0.06);
  border-color: var(--ord-color-blue);
}

:deep(.ord-dialog__content) {
  padding: 0;
}

:deep(.ord-dialog__title),
:deep(.ord-dialog__description) {
  display: none;
}

:deep(.ord-dialog__footer) {
  display: none;
}

:deep(.ord-dialog__close) {
  top: 20px;
  right: 20px;
}

@media (max-width: 992px) {
  .hero-card,
  .content-grid,
  .resource-layout {
    grid-template-columns: 1fr;
  }

  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .wide-card {
    grid-column: auto;
  }
}

@media (max-width: 768px) {
  .task-detail-view {
    padding: 92px 16px 24px;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .task-info-list {
    grid-template-columns: 1fr;
  }

  .modal-body {
    grid-template-columns: 1fr;
  }

  .modal-footer {
    align-items: stretch;
    flex-direction: column-reverse;
  }
}
</style>
