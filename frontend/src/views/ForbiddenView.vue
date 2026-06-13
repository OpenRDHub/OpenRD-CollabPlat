<script setup lang="ts">
import { useRouter } from 'vue-router'
import { OrdButton, OrdEmptyState } from '@/components/ui'

const router = useRouter()
</script>

<template>
  <div class="forbidden-view">
    <OrdEmptyState>
      <template #title>403 - 无权访问</template>
      <template #description>你没有权限访问此页面，请联系管理员</template>
      <template #action>
        <OrdButton @click="router.push('/dashboard')">返回工作台</OrdButton>
      </template>
    </OrdEmptyState>
  </div>
</template>

<style scoped>
.forbidden-view {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
