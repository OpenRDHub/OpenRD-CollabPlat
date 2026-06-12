<script setup lang="ts">
</script>

<template>
  <div class="ord-card-header">
    <slot />
  </div>
</template>

<style scoped>
.ord-card-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--ord-color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
