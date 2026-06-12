<script setup lang="ts">
import {
  TooltipRoot,
  TooltipTrigger,
  TooltipPortal,
  TooltipContent,
  TooltipArrow,
  TooltipProvider,
} from 'reka-ui'

interface Props {
  content: string
  side?: 'top' | 'bottom' | 'left' | 'right'
  delayDuration?: number
}

withDefaults(defineProps<Props>(), {
  side: 'top',
  delayDuration: 200,
})
</script>

<template>
  <TooltipProvider>
    <TooltipRoot :delay-duration="delayDuration">
      <TooltipTrigger as-child>
        <slot />
      </TooltipTrigger>
      <TooltipPortal>
        <TooltipContent :side="side" class="ord-tooltip__content" :side-offset="6">
          {{ content }}
          <TooltipArrow class="ord-tooltip__arrow" />
        </TooltipContent>
      </TooltipPortal>
    </TooltipRoot>
  </TooltipProvider>
</template>

<style scoped>
.ord-tooltip__content {
  background: var(--ord-color-gray-800, #222222);
  color: var(--ord-color-white);
  padding: 6px 12px;
  border-radius: var(--ord-radius-sm);
  font-size: 13px;
  max-width: 260px;
  z-index: 2000;
  animation: ord-tooltip-fade-in 100ms ease;
  line-height: 1.4;
}

.ord-tooltip__arrow {
  fill: var(--ord-color-gray-800, #222222);
}

@keyframes ord-tooltip-fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
