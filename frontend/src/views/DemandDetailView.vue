<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { demandsApi } from '@/api/demands'
import { useAuthStore } from '@/stores/auth'
import { demandStatusDict, convertStatusDict, dict as t } from '@/utils/dict'
import OrdButton from '@/components/ui/button/OrdButton.vue'
import OrdBadge from '@/components/ui/badge/OrdBadge.vue'
import OrdAvatar from '@/components/ui/avatar/OrdAvatar.vue'
import OrdTimeline from '@/components/ui/timeline/OrdTimeline.vue'
import OrdCard from '@/components/ui/card/OrdCard.vue'
import OrdCardHeader from '@/components/ui/card/OrdCardHeader.vue'
import OrdCardContent from '@/components/ui/card/OrdCardContent.vue'
import OrdTextarea from '@/components/ui/input/OrdTextarea.vue'
import OrdInput from '@/components/ui/input/OrdInput.vue'
import OrdSelect from '@/components/ui/select/OrdSelect.vue'
import OrdDialog from '@/components/ui/dialog/OrdDialog.vue'
import { useToast } from '@/components/ui/toast/useToast'
import TopNavbar from '@/components/TopNavbar.vue'

interface Thread {
  id: string
  pmName: string
  pmTitle: string
  status: string
  taskId: string
  summary: string
  scope: string
  messages: Message[]
}

interface Message {
  from: 'pm' | 'requester' | 'system'
  name: string
  time: string
  text: string
  attachment?: string
  revoked?: boolean
}

interface Demand {
  id: string
  title: string
  desc: string
  detail: string
  submittedAt: string
  status: string
  statusKey: string
  convertStatus: string
  taskId: string
  convertedBy: string
  progress: number
  contact: string
  privateContact: string
  attachments: string[]
  feedback: string
  timeline: [string, string, string, string][]
  demandMarkStatus: 'pending' | 'needs_supplement' | 'info_sufficient'
  lastMarkedBy: string
  threads: Thread[]
}

interface SimilarCandidate {
  id: string
  title: string
  taskId: string
  projectType: string
  owner: string
  keywords: string[]
  summary: string
  linkedDemandIds: string[]
}

const route = useRoute()
const router = useRouter()
const { show: showToast } = useToast()
const auth = useAuthStore()

const demandId = ref(route.params.id as string)
const activeThreadId = ref('')
const messageInput = ref('')
const showConversionModal = ref(false)
const showSimilarModal = ref(false)
const contactVisible = ref(false)
const loading = ref(true)
const demand = ref<Demand | null>(null)
const similarCandidates = ref<SimilarCandidate[]>([])
const similarSearchKeyword = ref('')
const pendingAttachments = ref<{ name: string; sizeMb: number }[]>([])
const conversionForm = ref({
  demandId: '',
  owner: '',
  title: '',
  type: '工具开发项目',
  priority: '中',
  scope: '',
  acceptance: '1. 明确需求边界和首版交付范围。\n2. 输出可被共建者认领的任务说明。\n3. 保留来源需求和需求者补充材料。',
})

const contextMenu = ref({ visible: false, x: 0, y: 0, messageIndex: -1 })

const isPM = computed(() => auth.userRole === 'operator' || auth.userRole === 'super_admin')
const isRequester = computed(() => auth.userRole === 'requester')

const myThreadId = computed(() => {
  if (!isPM.value || !demand.value) return ''
  return demand.value.threads[0]?.id || ''
})

const visibleThreads = computed(() => {
  if (!demand.value) return []
  return demand.value.threads
})

const activeThread = computed(() => {
  return visibleThreads.value.find(t => t.id === activeThreadId.value) || visibleThreads.value[0] || null
})

const isFrozen = computed(() => demand.value?.statusKey === 'converted')
const canSendMessage = computed(() => !isFrozen.value && (isPM.value || isRequester.value))
const canViewContact = computed(() => isPM.value)

const canMarkStatus = computed(() => isPM.value && myThreadId.value !== '')

const canConvert = computed(() => {
  if (!demand.value || !isPM.value) return false
  if (demand.value.statusKey === 'converted') return false
  return true
})

const canLinkSimilar = computed(() => {
  if (!demand.value || !isPM.value) return false
  return demand.value.statusKey !== 'converted'
})

const demandStatusBadge = computed(() => {
  if (!demand.value) return { text: '待沟通', variant: 'blue' }
  switch (demand.value.demandMarkStatus) {
    case 'info_sufficient': return { text: '信息充分', variant: 'green' }
    case 'needs_supplement': return { text: '需要补充', variant: 'orange' }
    default: return { text: '待沟通', variant: 'blue' }
  }
})

const timelineItems = computed(() => {
  if (!demand.value) return []
  return demand.value.timeline.map(([title, description, date, status]) => ({
    title, description, date,
    status: (status === 'done' ? 'done' : status === 'active' ? 'active' : 'pending') as 'done' | 'active' | 'pending',
  }))
})

const statusBadgeVariant = computed(() => {
  if (!demand.value) return 'blue'
  const map: Record<string, string> = { pending: 'orange', talking: 'blue', converted: 'green', closed: 'gray' }
  return map[demand.value.statusKey] || 'blue'
})

