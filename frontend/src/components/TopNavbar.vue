<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import DemandSubmitDialog from '@/components/DemandSubmitDialog.vue'

const router = useRouter()
const auth = useAuthStore()
const showDemandDialog = ref(false)

const emit = defineEmits<{
  'demand-submitted': [data: { title: string; description: string }]
}>()

const handleDemandSuccess = (data: { title: string; description: string }) => {
  emit('demand-submitted', data)
}

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}
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

      <div class="nav-actions">
        <router-link to="/workbench" class="ghost-button">
          返回
        </router-link>
        <router-link to="/hall" class="ghost-button">
          前往大厅
        </router-link>
        <button class="primary-button" type="button" @click="showDemandDialog = true">
          提需求
        </button>
        <router-link to="/workbench" class="ghost-button">
          工作台
        </router-link>

        <div class="profile-trigger">
          <button class="profile-button" type="button">
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
              <div><span>贡献积分</span><strong>1,280</strong></div>
              <div><span>参与任务</span><strong>12</strong></div>
              <div><span>角色等级</span><strong>中级</strong></div>
              <div><span>初始化</span><strong>已完成</strong></div>
            </div>
            <a class="logout-link" href="#" @click.stop.prevent="handleLogout">
              退出登录
            </a>
          </section>
        </div>
      </div>
    </div>

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

@media (max-width: 900px) {
  .top-nav-inner {
    align-items: flex-start;
    flex-direction: column;
    padding: 16px 0;
  }

  .nav-actions {
    width: 100%;
    justify-content: space-between;
    flex-wrap: wrap;
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
</style>
