import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import SessionManagementView from '../views/SessionManagementView.vue'

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async (path: string) => {
      if (path === '/sessions') {
        return { data: { items: [] } }
      }
      if (path === '/sessions/unresolved') {
        return { data: { items: [] } }
      }
      return { data: { id: 1, session_key: 'session-001', messages: [] } }
    }),
    put: vi.fn(async () => ({ data: {} })),
  },
}))

describe('SessionManagementView', () => {
  it('renders the session management title', () => {
    const wrapper = mount(SessionManagementView, {
      global: {
        stubs: {
          RouterLink: {
            template: '<a><slot /></a>',
          },
        },
      },
    })

    expect(wrapper.text()).toContain('会话记录与问题修正')
  })
})
