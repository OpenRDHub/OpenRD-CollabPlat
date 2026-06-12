<script setup lang="ts">
import { TabsTrigger } from 'reka-ui'

defineProps<{
  value: string
}>()
</script>

<template>
  <TabsTrigger :value="value" class="ord-tabs-trigger">
    <slot />
  </TabsTrigger>
</template>

<style scoped>
.ord-tabs-trigger {
  padding: 12px 20px;
  font-family: var(--ord-font-sans);
  font-size: 14px;
  font-weight: 500;
  color: var(--ord-color-gray-500);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 150ms ease;
}

.ord-tabs-trigger:hover {
  color: var(--ord-color-black);
}

.ord-tabs-trigger[data-state='active'] {
  color: var(--ord-color-blue);
  border-bottom-color: var(--ord-color-blue);
  font-weight: 600;
}
</style>
