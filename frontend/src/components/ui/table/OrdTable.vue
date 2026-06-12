<script setup lang="ts">
</script>

<template>
  <div class="ord-table">
    <table class="ord-table__inner">
      <slot />
    </table>
  </div>
</template>

<style scoped>
.ord-table {
  width: 100%;
  overflow-x: auto;
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-md);
}

.ord-table__inner {
  width: 100%;
  border-collapse: collapse;
}
</style>
