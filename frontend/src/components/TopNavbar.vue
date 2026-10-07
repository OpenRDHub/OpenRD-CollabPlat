<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { statsApi } from '@/api/stats'
import DemandSubmitDialog from '@/components/DemandSubmitDialog.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const showDemandDialog = ref(false)
const myTaskCount = ref(0)
const mobileMenuOpen = ref(false)
const profileOpen = ref(false)

const emit = defineEmits<{
  'demand-submitted': [data: { title: string; description: string }]
}>()

const handleDemandSuccess = (data: { title: string; description: string }) => {
  emit('demand-submitted', data)
}

const handleLogout = () => {
  auth.logout()
  mobileMenuOpen.value = false
  router.push('/login')
}

const RETURN_PATHS: Record<string, string> = {
  hall: '/hall',
  myDemands: '/my-demands',
  demandManagement: '/admin/demand-management',
  myTasks: '/my-tasks',
  taskManagement: '/admin/task-management',
}

function fallbackReturnPath() {
  if (route.name === 'demand-detail') {
    return ['operator', 'super_admin'].includes(auth.userRole) ? '/admin/demand-management' : '/my-demands'
  }
  if (route.name === 'task-detail') {
    return ['operator', 'super_admin'].includes(auth.userRole) ? '/admin/task-management' : '/my-tasks'
  }
  if (route.name === 'team-detail' && typeof route.params.taskId === 'string') {
    return `/tasks/${route.params.taskId}`
  }
  return '/workbench'
}

function handleReturn() {
  closeMobileMenu()
  const source = route.query.from
  const sourcePath = typeof source === 'string' ? RETURN_PATHS[source] : undefined
  if (sourcePath) {
    router.push(sourcePath)
    return
  }

  const previousPath = window.history.state?.back
  const isSafeInternalPath = typeof previousPath === 'string'
    && previousPath.startsWith('/')
    && !/^\/(login|register|forgot-password|onboarding)(\/|\?|$)/.test(previousPath)

  if (isSafeInternalPath) {
    router.back()
    return
  }
  router.push(fallbackReturnPath())
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
  profileOpen.value = false
}

onMounted(() => {
  statsApi.getMyStats().then(res => {
    if (res.data) myTaskCount.value = res.data.task_count
  }).catch(() => {})
})
</script>

<template>
  <nav class="top-nav">
    <div class="top-nav-inner">
      <router-link to="/hall" class="brand-row">
        <div class="brand-mark">RD</div>
        <div>
          <div class="brand-name">OpenRD 开源社区协作平台</div>
          <span class="brand-caption">Rare Disease Open Collaboration</span>
        </div>
      </router-link>

      <button
        class="mobile-menu-toggle"
        type="button"
        aria-label="打开导航菜单"
        :aria-expanded="mobileMenuOpen"
        @click="mobileMenuOpen = !mobileMenuOpen"
      >
        <span aria-hidden="true">☰</span>
      </button>

      <div class="nav-actions" :class="{ 'nav-actions--open': mobileMenuOpen }">
        <button type="button" class="ghost-button" @click="handleReturn">
          返回
        </button>
        <router-link to="/hall" class="ghost-button" @click="closeMobileMenu">
          前往大厅
        </router-link>
        <button class="primary-button" type="button" @click="showDemandDialog = true; closeMobileMenu()">
          提需求
        </button>
        <router-link to="/workbench" class="ghost-button" @click="closeMobileMenu">
          工作台
        </router-link>

        <div class="profile-trigger" :class="{ 'profile-trigger--open': profileOpen }">
          <button class="profile-button" type="button" @click="profileOpen = !profileOpen">
            <span class="avatar">{{ auth.user?.nickname?.charAt(0) || '用' }}</span>
            <span class="profile-name">{{ auth.user?.nickname || '用户' }}</span>
          </button>
          <section class="profile-card" @click="router.push('/profile')">
            <div class="profile-card-header">
              <span class="avatar">{{ auth.user?.nickname?.charAt(0) || '用' }}</span>
              <div>
                <h3>{{ auth.user?.nickname || '用户' }}</h3>
                <p>{{ auth.user?.role || '需求者' }} · {{ auth.user?.location || '位置未设置' }}</p>
              </div>
            </div>
            <div class="profile-meta">
              <div><span>平台号</span><strong>{{ auth.user?.platform_id || '-' }}</strong></div>
              <div><span>参与任务</span><strong>{{ myTaskCount }}</strong></div>
              <div><span>角色</span><strong>{{ auth.user?.role || '-' }}</strong></div>
              <div><span>所在地</span><strong>{{ auth.user?.province || '未设置' }}</strong></div>
            </div>
            <a class="logout-link" href="#" @click.stop.prevent="handleLogout">
              退出登录
            </a>
          </section>
        </div>
      </div>
    </div>

    <button
      v-if="mobileMenuOpen"
      class="mobile-menu-backdrop"
      type="button"
      aria-label="关闭导航菜单"
      @click="closeMobileMenu"
    />

    <DemandSubmitDialog v-model:open="showDemandDialog" @submit-success="handleDemandSuccess" />
  </nav>
</template>

<style scoped>
.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 20;
  min-height: 76px;
  padding: 0 32px;
  background: rgba(255, 255, 255, 0.94);
  border-bottom: 1px solid rgba(216, 216, 216, 0.86);
  box-shadow: 0 18px 40px rgba(8, 8, 8, 0.08);
  backdrop-filter: blur(16px);
}

.top-nav-inner {
  width: min(1460px, 100%);
  min-height: 76px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 16px 0;
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
  border-radius: 4px;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -0.3px;
}

