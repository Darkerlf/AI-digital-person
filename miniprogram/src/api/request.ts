const BASE_URL = 'http://localhost:8000/api'

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
      header['Authorization'] = `Bearer ${token}`
    }

    uni.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.data as Record<string, string> | undefined,
      header,
      timeout: options.timeout || 15000,
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data as T)
        } else if (res.statusCode === 401) {
          uni.removeStorageSync('token')
          reject(new Error('未授权'))
        } else {
          reject(new Error(`请求失败: ${res.statusCode}`))
        }
      },
      fail: (err) => {
        reject(err)
      },
    })
  })
}
