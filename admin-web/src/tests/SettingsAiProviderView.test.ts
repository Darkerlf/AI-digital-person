import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import SettingsAiProviderView from '../views/SettingsAiProviderView.vue'

const { putMock } = vi.hoisted(() => ({
  putMock: vi.fn(async (_path: string, _payload?: unknown) => ({ data: {} })),
}))

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async () => ({
      data: {
        items: [
          {
            id: 8,
            provider_name: 'qwen',
            model_type: 'chat',
            endpoint: 'https://example.com',
            api_key_masked: '****abcd',
            extra_config_json: { temperature: 0.2, stream: true },
            status: 'active',
          },
        ],
      },
    })),
    post: vi.fn(async (_path: string, _payload?: unknown) => ({ data: {} })),
    put: putMock,
  },
}))

describe('SettingsAiProviderView', () => {
  it('edits extra_config_json as formatted JSON and submits parsed config', async () => {
    const wrapper = mount(SettingsAiProviderView)
    await flushPromises()

    await wrapper.find('button[type="button"]').trigger('click')
    const textarea = wrapper.find('textarea[name="extra_config_json"]')
    expect((textarea.element as HTMLTextAreaElement).value).toContain('"temperature": 0.2')

    await textarea.setValue('{"temperature":0.6,"top_p":0.9}')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(putMock).toHaveBeenCalledWith('/settings/ai-providers/8', expect.objectContaining({
      extra_config_json: { temperature: 0.6, top_p: 0.9 },
    }))
  })
})
