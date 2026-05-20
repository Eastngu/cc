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
        meta: { title: '经营看板', roles: ['boss', 'finance'] },
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('@/views/customers/CustomerList.vue'),
        meta: { title: '客户管理', roles: ['boss', 'finance'] },
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/orders/OrderList.vue'),
        meta: { title: '订单管理', roles: ['boss', 'finance', 'workshop'] },
      },
      {
        path: 'settings/processes',
        name: 'Processes',
        component: () => import('@/views/settings/ProcessList.vue'),
        meta: { title: '工艺配置', roles: ['boss', 'finance'] },
      },
      {
        path: 'finance/receivables',
        name: 'Receivables',
        component: () => import('@/views/finance/ReceivableList.vue'),
        meta: { title: '应收账款', roles: ['boss', 'finance'] },
      },
      {
        path: 'finance/payables',
        name: 'Payables',
        component: () => import('@/views/finance/PayableList.vue'),
        meta: { title: '应付账款', roles: ['boss', 'finance'] },
      },
      {
        path: 'finance/payments',
        name: 'Payments',
        component: () => import('@/views/finance/PaymentList.vue'),
        meta: { title: '收付款记录', roles: ['boss', 'finance'] },
      },
      {
        path: 'finance/statements',
        name: 'Statements',
        component: () => import('@/views/finance/StatementList.vue'),
        meta: { title: '月度对账单', roles: ['boss', 'finance'] },
      },
      {
        path: 'costing',
        name: 'Costing',
        component: () => import('@/views/costing/CostList.vue'),
        meta: { title: '成本核算', roles: ['boss', 'finance'] },
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

  // Workshop users land on /orders since they can't see the dashboard
  if (to.path === '/' && auth.userRole === 'workshop') {
    next('/orders')
    return
  }

  // Block routes the current role isn't allowed to visit
  if (to.meta.roles && !to.meta.roles.includes(auth.userRole)) {
    next(auth.userRole === 'workshop' ? '/orders' : '/')
    return
  }

  next()
})

export default router
