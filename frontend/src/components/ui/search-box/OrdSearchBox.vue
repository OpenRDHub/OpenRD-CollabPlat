<script setup lang="ts">
interface Props {
  placeholder?: string
  width?: string
}

withDefaults(defineProps<Props>(), {
  placeholder: '搜索...',
  width: '260px',
})

const modelValue = defineModel<string>({ default: '' })
</script>

<template>
  <div class="ord-search-box" :style="{ width }">
    <svg class="ord-search-box__icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
    <input
      v-model="modelValue"
      type="text"
      class="ord-search-box__input"
      :placeholder="placeholder"
    />
  </div>
</template>

<style scoped>
.ord-search-box {
  position: relative;
}

.ord-search-box__icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--ord-color-gray-300);
  pointer-events: none;
}

.ord-search-box__input {
  width: 100%;
  height: 38px;
  padding: 0 12px 0 36px;
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-sm);
  font-size: 14px;
  color: var(--ord-color-black);
  background: var(--ord-color-white);
  outline: none;
  transition: var(--ord-transition-base);
}

.ord-search-box__input::placeholder {
  color: var(--ord-color-gray-300);
}

.ord-search-box__input:focus {
  border-color: var(--ord-color-blue);
  box-shadow: 0 0 0 3px rgba(20, 110, 245, 0.1);
}
</style>
