import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { describe, expect, it, vi } from 'vitest'

import LoginView from '../views/LoginView.vue'

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}))

describe('LoginView', () => {
  it('renders username and password inputs', () => {
    vi.stubGlobal('localStorage', {
      getItem: vi.fn(() => ''),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    })

    const wrapper = mount(LoginView, {
      global: {
        plugins: [createPinia()],
      },
    })

    expect(wrapper.text()).toContain('登录')
    expect(wrapper.find('input').exists()).toBe(true)
  })
})
