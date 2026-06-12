<script setup lang="ts">
import { TabsList } from 'reka-ui'
</script>

<template>
  <TabsList class="ord-tabs-list">
    <slot />
  </TabsList>
</template>

<style scoped>
.ord-tabs-list {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--ord-color-border);
}
</style>
