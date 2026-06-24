<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import TopNavbar from '@/components/TopNavbar.vue'
import { OrdButton } from '@/components/ui'
import { useToast } from '@/components/ui/toast/useToast'
import { messagesApi, type Message } from '@/api/messages'

const toast = useToast()

const messages = ref<Message[]>([])
const loading = ref(false)
const activeCategory = ref('all')
const unreadOnly = ref(false)
const keyword = ref('')
const detailMessage = ref<Message | null>(null)
const drawerOpen = ref(false)

const categories = [
  { key: 'all', label: '全部消息' },
  { key: 'system', label: '系统通知' },
  { key: 'task', label: '任务动态' },
  { key: 'demand', label: '需求进展' },
  { key: 'team', label: '团队申请' },
  { key: 'reply', label: '私信/回复' },
]

const categoryBadgeClass: Record<string, string> = {
  system: 'badge-system',
  task: 'badge-task',
  demand: 'badge-demand',
  team: 'badge-team',
  reply: 'badge-reply',
}

const unreadCount = computed(() => messages.value.filter(m => m.read_status === 0).length)

const summaryStats = computed(() => ({
  unread: unreadCount.value,
  task: messages.value.filter(m => m.category === 'task').length,
  demand: messages.value.filter(m => m.category === 'demand').length,
  team: messages.value.filter(m => m.category === 'team').length,
}))

const categoryUnread = computed(() => {
  const map: Record<string, number> = { all: unreadCount.value }
  for (const cat of categories.slice(1)) {
    map[cat.key] = messages.value.filter(
      m => m.category === cat.key && m.read_status === 0,
    ).length
  }
  return map
})

const filteredMessages = computed(() => {
  return messages.value.filter(m => {
    const matchCat = activeCategory.value === 'all' || m.category === activeCategory.value
    const matchUnread = !unreadOnly.value || m.read_status === 0
    const kw = keyword.value.trim().toLowerCase()
    const matchKw =
      !kw || `${m.title} ${m.summary} ${m.sender} ${m.target_id}`.toLowerCase().includes(kw)
    return matchCat && matchUnread && matchKw
  })
})

function getCategoryLabel(key: string) {
  return categories.find(c => c.key === key)?.label || key
}

function formatDate(iso: string) {
  if (!iso) return ''
  const d = new Date(iso)
  const p = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

async function loadMessages() {
  loading.value = true
  try {
    const res = await messagesApi.getList({ page: 1, page_size: 100 })
    messages.value = res.data.items
  } finally {
    loading.value = false
  }
}

async function handleMarkRead(id: string) {
  await messagesApi.markRead(id)
  const msg = messages.value.find(m => m.id === id)
  if (msg) msg.read_status = 1
  toast.show({ title: '已标记为已读', variant: 'success' })
}

async function handleMarkAllRead() {
  await messagesApi.markAllRead()
  messages.value.forEach(m => { m.read_status = 1 })
  toast.show({ title: '全部消息已标记为已读', variant: 'success' })
}

async function handleDelete(id: string) {
  await messagesApi.delete(id)
  messages.value = messages.value.filter(m => m.id !== id)
  if (detailMessage.value?.id === id) closeDrawer()
  toast.show({ title: '消息已删除', variant: 'default' })
}

async function openDrawer(id: string) {
  const msg = messages.value.find(m => m.id === id)
  if (!msg) return
  detailMessage.value = { ...msg }
  drawerOpen.value = true
  if (msg.read_status === 0) {
    await messagesApi.markRead(id)
    msg.read_status = 1
  }
}

function closeDrawer() {
  drawerOpen.value = false
  detailMessage.value = null
}

function handleEsc(e: KeyboardEvent) {
  if (e.key === 'Escape' && drawerOpen.value) closeDrawer()
}

onMounted(() => {
  loadMessages()
  document.addEventListener('keydown', handleEsc)
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleEsc)
})
</script>

