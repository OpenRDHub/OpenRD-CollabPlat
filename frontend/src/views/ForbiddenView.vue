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
  <div class="forbidden-view">
    <OrdEmptyState>
      <template #title>403 - 无权访问</template>
      <template #description>你没有权限访问此页面，请联系管理员</template>
      <template #action>
        <OrdButton @click="leavePage">返回上一页</OrdButton>
      </template>
    </OrdEmptyState>
  </div>
</template>

<style scoped>
.forbidden-view {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: max(24px, env(safe-area-inset-top)) 16px max(24px, env(safe-area-inset-bottom));
  overflow-wrap: anywhere;
}

@media (max-width: 767px) {
  .forbidden-view :deep(.ord-empty-state) {
    width: 100%;
    padding: 32px 16px;
  }

  .forbidden-view :deep(.ord-button) {
    min-height: var(--ord-touch-target);
  }
}
</style>
