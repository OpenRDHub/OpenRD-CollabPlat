<script setup lang="ts">
import { ToastProvider, ToastViewport } from 'reka-ui'
</script>

<template>
  <ToastProvider>
    <slot />
    <ToastViewport class="ord-toast-viewport" />
  </ToastProvider>
</template>

<style scoped>
:global(.ord-toast-viewport) {
  position: fixed;
  bottom: 24px;
  right: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 2000;
  max-width: 380px;
  width: max-content;
}

@media (max-width: 767px) {
  :global(.ord-toast-viewport) {
    right: var(--ord-page-padding);
    bottom: calc(16px + var(--ord-mobile-bottom-space));
    left: var(--ord-page-padding);
    max-width: none;
    width: auto;
  }
}
</style>
