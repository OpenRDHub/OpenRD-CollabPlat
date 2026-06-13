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
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 2000;
  max-width: 380px;
  width: max-content;
}
</style>