<template>
  <div class="messages-view">
    <TopNavbar />

    <main class="page-shell">
      <section class="message-frame">
        <!-- Hero 卡片 -->
        <div class="hero-card">
          <div>
            <p class="eyebrow">Message Center</p>
            <h1>消息中心</h1>
            <p class="hero-copy">集中查看系统通知、任务动态、需求进展、团队申请和私信回复，像站内信一样管理未读与协作提醒。</p>
          </div>
          <OrdButton variant="primary" @click="handleMarkAllRead">全部已读</OrdButton>
        </div>

        <!-- 概览统计 -->
        <div class="summary-grid">
          <article class="summary-card">
            <p class="summary-label">未读消息</p>
            <p class="summary-value">{{ summaryStats.unread }}</p>
            <p class="summary-desc">当前仍需处理的站内消息</p>
          </article>
          <article class="summary-card summary-card--green">
            <p class="summary-label">任务相关</p>
            <p class="summary-value">{{ summaryStats.task }}</p>
            <p class="summary-desc">任务进展、分配和验收动态</p>
          </article>
          <article class="summary-card summary-card--orange">
            <p class="summary-label">需求相关</p>
            <p class="summary-value">{{ summaryStats.demand }}</p>
            <p class="summary-desc">需求审核、沟通和转化提醒</p>
          </article>
          <article class="summary-card summary-card--purple">
            <p class="summary-label">团队申请</p>
            <p class="summary-value">{{ summaryStats.team }}</p>
            <p class="summary-desc">成员加入、邀请和队长审核</p>
          </article>
        </div>

        <!-- 消息主体 -->
        <section class="message-card">
          <div class="message-layout">
            <!-- 分类侧栏 -->
            <aside class="category-panel">
              <p class="category-title">消息分类</p>
              <div class="category-list">
                <button
                  v-for="cat in categories"
                  :key="cat.key"
                  class="category-button"
                  :class="{ 'is-active': activeCategory === cat.key }"
                  type="button"
                  @click="activeCategory = cat.key"
                >
                  <span>{{ cat.label }}</span>
                  <span class="category-count">{{ categoryUnread[cat.key] }}</span>
                </button>
              </div>
            </aside>

            <!-- 消息主区 -->
            <div class="message-main">
              <div class="message-toolbar">
                <div>
                  <h2 class="toolbar-title">{{ getCategoryLabel(activeCategory) }}</h2>
                  <p class="toolbar-note">
                    {{ unreadOnly ? '当前仅展示未读消息。' : '展示站内消息，可搜索、筛选未读并进行批量处理。' }}
                  </p>
                </div>
                <div class="toolbar-actions">
                  <input
                    v-model="keyword"
                    class="search-box"
                    type="search"
                    placeholder="搜索标题、摘要、关联对象"
                  />
                  <button
                    class="text-button"
                    type="button"
                    :aria-pressed="String(unreadOnly)"
                    @click="unreadOnly = !unreadOnly"
                  >
                    {{ unreadOnly ? '查看全部' : '只看未读' }}
                  </button>
                </div>
              </div>

              <div v-if="loading" class="empty-state is-visible">加载中...</div>
              <template v-else>
                <div class="message-list">
                  <article
                    v-for="msg in filteredMessages"
                    :key="msg.id"
                    class="message-item"
                    :class="{ 'is-unread': msg.read_status === 0 }"
                  >
                    <div>
                      <div class="message-title-row">
                        <span v-if="msg.read_status === 0" class="unread-dot" aria-label="未读" />
                        <h3 class="message-title">{{ msg.title }}</h3>
                        <span class="message-badge" :class="categoryBadgeClass[msg.category] || ''">
                          {{ getCategoryLabel(msg.category) }}
                        </span>
                      </div>
                      <p class="message-summary">{{ msg.summary }}</p>
                      <div class="message-meta">
                        <span class="message-badge badge-reply">{{ msg.sender }}</span>
                        <span class="message-badge badge-reply">{{ formatDate(msg.created_at) }}</span>
                        <span v-if="msg.target_id" class="message-badge badge-reply">{{ msg.target_id }}</span>
                      </div>
                    </div>
                    <div class="message-actions">
                      <button class="mark-button" type="button" @click="openDrawer(msg.id)">详情</button>
                      <button class="mark-button" type="button" @click="handleMarkRead(msg.id)">已读</button>
                      <button class="delete-button" type="button" @click="handleDelete(msg.id)">删除</button>
                    </div>
                  </article>
                </div>
                <div v-if="filteredMessages.length === 0" class="empty-state is-visible">
                  没有匹配的消息，试试切换分类或清空搜索。
                </div>
              </template>
            </div>
          </div>
        </section>
      </section>
    </main>

    <!-- 详情抽屉 -->
    <div
      class="drawer-backdrop"
      :class="{ 'is-open': drawerOpen }"
      :aria-hidden="String(!drawerOpen)"
      @click.self="closeDrawer"
    >
      <aside class="drawer-card" role="dialog" aria-modal="true">
        <div class="drawer-header">
          <div>
            <p class="eyebrow">Message Detail</p>
            <h2>{{ detailMessage?.title || '消息详情' }}</h2>
          </div>
          <button class="close-button" type="button" aria-label="关闭详情" @click="closeDrawer">×</button>
        </div>
        <div v-if="detailMessage" class="drawer-body">
          <div class="detail-card">
            <p class="detail-label">消息分类</p>
            <p class="detail-value">{{ getCategoryLabel(detailMessage.category) }}</p>
          </div>
          <div class="detail-card">
            <p class="detail-label">发送方</p>
            <p class="detail-value">{{ detailMessage.sender }}</p>
          </div>
          <div class="detail-card">
            <p class="detail-label">发送时间</p>
            <p class="detail-value">{{ formatDate(detailMessage.created_at) }}</p>
          </div>
          <div v-if="detailMessage.target_id" class="detail-card">
            <p class="detail-label">关联对象</p>
            <p class="detail-value">{{ detailMessage.target_id }}</p>
          </div>
          <div class="detail-card">
            <p class="detail-label">消息内容</p>
            <p class="detail-value">{{ detailMessage.content }}</p>
          </div>
          <div v-if="detailMessage.action_text" class="detail-card">
            <p class="detail-label">推荐操作</p>
            <p class="detail-value">{{ detailMessage.action_text }}</p>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.messages-view { min-height: 100vh; }

