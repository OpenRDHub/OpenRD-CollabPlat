<script setup lang="ts">
</script>

<template>
  <div class="ord-card">
    <slot />
  </div>
</template>

<style scoped>
.ord-card {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(216, 216, 216, 0.9);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  backdrop-filter: blur(16px);
  overflow: hidden;
}
</style>
