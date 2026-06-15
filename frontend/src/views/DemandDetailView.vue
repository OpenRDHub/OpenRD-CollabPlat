<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { demandsApi } from '@/api/demands'
import { useAuthStore } from '@/stores/auth'
import OrdButton from '@/components/ui/button/OrdButton.vue'
import OrdBadge from '@/components/ui/badge/OrdBadge.vue'
import OrdAvatar from '@/components/ui/avatar/OrdAvatar.vue'
import OrdTimeline from '@/components/ui/timeline/OrdTimeline.vue'
import OrdCard from '@/components/ui/card/OrdCard.vue'
import OrdCardHeader from '@/components/ui/card/OrdCardHeader.vue'
import OrdCardContent from '@/components/ui/card/OrdCardContent.vue'
import OrdTextarea from '@/components/ui/input/OrdTextarea.vue'
import { useToast } from '@/components/ui/toast/useToast'
import TopNavbar from '@/components/TopNavbar.vue'

interface Thread {
  id: string
  pmName: string
  pmTitle: string
  status: string
  statusKey: string
  canConvert: boolean
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
  threads: Thread[]
}

const route = useRoute()
const router = useRouter()
const { show: showToast } = useToast()
const auth = useAuthStore()

const demandId = ref(route.params.id as string)
const activeView = ref<'product' | 'requester' | 'readonly'>('readonly')
const activeThreadId = ref('')
const messageInput = ref('')
const showConversionModal = ref(false)
const showSimilarModal = ref(false)
const contactVisible = ref(false)
const loading = ref(true)
const demand = ref<Demand | null>(null)

// 权限控制 - 根据用户角色动态判断
const canUseProductMode = () => auth.userRole === 'operator' || auth.userRole === 'admin'
const canUsePublisherMode = () => {
  if (!demand.value) return false
  return demand.value.threads.some((t) => t.messages.some((m) => m.from === 'requester'))
    && (auth.userRole === 'requester' || auth.userRole === 'admin')
}
const canViewContact = () => auth.userRole === 'operator' || auth.userRole === 'admin'

const canSendConversation = () =>
  (activeView.value === 'product' && canUseProductMode()) ||
  (activeView.value === 'requester' && canUsePublisherMode())
const canConvertDemand = () => activeView.value === 'product' && canUseProductMode()

const getOperatorThread = () => {
  if (!demand.value) return null
  return demand.value.threads.find((t) => t.id === demand.value!.convertedBy) ||
    demand.value.threads.find((t) => t.canConvert) ||
    demand.value.threads[0]
}

const getVisibleThreads = () => {
  if (!demand.value) return []
  const operatorThread = getOperatorThread()
  return activeView.value === 'product' && operatorThread ? [operatorThread] : demand.value.threads
}

const syncActiveThread = () => {
  const visibleThreads = getVisibleThreads()
  if (!visibleThreads.some((t) => t.id === activeThreadId.value)) {
    activeThreadId.value = visibleThreads[0]?.id || ''
  }
}

const getActiveThread = () => {
  syncActiveThread()
  return getVisibleThreads().find((t) => t.id === activeThreadId.value) || getVisibleThreads()[0]
}

const timelineItems = computed(() => {
  if (!demand.value) return []
  return demand.value.timeline.map(([title, description, date, status]) => ({
    title,
    description,
    date,
    status: status as 'done' | 'active' | 'pending',
  }))
})

const statusBadgeVariant = computed(() => {
  if (!demand.value) return 'blue'
  const map: Record<string, any> = {
    pending: 'orange',
    talking: 'blue',
    converted: 'green',
    closed: 'gray',
  }
  return map[demand.value.statusKey] || 'blue'
})

const handleViewSwitch = (view: 'product' | 'requester' | 'readonly') => {
  if (view === 'product' && !canUseProductMode()) {
    showToast({ title: '当前账号无产品视角操作权限', variant: 'error' })
    return
  }
  if (view === 'requester' && !canUsePublisherMode()) {
    showToast({ title: '当前账号不是需求发布者', variant: 'error' })
    return
  }
  activeView.value = view
  if (view === 'product') {
    activeThreadId.value = getOperatorThread()?.id || ''
  }
}

