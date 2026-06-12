<script setup lang="ts">
defineProps<{
  header?: boolean
}>()
</script>

<template>
  <th v-if="header" class="ord-table-cell">
    <slot />
  </th>
  <td v-else class="ord-table-cell">
    <slot />
  </td>
</template>

<style scoped>
.ord-table-cell {
  padding: 14px 16px;
  text-align: left;
  font-family: var(--ord-font-sans);
  font-size: 14px;
}
</style>
