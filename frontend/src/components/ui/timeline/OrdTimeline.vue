<script setup lang="ts">
interface TimelineItem {
  title: string
  status: 'done' | 'active' | 'pending'
  description?: string
  date?: string
}

interface Props {
  items: TimelineItem[]
}

defineProps<Props>()
</script>

<template>
  <div class="ord-timeline">
    <div v-for="(item, index) in items" :key="index" class="ord-timeline__item">
      <div class="ord-timeline__indicator">
        <div :class="['ord-timeline__dot', `ord-timeline__dot--${item.status}`]" />
        <div v-if="index < items.length - 1" class="ord-timeline__line" />
      </div>
      <div class="ord-timeline__content">
        <div class="ord-timeline__title">{{ item.title }}</div>
        <div v-if="item.description" class="ord-timeline__description">{{ item.description }}</div>
        <div v-if="item.date" class="ord-timeline__date">{{ item.date }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ord-timeline {
  display: flex;
  flex-direction: column;
}

.ord-timeline__item {
  display: grid;
  grid-template-columns: 20px 1fr;
  gap: 0 12px;
}

.ord-timeline__indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.ord-timeline__dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 4px;
}

.ord-timeline__dot--done {
  background: var(--ord-color-green);
}

.ord-timeline__dot--active {
  background: var(--ord-color-blue);
  box-shadow: 0 0 0 3px var(--ord-color-soft-blue, rgba(20, 110, 245, 0.15));
}

.ord-timeline__dot--pending {
  background: var(--ord-color-border);
}

.ord-timeline__line {
  width: 2px;
  flex: 1;
  background: var(--ord-color-border);
  margin: 4px 0;
}

.ord-timeline__content {
  padding-bottom: 20px;
}

.ord-timeline__title {
  font-size: 14px;
  font-weight: 500;
  color: var(--ord-color-black);
}

.ord-timeline__description {
  font-size: 13px;
  color: var(--ord-color-gray-500);
  margin-top: 4px;
}

.ord-timeline__date {
  font-size: 12px;
  color: var(--ord-color-gray-300);
  margin-top: 4px;
}
</style>