const filteredCandidates = computed(() => {
  const kw = similarSearchKeyword.value.trim().toLowerCase()
  return similarCandidates.value.filter((c) => {
    if (c.id === demand.value?.id) return false
    if (!kw) {
      const haystack = `${demand.value?.title} ${demand.value?.desc} ${demand.value?.detail}`.toLowerCase()
      return c.keywords.some((k) => haystack.includes(k.toLowerCase()))
    }
    const haystack = `${c.id} ${c.title} ${c.taskId} ${c.projectType} ${c.owner} ${c.summary} ${c.keywords.join(' ')}`.toLowerCase()
    return haystack.includes(kw)
  })
})

const projectTypeOptions = [
  { value: '工具开发项目', label: '工具开发项目' },
  { value: '数据分析项目', label: '数据分析项目' },
  { value: '内容/文档项目', label: '内容/文档项目' },
  { value: '流程优化项目', label: '流程优化项目' },
  { value: '科研辅助项目', label: '科研辅助项目' },
  { value: '平台能力建设项目', label: '平台能力建设项目' },
]
const priorityOptions = [
  { value: '高', label: '高' },
  { value: '中', label: '中' },
  { value: '低', label: '低' },
]

const handleThreadSwitch = (threadId: string) => {
  activeThreadId.value = threadId
  messageInput.value = ''
  pendingAttachments.value = []
}

const handleMarkStatus = (newStatus: 'needs_supplement' | 'info_sufficient') => {
  if (!demand.value || !canMarkStatus.value) return
  demand.value.demandMarkStatus = newStatus
  demand.value.lastMarkedBy = myThreadId.value

  const thread = demand.value.threads.find(t => t.id === myThreadId.value)
  if (thread) {
    const label = newStatus === 'info_sufficient' ? '信息充分' : '需要补充'
    thread.messages.push({
      from: 'system', name: '系统', time: '刚刚',
      text: `${thread.pmName} 将需求状态标记为「${label}」。`,
    })
  }

  demandsApi.update(demandId.value, {
    demand_mark_status: newStatus,
    last_marked_by: myThreadId.value,
  }).catch(() => {})

  showToast({
    title: newStatus === 'info_sufficient' ? '已标记为信息充分' : '已标记为需要补充',
    variant: 'success',
  })
}

const sending = ref(false)

const handleSendMessage = async () => {
  if (!canSendMessage.value) {
    showToast({ title: '只读模式不能发送消息', variant: 'error' })
    return
  }
  const text = messageInput.value.trim()
  if (!text && !pendingAttachments.value.length) {
    showToast({ title: isPM.value ? '请输入询问内容' : '请输入回复或补充材料', variant: 'error' })
    return
  }

  if (!demand.value || sending.value) return
  sending.value = true

  const threadId = activeThread.value?.id || 'thread-default'
  const content = text || '补充了新的需求附件。'

  try {
    await demandsApi.sendReply(demandId.value, {
      thread_id: threadId,
      content,
    })

    const newMessage: Message = {
      from: isPM.value ? 'pm' : 'requester',
      name: isPM.value ? (activeThread.value?.pmName || '') : (auth.user?.nickname || '需求者'),
      time: '刚刚',
      text: content,
      attachment: pendingAttachments.value.length
        ? pendingAttachments.value.map((f) => `${f.name}（${f.sizeMb}MB）`).join('、')
        : undefined,
    }

    if (isRequester.value) {
      demand.value.threads.forEach(thread => {
        thread.messages.push({ ...newMessage })
      })
    } else {
      const thread = activeThread.value
      if (thread) thread.messages.push(newMessage)
    }

    messageInput.value = ''
    pendingAttachments.value = []
    showToast({ title: isPM.value ? '询问已发送' : '回复已发送', variant: 'success' })
    nextTick(() => {
      const list = document.querySelector('.message-list')
      if (list) list.scrollTop = list.scrollHeight
    })
  } catch (error: any) {
    showToast({ title: error.message || '发送失败，请重试', variant: 'error' })
  } finally {
    sending.value = false
  }
}

const handleAddAttachment = () => {
  if (pendingAttachments.value.length >= 5) {
    showToast({ title: '最多上传 5 个附件', variant: 'error' })
    return
  }
  const sizeMb = Math.min(20, 6 + pendingAttachments.value.length * 3)
  pendingAttachments.value.push({ name: `补充材料-${pendingAttachments.value.length + 1}.pdf`, sizeMb })
  showToast({ title: '已模拟选择补充附件', variant: 'success' })
}

const handleConvertAction = () => {
  if (!demand.value) return
  if (demand.value.statusKey === 'converted') {
    router.push(`/tasks/${demand.value.taskId}`)
    return
  }
  if (!canConvert.value) {
    showToast({ title: '当前不满足转化条件', variant: 'error' })
    return
  }
  const thread = activeThread.value
  if (!thread) return
  conversionForm.value = {
    demandId: demand.value.id,
    owner: auth.user?.nickname || '转化者',
    title: demand.value.title,
    type: '工具开发项目',
    priority: demand.value.statusKey === 'pending' ? '低' : '中',
    scope: thread.scope,
    acceptance: '1. 明确需求边界和首版交付范围。\n2. 输出可被共建者认领的任务说明。\n3. 保留来源需求和需求者补充材料。',
  }
  showConversionModal.value = true
}

const converting = ref(false)

