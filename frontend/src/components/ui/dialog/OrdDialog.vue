<script setup lang="ts">
import {
  DialogRoot,
  DialogPortal,
  DialogOverlay,
  DialogContent,
  DialogTitle,
  DialogDescription,
  DialogTrigger,
} from 'reka-ui'

defineProps<{
  title?: string
  description?: string
  ariaLabel?: string
  ariaDescription?: string
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
        <DialogTitle v-else class="ord-dialog__sr-only">
          {{ ariaLabel ?? '操作对话框' }}
        </DialogTitle>
        <DialogDescription v-if="description" class="ord-dialog__description">
          {{ description }}
        </DialogDescription>
        <DialogDescription v-else class="ord-dialog__sr-only">
          {{ ariaDescription ?? '请完成当前操作，或关闭对话框返回页面。' }}
        </DialogDescription>

        <slot />

        <div v-if="$slots.footer" class="ord-dialog__footer">
          <slot name="footer" />
        </div>
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
  width: min(760px, calc(100vw - 48px));
  max-height: calc(100dvh - 48px);
  overflow-y: auto;
  z-index: 1001;
  animation: ord-scale-in 200ms ease;
}

@media (max-width: 767px) {
  :global(.ord-dialog__content) {
    top: auto;
    bottom: 0;
    left: 0;
    transform: none;
    width: 100%;
    max-height: min(92dvh, 760px);
    padding: 24px var(--ord-page-padding) calc(20px + var(--ord-mobile-bottom-space));
    border-radius: var(--ord-radius-lg) var(--ord-radius-lg) 0 0;
    animation: ord-slide-up 200ms ease;
  }

  :global(.ord-dialog__footer) {
    position: sticky;
    bottom: calc(-1 * var(--ord-mobile-bottom-space));
    margin-inline: calc(-1 * var(--ord-page-padding));
    padding: 12px var(--ord-page-padding) var(--ord-mobile-bottom-space);
    background: var(--ord-color-white);
    border-top: 1px solid var(--ord-color-border);
  }

  :global(.ord-dialog__footer > *) {
    flex: 1;
  }
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

:global(.ord-dialog__sr-only) {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

:global(.ord-dialog__footer) {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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

@keyframes ord-slide-up {
  from {
    opacity: 0;
    transform: translateY(18px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
