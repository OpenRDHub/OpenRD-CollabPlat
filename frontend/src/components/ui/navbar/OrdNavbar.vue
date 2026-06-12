<script setup lang="ts">
</script>

<template>
  <header class="ord-navbar">
    <div class="ord-navbar__inner">
      <div class="ord-navbar__brand">
        <slot name="brand" />
      </div>
      <div class="ord-navbar__center">
        <slot name="center" />
      </div>
      <div class="ord-navbar__actions">
        <slot name="actions" />
      </div>
    </div>
  </header>
</template>

<style scoped>
.ord-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--ord-nav-height);
  background: rgba(255, 255, 255, 0.94);
  border-bottom: 1px solid rgba(216, 216, 216, 0.86);
  box-shadow: var(--ord-shadow-nav);
  backdrop-filter: blur(16px);
  z-index: 100;
}

.ord-navbar__inner {
  width: min(var(--ord-content-max-width), 100%);
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 0 32px;
}

.ord-navbar__brand {
  flex-shrink: 0;
}

.ord-navbar__center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.ord-navbar__actions {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
