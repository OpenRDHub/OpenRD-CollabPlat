<script setup lang="ts">
import { TabsRoot } from 'reka-ui'

const modelValue = defineModel<string>()

defineProps<{
  defaultValue?: string
}>()
</script>

<template>
  <TabsRoot v-model="modelValue" :default-value="defaultValue" class="ord-tabs">
    <slot />
  </TabsRoot>
</template>

<style scoped>
.ord-tabs {
  width: 100%;
}
</style>