const handleSaveConversion = async () => {
  if (!demand.value || converting.value) return
  converting.value = true

  const priorityMap: Record<string, string> = { '高': 'high', '中': 'medium', '低': 'low' }

  try {
    const res = await demandsApi.convert(demandId.value, {
      title: conversionForm.value.title,
      task_type: conversionForm.value.type,
      priority: priorityMap[conversionForm.value.priority] || 'medium',
      scope: conversionForm.value.scope || undefined,
      acceptance_criteria: conversionForm.value.acceptance || undefined,
    })

    const result = res.data as any
    const taskId = result?.task_id || ''

    demand.value.status = 'converted'
    demand.value.statusKey = 'converted'
    demand.value.convertStatus = 'converted'
    demand.value.taskId = taskId

    const thread = activeThread.value
    if (thread) {
      thread.status = 'converted'
      thread.messages.push({ from: 'system', name: '系统', time: '刚刚', text: `已将需求转化为任务 ${taskId}。` })
    }
    demand.value.timeline.push(['转为任务', `需求已转化为任务 ${taskId}。`, '刚刚', 'done'])
    showConversionModal.value = false
    showToast({ title: '已生成任务工单', variant: 'success' })
  } catch (error: any) {
    showToast({ title: error.message || '转化失败，请重试', variant: 'error' })
  } finally {
    converting.value = false
  }
}

const handleOpenSimilarModal = () => {
  if (!canLinkSimilar.value) {
    showToast({ title: '当前身份无权关联已有需求', variant: 'error' })
    return
  }
  if (demand.value?.statusKey === 'converted') {
    showToast({ title: '当前需求已经关联或转化为任务', variant: 'error' })
    return
  }
  similarSearchKeyword.value = ''
  showSimilarModal.value = true
}

const handleLinkCandidate = (candidate: SimilarCandidate) => {
  if (!demand.value) return
  const thread = activeThread.value
  if (!thread) return
  const nextProgress = Math.max(demand.value.progress, 42)
  const nextFeedback = `当前需求与 ${candidate.id}「${candidate.title}」相似，已关联至既有任务 ${candidate.taskId}。`

  demand.value.status = '已关联'
  demand.value.statusKey = 'converted'
  demand.value.convertStatus = '已关联既有任务'
  demand.value.taskId = candidate.taskId
  demand.value.convertedBy = thread.id
  demand.value.progress = nextProgress
  demand.value.feedback = nextFeedback
  thread.status = '已关联既有任务'
  thread.messages.push({ from: 'system', name: '系统', time: '刚刚', text: `${thread.pmName} 已将当前需求关联至 ${candidate.id} 对应的 ${candidate.taskId}。` })
  demand.value.timeline.push(['关联需求', `关联至已转任务需求 ${candidate.id}，共用任务 ${candidate.taskId}。`, '刚刚', 'done'])
  showSimilarModal.value = false

  demandsApi.update(demandId.value, {
    review_status: '已关联',
    convert_status: '已关联既有任务',
    task_id: candidate.taskId,
    progress: nextProgress,
    feedback: nextFeedback,
  }).catch(() => {})

  showToast({ title: `已关联至 ${candidate.taskId}`, variant: 'success' })
}

const handleViewContact = () => {
  if (!canViewContact.value) {
    showToast({ title: '仅产品经理和超级管理员可查看患者留存信息', variant: 'error' })
    return
  }
  contactVisible.value = true
  showToast({ title: '已显示患者留存联系方式', variant: 'success' })
}

const handleMessageContext = (event: MouseEvent, index: number) => {
  event.preventDefault()
  contextMenu.value = {
    visible: true,
    x: Math.min(event.clientX, window.innerWidth - 140),
    y: Math.min(event.clientY, window.innerHeight - 80),
    messageIndex: index,
  }
}

const canRevokeMessage = (msg: Message) => {
  if (!msg || msg.revoked) return false
  if (isPM.value) return msg.from === 'pm'
  if (isRequester.value) return msg.from === 'requester'
  return false
}

const handleCopyMessage = () => {
  const thread = activeThread.value
  if (!thread) return
  const msg = thread.messages[contextMenu.value.messageIndex]
  if (!msg) return
  const text = msg.revoked ? '该发言已撤回' : msg.attachment ? `${msg.text}\n附件：${msg.attachment}` : msg.text
  navigator.clipboard.writeText(text).catch(() => {})
  contextMenu.value.visible = false
  showToast({ title: '消息已复制', variant: 'success' })
}

const handleRevokeMessage = () => {
  const thread = activeThread.value
  if (!thread) return
  const msg = thread.messages[contextMenu.value.messageIndex]
  if (!msg || !canRevokeMessage(msg)) {
    showToast({ title: '只能撤回当前身份发送的发言', variant: 'error' })
    contextMenu.value.visible = false
    return
  }
  msg.revoked = true
  msg.text = '该发言已撤回'
  delete msg.attachment
  contextMenu.value.visible = false
  showToast({ title: '发言已撤回', variant: 'success' })
}

const closeContextMenu = () => { contextMenu.value.visible = false }