const handleThreadSwitch = (threadId: string) => {
  activeThreadId.value = threadId
  messageInput.value = ''
}

const handleSendMessage = () => {
  if (!canSendConversation()) {
    showToast({ title: '只读模式不能发送消息', variant: 'error' })
    return
  }
  const text = messageInput.value.trim()
  if (!text) {
    showToast({ title: '请输入消息内容', variant: 'error' })
    return
  }

  const thread = getActiveThread()
  if (!thread) return

  thread.messages.push({
    from: activeView.value === 'product' ? 'pm' : 'requester',
    name: activeView.value === 'product' ? thread.pmName : '陈北',
    time: '刚刚',
    text,
  })

  messageInput.value = ''
  showToast({ title: '消息已发送', variant: 'success' })
}

const handleConvert = () => {
  const thread = getActiveThread()
  if (!thread || !thread.canConvert) {
    showToast({ title: '当前会话信息仍需补充', variant: 'error' })
    return
  }
  showConversionModal.value = true
}

const handleViewContact = () => {
  if (!canViewContact()) {
    showToast({ title: '仅产品经理和超级管理员可查看患者留存信息', variant: 'error' })
    return
  }
  contactVisible.value = true
  showToast({ title: '已显示患者留存联系方式', variant: 'success' })
}

