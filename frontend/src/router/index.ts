import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = []

if (import.meta.env.DEV) {
  routes.push(
    {
      path: '/dev',
      component: () => import('@/views/DevPlayground.vue'),
    },
    {
      path: '/',
      redirect: '/dev',
    },
  )
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