const loadDemandDetail = async () => {
  try {
    loading.value = true
    const response = await demandsApi.getDetail(demandId.value)
    const raw = response.data as any

    const statusKeyMap: Record<string, string> = {
      pending: 'pending',
      pending_review: 'pending',
      reviewing: 'talking',
      approved: 'talking',
      converted: 'converted',
      linked: 'converted',
      rejected: 'closed',
      archived: 'closed',
    }

    const repliesRes = await demandsApi.getReplies(demandId.value).catch(() => null)
    const replies = (repliesRes?.data as any)?.items || []

    const messages: Message[] = replies.map((r: any) => ({
      from: r.sender_role === 'requester' ? 'requester' : 'pm',
      name: r.sender_role === 'requester' ? '需求者' : '运营',
      time: r.created_at ? new Date(r.created_at).toLocaleString('zh-CN') : '',
      text: r.content,
      attachment: r.attachment_ids?.length ? `${r.attachment_ids.length} 个附件` : undefined,
      revoked: r.is_revoked === 1,
    }))

    const thread: Thread = {
      id: 'thread-default',
      pmName: auth.user?.nickname || '运营',
      pmTitle: '需求运营',
      status: raw.status,
      taskId: raw.linked_task_id || '',
      summary: raw.description?.slice(0, 80) || '',
      scope: raw.description || '',
      messages,
    }

    const timeline: [string, string, string, string][] = [
      ['提交需求', '需求者提交了该需求。', raw.created_at ? new Date(raw.created_at).toLocaleDateString('zh-CN') : '', 'done'],
    ]
    if (raw.status !== 'pending') {
      timeline.push(['开始审核', '运营已开始审核需求。', raw.updated_at ? new Date(raw.updated_at).toLocaleDateString('zh-CN') : '', 'done'])
    }
    if (raw.linked_task_id) {
      timeline.push(['已转任务', `已转化为任务 ${raw.linked_task_id}。`, '', 'done'])
    }
    if (raw.status === 'pending') {
      timeline.push(['等待审核', '需求等待运营审核中。', '', 'active'])
    }

    demand.value = {
      id: raw.id,
      title: raw.title,
      desc: raw.description,
      detail: raw.description,
      submittedAt: raw.created_at ? new Date(raw.created_at).toLocaleString('zh-CN') : '',
      status: raw.status,
      statusKey: statusKeyMap[raw.status] || 'pending',
      convertStatus: raw.convert_status || '',
      taskId: raw.linked_task_id || '',
      convertedBy: '',
      progress: raw.progress || 0,
      contact: raw.contact_phone || '',
      privateContact: raw.contact_phone || '',
      attachments: raw.attachment_ids || [],
      feedback: raw.feedback || '',
      timeline,
      demandMarkStatus: 'pending',
      lastMarkedBy: '',
      threads: [thread],
    }
    activeThreadId.value = thread.id
  } catch (error) {
    showToast({ title: '加载需求详情失败', variant: 'error' })
  } finally {
    loading.value = false
  }
}

const loadSimilarCandidates = async () => {
  try {
    const response = await demandsApi.getSimilarCandidates(demandId.value)
    similarCandidates.value = (response.data as any) || []
  } catch {
    similarCandidates.value = []
  }
}

onMounted(() => {
  loadDemandDetail()
  loadSimilarCandidates()
  document.addEventListener('click', closeContextMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeContextMenu)
})
</script>

