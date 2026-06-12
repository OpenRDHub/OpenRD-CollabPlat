<script setup lang="ts">
defineProps<{
  variant?: 'primary' | 'ghost' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
}>()
</script>

<template>
  <button
    class="ord-button"
    :class="[
      `ord-button--${variant ?? 'primary'}`,
      `ord-button--${size ?? 'md'}`,
      { 'ord-button--disabled': disabled, 'ord-button--loading': loading },
    ]"
    :disabled="disabled || loading"
  >
    <span v-if="loading" class="ord-button__spinner" />
    <slot />
  </button>
</template>

<style scoped>
.ord-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 42px;
  padding: 0 16px;
  border-radius: var(--ord-radius-sm);
  font-family: var(--ord-font-sans);
  font-size: 15px;
  font-weight: 600;
  border: 1px solid transparent;
  cursor: pointer;
  transition: transform var(--ord-transition-base), background var(--ord-transition-base), border-color var(--ord-transition-base), color var(--ord-transition-base), box-shadow var(--ord-transition-base);
}

.ord-button:hover:not(:disabled) {
  transform: translateX(6px);
}

.ord-button--disabled {
  opacity: 0.5;
  pointer-events: none;
}

/* Primary */
.ord-button--primary {
  color: var(--ord-color-white);
  background: var(--ord-color-blue);
  border-color: var(--ord-color-blue);
}
.ord-button--primary:hover:not(:disabled) {
  background: var(--ord-color-blue-hover);
  border-color: var(--ord-color-blue-hover);
  box-shadow: var(--ord-shadow-button);
}

/* Ghost */
.ord-button--ghost {
  color: var(--ord-color-black);
  background: var(--ord-color-white);
  border-color: var(--ord-color-border);
}
.ord-button--ghost:hover:not(:disabled) {
  color: var(--ord-color-blue);
  border-color: var(--ord-color-blue);
}

/* Outline */
.ord-button--outline {
  color: var(--ord-color-blue);
  background: transparent;
  border-color: var(--ord-color-blue);
}

/* Sizes */
.ord-button--sm {
  min-height: 32px;
  padding: 0 12px;
  font-size: 13px;
}
.ord-button--lg {
  min-height: 48px;
  padding: 0 24px;
  font-size: 16px;
}

/* Loading spinner */
.ord-button__spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: ord-spin 600ms linear infinite;
}

@keyframes ord-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
