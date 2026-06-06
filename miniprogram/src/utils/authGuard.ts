export const HOME_PAGE_PATH = 'pages/index/index'
export const LOGIN_PAGE_PATH = 'pages/my/my'
export const LOGIN_PAGE_URL = `/${LOGIN_PAGE_PATH}`

const PROTECTED_INTERCEPTORS = ['navigateTo', 'redirectTo', 'reLaunch', 'switchTab'] as const
let installed = false
let prompting = false

export function normalizeRoutePath(url: string | undefined): string {
  return (url || '').split('?')[0].replace(/^\/+/, '')
}

export function isAuthenticatedFromStorage(): boolean {
  const token = String(uni.getStorageSync('token') || '').trim()
  const visitorDbId = Number(uni.getStorageSync('visitor_db_id') || 0)
  return !!token && visitorDbId > 0
}

export function canAccessPage(url: string | undefined): boolean {
  const path = normalizeRoutePath(url)
  if (path === LOGIN_PAGE_PATH || path === HOME_PAGE_PATH) return true
  return isAuthenticatedFromStorage()
}

export function installAuthNavigationGuards(): void {
  if (installed) return
  installed = true
  PROTECTED_INTERCEPTORS.forEach((method) => {
    uni.addInterceptor(method, {
      invoke(args: { url?: string }) {
        if (canAccessPage(args?.url)) return true
        promptLogin()
        return false
      },
    })
  })
}

export function guardCurrentPage(): void {
  if (isAuthenticatedFromStorage()) return
  const pages = typeof getCurrentPages === 'function' ? getCurrentPages() : []
  const current = pages[pages.length - 1]
  if (current && normalizeRoutePath(current.route) === LOGIN_PAGE_PATH) return
  promptLogin()
}

function promptLogin(): void {
  if (prompting) return
  prompting = true
  uni.showModal({
    title: '登录后使用',
    content: '请先登录后再使用小程序功能。',
    confirmText: '去登陆',
    cancelText: '稍后再说',
    success: (res) => {
      prompting = false
      if (res.confirm) {
        uni.switchTab({ url: LOGIN_PAGE_URL })
      }
    },
    complete: () => {
      prompting = false
    },
  })
}