const loadDemandDetail = async () => {
  try {
    loading.value = true
    const response = await demandsApi.getDetail(demandId.value)
    demand.value = response.data as any
    activeThreadId.value = demand.value?.threads[0]?.id || ''
  } catch (error) {
    showToast({ title: '加载需求详情失败', variant: 'error' })
    console.error('Failed to load demand detail:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDemandDetail()
})
</script>

<template>
  <div class="demand-detail-page">
    <TopNavbar />
    <div v-if="loading" class="demand-detail-view">
    <OrdCard class="loading-card">
      <p>加载中...</p>
    </OrdCard>
  </div>

  <div v-else-if="!demand" class="demand-detail-view">
    <OrdCard class="empty-card">
      <p class="eyebrow">Demand Not Found</p>
      <h1>没有找到该需求</h1>
      <p>当前需求 ID 不存在或已被移除，请返回我的需求列表重新选择。</p>
      <OrdButton variant="primary" @click="router.push('/my-demands')">返回我的需求</OrdButton>
    </OrdCard>
  </div>

  <div v-else class="demand-detail-view">
    <!-- 概览卡片 -->
    <OrdCard class="overview-card">
      <div class="hero-section">
        <div class="hero-content">
          <p class="eyebrow">Demand Detail</p>
          <h1 class="hero-title">{{ demand.title }}</h1>
          <p class="hero-desc">{{ demand.desc }}</p>
        </div>
        <div class="hero-actions">
          <div class="view-switch">
            <button
              :class="['view-button', { 'is-active': activeView === 'product' }]"
              :disabled="!canUseProductMode()"
              @click="handleViewSwitch('product')"
            >
              产品视角
            </button>
            <button
              :class="['view-button', { 'is-active': activeView === 'requester' }]"
              :disabled="!canUsePublisherMode()"
              @click="handleViewSwitch('requester')"
            >
              发布者视角
            </button>
            <button
              :class="['view-button', { 'is-active': activeView === 'readonly' }]"
              @click="handleViewSwitch('readonly')"
            >
              只读
            </button>
          </div>
          <div class="hero-action-row">
            <OrdButton v-if="canConvertDemand()" variant="outline" @click="showSimilarModal = true">
              关联已有类似需求
            </OrdButton>
            <OrdButton v-if="canConvertDemand()" variant="primary" @click="handleConvert">
              转化任务
            </OrdButton>
          </div>
        </div>
      </div>

      <!-- 状态概览 -->
      <div class="status-grid">
        <div class="info-card">
          <p class="info-label">需求编号</p>
          <p class="info-value">{{ demand.id }}</p>
          <p class="info-desc">需求跟踪唯一编号</p>
        </div>
        <div class="info-card">
          <p class="info-label">审核状态</p>
          <p class="info-value">{{ demand.status }}</p>
          <p class="info-desc">运营管理员审核进度</p>
        </div>
        <div class="info-card">
          <p class="info-label">转化状态</p>
          <p class="info-value">{{ demand.convertStatus }}</p>
          <p class="info-desc">是否已转为协作任务</p>
        </div>
        <div class="info-card">
          <p class="info-label">当前进度</p>
          <p class="info-value">{{ demand.progress }}%</p>
          <p class="info-desc">需求处理与任务推进状态</p>
        </div>
      </div>
    </OrdCard>

    <!-- 内容区域 -->
    <div class="content-grid">
      <div class="panel-grid">
        <!-- 需求信息 -->
        <OrdCard>
          <OrdCardHeader>
            <h2 class="panel-title">需求信息</h2>
            <OrdBadge :variant="statusBadgeVariant">{{ demand.status }}</OrdBadge>
          </OrdCardHeader>
          <OrdCardContent class="field-grid">
            <div class="field-card">
              <p class="field-label">提交时间</p>
              <p class="field-value">{{ demand.submittedAt }}</p>
            </div>
            <div class="field-card">
              <p class="field-label">联系方式</p>
              <div class="contact-row">
                <p class="field-value">{{ contactVisible ? demand.privateContact : demand.contact }}</p>
                <button v-if="canViewContact()" class="mini-action-button" @click="handleViewContact">
                  {{ contactVisible ? '已查看' : '查看' }}
                </button>
              </div>
            </div>
            <div class="field-card">
              <p class="field-label">关联任务</p>
              <p class="field-value">{{ demand.taskId }}</p>
            </div>
            <div class="field-card">
              <p class="field-label">附件</p>
              <p class="field-value">{{ demand.attachments.length ? demand.attachments.join('、') : '暂无附件' }}</p>
            </div>
            <div class="field-card is-full">
              <p class="field-label">需求详情</p>
              <p class="field-value">{{ demand.detail }}</p>
            </div>
            <div class="field-card is-full">
              <p class="field-label">平台反馈</p>
              <p class="field-value">{{ demand.feedback }}</p>
            </div>
          </OrdCardContent>
        </OrdCard>

        <!-- 处理流程 -->
        <OrdCard>
          <OrdCardHeader>
            <h2 class="panel-title">处理流程</h2>
            <OrdBadge variant="blue">Timeline</OrdBadge>
          </OrdCardHeader>
          <OrdCardContent>
            <OrdTimeline :items="timelineItems" />
          </OrdCardContent>
        </OrdCard>
      </div>

      <!-- 沟通区 -->
      <OrdCard class="conversation-card">
        <div class="conversation-head">
          <div>
            <p class="eyebrow">Conversation</p>
            <h2>沟通区</h2>
          </div>
          <OrdBadge variant="blue">{{ activeView === 'product' ? '产品视角' : activeView === 'requester' ? '发布者视角' : '只读' }}</OrdBadge>
        </div>
        <div class="conversation-body">
          <!-- 会话列表 -->
          <div class="thread-tabs">
            <button
              v-for="thread in getVisibleThreads()"
              :key="thread.id"
              :class="['thread-tab', { 'is-active': thread.id === activeThreadId }]"
              @click="handleThreadSwitch(thread.id)"
            >
              <OrdAvatar :name="thread.pmName" size="md" />
              <div class="thread-info">
                <div class="thread-name">{{ activeView === 'product' ? '我的会话' : thread.pmName }} · {{ thread.pmTitle }}</div>
                <div class="thread-meta">{{ thread.messages.length }} 条消息 · {{ thread.summary }}</div>
              </div>
              <OrdBadge :variant="thread.statusKey === 'ready' ? 'green' : 'orange'">{{ thread.status }}</OrdBadge>
            </button>
          </div>

          <!-- 聊天面板 -->
          <div class="chat-pane">
            <div class="conversation-summary">
              <p>{{ getActiveThread()?.summary }}</p>
            </div>
            <div class="message-list">
              <div
                v-for="(msg, idx) in getActiveThread()?.messages"
                :key="idx"
                :class="['message-item', { 'from-requester': msg.from === 'requester' }]"
              >
                <div class="message-meta">{{ msg.name }} · {{ msg.time }}</div>
                <div class="message-bubble">
                  {{ msg.text }}
                  <span v-if="msg.attachment" class="message-attachment">附件：{{ msg.attachment }}</span>
                </div>
              </div>
            </div>
            <div class="conversation-input">
              <OrdTextarea
                v-model="messageInput"
                :placeholder="canSendConversation() ? '输入消息' : '只读模式不能发送消息'"
                :disabled="!canSendConversation()"
                rows="3"
              />
              <div class="conversation-actions">
                <span class="attachment-status">
                  <span class="attachment-limit">最多 5 个附件，单个不超过 20MB，格式不限</span>
                </span>
                <div class="action-buttons">
                  <OrdButton v-if="canConvertDemand()" variant="outline" size="sm" @click="handleConvert">转化任务</OrdButton>
                  <OrdButton v-if="canSendConversation()" variant="primary" size="sm" @click="handleSendMessage">
                    {{ activeView === 'product' ? '发送询问' : '发送回复' }}
                  </OrdButton>
                </div>
              </div>
            </div>
          </div>
        </div>
      </OrdCard>
    </div>
  </div>
  </div>
</template>

<style scoped>
.demand-detail-page {
  padding: 96px 32px 32px;
}

.demand-detail-view {
  max-width: 1460px;
  margin: 0 auto;
  padding: 0;
  display: grid;
  gap: 18px;
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

.hero-section {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 24px;
  align-items: center;
  padding-bottom: 22px;
  border-bottom: 1px solid var(--ord-color-border-light);
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

.view-switch {
  display: inline-grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 3px;
  padding: 3px;
  background: #f2f6ff;
  border: 1px solid rgba(20, 110, 245, 0.18);
  border-radius: 6px;
}

.view-button {
  height: 34px;
  padding: 0 12px;
  color: var(--ord-color-gray-700);
  background: transparent;
  border: 0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
  transition: all var(--ord-transition-base);
}

.view-button.is-active {
  color: var(--ord-color-white);
  background: var(--ord-color-blue);
  box-shadow: 0 8px 18px rgba(20, 110, 245, 0.2);
}

.view-button:disabled {
  opacity: 0.42;
  cursor: not-allowed;
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
  align-items: start;
}

.panel-title {
  margin: 0;
  color: var(--ord-color-black);
  font-size: 19px;
  font-weight: 600;
  line-height: 1.2;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.field-card {
  padding: 12px;
  border: 1px solid var(--ord-color-border-light);
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
}

.conversation-head {
  min-height: 62px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 15px 18px;
  border-bottom: 1px solid var(--ord-color-border-light);
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
  border-right: 1px solid var(--ord-color-border-light);
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
  border-bottom: 1px solid var(--ord-color-border-light);
}

.conversation-summary p {
  margin: 0;
  color: var(--ord-color-gray-700);
  font-size: 13px;
  line-height: 1.55;
}

.message-list {
  min-height: 0;
  max-height: 360px;
  overflow-y: auto;
  display: grid;
  align-content: start;
  gap: 12px;
  padding: 18px;
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
  border: 1px solid var(--ord-color-border-light);
  border-radius: 6px;
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
  border-top: 1px solid var(--ord-color-border-light);
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
    border-bottom: 1px solid var(--ord-color-border-light);
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
</style>

