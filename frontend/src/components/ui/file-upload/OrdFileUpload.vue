<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  accept?: string
  multiple?: boolean
}

withDefaults(defineProps<Props>(), {
  accept: '*',
  multiple: false,
})

const files = defineModel<File[]>('modelValue', { default: () => [] })
const isDragover = ref(false)
const inputRef = ref<HTMLInputElement | null>(null)

function openFileDialog() {
  inputRef.value?.click()
}

function handleFiles(fileList: FileList | null) {
  if (!fileList) return
  files.value = Array.from(fileList)
}

function onDrop(e: DragEvent) {
  isDragover.value = false
  handleFiles(e.dataTransfer?.files ?? null)
}

function onInputChange(e: Event) {
  const target = e.target as HTMLInputElement
  handleFiles(target.files)
}
</script>

<template>
  <div class="ord-file-upload">
    <div
      :class="['ord-file-upload__zone', { 'ord-file-upload__zone--dragover': isDragover }]"
      @click="openFileDialog"
      @dragover.prevent="isDragover = true"
      @dragleave.prevent="isDragover = false"
      @drop.prevent="onDrop"
    >
      <div class="ord-file-upload__icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
      </div>
      <span class="ord-file-upload__text">点击或拖拽文件到此处</span>
    </div>
    <input
      ref="inputRef"
      type="file"
      class="ord-file-upload__input"
      :accept="accept"
      :multiple="multiple"
      @change="onInputChange"
    />
    <ul v-if="files.length" class="ord-file-upload__list">
      <li v-for="(file, i) in files" :key="i" class="ord-file-upload__file">
        {{ file.name }}
      </li>
    </ul>
  </div>
</template>

<style scoped>
.ord-file-upload__zone {
  border: 2px dashed var(--ord-color-border);
  border-radius: var(--ord-radius-md);
  padding: 24px;
  min-height: 116px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: var(--ord-transition-base);
}

.ord-file-upload__zone:hover,
.ord-file-upload__zone--dragover {
  border-color: var(--ord-color-blue);
  background: var(--ord-color-soft-blue, rgba(20, 110, 245, 0.04));
}

.ord-file-upload__icon {
  color: var(--ord-color-gray-300);
}

.ord-file-upload__text {
  font-size: 14px;
  color: var(--ord-color-gray-500);
}

.ord-file-upload__input {
  display: none;
}

.ord-file-upload__list {
  list-style: none;
  padding: 0;
  margin: 8px 0 0;
}

.ord-file-upload__file {
  font-size: 13px;
  color: var(--ord-color-black);
  padding: 4px 0;
}
</style>
