<script setup lang="ts">
import { TabsContent } from 'reka-ui'

defineProps<{
  value: string
}>()
</script>

<template>
  <TabsContent :value="value" class="ord-tabs-content">
    <slot />
  </TabsContent>
</template>

<style scoped>
.ord-tabs-content {
  padding-top: 20px;
}
</style>
