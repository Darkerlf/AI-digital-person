import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(uni.getStorageSync('token') || '')
  const visitorId = ref<string>(uni.getStorageSync('visitor_id') || '')
  const isLoggedIn = ref<boolean>(!!token.value)

  function setToken(newToken: string) {
    token.value = newToken
    isLoggedIn.value = true
    uni.setStorageSync('token', newToken)
  }

  function setVisitorId(id: string) {
    visitorId.value = id
    uni.setStorageSync('visitor_id', id)
  }

  function logout() {
    token.value = ''
    visitorId.value = ''
    isLoggedIn.value = false
    uni.removeStorageSync('token')
    uni.removeStorageSync('visitor_id')
  }

  function ensureVisitor() {
    if (!visitorId.value) {
      const id = `v_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
      setVisitorId(id)
    }
  }

  return { token, visitorId, isLoggedIn, setToken, setVisitorId, logout, ensureVisitor }
})
