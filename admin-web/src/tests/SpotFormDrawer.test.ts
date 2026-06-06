import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import SpotFormDrawer from '../components/SpotFormDrawer.vue'

describe('SpotFormDrawer', () => {
  it('emits product content fields when saving', async () => {
    const wrapper = mount(SpotFormDrawer, {
      props: {
        open: true,
        scenicAreas: [{ id: 1, name: 'Area' }],
      },
    })

    await wrapper.find('select[name="scenic_area_id"]').setValue('1')
    await wrapper.find('input[name="spot_code"]').setValue('SPOT-1')
    await wrapper.find('input[name="name"]').setValue('Spot')
    await wrapper.find('input[name="cover_image_url"]').setValue('https://example.com/cover.jpg')
    await wrapper.find('textarea[name="guide_text"]').setValue('Guide script')
    await wrapper.find('input[name="target_audience"]').setValue('families')
    await wrapper.find('textarea[name="highlights"]').setValue('Photo point')
    await wrapper.find('input[name="suggested_duration_minutes"]').setValue('25')
    await wrapper.find('.spot-drawer__form button').trigger('click')

    expect(wrapper.emitted('save')?.[0]?.[0]).toMatchObject({
      scenic_area_id: 1,
      spot_code: 'SPOT-1',
      name: 'Spot',
      cover_image_url: 'https://example.com/cover.jpg',
      guide_text: 'Guide script',
      target_audience: 'families',
      highlights: 'Photo point',
      suggested_duration_minutes: 25,
    })
  })
})
