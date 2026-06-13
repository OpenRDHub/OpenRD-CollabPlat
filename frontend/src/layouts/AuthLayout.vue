<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<template>
  <div class="auth-layout">
    <div class="auth-layout__brand">
      <div class="auth-layout__brand-content">
        <div class="auth-layout__brand-logo">
          <span>Open</span><span class="auth-layout__brand-rd">RD</span>
        </div>
        <h2 class="auth-layout__brand-title">罕见病需求协作平台</h2>
        <p class="auth-layout__brand-desc">连接患者、志愿者与技术力量，<br>让每一个罕见需求都被看见。</p>
      </div>
      <div class="auth-layout__brand-decor">
        <div class="auth-layout__circle auth-layout__circle--1"></div>
        <div class="auth-layout__circle auth-layout__circle--2"></div>
        <div class="auth-layout__circle auth-layout__circle--3"></div>
      </div>
    </div>
    <div class="auth-layout__form-side">
      <div class="auth-layout__form-container">
        <h1 class="auth-layout__title">{{ title }}</h1>
        <p v-if="subtitle" class="auth-layout__subtitle">{{ subtitle }}</p>
        <slot />
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-layout {
  display: flex;
  min-height: 100vh;
}

.auth-layout__brand {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0a1628 0%, #0d2b5e 50%, #143a7a 100%);
  overflow: hidden;
}

.auth-layout__brand-content {
  position: relative;
  z-index: 2;
  text-align: center;
  color: #fff;
  padding: 40px;
}

.auth-layout__brand-logo {
  font-size: 48px;
  font-weight: 600;
  letter-spacing: -1.5px;
  margin-bottom: 24px;
}

.auth-layout__brand-rd {
  color: var(--ord-color-blue-400);
}

.auth-layout__brand-title {
  font-size: 22px;
  font-weight: 500;
  margin-bottom: 16px;
  opacity: 0.95;
}

.auth-layout__brand-desc {
  font-size: 15px;
  line-height: 1.7;
  opacity: 0.7;
}

.auth-layout__brand-decor {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.auth-layout__circle {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(59, 137, 255, 0.15);
}

.auth-layout__circle--1 {
  width: 400px;
  height: 400px;
  top: -100px;
  right: -80px;
}

.auth-layout__circle--2 {
  width: 300px;
  height: 300px;
  bottom: -60px;
  left: -40px;
}

.auth-layout__circle--3 {
  width: 180px;
  height: 180px;
  top: 50%;
  left: 60%;
  background: radial-gradient(circle, rgba(20, 110, 245, 0.08) 0%, transparent 70%);
}

.auth-layout__form-side {
  width: 515px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: var(--ord-color-white);
}

.auth-layout__form-container {
  width: 100%;
  max-width: 400px;
}

.auth-layout__title {
  font-size: 28px;
  font-weight: 600;
  color: var(--ord-color-black);
  margin-bottom: 8px;
}

.auth-layout__subtitle {
  font-size: 14px;
  color: var(--ord-color-gray-500);
  margin-bottom: 32px;
}

@media (max-width: 991px) {
  .auth-layout__brand {
    display: none;
  }

  .auth-layout__form-side {
    width: 100%;
  }
}
</style>
