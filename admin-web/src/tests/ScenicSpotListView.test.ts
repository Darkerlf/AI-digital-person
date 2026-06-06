import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import ScenicSpotListView from '../views/ScenicSpotListView.vue'

const mocks = vi.hoisted(() => {
  const getMock = vi.fn(async (path: string) => {
    if (path === '/scenic-spots') {
      return {
        data: {
          items: [
            {
              id: 1,
              scenic_area_id: 1,
              spot_code: 'SPOT-1',
              name: 'Buddha Plaza',
              alias: null,
              location_text: null,
              latitude: null,
              longitude: null,
              coordinate_source: null,
              coordinate_confidence: null,
              coordinate_verified: false,
              tencent_poi_id: null,
              coordinate_address: null,
              coordinate_raw_json: null,
              cover_image_url: null,
              guide_text: null,
              target_audience: null,
              parameters_text: null,
              core_function: null,
              cultural_value: null,
              detail_intro: null,
              highlights: null,
              performance_info: null,
              remarks: null,
              suggested_duration_minutes: null,
              open_status: 'open',
              tags: [],
            },
          ],
        },
      }
    }
    if (path === '/scenic-areas') {
      return { data: [{ id: 1, name: 'Test Area' }] }
    }
    if (path === '/scenic-spots/1/coordinate-candidates') {
      return {
        data: {
          spot_id: 1,
          search_keyword: 'Test Area Buddha Plaza',
          center: { latitude: 31.428076, longitude: 120.098006 },
          candidates: [
            {
              provider: 'tencent_place',
              title: 'Buddha Plaza',
              address: 'Inside Test Area',
              category: 'tourism',
              latitude: 31.430266,
              longitude: 120.096427,
              confidence: 92,
              distance_meters: 300,
              tencent_poi_id: 'poi-close',
              raw: { id: 'poi-close', title: 'Buddha Plaza' },
            },
          ],
        },
      }
    }
    return { data: {} }
  })
  const postMock = vi.fn(async () => ({ data: {} }))
  return { getMock, postMock }
})

vi.mock('../api/client', () => ({
  apiClient: {
    get: mocks.getMock,
    post: mocks.postMock,
    put: vi.fn(async () => ({ data: {} })),
    delete: vi.fn(async () => ({ data: {} })),
  },
}))

vi.mock('vue-router', () => ({
  RouterLink: { template: '<a><slot /></a>' },
}))

describe('ScenicSpotListView', () => {
  async function flushPromises() {
    await Promise.resolve()
    await Promise.resolve()
    await new Promise((resolve) => setTimeout(resolve, 0))
  }

  it('loads Tencent map coordinate candidates and confirms one', async () => {
    const wrapper = mount(ScenicSpotListView)
    await flushPromises()

    expect(wrapper.text()).toContain('待校准')
    await wrapper.find('button[name="load-coordinate-candidates"]').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('腾讯地图候选')
    expect(wrapper.text()).toContain('Buddha Plaza')
    await wrapper.find('button[name="confirm-coordinate-candidate"]').trigger('click')

    expect(mocks.postMock).toHaveBeenCalledWith('/scenic-spots/1/coordinate-candidates/confirm', {
      latitude: 31.430266,
      longitude: 120.096427,
      coordinate_source: 'tencent_place',
      coordinate_confidence: 92,
      tencent_poi_id: 'poi-close',
      coordinate_address: 'Inside Test Area',
      coordinate_raw_json: { id: 'poi-close', title: 'Buddha Plaza' },
    })
  })
})
