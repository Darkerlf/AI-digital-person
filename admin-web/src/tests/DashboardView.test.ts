import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { apiClient } from '../api/client'
import DashboardView from '../views/DashboardView.vue'

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}))

describe('DashboardView', () => {
  beforeEach(() => {
    vi.mocked(apiClient.get).mockReset()
    vi.mocked(apiClient.get).mockResolvedValue({ data: { items: [] } })
  })

  it('renders the overview title in Chinese', () => {
    const wrapper = mount(DashboardView, {
      global: {
        stubs: {
          DashboardCharts: true,
          RouterLink: {
            template: '<a><slot /></a>',
          },
        },
      },
    })

    expect(wrapper.text()).toContain('运营概览')
  })

  it('keeps overview metrics visible when chart requests fail', async () => {
    vi.mocked(apiClient.get).mockImplementation((url: string) => {
      if (url === '/dashboard/overview') {
        return Promise.resolve({
          data: {
            total_events: 12,
            total_spots: 3,
            total_documents: 2,
            recent_import_jobs: [{ id: 1 }],
          },
        })
      }
      return Promise.reject(new Error('chart data failed'))
    })

    const wrapper = mount(DashboardView, {
      global: {
        stubs: {
          DashboardCharts: true,
        },
      },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('12')
    expect(wrapper.text()).toContain('3')
    expect(wrapper.text()).not.toContain('暂时无法加载运营概览数据。')
  })
})
