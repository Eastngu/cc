import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '经营看板' },
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('@/views/customers/CustomerList.vue'),
        meta: { title: '客户管理' },
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/orders/OrderList.vue'),
        meta: { title: '订单管理' },
      },
      {
        path: 'settings/processes',
        name: 'Processes',
        component: () => import('@/views/settings/ProcessList.vue'),
        meta: { title: '工艺配置' },
      },
      {
        path: 'finance/receivables',
        name: 'Receivables',
        component: () => import('@/views/finance/ReceivableList.vue'),
        meta: { title: '应收账款' },
      },
      {
        path: 'finance/payables',
        name: 'Payables',
        component: () => import('@/views/finance/PayableList.vue'),
        meta: { title: '应付账款' },
      },
      {
        path: 'finance/payments',
        name: 'Payments',
        component: () => import('@/views/finance/PaymentList.vue'),
        meta: { title: '收付款记录' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth === false) {
    if (auth.isLoggedIn) {
      next('/')
    } else {
      next()
    }
    return
  }

  if (!auth.isLoggedIn) {
    next('/login')
    return
  }

  if (!auth.user) {
    await auth.fetchUser()
  }

  next()
})

export default router
