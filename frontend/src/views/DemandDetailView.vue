<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const demandId = ref(route.params.id as string)
</script>

<template>
  <div class="demand-detail-view">
    <h1>需求详情</h1>
    <p>需求 ID: {{ demandId }}</p>
    <p>需求详情页将在后续迭代中完成。</p>
  </div>
</template>

<style scoped>
.demand-detail-view {
  width: min(1460px, 100%);
  margin: 0 auto;
  padding: 28px;
  background: var(--ord-color-white);
  border-radius: var(--ord-radius-md);
  box-shadow: var(--ord-shadow-cascade);
}

.demand-detail-view h1 {
  margin: 0 0 16px;
  color: var(--ord-color-black);
  font-size: 32px;
  font-weight: 600;
  line-height: 1.2;
}

.demand-detail-view p {
  margin: 8px 0;
  color: var(--ord-color-gray-500);
  font-size: 15px;
  line-height: 1.6;
}
</style>
