import axios from 'axios'

function getDefaultRouteByRole(role: string | null): string {
  if (role === 'content_admin') {
    return '/knowledge/documents'
  }
  if (role === 'ops_admin') {
    return '/analytics/dashboard'
  }
  return '/'
}

export const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    if (status === 401) {
      localStorage.removeItem('accessToken')
      localStorage.removeItem('username')
      localStorage.removeItem('role')
      window.location.href = '/login'
    }
    if (status === 403) {
      const defaultRoute = getDefaultRouteByRole(localStorage.getItem('role'))
      window.location.href = defaultRoute
    }
    return Promise.reject(error)
  },
)
