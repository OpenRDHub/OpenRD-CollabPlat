<script setup lang="ts">
import {
  DialogRoot,
  DialogPortal,
  DialogOverlay,
  DialogContent,
  DialogTitle,
  DialogDescription,
  DialogClose,
  DialogTrigger,
} from 'reka-ui'

defineProps<{
  title?: string
  description?: string
}>()

const open = defineModel<boolean>({ default: false })
</script>

<template>
  <DialogRoot v-model:open="open">
    <DialogTrigger as-child>
      <slot name="trigger" />
    </DialogTrigger>

    <DialogPortal>
      <DialogOverlay class="ord-dialog__overlay" />
      <DialogContent class="ord-dialog__content">
        <DialogTitle v-if="title" class="ord-dialog__title">
          {{ title }}
        </DialogTitle>
        <DialogDescription v-if="description" class="ord-dialog__description">
          {{ description }}
        </DialogDescription>

        <slot />

        <div v-if="$slots.footer" class="ord-dialog__footer">
          <slot name="footer" />
        </div>

        <DialogClose class="ord-dialog__close" aria-label="Close">
          &#x2715;
        </DialogClose>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>

<style scoped>
:global(.ord-dialog__overlay) {
  position: fixed;
  inset: 0;
  background: rgba(8, 8, 8, 0.4);
  backdrop-filter: blur(4px);
  z-index: 1000;
  animation: ord-fade-in 150ms ease;
}

:global(.ord-dialog__content) {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: var(--ord-color-white);
  border-radius: var(--ord-radius-md);
  border: 1px solid var(--ord-color-border);
  box-shadow: var(--ord-shadow-cascade);
  padding: 32px;
  width: min(520px, calc(100vw - 48px));
  max-height: calc(100vh - 48px);
  overflow-y: auto;
  z-index: 1001;
  animation: ord-scale-in 200ms ease;
}

:global(.ord-dialog__title) {
  font-family: var(--ord-font-sans);
  font-size: 22px;
  font-weight: 600;
  color: var(--ord-color-black);
  margin: 0 0 8px;
}

:global(.ord-dialog__description) {
  font-family: var(--ord-font-sans);
  font-size: 15px;
  color: var(--ord-color-gray-500);
  margin: 0 0 24px;
}

:global(.ord-dialog__footer) {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:global(.ord-dialog__close) {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border: none;
  background: none;
  font-size: 20px;
  color: var(--ord-color-gray-500);
  cursor: pointer;
  border-radius: var(--ord-radius-sm);
  transition: background var(--ord-transition-base), color var(--ord-transition-base);
}

:global(.ord-dialog__close:hover) {
  background: var(--ord-color-bg-subtle);
  color: var(--ord-color-black);
}

@keyframes ord-fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes ord-scale-in {
  from {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}
</style>
