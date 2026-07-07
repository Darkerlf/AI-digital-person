import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

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
  beforeEach(() => {
    vi.clearAllMocks()
  })

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

  it('can create a named digital human called Lingling', async () => {
    const wrapper = mount(DigitalHumanView)
    await Promise.resolve()
    await Promise.resolve()

    await wrapper.find('input[name="name"]').setValue('灵灵')
    await wrapper.find('input[name="voice_style"]').setValue('loongbella_v3')
    await wrapper.find('input[name="default_mode"]').setValue('guide')
    await wrapper.find('textarea[name="welcome_text"]').setValue('你好，我是灵灵，欢迎来到灵山胜境。')
    await wrapper.find('form').trigger('submit.prevent')

    expect(apiClient.post).toHaveBeenCalledWith('/digital-humans', expect.objectContaining({
      name: '灵灵',
      voice_style: 'loongbella_v3',
      default_mode: 'guide',
      welcome_text: '你好，我是灵灵，欢迎来到灵山胜境。',
      status: 'active',
    }))
  })
})
