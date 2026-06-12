<script setup lang="ts">
</script>

<template>
  <div class="ord-empty-state">
    <div v-if="$slots.icon" class="ord-empty-state__icon">
      <slot name="icon" />
    </div>
    <div class="ord-empty-state__title">
      <slot name="title" />
    </div>
    <div class="ord-empty-state__description">
      <slot name="description" />
    </div>
    <div v-if="$slots.action" class="ord-empty-state__action">
      <slot name="action" />
    </div>
  </div>
</template>

<style scoped>
.ord-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 48px 24px;
  gap: 12px;
}

.ord-empty-state__icon {
  margin-bottom: 8px;
}

.ord-empty-state__title {
  font-size: 18px;
  font-weight: 600;
  color: var(--ord-color-black);
}

.ord-empty-state__description {
  font-size: 14px;
  color: var(--ord-color-gray-500);
  max-width: 400px;
}

.ord-empty-state__action {
  margin-top: 8px;
}
</style>