<template>
  <div class="demand-detail-page">
    <TopNavbar />
    <div v-if="loading" class="demand-detail-view">
      <OrdCard class="loading-card"><p>加载中...</p></OrdCard>
    </div>

    <div v-else-if="!demand" class="demand-detail-view">
      <OrdCard class="empty-card">
        <div>
          <p class="eyebrow">Demand Not Found</p>
          <h1>没有找到该需求</h1>
          <p>当前需求 ID 不存在或已被移除，请返回我的需求列表重新选择。</p>
          <OrdButton variant="primary" @click="router.push('/my-demands')">返回我的需求</OrdButton>
        </div>
      </OrdCard>
    </div>

    <div v-else class="demand-detail-view">
      <OrdCard class="overview-card">
        <div class="hero-section">
          <div class="hero-content">
            <p class="eyebrow">Demand Detail</p>
            <h1 class="hero-title">{{ demand.title }}</h1>
            <p class="hero-desc">{{ demand.desc }}</p>
          </div>
          <div class="hero-actions">
            <div class="hero-action-row">
              <OrdButton v-if="canLinkSimilar" variant="outline" @click="handleOpenSimilarModal">关联已有类似需求</OrdButton>
              <OrdButton v-if="canConvert" variant="primary" @click="handleConvertAction">转化任务</OrdButton>
              <OrdButton v-if="isPM && demand.statusKey === 'converted'" variant="primary" @click="handleConvertAction">查看任务工单</OrdButton>
            </div>
          </div>
        </div>

        <div class="status-grid">
          <div class="info-card"><p class="info-label">需求编号</p><p class="info-value">{{ demand.id }}</p><p class="info-desc">需求跟踪唯一编号</p></div>
          <div class="info-card"><p class="info-label">审核状态</p><p class="info-value">{{ t(demandStatusDict, demand.status) }}</p><p class="info-desc">产品经理审核进度</p></div>
          <div class="info-card"><p class="info-label">转化状态</p><p class="info-value">{{ t(convertStatusDict, demand.convertStatus) }}</p><p class="info-desc">是否已转为协作任务</p></div>
          <div class="info-card"><p class="info-label">当前进度</p><p class="info-value">{{ demand.progress }}%</p><p class="info-desc">需求处理与任务推进状态</p></div>
        </div>
      </OrdCard>

      <div class="content-grid">
        <div class="panel-grid">
          <OrdCard>
            <OrdCardHeader>
              <h2 class="panel-title">需求信息</h2>
              <OrdBadge :variant="statusBadgeVariant">{{ t(demandStatusDict, demand.status) }}</OrdBadge>
            </OrdCardHeader>
            <OrdCardContent class="field-grid">
              <div class="field-card"><p class="field-label">提交时间</p><p class="field-value">{{ demand.submittedAt }}</p></div>
              <div class="field-card">
                <p class="field-label">联系方式</p>
                <div class="contact-row">
                  <p class="field-value">{{ contactVisible ? demand.privateContact : demand.contact }}</p>
                  <button v-if="canViewContact" class="mini-action-button" @click="handleViewContact">{{ contactVisible ? '已查看' : '查看' }}</button>
                </div>
              </div>
              <div class="field-card"><p class="field-label">关联任务</p><p class="field-value">{{ demand.taskId }}</p></div>
              <div class="field-card"><p class="field-label">附件</p><p class="field-value">{{ demand.attachments.length ? demand.attachments.join('、') : '暂无附件' }}</p></div>
              <div class="field-card is-full"><p class="field-label">需求详情</p><p class="field-value">{{ demand.detail }}</p></div>
              <div class="field-card is-full"><p class="field-label">平台反馈</p><p class="field-value">{{ demand.feedback }}</p></div>
            </OrdCardContent>
          </OrdCard>

          <OrdCard class="timeline-card">
            <OrdCardHeader>
              <h2 class="panel-title">处理流程</h2>
              <OrdBadge variant="blue">Timeline</OrdBadge>
            </OrdCardHeader>
            <OrdCardContent>
              <div class="timeline-scroll">
                <OrdTimeline :items="timelineItems" />
              </div>
            </OrdCardContent>
          </OrdCard>
        </div>

        <OrdCard class="conversation-card">
          <div class="conversation-head">
            <div><p class="eyebrow">Conversation</p><h2>沟通区</h2></div>
            <OrdBadge :variant="demandStatusBadge.variant">{{ demandStatusBadge.text }}</OrdBadge>
          </div>
          <div class="conversation-body">
            <div class="thread-tabs">
              <button v-for="thread in visibleThreads" :key="thread.id" :class="['thread-tab', { 'is-active': thread.id === activeThreadId }]" @click="handleThreadSwitch(thread.id)">
                <OrdAvatar :name="thread.pmName" size="md" />
                <div class="thread-info">
                  <div class="thread-name">{{ isPM ? '我的会话' : thread.pmName }} · {{ thread.pmTitle }}</div>
                  <div class="thread-meta">{{ thread.messages.length }} 条消息 · {{ thread.summary }}</div>
                </div>
                <OrdBadge :variant="demandStatusBadge.variant">{{ t(demandStatusDict, thread.status) }}</OrdBadge>
              </button>
            </div>

            <div class="chat-pane">
              <div class="conversation-summary">
                <p v-if="isPM">当前仅可查看自己的沟通记录。{{ activeThread?.pmName }} 的判断：{{ activeThread?.summary }}</p>
                <p v-else-if="isRequester">你可以查看所有产品经理的询问，你的回复会同步发送到所有会话。</p>
                <p v-else>只读模式，你可以查看所有沟通记录。</p>
              </div>
              <div v-if="canMarkStatus" class="status-marking">
                <span class="marking-label">需求状态标记：</span>
                <OrdButton :variant="demand.demandMarkStatus === 'needs_supplement' ? 'primary' : 'outline'" size="sm" @click="handleMarkStatus('needs_supplement')">需要补充</OrdButton>
                <OrdButton :variant="demand.demandMarkStatus === 'info_sufficient' ? 'primary' : 'outline'" size="sm" @click="handleMarkStatus('info_sufficient')">信息充分</OrdButton>
                <span v-if="demand.lastMarkedBy && demand.lastMarkedBy !== myThreadId" class="marking-hint">（其他产品经理已标记，你可以覆盖）</span>
              </div>
              <div class="message-list">
                <div v-for="(msg, idx) in activeThread?.messages" :key="idx" :class="['message-item', { 'from-requester': msg.from === 'requester', 'is-revoked': msg.revoked }]">
                  <div class="message-meta">{{ msg.name }} · {{ msg.time }}</div>
                  <div class="message-bubble" @contextmenu="handleMessageContext($event, idx)">
                    <template v-if="msg.revoked">该发言已撤回</template>
                    <template v-else>
                      {{ msg.text }}
                      <span v-if="msg.attachment" class="message-attachment">附件：{{ msg.attachment }}</span>
                    </template>
                  </div>
                </div>
              </div>
              <div class="conversation-input">
                <OrdTextarea v-model="messageInput" :placeholder="isFrozen ? '需求已转为任务，沟通区已冻结' : isPM ? `以${activeThread?.pmName}身份继续询问需求者` : isRequester ? '回复将同步发送到所有产品经理会话' : '只读模式不能发送消息'" :disabled="!canSendMessage" rows="3" />
                <div class="conversation-actions">
                  <span class="attachment-status">
                    <span class="attachment-name">{{ pendingAttachments.length ? `已选择 ${pendingAttachments.length}/5 个` : '未选择附件' }}</span>
                    <span class="attachment-limit">最多 5 个附件，单个不超过 20MB，格式不限</span>
                  </span>
                  <div class="action-buttons">
                    <OrdButton v-if="canSendMessage" variant="outline" size="sm" @click="handleAddAttachment">补充附件</OrdButton>
                    <OrdButton v-if="canSendMessage" variant="primary" size="sm" :disabled="sending" @click="handleSendMessage">
                      {{ isPM ? '发送询问' : '发送回复' }}
                    </OrdButton>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </OrdCard>
      </div>
    </div>

    <div v-if="contextMenu.visible" class="message-context-menu" :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }" @click.stop>
      <button @click="handleCopyMessage">复制</button>
      <button v-if="canRevokeMessage(activeThread?.messages[contextMenu.messageIndex]!)" @click="handleRevokeMessage">撤回</button>
    </div>

    <OrdDialog v-model:open="showConversionModal" title="转化任务工单">
      <template #trigger><span></span></template>
      <template #description>将需求转化为可被共建者认领的任务工单。</template>
      <div class="conversion-form">
        <div class="form-row">
          <div class="form-field"><label>来源需求</label><OrdInput v-model="conversionForm.demandId" disabled /></div>
          <div class="form-field"><label>转化产品经理</label><OrdInput v-model="conversionForm.owner" disabled /></div>
        </div>
        <div class="form-field full"><label>任务标题</label><OrdInput v-model="conversionForm.title" /></div>
        <div class="form-row">
          <div class="form-field"><label>项目分类</label><OrdSelect v-model="conversionForm.type" :options="projectTypeOptions" /></div>
          <div class="form-field"><label>优先级</label><OrdSelect v-model="conversionForm.priority" :options="priorityOptions" /></div>
        </div>
        <div class="form-field full"><label>工单范围</label><OrdTextarea v-model="conversionForm.scope" rows="3" /></div>
        <div class="form-field full"><label>验收标准</label><OrdTextarea v-model="conversionForm.acceptance" rows="3" /></div>
      </div>
      <template #footer>
        <OrdButton variant="ghost" @click="showConversionModal = false">取消</OrdButton>
        <OrdButton variant="primary" :disabled="converting" @click="handleSaveConversion">生成任务工单</OrdButton>
      </template>
    </OrdDialog>

    <OrdDialog v-model:open="showSimilarModal" title="关联已有类似需求">
      <template #trigger><span></span></template>
      <template #description>搜索已转任务且未被关联的需求进行关联。</template>
      <div class="similar-form">
        <div class="form-field full"><label>关键词匹配</label><OrdInput v-model="similarSearchKeyword" placeholder="搜索已转任务且未被关联的需求" /></div>
        <div class="candidate-list">
          <button v-for="candidate in filteredCandidates" :key="candidate.id" class="candidate-card" @click="handleLinkCandidate(candidate)">
            <div class="candidate-head">
              <div>
                <p class="candidate-title">{{ candidate.title }}</p>
                <p class="candidate-summary">{{ candidate.summary }}</p>
              </div>
              <OrdBadge variant="green">{{ candidate.taskId }}</OrdBadge>
            </div>
            <div class="candidate-meta">
              <span>{{ candidate.id }}</span>
              <span>{{ candidate.projectType }}</span>
              <span>负责人：{{ candidate.owner }}</span>
              <span>已承接相似需求：{{ candidate.linkedDemandIds.length }}</span>
            </div>
          </button>
          <p v-if="!filteredCandidates.length" class="empty-candidate">没有匹配到可关联的已转任务需求。</p>
        </div>
      </div>
      <template #footer>
        <OrdButton variant="ghost" @click="showSimilarModal = false">取消</OrdButton>
      </template>
    </OrdDialog>
  </div>
