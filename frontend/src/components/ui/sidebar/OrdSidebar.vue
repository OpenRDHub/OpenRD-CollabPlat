<script setup lang="ts">
export interface SidebarItem {
  label: string
  icon?: string
  to?: string
  active?: boolean
}

defineProps<{
  items: SidebarItem[]
}>()

const emit = defineEmits<{
  select: [item: SidebarItem]
}>()
</script>

<template>
  <nav class="ord-sidebar">
    <button
      v-for="(item, idx) in items"
      :key="idx"
      class="ord-sidebar__item"
      :class="{ 'ord-sidebar__item--active': item.active }"
      @click="emit('select', item)"
    >
      <span v-if="item.icon" class="ord-sidebar__icon">{{ item.icon }}</span>
      <span class="ord-sidebar__label">{{ item.label }}</span>
    </button>
  </nav>
</template>

<style scoped>
.ord-sidebar {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px 0;
}

.ord-sidebar__item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border: none;
  background: none;
  border-radius: var(--ord-radius-sm);
  font-family: var(--ord-font-sans);
  font-size: 14px;
  font-weight: 500;
  color: var(--ord-color-gray-700);
  cursor: pointer;
  transition: all 150ms ease;
  text-align: left;
  width: 100%;
}

.ord-sidebar__item:hover {
  background: var(--ord-color-bg-subtle);
  color: var(--ord-color-black);
}

.ord-sidebar__item--active {
  background: rgba(20, 110, 245, 0.06);
  color: var(--ord-color-blue);
  font-weight: 600;
  border-left: 3px solid var(--ord-color-blue);
  padding-left: 13px;
}

.ord-sidebar__icon {
  flex-shrink: 0;
  width: 18px;
  text-align: center;
}

.ord-sidebar__label {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
