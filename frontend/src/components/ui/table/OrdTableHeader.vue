<script setup lang="ts">
</script>

<template>
  <thead class="ord-table-header">
    <tr>
      <slot />
    </tr>
  </thead>
</template>

<style scoped>
.ord-table-header {
  background: var(--ord-color-bg-subtle);
}

.ord-table-header :deep(th) {
  text-transform: uppercase;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.6px;
  color: var(--ord-color-gray-500);
}
</style>
