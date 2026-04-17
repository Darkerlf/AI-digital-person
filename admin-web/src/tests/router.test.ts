import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { router } from '../router'
import { useAuthStore } from '../stores/auth'

describe('router role guard', () => {
  beforeEach(async () => {
    vi.stubGlobal('localStorage', {
      getItem: vi.fn(() => ''),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    })

    setActivePinia(createPinia())
  })

  it('redirects content_admin away from ops routes', async () => {
    const store = useAuthStore()
    store.accessToken = 'token-1'
    store.setProfile({ username: 'content_admin', role: 'content_admin' })

    await router.push('/feedback-report')

    expect(router.currentRoute.value.fullPath).toBe('/knowledge/documents')
  })
})
