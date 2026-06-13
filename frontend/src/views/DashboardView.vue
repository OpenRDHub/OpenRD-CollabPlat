<script setup lang="ts">
import { OrdCard, OrdCardHeader, OrdCardContent } from '@/components/ui'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>

<template>
  <div class="dashboard-view">
    <h1 class="dashboard-view__title">工作台</h1>
    <p class="dashboard-view__welcome">欢迎回来，{{ auth.user?.nickname }}</p>
    <div class="dashboard-view__grid">
      <OrdCard>
        <OrdCardHeader>快捷操作</OrdCardHeader>
        <OrdCardContent>
          <p class="dashboard-view__placeholder">功能开发中...</p>
        </OrdCardContent>
      </OrdCard>
      <OrdCard>
        <OrdCardHeader>最近动态</OrdCardHeader>
        <OrdCardContent>
          <p class="dashboard-view__placeholder">功能开发中...</p>
        </OrdCardContent>
      </OrdCard>
    </div>
  </div>
</template>

<style scoped>
.dashboard-view__title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: var(--ord-space-1);
}

.dashboard-view__welcome {
  font-size: 14px;
  color: var(--ord-color-gray-500);
  margin-bottom: var(--ord-space-8);
}

.dashboard-view__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: var(--ord-space-6);
}

.dashboard-view__placeholder {
  font-size: 14px;
  color: var(--ord-color-gray-300);
  padding: var(--ord-space-6) 0;
  text-align: center;
}
</style>
