<template>
  <div class="profile-view">
    <TopNavbar />
    <main class="page-shell">
      <section class="profile-frame">
        <!-- Hero 卡片 -->
        <div class="hero-card">
          <div class="avatar-card">
            <div>
              <div class="avatar-large">{{ avatarInitial }}</div>
              <p>Profile Avatar</p>
            </div>
          </div>
          <div>
            <p class="eyebrow">Personal Profile</p>
            <h1>个人信息</h1>
            <p class="hero-copy">{{ profile.intro || '暂无个人介绍' }}</p>
            <div class="tag-row">
              <span class="role-badge" :class="roleClass">{{ roleLabel }}</span>
              <span v-if="profile.position" class="tag-chip">{{ profile.position }}</span>
              <span v-if="profile.province" class="tag-chip">{{ profile.province }}</span>
              <span v-for="tag in profile.tags?.slice(0, 2)" :key="tag" class="tag-chip">{{ tag }}</span>
            </div>
          </div>
          <OrdButton variant="primary" @click="openEditModal">编辑资料</OrdButton>
        </div>

        <!-- 统计卡片 -->
        <div class="stat-grid">
          <article class="info-card">
            <p class="info-label">平台号</p>
            <p class="info-value">{{ profile.platform_id }}</p>
            <p class="info-desc">平台唯一身份标识，不可修改</p>
          </article>
          <article class="info-card">
            <p class="info-label">参与任务</p>
            <p class="info-value">{{ stats.taskCount }}</p>
            <p class="info-desc">包含负责、参与和已完成任务</p>
          </article>
          <article class="info-card">
            <p class="info-label">贡献积分</p>
            <p class="info-value">{{ stats.points }}</p>
            <p class="info-desc">来自任务协作与需求转化</p>
          </article>
          <article class="info-card">
            <p class="info-label">初始化状态</p>
            <p class="info-value">{{ profile.onboarding_completed ? '已完成' : '未完成' }}</p>
            <p class="info-desc">已完成身份、岗位和擅长领域配置</p>
          </article>
        </div>

        <!-- 内容区 -->
        <div class="content-grid">
          <!-- 基础资料 -->
          <section class="panel-card">
            <div class="panel-head">
              <h2 class="panel-title">基础资料</h2>
              <OrdBadge :variant="roleBadgeVariant">{{ roleLabel }}</OrdBadge>
            </div>
            <div class="panel-body">
              <div class="field-grid">
                <article class="field-card">
                  <p class="field-label">昵称</p>
                  <p class="field-value">{{ profile.nickname }}</p>
                </article>
                <article class="field-card">
                  <p class="field-label">手机号</p>
                  <p class="field-value">{{ maskedPhone }}</p>
                </article>
                <article class="field-card">
                  <p class="field-label">身份</p>
                  <p class="field-value">{{ profile.identity }}</p>
                </article>
                <article class="field-card">
                  <p class="field-label">工作职业</p>
                  <p class="field-value">{{ profile.position || '-' }}</p>
                </article>
                <article class="field-card">
                  <p class="field-label">所在地区</p>
                  <p class="field-value">{{ profile.province || '-' }}</p>
                </article>
                <article class="field-card">
                  <p class="field-label">擅长领域</p>
                  <div class="skill-tags">
                    <span v-for="tag in profile.tags" :key="tag" class="tag-chip">{{ tag }}</span>
                    <span v-if="!profile.tags?.length" class="field-value">-</span>
                  </div>
                </article>
                <article class="field-card is-full">
                  <p class="field-label">个人介绍</p>
                  <p class="field-value">{{ profile.intro || '-' }}</p>
                </article>
              </div>
            </div>
          </section>

          <!-- 近期参与 -->
          <section class="panel-card">
            <div class="panel-head">
              <h2 class="panel-title">近期参与</h2>
              <OrdBadge variant="blue">Active</OrdBadge>
            </div>
            <div class="panel-body">
              <div class="activity-list">
                <div v-for="item in recentActivities" :key="item.title" class="activity-item">
                  <div>
                    <span class="activity-title">{{ item.title }}</span>
                    <span class="activity-meta">{{ item.role }} · {{ item.status }}</span>
                  </div>
                  <span class="tag-chip">{{ item.progress }}</span>
                </div>
                <div v-if="!recentActivities.length" class="activity-empty">
                  暂无近期参与记录
                </div>
              </div>
            </div>
          </section>
        </div>
      </section>
    </main>

    <!-- 编辑弹窗 -->
    <OrdDialog v-model:open="editDialogOpen">
      <template #trigger><span /></template>
      <div class="edit-modal-content">
        <div class="modal-header">
          <div>
            <p class="eyebrow">Edit Profile</p>
            <h2 class="modal-title">编辑个人资料</h2>
            <p class="modal-subtitle">平台号作为唯一账号标识不可修改，其他资料可即时更新。</p>
          </div>
          <button class="close-button" type="button" @click="editDialogOpen = false">×</button>
        </div>

        <form class="edit-form" @submit.prevent="handleSave">
          <div class="form-grid">
            <div class="form-field">
              <label>头像缩写</label>
              <OrdInput v-model="form.avatar" type="text" placeholder="最多2个字符" />
            </div>
            <div class="form-field">
              <label>平台号</label>
              <OrdInput :model-value="profile.platform_id" disabled />
            </div>
            <div class="form-field">
              <label>昵称</label>
              <OrdInput v-model="form.nickname" type="text" placeholder="请输入昵称" />
            </div>
            <div class="form-field">
              <label>手机号</label>
              <OrdInput v-model="form.phone" type="tel" placeholder="请输入手机号" />
            </div>
            <div class="form-field">
              <label>身份</label>
              <OrdInput :model-value="form.identity" disabled />
              <p class="field-hint">身份由平台权限管理控制，用户不可自行修改。</p>
            </div>
            <div class="form-field">
              <label>工作职业</label>
              <OrdInput v-model="form.position" type="text" placeholder="请输入工作职业" />
            </div>
            <div class="form-field">
              <label>所在地区</label>
              <OrdSelect v-model="form.province" :options="provinceOptions" placeholder="请选择地区" />
            </div>
            <div class="form-field">
              <label>擅长领域</label>
              <div class="tag-editor">
                <div class="tag-input-row">
                  <OrdInput v-model="tagInputValue" type="text" placeholder="输入标签后点击添加" @keydown.enter.prevent="addTag" />
                  <OrdButton variant="ghost" type="button" @click="addTag">添加</OrdButton>
                </div>
                <div class="edit-tags">
                  <span v-for="tag in form.tags" :key="tag" class="tag-chip">
                    {{ tag }}
                    <button class="remove-tag" type="button" @click="removeTag(tag)">×</button>
                  </span>
                </div>
              </div>
            </div>
            <div class="form-field is-full">
              <label>个人介绍</label>
              <OrdTextarea v-model="form.intro" placeholder="请输入个人介绍（最多200字）" :rows="4" />
            </div>
          </div>
          <div class="modal-footer">
            <span class="form-message" :class="{ 'is-error': formError }">{{ formMessage }}</span>
            <OrdButton variant="primary" type="submit" :loading="saving">保存资料</OrdButton>
          </div>
        </form>
      </div>
    </OrdDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/api/client'
