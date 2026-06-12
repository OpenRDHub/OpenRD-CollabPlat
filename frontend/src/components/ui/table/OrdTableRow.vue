<script setup lang="ts">
</script>

<template>
  <tr class="ord-table-row">
    <slot />
  </tr>
</template>

<style scoped>
.ord-table-row {
  border-bottom: 1px solid var(--ord-color-border);
  transition: background var(--ord-transition-base);
}

.ord-table-row:hover {
  background: var(--ord-color-bg-subtle);
}

.ord-table-row:last-child {
  border-bottom: none;
}
</style>
