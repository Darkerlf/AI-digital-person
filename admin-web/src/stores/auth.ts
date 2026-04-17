import { defineStore } from 'pinia'

import { apiClient } from '../api/client'

export type AdminRole = 'super_admin' | 'content_admin' | 'ops_admin'

export function getDefaultRouteByRole(role: AdminRole | string): string {
  if (role === 'content_admin') {
    return '/knowledge/documents'
  }
  if (role === 'ops_admin') {
    return '/analytics/dashboard'
  }
  return '/'
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('accessToken') ?? '',
    username: localStorage.getItem('username') ?? '',
    role: localStorage.getItem('role') ?? '',
    profileLoaded: Boolean(localStorage.getItem('username') && localStorage.getItem('role')),
  }),
  actions: {
    setToken(token: string) {
      this.accessToken = token
      localStorage.setItem('accessToken', token)
      this.profileLoaded = false
    },
    setProfile(profile: { username: string; role: AdminRole | string }) {
      this.username = profile.username
      this.role = profile.role
      this.profileLoaded = true
      localStorage.setItem('username', profile.username)
      localStorage.setItem('role', profile.role)
    },
    async fetchProfile() {
      const response = await apiClient.get('/auth/me')
      this.setProfile(response.data)
      return response.data
    },
    clearAuth() {
      this.accessToken = ''
      this.username = ''
      this.role = ''
      this.profileLoaded = false
      localStorage.removeItem('accessToken')
      localStorage.removeItem('username')
      localStorage.removeItem('role')
    },
  },
})
