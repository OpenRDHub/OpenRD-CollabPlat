<script setup lang="ts">
import { useRouter } from 'vue-router'
import { OrdButton, OrdEmptyState } from '@/components/ui'

const router = useRouter()

function leavePage() {
  const previous = window.history.state?.back
  if (typeof previous === 'string' && previous !== router.currentRoute.value.fullPath) {
    router.back()
    return
  }
  router.replace('/workbench')
}
</script>

<template>
  <div class="not-found-view">
    <OrdEmptyState>
      <template #title>404 - 页面不存在</template>
      <template #description>你访问的页面已被移除或地址有误</template>
      <template #action>
        <OrdButton @click="leavePage">返回上一页</OrdButton>
      </template>
    </OrdEmptyState>
  </div>
</template>

<style scoped>
.not-found-view {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: max(24px, env(safe-area-inset-top)) 16px max(24px, env(safe-area-inset-bottom));
  overflow-wrap: anywhere;
}

@media (max-width: 767px) {
  .not-found-view :deep(.ord-empty-state) {
    width: 100%;
    padding: 32px 16px;
  }

  .not-found-view :deep(.ord-button) {
    min-height: var(--ord-touch-target);
  }
}
</style>
