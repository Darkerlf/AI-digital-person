import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { describe, expect, it, vi } from 'vitest'

import AppHeader from '../components/AppHeader.vue'
import { useAuthStore } from '../stores/auth'

const { pushMock } = vi.hoisted(() => ({
  pushMock: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRoute: () => ({
    meta: {
      title: '工作台',
      description: '运营概览',
    },
  }),
  useRouter: () => ({
    push: pushMock,
  }),
}))

describe('AppHeader', () => {
  it('clears auth store and routes to login after logout', async () => {
    const localStorageMock = {
      getItem: vi.fn((key: string) => {
        if (key === 'accessToken') return 'token-1'
        if (key === 'username') return 'admin'
        if (key === 'role') return 'super_admin'
        return null
      }),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    }
    vi.stubGlobal('localStorage', localStorageMock)
    pushMock.mockClear()

    setActivePinia(createPinia())
    const authStore = useAuthStore()
    expect(authStore.accessToken).toBe('token-1')

    const wrapper = mount(AppHeader)
    await wrapper.find('button').trigger('click')

    expect(authStore.accessToken).toBe('')
    expect(authStore.username).toBe('')
    expect(authStore.role).toBe('')
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('accessToken')
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('username')
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('role')
    expect(pushMock).toHaveBeenCalledWith('/login')
  })
})