.page-shell {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 96px 32px 32px;
}

.message-frame {
  position: relative;
  width: min(1460px, 100%);
  display: grid;
  gap: 18px;
}

.message-frame::before,
.message-frame::after {
  content: '';
  position: absolute;
  z-index: -1;
  border: 1px solid rgba(216, 216, 216, 0.7);
  background: rgba(255, 255, 255, 0.45);
}

.message-frame::before {
  width: 180px; height: 86px; top: 96px; right: 42px;
  transform: rotate(-2deg);
}

.message-frame::after {
  width: 108px; height: 108px; right: 214px; bottom: 56px;
  transform: rotate(4deg);
}

.hero-card {
  position: relative; overflow: hidden;
  display: grid; grid-template-columns: 1fr auto;
  gap: 24px; align-items: center; padding: 28px;
  background: rgba(255,255,255,0.94);
  border: 1px solid rgba(216,216,216,0.86);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
}

.hero-card::after {
  content: ''; position: absolute; right: -56px; top: -56px;
  width: 220px; height: 220px;
  background:
    linear-gradient(90deg, rgba(20,110,245,0.16) 1px, transparent 1px),
    linear-gradient(0deg, rgba(20,110,245,0.16) 1px, transparent 1px);
  background-size: 22px 22px;
  transform: rotate(8deg); pointer-events: none;
}

.eyebrow {
  margin: 0 0 10px; color: var(--ord-color-blue);
  font-size: 12px; font-weight: 700; letter-spacing: 1.4px; text-transform: uppercase;
}

h1 {
  margin: 0; color: var(--ord-color-black);
  font-size: clamp(34px, 4vw, 56px); font-weight: 600;
  line-height: 1.04; letter-spacing: -0.6px;
}

.hero-copy {
  max-width: 760px; margin: 16px 0 0;
  color: var(--ord-color-gray-700); font-size: 16px; line-height: 1.65;
}

.summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }

.summary-card {
  min-height: 106px; padding: 18px;
  background: rgba(255,255,255,0.94); border: 1px solid rgba(216,216,216,0.86);
  border-top: 4px solid var(--ord-color-blue);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade); backdrop-filter: blur(16px);
}
.summary-card--green  { border-top-color: var(--ord-color-green); }
.summary-card--orange { border-top-color: var(--ord-color-orange); }
.summary-card--purple { border-top-color: var(--ord-color-purple); }