import { useToast } from '@/components/ui/toast/useToast'
import { OrdButton, OrdBadge, OrdInput, OrdTextarea, OrdSelect, OrdDialog } from '@/components/ui'
import TopNavbar from '@/components/TopNavbar.vue'

const auth = useAuthStore()
const toast = useToast()

interface ProfileData {
  id: string
  platform_id: string
  nickname: string
  phone: string
  avatar_url: string
  role: string
  identity: string
  position: string
  province: string
  tags: string[]
  intro: string
  onboarding_completed: number
}

const profile = ref<ProfileData>({
  id: '',
  platform_id: '',
  nickname: '',
  phone: '',
  avatar_url: '',
  role: '',
  identity: '',
  position: '',
  province: '',
  tags: [],
  intro: '',
  onboarding_completed: 0,
})

const stats = reactive({
  taskCount: 0,
  points: 0,
})

const recentActivities = ref<{ title: string; role: string; status: string; progress: string }[]>([])

const editDialogOpen = ref(false)
const saving = ref(false)
const formMessage = ref('')
const formError = ref(false)
const tagInputValue = ref('')

const form = reactive({
  avatar: '',
  nickname: '',
  phone: '',
  identity: '',
  position: '',
  province: '',
  tags: [] as string[],
  intro: '',
})

