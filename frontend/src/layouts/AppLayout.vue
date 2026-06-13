<script setup lang="ts">
import { computed } from 'vue'
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

const menuItems = computed(() => {
  return getMenuByRole(auth.userRole).map((item) => ({
    ...item,
    active: route.path === item.to || route.path.startsWith(item.to + '/'),
  }))
})

function handleSidebarSelect(item: { to?: string }) {
  if (item.to) {
    router.push(item.to)
  }
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="app-layout">
    <OrdNavbar>
      <template #brand>
        <router-link to="/dashboard" class="app-layout__brand">
          <span class="app-layout__brand-open">Open</span><span class="app-layout__brand-rd">RD</span>
        </router-link>
      </template>
      <template #actions>
        <OrdDropdown>
          <template #trigger>
            <button class="app-layout__user-trigger">
              <OrdAvatar :name="auth.user?.nickname || ''" size="sm" />
              <span class="app-layout__username">{{ auth.user?.nickname }}</span>
            </button>
          </template>
          <OrdDropdownItem @click="router.push('/settings')">个人设置</OrdDropdownItem>
          <OrdDropdownItem @click="handleLogout">退出登录</OrdDropdownItem>
        </OrdDropdown>
      </template>
    </OrdNavbar>

    <aside class="app-layout__sidebar">
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
}

.app-layout__content {
  margin-top: var(--ord-nav-height);
  margin-left: 240px;
  padding: var(--ord-space-8);
  min-height: calc(100vh - var(--ord-nav-height));
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
</style>
