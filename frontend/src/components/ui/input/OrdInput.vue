<script setup lang="ts">
defineProps<{
  type?: string
  placeholder?: string
  disabled?: boolean
  error?: boolean
}>()

const modelValue = defineModel<string>({ default: '' })
</script>

<template>
  <input
    v-model="modelValue"
    class="ord-input"
    :class="{ 'ord-input--error': error, 'ord-input--disabled': disabled }"
    :type="type ?? 'text'"
    :placeholder="placeholder"
    :disabled="disabled"
  />
</template>

<style scoped>
.ord-input {
  width: 100%;
  height: 42px;
  padding: 0 14px;
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-sm);
  font-family: var(--ord-font-sans);
  font-size: 15px;
  color: var(--ord-color-black);
  background: var(--ord-color-white);
  outline: none;
  transition: border-color var(--ord-transition-base), box-shadow var(--ord-transition-base);
}

.ord-input::placeholder {
  color: var(--ord-color-gray-300);
}

.ord-input:focus {
  border-color: var(--ord-color-blue);
  box-shadow: 0 0 0 3px rgba(20, 110, 245, 0.1);
}

.ord-input--error {
  border-color: var(--ord-color-red);
}

.ord-input--disabled {
  opacity: 0.6;
  background: var(--ord-color-bg-subtle);
  pointer-events: none;
}
</style>
