<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  OrdNavbar,
  OrdSidebar,
  OrdAvatar,
  OrdDropdown,
  OrdDropdownItem,
} from '@/components/ui'
import { useAuthStore } from '@/stores/auth'
import { getMenuByRole } from '@/router/menus'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const sidebarOpen = ref(false)

const menuItems = computed(() => {
  return getMenuByRole(auth.userRole).map((item) => ({
    ...item,
    active: route.path === item.to || route.path.startsWith(item.to + '/'),
  }))
})

function handleSidebarSelect(item: { to?: string }) {
  sidebarOpen.value = false
  if (item.to) {
    router.push(item.to)
  }
}

function closeSidebar() {
  sidebarOpen.value = false
}

watch(sidebarOpen, (open) => {
  document.body.classList.toggle('ord-sidebar-open', open)
})

watch(() => route.fullPath, closeSidebar)

onUnmounted(() => {
  document.body.classList.remove('ord-sidebar-open')
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="app-layout">
    <OrdNavbar>
      <template #brand>
        <div class="app-layout__brand-group">
          <button
            class="app-layout__menu-button"
            type="button"
            aria-label="打开导航菜单"
            :aria-expanded="sidebarOpen"
            @click="sidebarOpen = !sidebarOpen"
          >
            <span aria-hidden="true">☰</span>
          </button>
          <router-link to="/dashboard" class="app-layout__brand">
            <span class="app-layout__brand-open">Open</span><span class="app-layout__brand-rd">RD</span>
          </router-link>
        </div>
      </template>
      <template #actions>
        <OrdDropdown>
          <template #trigger>
            <button class="app-layout__user-trigger">
              <OrdAvatar :name="auth.user?.nickname || ''" size="sm" />
              <span class="app-layout__username">{{ auth.user?.nickname }}</span>
            </button>
          </template>
          <OrdDropdownItem @click="router.push('/profile')">个人设置</OrdDropdownItem>
          <OrdDropdownItem @click="handleLogout">退出登录</OrdDropdownItem>
        </OrdDropdown>
      </template>
    </OrdNavbar>

    <button
      v-if="sidebarOpen"
      class="app-layout__sidebar-overlay"
      type="button"
      aria-label="关闭导航菜单"
      @click="closeSidebar"
    />

    <aside class="app-layout__sidebar" :class="{ 'app-layout__sidebar--open': sidebarOpen }">
      <button
        class="app-layout__sidebar-close"
        type="button"
        aria-label="关闭导航菜单"
        @click="closeSidebar"
      >
        ×
      </button>
      <OrdSidebar :items="menuItems" @select="handleSidebarSelect" />
    </aside>

    <main class="app-layout__content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-layout__sidebar {
  position: fixed;
  top: var(--ord-nav-height);
  left: 0;
  bottom: 0;
  width: 240px;
  border-right: 1px solid var(--ord-color-border);
  background: var(--ord-color-white);
  overflow-y: auto;
  z-index: 50;
  transition: transform var(--ord-transition-base), box-shadow var(--ord-transition-base);
}

.app-layout__sidebar-overlay,
.app-layout__sidebar-close,
.app-layout__menu-button {
  display: none;
}

.app-layout__content {
  margin-top: var(--ord-nav-height);
  margin-left: 240px;
  padding: var(--ord-space-8);
  min-height: calc(100dvh - var(--ord-nav-height));
}

.app-layout__brand-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.app-layout__brand {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: -0.5px;
}

.app-layout__brand-open {
  color: var(--ord-color-black);
}

.app-layout__brand-rd {
  color: var(--ord-color-blue);
}

.app-layout__user-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: var(--ord-radius-sm);
  transition: background var(--ord-transition-base);
}

.app-layout__user-trigger:hover {
  background: var(--ord-color-bg-subtle);
}

.app-layout__username {
  font-size: 14px;
  font-weight: 500;
  color: var(--ord-color-gray-700);
}

@media (max-width: 767px) {
  .app-layout__menu-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: var(--ord-touch-target);
    height: var(--ord-touch-target);
    color: var(--ord-color-gray-700);
    border-radius: var(--ord-radius-sm);
    font-size: 22px;
  }

  .app-layout__menu-button:focus-visible,
  .app-layout__menu-button:hover {
    background: var(--ord-color-bg-subtle);
  }

  .app-layout__sidebar {
    width: min(280px, calc(100vw - 48px));
    transform: translateX(-105%);
    box-shadow: none;
    z-index: 120;
  }

  .app-layout__sidebar--open {
    transform: translateX(0);
    box-shadow: var(--ord-shadow-cascade);
  }

  .app-layout__sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 110;
    background: rgba(8, 8, 8, 0.35);
  }

  .app-layout__sidebar-close {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: var(--ord-touch-target);
    height: var(--ord-touch-target);
    margin: 8px 8px 0 auto;
    color: var(--ord-color-gray-700);
    font-size: 28px;
    line-height: 1;
  }

  .app-layout__content {
    margin-top: 0;
    margin-left: 0;
    padding: calc(var(--ord-nav-height) + var(--ord-page-padding)) var(--ord-page-padding) calc(var(--ord-page-padding) + var(--ord-mobile-bottom-space));
  }

  .app-layout__username {
    display: none;
  }
}
</style>
