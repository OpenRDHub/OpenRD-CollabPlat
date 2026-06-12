<script setup lang="ts">
interface Props {
  value: number
  variant?: 'blue' | 'gradient'
}

withDefaults(defineProps<Props>(), {
  variant: 'blue',
})
</script>

<template>
  <div class="ord-progress">
    <div
      :class="['ord-progress__bar', `ord-progress__bar--${variant}`]"
      :style="{ width: `${Math.min(Math.max(value, 0), 100)}%` }"
    />
  </div>
</template>

<style scoped>
.ord-progress {
  width: 100%;
  height: 8px;
  background: var(--ord-color-bg-subtle);
  border-radius: var(--ord-radius-full);
  overflow: hidden;
}

.ord-progress__bar {
  height: 100%;
  border-radius: var(--ord-radius-full);
  transition: width 300ms ease;
}

.ord-progress__bar--blue {
  background: var(--ord-color-blue);
}

.ord-progress__bar--gradient {
  background: linear-gradient(90deg, var(--ord-color-yellow, #ffae13), var(--ord-color-blue));
}
</style>
