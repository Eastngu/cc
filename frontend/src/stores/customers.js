import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getCustomers,
  createCustomer,
  updateCustomer,
  deleteCustomer,
} from '@/api/customers'

export const useCustomerStore = defineStore('customers', () => {
  const customers = ref([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchCustomers(params = {}) {
    loading.value = true
    try {
      const { data } = await getCustomers(params)
      customers.value = data.results
      total.value = data.count
    } finally {
      loading.value = false
    }
  }

  async function addCustomer(data) {
    const { data: newCustomer } = await createCustomer(data)
    return newCustomer
  }

  async function editCustomer(id, data) {
    const { data: updated } = await updateCustomer(id, data)
    return updated
  }

  async function removeCustomer(id) {
    await deleteCustomer(id)
  }

  return { customers, total, loading, fetchCustomers, addCustomer, editCustomer, removeCustomer }
})
