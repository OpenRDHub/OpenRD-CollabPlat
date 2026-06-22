<script setup lang="ts">
import { ToastRoot, ToastTitle, ToastDescription } from 'reka-ui'

defineProps<{
  title: string
  description?: string
  variant?: 'default' | 'success' | 'error'
}>()

const emit = defineEmits<{
  close: []
}>()

const handleOpenChange = (val: boolean) => {
  if (!val) {
    emit('close')
  }
}
</script>

<template>
  <ToastRoot
    class="ord-toast"
    :class="[`ord-toast--${variant ?? 'default'}`]"
    @update:open="handleOpenChange"
  >
    <ToastTitle class="ord-toast__title">{{ title }}</ToastTitle>
    <ToastDescription v-if="description" class="ord-toast__description">
      {{ description }}
    </ToastDescription>
  </ToastRoot>
</template>

<style scoped>
:global(.ord-toast) {
  background: var(--ord-color-white);
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-sm);
  box-shadow: var(--ord-shadow-cascade);
  padding: 10px 18px;
  display: flex;
  gap: 10px;
  align-items: center;
  white-space: nowrap;
  animation: ord-toast-slide-in 200ms ease;
}

:global(.ord-toast--success) {
  border-left: 3px solid #00d722;
}

:global(.ord-toast--error) {
  border-left: 3px solid #ee1d36;
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
  margin: 0;
}

@keyframes ord-toast-slide-in {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>