.summary-label {
  margin: 0; color: var(--ord-color-gray-500);
  font-size: 11px; font-weight: 700; letter-spacing: 1.1px; text-transform: uppercase;
}
.summary-value { margin: 12px 0 0; color: var(--ord-color-black); font-size: 34px; font-weight: 600; line-height: 1; }
.summary-desc  { margin: 10px 0 0; color: var(--ord-color-gray-500); font-size: 13px; line-height: 1.45; }

.message-card {
  overflow: hidden; background: rgba(255,255,255,0.94);
  border: 1px solid rgba(216,216,216,0.86); border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade); backdrop-filter: blur(16px);
}

.message-layout { display: grid; grid-template-columns: 260px 1fr; min-height: 620px; }

.category-panel { padding: 18px; border-right: 1px solid #ececec; background: rgba(250,250,250,0.74); }
.category-title {
  margin: 0 0 14px; color: var(--ord-color-gray-500);
  font-size: 11px; font-weight: 700; letter-spacing: 1.1px; text-transform: uppercase;
}
.category-list { display: grid; gap: 8px; }

.category-button {
  width: 100%; min-height: 42px; display: flex; align-items: center;
  justify-content: space-between; gap: 12px; padding: 0 12px;
  color: var(--ord-color-gray-700); background: var(--ord-color-white);
  border: 1px solid var(--ord-color-border); border-radius: var(--ord-radius-sm);
  font: inherit; font-size: 14px; font-weight: 600; cursor: pointer;
  transition: var(--ord-transition-base);
}
.category-button.is-active { color: var(--ord-color-white); background: var(--ord-color-black); border-color: var(--ord-color-black); }

.category-count {
  min-width: 24px; height: 24px; display: grid; place-items: center; padding: 0 7px;
  color: var(--ord-color-blue); background: rgba(20,110,245,0.08);
  border-radius: var(--ord-radius-full); font-size: 12px; font-weight: 700;
}
.category-button.is-active .category-count { color: var(--ord-color-black); background: var(--ord-color-white); }

.message-main { display: grid; grid-template-rows: auto 1fr; min-width: 0; position: relative; }

.message-main::after {
  content: '';
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  height: 48px;
  background: linear-gradient(to bottom, transparent, rgba(255,255,255,0.92));
  pointer-events: none;
  display: block;
}

.message-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; padding: 18px; border-bottom: 1px solid #ececec;
}
.toolbar-title { margin: 0; color: var(--ord-color-black); font-size: 22px; font-weight: 600; line-height: 1.2; }
.toolbar-note  { margin: 7px 0 0; color: var(--ord-color-gray-500); font-size: 13px; line-height: 1.45; }
.toolbar-actions { display: flex; align-items: center; justify-content: flex-end; flex-wrap: wrap; gap: 10px; }

.search-box {
  width: 260px; height: 42px; padding: 0 12px;
  border: 1px solid var(--ord-color-border); border-radius: var(--ord-radius-sm);
  background: var(--ord-color-white); color: var(--ord-color-black);
  font: inherit; font-size: 14px; outline: none;
  transition: border-color var(--ord-transition-base), box-shadow var(--ord-transition-base);
}
.search-box:focus { border-color: var(--ord-color-blue); box-shadow: 0 0 0 4px rgba(20,110,245,0.12); }

.text-button, .mark-button, .delete-button {
  height: 34px; padding: 0 12px;
  color: var(--ord-color-gray-700); background: var(--ord-color-white);
  border: 1px solid var(--ord-color-border); border-radius: var(--ord-radius-sm);
  font: inherit; font-size: 13px; font-weight: 600; cursor: pointer;
  transition: var(--ord-transition-base);
}
.text-button:hover, .mark-button:hover, .delete-button:hover {
  color: var(--ord-color-blue); border-color: var(--ord-color-blue); transform: translateX(6px);
}

.message-list {
  display: grid;
  align-content: start;
  max-height: 440px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: var(--ord-color-border) transparent;
}

.message-list::-webkit-scrollbar { width: 4px; }
.message-list::-webkit-scrollbar-track { background: transparent; }
.message-list::-webkit-scrollbar-thumb { background: var(--ord-color-border); border-radius: 2px; }

