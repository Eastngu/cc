import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getMe } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token') || '')

  const isLoggedIn = computed(() => !!accessToken.value)
  const userRole = computed(() => user.value?.role || '')

  async function login(username, password) {
    const { data } = await loginApi(username, password)
    accessToken.value = data.access
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    user.value = data.user
  }

  async function fetchUser() {
    try {
      const { data } = await getMe()
      user.value = data
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    accessToken.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { user, accessToken, isLoggedIn, userRole, login, fetchUser, logout }
})
