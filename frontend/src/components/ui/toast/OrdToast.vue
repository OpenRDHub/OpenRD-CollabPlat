<script setup lang="ts">
import { ToastRoot, ToastTitle, ToastDescription, ToastClose } from 'reka-ui'

defineProps<{
  title: string
  description?: string
  variant?: 'default' | 'success' | 'error'
}>()

defineEmits<{
  close: []
}>()
</script>

<template>
  <ToastRoot
    class="ord-toast"
    :class="[`ord-toast--${variant ?? 'default'}`]"
    @update:open="(val: boolean) => { if (!val) $emit('close') }"
  >
    <div class="ord-toast__body">
      <ToastTitle class="ord-toast__title">{{ title }}</ToastTitle>
      <ToastDescription v-if="description" class="ord-toast__description">
        {{ description }}
      </ToastDescription>
    </div>
    <ToastClose class="ord-toast__close" aria-label="关闭">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path d="M11 3L3 11M3 3l8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
    </ToastClose>
  </ToastRoot>
</template>

<style scoped>
:global(.ord-toast) {
  background: var(--ord-color-white);
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  padding: 16px 20px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
  animation: ord-toast-slide-in 200ms ease;
}

:global(.ord-toast--success) {
  border-left: 3px solid #00d722;
}

:global(.ord-toast--error) {
  border-left: 3px solid #ee1d36;
}

:global(.ord-toast__body) {
  flex: 1;
  min-width: 0;
}

:global(.ord-toast__title) {
  font-family: var(--ord-font-sans);
  font-size: 14px;
  font-weight: 600;
  color: var(--ord-color-black);
  margin: 0;
}

:global(.ord-toast__description) {
  font-family: var(--ord-font-sans);
  font-size: 13px;
  color: var(--ord-color-gray-500);
  margin-top: 4px;
}

:global(.ord-toast__close) {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  color: var(--ord-color-gray-300);
  cursor: pointer;
  border-radius: var(--ord-radius-sm);
  transition: all 150ms ease;
}

:global(.ord-toast__close:hover) {
  color: var(--ord-color-black);
  background: var(--ord-color-bg-subtle);
}

@keyframes ord-toast-slide-in {
  from {
    opacity: 0;
    transform: translateY(-100%);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