.brand-name {
  color: var(--ord-color-black);
  font-size: 20px;
  font-weight: 600;
  line-height: 1.15;
  letter-spacing: -0.2px;
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

.nav-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
  z-index: 2;
}

.mobile-menu-toggle,
.mobile-menu-backdrop {
  display: none;
}

.primary-button,
.ghost-button {
  height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  transition: transform 180ms ease, background 180ms ease, border-color 180ms ease, color 180ms ease, box-shadow 180ms ease;
}

.primary-button {
  padding: 0 18px;
  color: var(--ord-color-white);
  background: var(--ord-color-blue);
  border: 0;
}

.primary-button:hover {
  background: var(--ord-color-blue-hover);
  box-shadow: 0 14px 28px rgba(20, 110, 245, 0.22);
  transform: translateX(6px);
}

.ghost-button {
  padding: 0 16px;
  color: var(--ord-color-black);
  background: var(--ord-color-white);
  border: 1px solid var(--ord-color-border);
}

.ghost-button:hover {
  color: var(--ord-color-blue);
  border-color: var(--ord-color-blue);
  transform: translateX(6px);
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
  border-radius: 4px;
  cursor: pointer;
  transition: transform 180ms ease, border-color 180ms ease, color 180ms ease;
}

.profile-button:hover {
  color: var(--ord-color-blue);
  border-color: var(--ord-color-blue);
  transform: translateX(6px);
}

.avatar {
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  color: var(--ord-color-white);
  background: var(--ord-color-black);
  border-radius: 50%;
  font-size: 11px;
  font-weight: 700;
}

.profile-name {
  font-size: 14px;
  font-weight: 600;
}

.profile-card {
  cursor: pointer;
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  width: 260px;
  padding: 16px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-4px);
  background: var(--ord-color-white);
  border: 1px solid var(--ord-color-border);
  border-radius: 8px;
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
  line-height: 1.25;
}

.profile-card p {
  margin: 4px 0 0;
  color: var(--ord-color-gray-500);
  font-size: 13px;
  line-height: 1.4;
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
  border-radius: 4px;
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
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 36px;
  margin-top: 12px;
  color: var(--ord-color-red);
  background: rgba(238, 29, 54, 0.08);
  border: 1px solid rgba(238, 29, 54, 0.18);
  border-radius: 4px;
  font-size: 13px;
  font-weight: 650;
  text-decoration: none;
  transition: transform 180ms ease, background 180ms ease, border-color 180ms ease;
}

.logout-link:hover {
  background: rgba(238, 29, 54, 0.12);
  border-color: rgba(238, 29, 54, 0.34);
  transform: translateX(6px);
}

@media (max-width: 1023px) and (min-width: 768px) {
  .top-nav-inner {
    gap: 12px;
    padding-inline: 0;
  }

  .brand-name {
    max-width: 260px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 18px;
  }

  .brand-caption {
    display: none;
  }

  .nav-actions {
    gap: 6px;
  }

  .primary-button,
  .ghost-button,
  .profile-button {
    padding-inline: 10px;
    font-size: 13px;
  }
}

@media (max-width: 520px) {
  .top-nav {
    padding-left: 16px;
    padding-right: 16px;
  }

  .primary-button,
  .ghost-button,
  .profile-trigger {
    flex: 1;
  }

  .primary-button,
  .ghost-button,
  .profile-button {
    width: 100%;
  }

  .profile-card {
    right: auto;
    left: 0;
    width: min(260px, calc(100vw - 32px));
  }
}

@media (max-width: 767px) {
  .top-nav {
    min-height: var(--ord-nav-height);
    padding: 0 var(--ord-page-padding);
  }

  .top-nav-inner {
    min-height: var(--ord-nav-height);
    height: var(--ord-nav-height);
    padding: 8px 0;
    flex-direction: row;
    align-items: center;
  }

  .brand-row {
    min-width: 0;
    gap: 8px;
  }

  .brand-mark {
    width: 36px;
    height: 36px;
  }

  .brand-name {
    max-width: min(58vw, 230px);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 16px;
  }

  .brand-caption {
    display: none;
  }

  .mobile-menu-toggle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 var(--ord-touch-target);
    width: var(--ord-touch-target);
    height: var(--ord-touch-target);
    margin-left: auto;
    color: var(--ord-color-gray-700);
    background: var(--ord-color-white);
    border: 1px solid var(--ord-color-border);
    border-radius: var(--ord-radius-sm);
    font-size: 20px;
    position: relative;
    z-index: 3;
  }

  .nav-actions {
    display: none;
    position: absolute;
    top: calc(var(--ord-nav-height) + 8px);
    right: var(--ord-page-padding);
    left: var(--ord-page-padding);
    width: auto;
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    padding: 12px;
    background: var(--ord-color-white);
    border: 1px solid var(--ord-color-border);
    border-radius: var(--ord-radius-md);
    box-shadow: var(--ord-shadow-cascade);
  }

  .nav-actions--open {
    display: flex;
  }

  .primary-button,
  .ghost-button,
  .profile-trigger,
  .profile-button {
    width: 100%;
    min-height: var(--ord-touch-target);
  }

  .profile-trigger {
    display: block;
  }

  .profile-card {
    display: none;
    position: static;
    width: 100%;
    margin-top: 8px;
    opacity: 1;
    visibility: visible;
    transform: none;
  }

  .profile-trigger--open .profile-card {
    display: block;
  }

  .mobile-menu-backdrop {
    display: block;
    position: fixed;
    inset: var(--ord-nav-height) 0 0;
    z-index: 1;
    background: rgba(8, 8, 8, 0.18);
  }
}
</style>