const roleMap: Record<string, { label: string; class: string; badge: string }> = {
  builder: { label: '共建者', class: 'builder', badge: 'blue' },
  requester: { label: '需求者', class: 'requester', badge: 'orange' },
  super_admin: { label: '超级管理员', class: 'superAdmin', badge: 'purple' },
  operator: { label: '运营管理员', class: 'operator', badge: 'green' },
}

const roleLabel = computed(() => roleMap[profile.value.role]?.label || profile.value.identity || '用户')
const roleClass = computed(() => roleMap[profile.value.role]?.class || '')
const roleBadgeVariant = computed(() => (roleMap[profile.value.role]?.badge || 'blue') as 'blue' | 'purple' | 'green' | 'orange')

const avatarInitial = computed(() => {
  if (form.avatar && editDialogOpen.value) return form.avatar
  return profile.value.nickname?.slice(0, 1) || 'U'
})

const maskedPhone = computed(() => {
  const p = profile.value.phone
  if (!p || p.length < 7) return p || '-'
  return p.slice(0, 3) + '****' + p.slice(-4)
})

const identityOptions = [
  { value: '共建者', label: '共建者' },
  { value: '需求者', label: '需求者' },
  { value: '超级管理员', label: '超级管理员' },
  { value: '运营管理员', label: '运营管理员' },
]

const provinceOptions = [
  { value: '北京', label: '北京' },
  { value: '上海', label: '上海' },
  { value: '广东', label: '广东' },
  { value: '浙江', label: '浙江' },
  { value: '江苏', label: '江苏' },
  { value: '四川', label: '四川' },
  { value: '湖北', label: '湖北' },
  { value: '陕西', label: '陕西' },
  { value: '福建', label: '福建' },
  { value: '山东', label: '山东' },
]

async function fetchProfile() {
  const res = await api.get<ProfileData>('/me')
  profile.value = res.data
  // 模拟统计数据（基于角色）
  if (profile.value.role === 'builder') {
    stats.taskCount = 12
    stats.points = 1280
    recentActivities.value = [
      { title: '用药提醒 API', role: '后端开发', status: '进行中', progress: '68%' },
      { title: '自然语言病历摘要', role: '任务队长', status: '待审核申请', progress: '待处理' },
      { title: '复诊问题清单原型', role: '产品协作', status: '已验收', progress: '完成' },
    ]
  } else if (profile.value.role === 'requester') {
    stats.taskCount = 3
    stats.points = 420
    recentActivities.value = [
      { title: '药物信息共享需求', role: '需求提交者', status: '已转化', progress: '完成' },
      { title: '患者社区功能建议', role: '需求提交者', status: '审核中', progress: '待处理' },
    ]
  } else if (profile.value.role === 'operator') {
    stats.taskCount = 36
    stats.points = 2100
    recentActivities.value = [
      { title: '需求审核批次 #28', role: '审核人', status: '进行中', progress: '12/18' },
      { title: '任务转化跟踪', role: '产品经理', status: '进行中', progress: '62%' },
      { title: '用户反馈收集', role: '产品经理', status: '已完成', progress: '完成' },
    ]
  } else if (profile.value.role === 'super_admin') {
    stats.taskCount = 74
    stats.points = 5000
    recentActivities.value = [
      { title: '权限配置审计', role: '管理员', status: '进行中', progress: '进行中' },
      { title: '系统安全巡检', role: '管理员', status: '已完成', progress: '完成' },
      { title: '用户行为分析报告', role: '管理员', status: '已完成', progress: '完成' },
    ]
  }
}