</template>

<style scoped>
.demand-detail-page {
  padding: 96px 32px 32px;
}

.demand-detail-view {
  position: relative;
  max-width: 1460px;
  margin: 0 auto;
  padding: 0;
  display: grid;
  gap: 18px;
}

.demand-detail-view::before,
.demand-detail-view::after {
  content: "";
  position: absolute;
  z-index: -1;
  border: 1px solid rgba(216, 216, 216, 0.7);
  background: rgba(255, 255, 255, 0.45);
}

.demand-detail-view::before {
  width: 180px;
  height: 86px;
  top: 96px;
  right: 42px;
  transform: rotate(-2deg);
}

.demand-detail-view::after {
  width: 108px;
  height: 108px;
  right: 214px;
  bottom: 56px;
  transform: rotate(4deg);
}

.overview-card {
  position: relative;
  overflow: hidden;
  padding: 28px;
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

.overview-card :deep(.ord-card__content) {
  padding: 0;
}

.hero-section {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 24px;
  align-items: center;
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
  margin: 0;
  color: var(--ord-color-black);
  font-size: clamp(34px, 4vw, 56px);
  font-weight: 600;
  line-height: 1.04;
  letter-spacing: -0.6px;
}

.hero-desc {
  max-width: 760px;
  margin: 16px 0 0;
  color: var(--ord-color-gray-700);
  font-size: 16px;
  line-height: 1.65;
}

.hero-actions {
  display: grid;
  justify-items: end;
  gap: 12px;
}

.hero-action-row {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.status-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-top: 20px;
}

.info-card {
  min-height: 96px;
  padding: 16px;
  background: var(--ord-color-white);
  border: 1px solid rgba(216, 216, 216, 0.82);
  border-left: 4px solid var(--ord-color-blue);
  border-radius: 6px;
}

.info-card:nth-child(2) {
  border-left-color: var(--ord-color-orange);
}

.info-card:nth-child(3) {
  border-left-color: var(--ord-color-green);
}

.info-card:nth-child(4) {
  border-left-color: var(--ord-color-purple);
}

.info-label {
  margin: 0;
  color: var(--ord-color-gray-500);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.1px;
  text-transform: uppercase;
}

.info-value {
  margin: 8px 0 0;
  color: var(--ord-color-black);
  font-size: 20px;
  font-weight: 600;
  line-height: 1.2;
}

.info-desc {
  margin: 6px 0 0;
  color: var(--ord-color-gray-500);
  font-size: 12px;
  line-height: 1.4;
}

.content-grid {
  display: grid;
  gap: 16px;
}

.panel-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(420px, 0.92fr);
  gap: 16px;
  align-items: stretch;
}

.panel-title {
  margin: 0;
  color: var(--ord-color-black);
  font-size: 19px;
  font-weight: 600;
  line-height: 1.2;
}

