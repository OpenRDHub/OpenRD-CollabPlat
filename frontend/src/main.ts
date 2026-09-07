import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { handleUnhandledMockRequest, isMockEnabled } from './config/mock-mode.js'

import '@/styles/tokens.css'
import '@/styles/base.css'

async function bootstrap() {
  if (import.meta.env.DEV && isMockEnabled(import.meta.env.VITE_ENABLE_MOCK)) {
    const { worker } = await import('@/mocks/browser')
    await worker.start({
      onUnhandledRequest: handleUnhandledMockRequest,
    })
  }

  const app = createApp(App)

  app.use(createPinia())
  app.use(router)

  app.mount('#app')
}

bootstrap()
