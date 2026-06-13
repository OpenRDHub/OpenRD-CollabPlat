<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { OrdCard, OrdCardContent, OrdInput, OrdButton } from '@/components/ui'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/components/ui'

const router = useRouter()
const auth = useAuthStore()
const { show } = useToast()

const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) {
    show({ title: '请输入用户名和密码', variant: 'error' })
    return
  }
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    show({ title: '登录成功', variant: 'success' })
    router.push('/dashboard')
  } catch {
    show({ title: '登录失败', description: '用户名或密码错误', variant: 'error' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-view">
    <div class="login-view__container">
      <div class="login-view__header">
        <h1 class="login-view__brand">
          <span>Open</span><span class="login-view__brand-rd">RD</span>
        </h1>
        <p class="login-view__subtitle">罕见病需求协作平台</p>
      </div>
      <OrdCard>
        <OrdCardContent>
          <form class="login-view__form" @submit.prevent="handleLogin">
            <OrdInput v-model="username" placeholder="用户名" />
            <OrdInput v-model="password" type="password" placeholder="密码" />
            <OrdButton variant="primary" size="lg" :loading="loading" style="width: 100%">
              登录
            </OrdButton>
          </form>
          <p class="login-view__hint">
            测试账号：chenbei / linzixuan / zhaoming / admin，密码：OpenRD#2026
          </p>
        </OrdCardContent>
      </OrdCard>
    </div>
  </div>
</template>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--ord-space-6);
}

.login-view__container {
  width: 100%;
  max-width: 400px;
}

.login-view__header {
  text-align: center;
  margin-bottom: var(--ord-space-8);
}

.login-view__brand {
  font-size: 36px;
  font-weight: 600;
  letter-spacing: -1px;
  color: var(--ord-color-black);
}

.login-view__brand-rd {
  color: var(--ord-color-blue);
}

.login-view__subtitle {
  font-size: 14px;
  color: var(--ord-color-gray-500);
  margin-top: var(--ord-space-2);
}

.login-view__form {
  display: flex;
  flex-direction: column;
  gap: var(--ord-space-4);
}

.login-view__hint {
  margin-top: var(--ord-space-4);
  font-size: 12px;
  color: var(--ord-color-gray-300);
  text-align: center;
  line-height: 1.5;
}
</style>
