import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getOrders, createOrder, updateOrder, changeOrderStatus } from '@/api/orders'

export const useOrderStore = defineStore('orders', () => {
  const orders = ref([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchOrders(params = {}) {
    loading.value = true
    try {
      const { data } = await getOrders(params)
      orders.value = data.results
      total.value = data.count
    } finally {
      loading.value = false
    }
  }

  async function addOrder(data) {
    const { data: newOrder } = await createOrder(data)
    return newOrder
  }

  async function editOrder(id, data) {
    const { data: updated } = await updateOrder(id, data)
    return updated
  }

  async function updateStatus(id, status) {
    const { data: updated } = await changeOrderStatus(id, status)
    return updated
  }

  return { orders, total, loading, fetchOrders, addOrder, editOrder, updateStatus }
})
