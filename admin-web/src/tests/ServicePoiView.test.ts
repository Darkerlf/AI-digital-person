import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import ServicePoiView from '../views/ServicePoiView.vue'

const { apiGet, apiPost, apiPut, apiDelete } = vi.hoisted(() => {
  const apiGet = vi.fn(async (path: string) => {
    if (path === '/scenic-areas') {
      return { data: [{ id: 1, code: 'LS', name: 'Lingshan', description: null, status: 'active' }] }
    }
    if (path === '/service-pois') {
      return {
        data: {
          items: [
            {
              id: 1,
              scenic_area_id: 1,
              name: 'Visitor Center',
              category: 'service_center',
              area_text: 'Main entrance',
              description: 'Information desk',
              open_hours: '08:30-17:00',
              latitude: 31.42034,
              longitude: 120.10355,
              status: 'active',
            },
          ],
        },
      }
    }
    return { data: {} }
  })
  return {
    apiGet,
    apiPost: vi.fn(async () => ({ data: {} })),
    apiPut: vi.fn(async () => ({ data: {} })),
    apiDelete: vi.fn(async () => ({ data: {} })),
  }
})

vi.mock('../api/client', () => ({
  apiClient: {
    get: apiGet,
    post: apiPost,
    put: apiPut,
    delete: apiDelete,
  },
}))

describe('ServicePoiView', () => {
  it('loads service POIs and posts a new POI from the admin form', async () => {
    const wrapper = mount(ServicePoiView)
    await flushPromises()

    expect(wrapper.text()).toContain('便民服务点管理')
    expect(wrapper.text()).toContain('Visitor Center')

    await wrapper.find('input[placeholder="服务点名称"]').setValue('Public Toilet')
    await wrapper.find('select[name="category"]').setValue('toilet')
    await wrapper.find('input[placeholder="纬度"]').setValue('31.421872')
    await wrapper.find('input[placeholder="经度"]').setValue('120.103365')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(apiPost).toHaveBeenCalledWith('/service-pois', expect.objectContaining({
      name: 'Public Toilet',
      category: 'toilet',
      latitude: 31.421872,
      longitude: 120.103365,
    }))
  })
})