function openEditModal() {
  form.avatar = profile.value.nickname?.slice(0, 1) || ''
  form.nickname = profile.value.nickname
  form.phone = profile.value.phone
  form.identity = roleLabel.value
  form.position = profile.value.position
  form.province = profile.value.province
  form.tags = [...(profile.value.tags || [])]
  form.intro = profile.value.intro
  formMessage.value = ''
  formError.value = false
  editDialogOpen.value = true
}

function addTag() {
  const tag = tagInputValue.value.trim()
  if (!tag) return
  if (form.tags.includes(tag)) {
    formMessage.value = '该标签已存在。'
    formError.value = true
    return
  }
  if (form.tags.length >= 6) {
    formMessage.value = '最多添加 6 个擅长领域标签。'
    formError.value = true
    return
  }
  form.tags.push(tag)
  tagInputValue.value = ''
  formMessage.value = `已选择 ${form.tags.length}/6 个擅长领域标签。`
  formError.value = false
}

function removeTag(tag: string) {
  form.tags = form.tags.filter(t => t !== tag)
  formMessage.value = `已选择 ${form.tags.length}/6 个擅长领域标签。`
  formError.value = false
}

async function handleSave() {
  if (!form.nickname.trim() || !form.phone.trim() || !form.position.trim() || !form.intro.trim()) {
    formMessage.value = '请完整填写昵称、手机号、职业和个人介绍。'
    formError.value = true
    return
  }

  saving.value = true
  try {
    await api.patch('/me/profile', {
      nickname: form.nickname.trim(),
      phone: form.phone.trim(),
      position: form.position.trim(),
      province: form.province,
      tags: form.tags,
      intro: form.intro.trim(),
    })
    await fetchProfile()
    await auth.fetchMe()
    editDialogOpen.value = false
    toast.show({ title: '保存成功', description: '个人资料已更新。', variant: 'success' })
  } catch {
    formMessage.value = '保存失败，请稍后重试。'
    formError.value = true
  } finally {
    saving.value = false
  }
}

onMounted(fetchProfile)
</script>

<style scoped>
.profile-view {
  min-height: 100vh;
}

.page-shell {
  min-height: calc(100vh - 76px);
  display: flex;
  justify-content: center;
  padding: 96px 32px 32px;
}

.profile-frame {
  position: relative;
  display: grid;
  gap: 18px;
  width: min(1460px, 100%);
}

.profile-frame::before,
.profile-frame::after {
  content: "";
  position: absolute;
  z-index: -1;
  border: 1px solid rgba(216, 216, 216, 0.7);
  background: rgba(255, 255, 255, 0.45);
  transform: rotate(-2deg);
}

.profile-frame::before {
  width: 180px;
  height: 86px;
  top: 96px;
  right: 42px;
}

.profile-frame::after {
  width: 108px;
  height: 108px;
  right: 214px;
  bottom: 56px;
  transform: rotate(4deg);
}

