import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { describe, expect, it, vi } from 'vitest'

import AppSidebar from '../components/AppSidebar.vue'
import { useAuthStore } from '../stores/auth'

describe('AppSidebar', () => {
  it('shows only ops items for ops_admin', () => {
    vi.stubGlobal('localStorage', {
      getItem: vi.fn(() => ''),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    })

    setActivePinia(createPinia())
    const store = useAuthStore()
    store.setProfile({ username: 'ops_admin', role: 'ops_admin' })

    const wrapper = mount(AppSidebar, {
      global: {
        stubs: {
          RouterLink: {
            template: '<a><slot /></a>',
          },
        },
      },
    })

    expect(wrapper.text()).toContain('感受度报告')
    expect(wrapper.text()).not.toContain('知识管理')
    expect(wrapper.text()).not.toContain('路线模板')
  })
})
