// #ifdef H5
export const API_BASE_URL = '/api'
export const API_BASE_URLS = [API_BASE_URL]
// #endif
// #ifndef H5
export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'
).replace(/\/+$/, '')
export const API_BASE_URLS = [API_BASE_URL]
// #endif

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: Record<string, unknown> | object
  header?: Record<string, string>
  timeout?: number
}

type RequestOptionBody = Omit<RequestOptions, 'url'>

export function request<T = unknown>(url: string, body?: RequestOptionBody): Promise<T> {
  const options: RequestOptions = { url, ...body }
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    const header: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.header,
    }
    if (token) {
      header.Authorization = `Bearer ${token}`
    }

    function tryRequest(baseIndex: number) {
      const baseUrl = API_BASE_URLS[baseIndex]
      uni.request({
        url: `${baseUrl}${options.url}`,
        method: options.method || 'GET',
        data: options.data as Record<string, unknown> | undefined,
        header,
        timeout: options.timeout || 15000,
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data as T)
            return
          }
          if (res.statusCode === 401) {
            uni.removeStorageSync('token')
            reject(new Error('Unauthorized'))
            return
          }
          if (baseIndex + 1 < API_BASE_URLS.length) {
            tryRequest(baseIndex + 1)
            return
          }
          reject(new Error(`Request failed: ${res.statusCode} ${JSON.stringify(res.data || {})}`))
        },
        fail: (err) => {
          if (baseIndex + 1 < API_BASE_URLS.length) {
            tryRequest(baseIndex + 1)
            return
          }
          reject(new Error(err.errMsg || 'Network request failed'))
        },
      })
    }

    tryRequest(0)
  })
}