/* Hero 卡片 */
.hero-card {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: 260px 1fr auto;
  gap: 24px;
  align-items: center;
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

.avatar-card {
  position: relative;
  z-index: 1;
  display: grid;
  place-items: center;
  min-height: 220px;
  background: var(--ord-color-black);
  border-radius: var(--ord-radius-md);
  color: var(--ord-color-white);
}

.avatar-card p {
  margin: 14px 0 0;
  color: rgba(255, 255, 255, 0.72);
  font-size: 13px;
}

.avatar-large {
  width: 112px;
  height: 112px;
  display: grid;
  place-items: center;
  background: var(--ord-color-blue);
  border-radius: 50%;
  color: var(--ord-color-white);
  font-size: 40px;
  font-weight: 700;
  letter-spacing: -1px;
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
  max-width: 760px;
  margin: 16px 0 0;
  color: var(--ord-color-gray-600);
  font-size: 16px;
  line-height: 1.65;
}

.tag-row,
.skill-tags,
.edit-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.role-badge,
.tag-chip {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: var(--ord-radius-sm);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.role-badge {
  color: var(--ord-color-blue);
  background: rgba(20, 110, 245, 0.08);
}

.role-badge.requester { color: #b27600; background: rgba(255, 174, 19, 0.16); }
.role-badge.superAdmin { color: #7a3dff; background: rgba(122, 61, 255, 0.1); }
.role-badge.operator { color: #009e19; background: rgba(0, 215, 34, 0.12); }
.role-badge.builder { color: var(--ord-color-blue); background: rgba(20, 110, 245, 0.08); }

.tag-chip {
  color: var(--ord-color-blue);
  background: rgba(20, 110, 245, 0.08);
}

/* 统计卡片 */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.info-card {
  min-height: 106px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(216, 216, 216, 0.86);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
  border-top: 4px solid var(--ord-color-blue);
}

.info-card:nth-child(2) { border-top-color: #ff6b00; }
.info-card:nth-child(3) { border-top-color: #00d722; }
.info-card:nth-child(4) { border-top-color: #7a3dff; }

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
  font-size: 22px;
  font-weight: 600;
  line-height: 1.2;
}

.info-desc {
  margin: 9px 0 0;
  color: var(--ord-color-gray-500);
  font-size: 13px;
  line-height: 1.45;
}

/* 内容区 */
.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 0.72fr);
  gap: 18px;
}

.panel-card {
  overflow: hidden;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(216, 216, 216, 0.86);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 18px;
  border-bottom: 1px solid #ececec;
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
  padding: 18px;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.field-card {
  min-height: 76px;
  padding: 13px;
  border: 1px solid #ececec;
  border-radius: 6px;
  background: #fff;
}

.field-card.is-full { grid-column: 1 / -1; }

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

/* 近期参与 */
.activity-list {
  display: grid;
  gap: 10px;
}

.activity-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 56px;
  padding: 12px;
  border: 1px solid #ececec;
  border-radius: 6px;
  background: #fff;
}

.activity-title {
  display: block;
  color: var(--ord-color-black);
  font-size: 14px;
  font-weight: 700;
}

.activity-meta {
  display: block;
  margin-top: 4px;
  color: var(--ord-color-gray-500);
  font-size: 12px;
  line-height: 1.45;
}

.activity-empty {
  text-align: center;
  color: var(--ord-color-gray-500);
  font-size: 14px;
  padding: 24px 0;
}

/* 编辑弹窗覆盖样式 */
:deep(.ord-dialog__content) {
  width: min(1080px, calc(100vw - 48px));
  max-height: min(72vh, 640px);
  padding: 0;
  overflow-y: auto;
}

.edit-modal-content {
  overflow-y: auto;
}

.modal-header {
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

.close-button {
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
  transition: color var(--ord-transition-base), border-color var(--ord-transition-base);
}

.close-button:hover {
  color: var(--ord-color-blue);
  border-color: var(--ord-color-blue);
}

.edit-form {
  padding: 22px 24px 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.form-field label {
  display: block;
  margin-bottom: 7px;
  color: var(--ord-color-gray-500);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.form-field.is-full { grid-column: 1 / -1; }

.field-hint {
  margin: 6px 0 0;
  color: var(--ord-color-gray-500);
  font-size: 12px;
  line-height: 1.4;
}

.tag-editor {
  display: grid;
  gap: 10px;
}

.tag-input-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
}

.edit-tags {
  margin-top: 0;
}

.remove-tag {
  margin-left: 6px;
  padding: 0;
  color: inherit;
  background: transparent;
  border: 0;
  font-size: 14px;
  cursor: pointer;
  transition: opacity var(--ord-transition-base);
}

.remove-tag:hover { opacity: 0.6; }

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid #ececec;
}

.form-message {
  color: var(--ord-color-gray-500);
  font-size: 13px;
  line-height: 1.45;
}

.form-message.is-error {
  color: #ee1d36;
}

/* 响应式 */
@media (max-width: 992px) {
  .hero-card,
  .content-grid { grid-template-columns: 1fr; }
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .page-shell { padding: 92px 16px 24px; }
  .stat-grid,
  .field-grid,
  .form-grid { grid-template-columns: 1fr; }
  .field-card.is-full,
  .form-field.is-full { grid-column: auto; }
}
</style>
