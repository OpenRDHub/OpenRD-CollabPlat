<script setup lang="ts">
import {
  SelectRoot,
  SelectTrigger,
  SelectPortal,
  SelectContent,
  SelectViewport,
  SelectItem,
  SelectItemText,
  SelectValue,
  SelectIcon,
} from 'reka-ui'

defineProps<{
  options: { value: string; label: string }[]
  placeholder?: string
}>()

const modelValue = defineModel<string>()
</script>

<template>
  <SelectRoot v-model="modelValue">
    <SelectTrigger class="ord-select__trigger">
      <SelectValue :placeholder="placeholder ?? '请选择'" />
      <SelectIcon class="ord-select__icon">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
          <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </SelectIcon>
    </SelectTrigger>
    <SelectPortal>
      <SelectContent class="ord-select__content" position="popper" :side-offset="6">
        <SelectViewport>
          <SelectItem
            v-for="option in options"
            :key="option.value"
            :value="option.value"
            class="ord-select__item"
          >
            <SelectItemText>{{ option.label }}</SelectItemText>
          </SelectItem>
        </SelectViewport>
      </SelectContent>
    </SelectPortal>
  </SelectRoot>
</template>

<style scoped>
.ord-select__trigger {
  height: 42px;
  min-width: 150px;
  padding: 0 14px;
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-sm);
  font-family: var(--ord-font-sans);
  font-size: 15px;
  color: var(--ord-color-black);
  background: var(--ord-color-white);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  width: auto;
  cursor: pointer;
  transition: border-color var(--ord-transition-base);
  outline: none;
}

.ord-select__trigger:hover {
  border-color: var(--ord-color-border-hover);
}

.ord-select__trigger:focus {
  border-color: var(--ord-color-blue);
}

.ord-select__icon {
  color: var(--ord-color-gray-500);
  flex-shrink: 0;
}

:global(.ord-select__content) {
  background: var(--ord-color-white);
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
  padding: 6px;
  min-width: var(--reka-popper-anchor-width);
  max-height: 260px;
  overflow-y: auto;
  z-index: 1100;
}

:global(.ord-select__item) {
  padding: 10px 14px;
  border-radius: var(--ord-radius-sm);
  font-family: var(--ord-font-sans);
  font-size: 14px;
  color: var(--ord-color-black);
  cursor: pointer;
  outline: none;
  transition: all 150ms ease;
}

:global(.ord-select__item[data-highlighted]) {
  background: var(--ord-color-bg-subtle);
  color: var(--ord-color-blue);
}

:global(.ord-select__item[data-state='checked']) {
  font-weight: 600;
  color: var(--ord-color-blue);
}
</style>
