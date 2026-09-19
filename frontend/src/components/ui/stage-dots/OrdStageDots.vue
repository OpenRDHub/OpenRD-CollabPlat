<script setup lang="ts">
interface Props {
  /** 阶段名称，按从左到右顺序排列 */
  stages?: string[]
  /** 当前所处阶段索引（0 起）。该阶段显示为进行中（红色）；
   *  索引小于 current 的为已完成（绿色）；大于 current 的为未到达（灰色）。
   *  当 current >= stages.length 时，所有阶段均视为已完成。 */
  current?: number
  /** 是否显示阶段文字标签 */
  showLabels?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  stages: () => ['组队', '开发', '内测', '开源'],
  current: 0,
  showLabels: true,
})

type StageState = 'done' | 'active' | 'pending'

function stateOf(index: number): StageState {
  if (index < props.current) return 'done'
  if (index === props.current) return 'active'
  return 'pending'
}
</script>

<template>
  <div class="ord-stage-dots" role="list" :aria-label="`项目阶段进度：${current + 1} / ${stages.length}`">
    <div
      v-for="(stage, i) in stages"
      :key="i"
      class="ord-stage-dots__item"
      :class="`is-${stateOf(i)}`"
      role="listitem"
    >
      <div class="ord-stage-dots__track">
        <span class="ord-stage-dots__dot" :aria-label="stateOf(i)" />
      </div>
      <span v-if="showLabels" class="ord-stage-dots__label">{{ stage }}</span>
      <span
        v-if="i < stages.length - 1"
        class="ord-stage-dots__connector"
        :class="{ 'is-done': i < current }"
      />
    </div>
  </div>
</template>

<style scoped>
.ord-stage-dots {
  display: flex;
  align-items: flex-start;
  width: 100%;
}

.ord-stage-dots__item {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.ord-stage-dots__track {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 20px;
}

.ord-stage-dots__dot {
  position: relative;
  z-index: 1;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--ord-color-gray-300);
  transition: background 240ms ease, transform 240ms ease, box-shadow 240ms ease;
}

.ord-stage-dots__connector {
  position: absolute;
  top: 9px;
  left: 50%;
  width: 100%;
  height: 3px;
  background: var(--ord-color-gray-300);
  z-index: 0;
  transition: background 240ms ease;
}

/* 已完成：绿色 */
.ord-stage-dots__item.is-done .ord-stage-dots__dot {
  background: var(--ord-color-green);
}

.ord-stage-dots__item.is-done .ord-stage-dots__connector {
  background: var(--ord-color-green);
}

.ord-stage-dots__item.is-done .ord-stage-dots__label {
  color: var(--ord-color-green);
}

/* 进行中：红色 + 呼吸光环 */
.ord-stage-dots__item.is-active .ord-stage-dots__dot {
  background: var(--ord-color-red);
  transform: scale(1.15);
  box-shadow: 0 0 0 4px rgba(238, 29, 54, 0.18);
}

.ord-stage-dots__item.is-active .ord-stage-dots__label {
  color: var(--ord-color-red);
  font-weight: 700;
}

/* 未到达：灰色 */
.ord-stage-dots__item.is-pending .ord-stage-dots__label {
  color: var(--ord-color-gray-500);
}

.ord-stage-dots__label {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  transition: color 240ms ease;
}
</style>
