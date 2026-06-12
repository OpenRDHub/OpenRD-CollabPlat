<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  total: number
  pageSize?: number
}>(), {
  pageSize: 10,
})

const currentPage = defineModel<number>('currentPage', { default: 1 })

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))

const visiblePages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)

  if (current <= 4) return [1, 2, 3, 4, 5, -1, total]
  if (current >= total - 3) return [1, -1, total - 4, total - 3, total - 2, total - 1, total]
  return [1, -1, current - 1, current, current + 1, -2, total]
})

function goTo(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}
</script>

<template>
  <nav class="ord-pagination" aria-label="分页">
    <button
      class="ord-pagination__btn"
      :class="{ 'ord-pagination__btn--disabled': currentPage <= 1 }"
      :disabled="currentPage <= 1"
      @click="goTo(currentPage - 1)"
    >
      &lt;
    </button>
    <template v-for="page in visiblePages" :key="page">
      <span v-if="page < 0" class="ord-pagination__ellipsis">...</span>
      <button
        v-else
        class="ord-pagination__btn"
        :class="{ 'ord-pagination__btn--active': page === currentPage }"
        @click="goTo(page)"
      >
        {{ page }}
      </button>
    </template>
    <button
      class="ord-pagination__btn"
      :class="{ 'ord-pagination__btn--disabled': currentPage >= totalPages }"
      :disabled="currentPage >= totalPages"
      @click="goTo(currentPage + 1)"
    >
      &gt;
    </button>
  </nav>
</template>

<style scoped>
.ord-pagination {
  display: flex;
  align-items: center;
  gap: 6px;
}

.ord-pagination__btn {
  min-width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-sm);
  font-family: var(--ord-font-sans);
  font-size: 14px;
  font-weight: 500;
  color: var(--ord-color-black);
  background: var(--ord-color-white);
  cursor: pointer;
  transition: all 150ms ease;
}

.ord-pagination__btn:hover:not(:disabled) {
  border-color: var(--ord-color-border-hover);
}

.ord-pagination__btn--active {
  background: var(--ord-color-blue);
  color: var(--ord-color-white);
  border-color: var(--ord-color-blue);
}

.ord-pagination__btn--disabled {
  opacity: 0.4;
  pointer-events: none;
}

.ord-pagination__ellipsis {
  min-width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: var(--ord-color-gray-500);
}
</style>
