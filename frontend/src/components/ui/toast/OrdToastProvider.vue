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
</style>
