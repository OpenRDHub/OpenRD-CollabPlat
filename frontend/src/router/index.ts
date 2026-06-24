import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/hall' },
  { path: '/hall', name: 'hall', component: () => import('@/views/HallView.vue'), meta: { requiresAuth: true } },
  { path: '/dashboard', redirect: '/workbench' },
  { path: '/workbench', name: 'workbench', component: () => import('@/views/WorkbenchView.vue'), meta: { requiresAuth: true } },
  { path: '/my-demands', name: 'my-demands', component: () => import('@/views/MyDemandsView.vue'), meta: { requiresAuth: true } },
  { path: '/demands/:id', name: 'demand-detail', component: () => import('@/views/DemandDetailView.vue'), meta: { requiresAuth: true } },
  { path: '/tasks/:id', name: 'task-detail', component: () => import('@/views/TaskDetailView.vue'), meta: { requiresAuth: true } },
  { path: '/teams', name: 'team-detail', component: () => import('@/views/TeamDetailView.vue'), meta: { requiresAuth: true } },
  { path: '/messages', name: 'messages', component: () => import('@/views/MessagesView.vue'), meta: { requiresAuth: true } },
  { path: '/profile', name: 'profile', component: () => import('@/views/ProfileView.vue'), meta: { requiresAuth: true } },
  {
    path: '/admin/demand-management',
    name: 'demand-management',
    component: () => import('@/views/DemandManagementView.vue'),
    meta: { requiresAuth: true, permission: 'admin:demands' }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/RegisterView.vue'),
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: () => import('@/views/ForgotPasswordView.vue'),
  },
  {
    path: '/onboarding',
    name: 'onboarding',
    component: () => import('@/views/OnboardingView.vue'),
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

  const publicPages = ['login', 'register', 'forgot-password', 'onboarding', 'not-found', 'forbidden']
  if (publicPages.includes(to.name as string)) {
    if (to.name === 'login' && auth.isLoggedIn) return '/hall'
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
