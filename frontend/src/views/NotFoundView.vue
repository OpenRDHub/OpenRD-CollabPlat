<script setup lang="ts">
import { useRouter } from 'vue-router'
import { OrdButton, OrdEmptyState } from '@/components/ui'

const router = useRouter()
</script>

<template>
  <div class="not-found-view">
    <OrdEmptyState>
      <template #title>404 - 页面不存在</template>
      <template #description>你访问的页面已被移除或地址有误</template>
      <template #action>
        <OrdButton @click="router.push('/dashboard')">返回工作台</OrdButton>
      </template>
    </OrdEmptyState>
  </div>
</template>

<style scoped>
.not-found-view {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
