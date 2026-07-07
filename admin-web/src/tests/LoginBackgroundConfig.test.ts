import { afterEach, describe, expect, it, vi } from 'vitest'

describe('login background config', () => {
  afterEach(() => {
    vi.unstubAllEnvs()
    vi.resetModules()
  })

  it('uses the OSS URL when VITE_LOGIN_BACKGROUND_URL is configured', async () => {
    vi.stubEnv('VITE_LOGIN_BACKGROUND_URL', 'https://example.oss-cn-beijing.aliyuncs.com/login-bg.jpg')

    const { loginBackground } = await import('../config/loginBackground')

    expect(loginBackground).toBe('https://example.oss-cn-beijing.aliyuncs.com/login-bg.jpg')
  })

  it('falls back to the bundled image when no OSS URL is configured', async () => {
    vi.stubEnv('VITE_LOGIN_BACKGROUND_URL', '')

    const { loginBackground } = await import('../config/loginBackground')

    expect(loginBackground).toContain('lingshan-login-bg')
  })
})
