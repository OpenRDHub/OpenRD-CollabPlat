<script setup lang="ts">
defineProps<{
  placeholder?: string
  disabled?: boolean
  rows?: number
  error?: boolean
}>()

const modelValue = defineModel<string>({ default: '' })
</script>

<template>
  <textarea
    v-model="modelValue"
    class="ord-textarea"
    :class="{ 'ord-textarea--error': error, 'ord-textarea--disabled': disabled }"
    :placeholder="placeholder"
    :rows="rows ?? 4"
    :disabled="disabled"
  />
</template>

<style scoped>
.ord-textarea {
  width: 100%;
  min-height: auto;
  padding: 12px 14px;
  border: 1px solid var(--ord-color-border);
  border-radius: var(--ord-radius-sm);
  font-family: var(--ord-font-sans);
  font-size: 15px;
  color: var(--ord-color-black);
  background: var(--ord-color-white);
  outline: none;
  resize: vertical;
  transition: border-color var(--ord-transition-base), box-shadow var(--ord-transition-base);
}

.ord-textarea::placeholder {
  color: var(--ord-color-gray-300);
}

.ord-textarea:focus {
  border-color: var(--ord-color-blue);
  box-shadow: 0 0 0 3px rgba(20, 110, 245, 0.1);
}

.ord-textarea--error {
  border-color: var(--ord-color-red);
}

.ord-textarea--disabled {
  opacity: 0.6;
  background: var(--ord-color-bg-subtle);
  pointer-events: none;
}
</style>
