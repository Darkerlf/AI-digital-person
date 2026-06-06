import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import { apiClient } from '../api/client'
import DigitalHumanView from '../views/DigitalHumanView.vue'

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async (path: string) => {
      if (path === '/digital-humans') return { data: { items: [] } }
      if (path === '/scenic-areas') return { data: [] }
      return { data: {} }
    }),
    post: vi.fn(async () => ({ data: {} })),
    put: vi.fn(async () => ({ data: {} })),
  },
}))

describe('DigitalHumanView', () => {
  it('submits avatar url and parsed config json', async () => {
    const wrapper = mount(DigitalHumanView)
    await Promise.resolve()
    await Promise.resolve()

    await wrapper.find('input[name="name"]').setValue('Guide')
    await wrapper.find('input[name="avatar_url"]').setValue('https://example.com/avatar.png')
    await wrapper.find('textarea[name="config_json"]').setValue('{"pose":"welcome"}')
    await wrapper.find('form').trigger('submit.prevent')

    expect(apiClient.post).toHaveBeenCalledWith('/digital-humans', expect.objectContaining({
      name: 'Guide',
      avatar_url: 'https://example.com/avatar.png',
      config_json: { pose: 'welcome' },
    }))
  })
})
