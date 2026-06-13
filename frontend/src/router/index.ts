import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/layouts/AppLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
    ],
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
  },
  {
    path: '/403',
    name: 'forbidden',
    component: () => import('@/views/ForbiddenView.vue'),
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
  },
]

if (import.meta.env.DEV) {
  const appRoute = routes.find((r) => r.path === '/')
  if (appRoute && 'children' in appRoute) {
    appRoute.children!.push({
      path: 'dev',
      component: () => import('@/views/DevPlayground.vue'),
    })
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.name === 'login') {
    if (auth.isLoggedIn) return '/dashboard'
    return true
  }

  const requiresAuth = to.matched.some((r) => r.meta.requiresAuth)
  if (!requiresAuth) return true

  if (!auth.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (!auth.user) {
    const ok = await auth.restore()
    if (!ok) return { name: 'login' }
  }

  const permission = to.meta.permission as string | undefined
  if (permission && !auth.hasPermission(permission)) {
    return '/403'
  }

  return true
})

export default router