.message-item {
  display: grid; grid-template-columns: 1fr auto; gap: 16px;
  padding: 18px; border-bottom: 1px solid #ececec;
  background: var(--ord-color-white); transition: background var(--ord-transition-base);
}
.message-item:hover     { background: rgba(20,110,245,0.03); }
.message-item.is-unread { background: rgba(20,110,245,0.045); }

.message-title-row { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 6px; }
.unread-dot { width: 8px; height: 8px; flex-shrink: 0; background: var(--ord-color-red); border-radius: 50%; }
.message-title   { margin: 0; color: var(--ord-color-black); font-size: 16px; font-weight: 700; line-height: 1.35; }
.message-summary { margin: 0; color: var(--ord-color-gray-700); font-size: 13px; line-height: 1.55; }
.message-meta    { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
.message-actions { display: flex; align-items: flex-start; gap: 8px; }

.message-badge {
  display: inline-flex; align-items: center; min-height: 24px; padding: 0 8px;
  border-radius: var(--ord-radius-sm);
  color: var(--ord-color-blue); background: rgba(20,110,245,0.08);
  font-size: 11px; font-weight: 700; white-space: nowrap;
}
.badge-system { color: var(--ord-color-purple); background: rgba(122,61,255,0.1); }
.badge-task   { color: var(--ord-color-blue);   background: rgba(20,110,245,0.08); }
.badge-demand { color: #009e19;                 background: rgba(0,215,34,0.12); }
.badge-team   { color: #b27600;                 background: rgba(255,174,19,0.16); }
.badge-reply  { color: var(--ord-color-gray-700); background: #f4f4f4; }

.empty-state { display: none; padding: 56px 24px; color: var(--ord-color-gray-500); text-align: center; }
.empty-state.is-visible { display: block; }

.drawer-backdrop {
  position: fixed; inset: 0; z-index: 50;
  opacity: 0; pointer-events: none;
  background: rgba(8,8,8,0.42); transition: opacity 180ms ease;
}
.drawer-backdrop.is-open { opacity: 1; pointer-events: auto; }

.drawer-card {
  position: fixed; top: 0; right: 0;
  width: min(520px, 100%); height: 100vh; overflow-y: auto;
  background: rgba(255,255,255,0.94); border-left: 1px solid rgba(216,216,216,0.86);
  box-shadow: var(--ord-shadow-cascade); backdrop-filter: blur(16px);
  transform: translateX(24px); transition: transform 180ms ease;
}
.drawer-backdrop.is-open .drawer-card { transform: translateX(0); }

.drawer-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  gap: 16px; padding: 24px; border-bottom: 1px solid #ececec;
}
.drawer-header h2 { margin: 0; color: var(--ord-color-black); font-size: 26px; font-weight: 600; line-height: 1.2; }

.close-button {
  width: 36px; height: 36px; display: grid; place-items: center; flex: 0 0 auto;
  color: var(--ord-color-black); background: var(--ord-color-white);
  border: 1px solid var(--ord-color-border); border-radius: var(--ord-radius-sm);
  font-size: 20px; line-height: 1; cursor: pointer; transition: var(--ord-transition-base);
}
.close-button:hover { color: var(--ord-color-blue); border-color: var(--ord-color-blue); }

.drawer-body { display: grid; gap: 14px; padding: 24px; }

.detail-card { padding: 14px; border: 1px solid #ececec; border-radius: 6px; background: var(--ord-color-white); }
.detail-label {
  margin: 0 0 7px; color: var(--ord-color-gray-500);
  font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
}
.detail-value { margin: 0; color: var(--ord-color-black); font-size: 14px; line-height: 1.65; }

@media (max-width: 992px) {
  .hero-card       { grid-template-columns: 1fr; }
  .summary-grid    { grid-template-columns: repeat(2, 1fr); }
  .message-layout  { grid-template-columns: 1fr; }
  .category-panel  { border-right: 0; border-bottom: 1px solid #ececec; }
  .category-list   { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .message-toolbar { align-items: stretch; flex-direction: column; }
  .toolbar-actions { justify-content: flex-start; }
}

@media (max-width: 768px) {
  .page-shell    { padding: 92px 16px 24px; }
  .summary-grid,
  .category-list { grid-template-columns: 1fr; }
  .message-item  { grid-template-columns: 1fr; }
  .search-box    { width: 100%; }
}
</style>
