<script setup lang="ts">
defineProps<{
  variant?: 'blue' | 'purple' | 'green' | 'orange' | 'pink' | 'red' | 'gray'
}>()
</script>

<template>
  <span class="ord-badge" :class="`ord-badge--${variant ?? 'blue'}`">
    <slot />
  </span>
</template>

<style scoped>
.ord-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: var(--ord-radius-sm);
  font-family: var(--ord-font-sans);
  font-size: 12.8px;
  font-weight: 550;
  line-height: 1.2;
}

.ord-badge--blue {
  background: var(--ord-color-soft-blue);
  color: var(--ord-color-blue);
}
.ord-badge--purple {
  background: var(--ord-color-soft-purple);
  color: var(--ord-color-purple);
}
.ord-badge--green {
  background: var(--ord-color-soft-green);
  color: var(--ord-color-green);
}
.ord-badge--orange {
  background: var(--ord-color-soft-orange);
  color: var(--ord-color-orange);
}
.ord-badge--pink {
  background: var(--ord-color-soft-pink);
  color: var(--ord-color-pink);
}
.ord-badge--red {
  background: var(--ord-color-soft-red);
  color: var(--ord-color-red);
}
.ord-badge--gray {
  background: var(--ord-color-bg-subtle);
  color: var(--ord-color-gray-500);
}
</style>
