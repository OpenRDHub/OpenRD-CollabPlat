<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  name: string
  src?: string
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
})

const initials = computed(() => {
  const chars = props.name.trim().split(/\s+/)
  if (chars.length >= 2) {
    return chars[0][0] + chars[1][0]
  }
  return chars[0]?.slice(0, 2) ?? ''
})
</script>

<template>
  <div :class="['ord-avatar', `ord-avatar--${size}`]">
    <img v-if="src" :src="src" :alt="name" class="ord-avatar__img" />
    <span v-else class="ord-avatar__initials">{{ initials }}</span>
  </div>
</template>

<style scoped>
.ord-avatar {
  border-radius: 50%;
  overflow: hidden;
  display: grid;
  place-items: center;
  background: rgba(20, 110, 245, 0.1);
  flex-shrink: 0;
}

.ord-avatar--sm {
  width: 28px;
  height: 28px;
  font-size: 11px;
}

.ord-avatar--md {
  width: 36px;
  height: 36px;
  font-size: 13px;
}

.ord-avatar--lg {
  width: 48px;
  height: 48px;
  font-size: 16px;
}

.ord-avatar__initials {
  color: var(--ord-color-blue);
  font-weight: 600;
  text-transform: uppercase;
  user-select: none;
}

.ord-avatar__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