.panel-grid :deep(.ord-card) {
  overflow: hidden;
}

.panel-grid :deep(.ord-card-header) {
  padding: 15px 16px;
  border-bottom: 1px solid #ececec;
}

.panel-grid :deep(.ord-card-content) {
  padding: 14px;
}

.timeline-card {
  align-self: start;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.timeline-card :deep(.ord-card-content) {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  padding: 14px;
}

.timeline-scroll {
  position: relative;
  overflow: hidden;
  padding: 10px;
  background: linear-gradient(180deg, #ffffff, #f8fbff);
  border: 1px solid rgba(20, 110, 245, 0.14);
  border-radius: 8px;
  max-height: 322px;
}

.timeline-scroll::after {
  content: "";
  position: absolute;
  left: 10px;
  right: 10px;
  bottom: 10px;
  height: 42px;
  pointer-events: none;
  background: linear-gradient(180deg, rgba(248, 251, 255, 0), rgba(248, 251, 255, 0.98));
}

.timeline-scroll :deep(.ord-timeline) {
  max-height: 280px;
  overflow-y: auto;
  padding: 0 8px 56px 0;
  scroll-padding-bottom: 56px;
}

.timeline-scroll :deep(.ord-timeline)::-webkit-scrollbar {
  width: 6px;
}

.timeline-scroll :deep(.ord-timeline)::-webkit-scrollbar-thumb {
  background: rgba(20, 110, 245, 0.22);
  border-radius: 999px;
}

.conversation-card :deep(.ord-card-content) {
  padding: 0;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.field-card {
  padding: 12px;
  border: 1px solid #ececec;
  border-radius: var(--ord-radius-sm);
  background: var(--ord-color-white);
}

.field-card.is-full {
  grid-column: 1 / -1;
}

.field-label {
  margin: 0 0 7px;
  color: var(--ord-color-gray-500);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.field-value {
  margin: 0;
  color: var(--ord-color-black);
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.contact-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.mini-action-button {
  min-height: 28px;
  padding: 0 10px;
  color: var(--ord-color-blue);
  background: rgba(20, 110, 245, 0.08);
  border: 1px solid rgba(20, 110, 245, 0.18);
  border-radius: var(--ord-radius-sm);
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
  transition: all var(--ord-transition-base);
}

.mini-action-button:hover {
  background: rgba(20, 110, 245, 0.12);
  border-color: rgba(20, 110, 245, 0.36);
  transform: translateX(4px);
}

.conversation-card {
  overflow: hidden;
  min-height: 640px;
  box-shadow: var(--ord-shadow-cascade);
}

.conversation-head {
  min-height: 62px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 15px 18px;
  border-bottom: 1px solid #ececec;
  background: var(--ord-color-white);
}

.conversation-head h2 {
  margin: 0;
  color: var(--ord-color-black);
  font-size: 22px;
  font-weight: 600;
}

.conversation-body {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  min-height: 576px;
}

.thread-tabs {
  display: grid;
  align-content: start;
  gap: 2px;
  padding: 10px;
  background: #f6f8fc;
  border-right: 1px solid #ececec;
}

.thread-tab {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 10px;
  align-items: center;
  width: 100%;
  min-height: 68px;
  padding: 10px;
  color: var(--ord-color-black);
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--ord-radius-sm);
  cursor: pointer;
  text-align: left;
  transition: all var(--ord-transition-base);
}

.thread-tab:hover {
  background: var(--ord-color-white);
  border-color: rgba(20, 110, 245, 0.18);
  transform: translateX(3px);
}

.thread-tab.is-active {
  background: var(--ord-color-white);
  border-color: rgba(20, 110, 245, 0.3);
  box-shadow: inset 4px 0 0 var(--ord-color-blue);
}

.thread-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.thread-name {
  color: var(--ord-color-black);
  font-size: 14px;
  font-weight: 700;
  line-height: 1.3;
}

.thread-meta {
  color: var(--ord-color-gray-500);
  font-size: 12px;
  line-height: 1.4;
}

.chat-pane {
  display: grid;
  grid-template-rows: auto 1fr auto;
  min-height: 576px;
  background: #f5f7fb;
}

.conversation-summary {
  padding: 12px 16px;
  background: var(--ord-color-white);
  border-bottom: 1px solid #ececec;
}

.conversation-summary p {
  margin: 0;
  color: var(--ord-color-gray-700);
  font-size: 13px;
  line-height: 1.55;
}

.status-marking {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 44px;
  padding: 0 16px;
  background: #f9fafb;
  border-bottom: 1px solid #ececec;
}

.marking-label {
  color: var(--ord-color-gray-700);
  font-size: 13px;
  font-weight: 500;
}

.marking-hint {
  color: var(--ord-color-gray-500);
  font-size: 12px;
}

.message-list {
  min-height: 0;
  max-height: 360px;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  display: grid;
  align-content: start;
  gap: 12px;
  padding: 18px;
  background: #f5f7fb;
}

.message-list::-webkit-scrollbar {
  width: 0;
  height: 0;
  display: none;
}

.message-item {
  display: grid;
  gap: 6px;
  max-width: 74%;
}

.message-item.from-requester {
  justify-self: end;
}

.message-meta {
  color: var(--ord-color-gray-500);
  font-size: 12px;
}

.message-bubble {
  padding: 11px 12px;
  color: var(--ord-color-gray-700);
  background: var(--ord-color-white);
  border: 1px solid #ececec;
  border-radius: 6px;
  cursor: context-menu;
  font-size: 14px;
  line-height: 1.6;
  box-shadow: 0 6px 16px rgba(8, 8, 8, 0.04);
}

.message-item.from-requester .message-bubble {
  color: var(--ord-color-white);
  background: var(--ord-color-blue);
  border-color: var(--ord-color-blue);
}

.message-attachment {
  display: inline-flex;
  margin-top: 8px;
  padding: 4px 8px;
  color: var(--ord-color-blue);
  background: rgba(20, 110, 245, 0.08);
  border-radius: var(--ord-radius-sm);
  font-size: 12px;
  font-weight: 700;
}

.message-item.from-requester .message-attachment {
  color: var(--ord-color-white);
  background: rgba(255, 255, 255, 0.18);
}

.conversation-input {
  display: grid;
  gap: 10px;
  padding: 14px 16px;
  background: var(--ord-color-white);
  border-top: 1px solid #ececec;
}

.conversation-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.attachment-status {
  display: grid;
  gap: 3px;
}

.attachment-limit {
  color: var(--ord-color-gray-500);
  font-size: 12px;
  line-height: 1.35;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

@media (max-width: 992px) {
  .hero-section {
    grid-template-columns: 1fr;
  }

  .status-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .panel-grid {
    grid-template-columns: 1fr;
  }

  .conversation-body {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .thread-tabs {
    grid-auto-flow: column;
    grid-auto-columns: minmax(230px, 1fr);
    overflow-x: auto;
    border-right: 0;
    border-bottom: 1px solid #ececec;
  }
}

@media (max-width: 768px) {
  .status-grid,
  .field-grid {
    grid-template-columns: 1fr;
  }

  .field-card.is-full {
    grid-column: auto;
  }
}

.loading-card,
.empty-card {
  min-height: 400px;
  display: grid;
  place-items: center;
  text-align: center;
  padding: 48px 24px;
}

.loading-card p {
  color: var(--ord-color-gray-500);
  font-size: 16px;
}

.empty-card h1 {
  margin: 16px 0;
  font-size: 32px;
}

.empty-card p {
  max-width: 540px;
  margin: 14px auto 22px;
  color: var(--ord-color-gray-500);
  font-size: 15px;
  line-height: 1.7;
}

.message-item.is-revoked .message-bubble {
  color: var(--ord-color-gray-500);
  background: var(--ord-color-white);
  border-style: dashed;
  box-shadow: none;
}

.message-item.from-requester.is-revoked .message-bubble {
  color: var(--ord-color-gray-500);
  background: var(--ord-color-white);
  border-color: #ececec;
}

.message-item.is-revoked .message-attachment {
  display: none;
}

.message-context-menu {
  position: fixed;
  z-index: 120;
  min-width: 132px;
  padding: 6px;
  background: var(--ord-color-white);
  border: 1px solid rgba(216, 216, 216, 0.92);
  border-radius: var(--ord-radius-sm);
  box-shadow: var(--ord-shadow-cascade);
  display: grid;
  gap: 2px;
}

.message-context-menu button {
  height: 34px;
  padding: 0 10px;
  color: var(--ord-color-black);
  background: transparent;
  border: 0;
  border-radius: var(--ord-radius-sm);
  cursor: pointer;
  font-size: 13px;
  font-weight: 650;
  text-align: left;
}

.message-context-menu button:hover {
  color: var(--ord-color-blue);
  background: rgba(20, 110, 245, 0.08);
}

.attachment-name {
  color: var(--ord-color-gray-500);
  font-size: 13px;
}

.conversion-form,
.similar-form {
  display: grid;
  gap: 12px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.form-field {
  display: grid;
  gap: 7px;
}

.form-field.full {
  grid-column: 1 / -1;
}

.form-field label {
  color: var(--ord-color-gray-500);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.candidate-list {
  display: grid;
  gap: 10px;
}

.candidate-card {
  width: 100%;
  display: grid;
  gap: 8px;
  padding: 12px;
  color: var(--ord-color-black);
  background: var(--ord-color-white);
  border: 1px solid var(--ord-color-border-light);
  border-radius: var(--ord-radius-sm);
  cursor: pointer;
  text-align: left;
  transition: border-color var(--ord-transition-base), box-shadow var(--ord-transition-base), transform var(--ord-transition-base);
}

.candidate-card:hover {
  border-color: rgba(20, 110, 245, 0.38);
  box-shadow: 0 10px 22px rgba(8, 8, 8, 0.08);
  transform: translateX(4px);
}

.candidate-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.candidate-title {
  margin: 0;
  color: var(--ord-color-black);
  font-size: 15px;
  font-weight: 700;
  line-height: 1.35;
}

.candidate-summary {
  margin: 4px 0 0;
  color: var(--ord-color-gray-700);
  font-size: 13px;
  line-height: 1.55;
}

.candidate-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.candidate-meta span {
  display: inline-flex;
  min-height: 24px;
  align-items: center;
  padding: 0 8px;
  color: var(--ord-color-gray-700);
  background: #f6f8fc;
  border: 1px solid var(--ord-color-border-light);
  border-radius: var(--ord-radius-sm);
  font-size: 12px;
  font-weight: 700;
}

.empty-candidate {
  margin: 0;
  padding: 16px;
  color: var(--ord-color-gray-500);
  background: var(--ord-color-white);
  border: 1px dashed var(--ord-color-border);
  border-radius: var(--ord-radius-sm);
  font-size: 14px;
  line-height: 1.6;
}
</style>

