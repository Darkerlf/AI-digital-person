import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import { apiClient } from '../api/client'
import RouteTemplateView from '../views/RouteTemplateView.vue'

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async (path: string) => {
      if (path === '/scenic-areas') {
        return { data: [{ id: 1, code: 'LS', name: '灵山胜境', description: null, status: 'active' }] }
      }
      if (path === '/scenic-spots') {
        return { data: { items: [{ id: 1, scenic_area_id: 1, spot_code: 'LS-001', name: '灵山大佛' }] } }
      }
      if (path === '/route-templates') {
        return { data: { items: [] } }
      }
      return { data: {} }
    }),
    post: vi.fn(async () => ({ data: {} })),
    put: vi.fn(async () => ({ data: {} })),
    delete: vi.fn(async () => ({ data: {} })),
  },
}))

async function flushPromises() {
  await Promise.resolve()
  await Promise.resolve()
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('RouteTemplateView validation', () => {
  it('blocks invalid template submission before calling api', async () => {
    const wrapper = mount(RouteTemplateView)
    await flushPromises()
    vi.mocked(apiClient.post).mockClear()

    await wrapper.find('form').trigger('submit')

    expect(wrapper.text()).toContain('请填写模板名称。')
    expect(apiClient.post).not.toHaveBeenCalled()
  })
})
