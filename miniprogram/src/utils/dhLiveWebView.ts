const LOCAL_HOSTS = new Set(['localhost', '127.0.0.1', '::1'])

export function currentPlatform(): string {
  try {
    return String(uni.getSystemInfoSync().platform || '').toLowerCase()
  } catch {
    return ''
  }
}

export function isSafeDhLiveWebViewUrl(url: string, platform = currentPlatform()): boolean {
  const parsed = parseUrl(url)
  if (!parsed) return false
  if (parsed.protocol === 'https') return true
  if (isDevtoolsPlatform(platform) && parsed.protocol === 'http' && LOCAL_HOSTS.has(parsed.hostname)) {
    return true
  }
  return false
}

export function webViewBlockedReason(url: string, platform = currentPlatform()): string {
  if (isSafeDhLiveWebViewUrl(url, platform)) return ''
  if (!url) return '数字人页面地址未配置，请先配置 HTTPS 业务域名。'
  if (url.startsWith('http://localhost') || url.startsWith('http://127.0.0.1')) {
    return '当前环境不能打开 localhost 数字人页面，请配置 HTTPS 业务域名后再进行真机测试。'
  }
  return '当前数字人页面地址不可用于真机 web-view，请配置 HTTPS 业务域名。'
}

function isDevtoolsPlatform(platform: string): boolean {
  return platform.toLowerCase() === 'devtools'
}

function parseUrl(url: string): { protocol: string; hostname: string } | null {
  const match = /^([a-z][a-z0-9+.-]*):\/\/([^/:?#]+)/i.exec((url || '').trim())
  if (!match) return null
  return {
    protocol: match[1].toLowerCase(),
    hostname: match[2].toLowerCase(),
  }
}
