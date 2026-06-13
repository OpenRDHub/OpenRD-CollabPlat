<script setup lang="ts">
import { DropdownMenuItem } from 'reka-ui'
</script>

<template>
  <DropdownMenuItem class="ord-dropdown-item">
    <slot />
  </DropdownMenuItem>
</template>

<style scoped>
:global(.ord-dropdown-item) {
  padding: 10px 14px;
  border-radius: var(--ord-radius-sm);
  font-family: var(--ord-font-sans);
  font-size: 14px;
  color: var(--ord-color-black);
  cursor: pointer;
  transition: all 150ms ease;
  outline: none;
}

:global(.ord-dropdown-item:hover),
:global(.ord-dropdown-item[data-highlighted]) {
  background: var(--ord-color-bg-subtle);
  color: var(--ord-color-blue);
}
</style>
