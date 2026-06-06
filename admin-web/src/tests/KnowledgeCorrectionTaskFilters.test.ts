import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'

import KnowledgeCorrectionTaskView from '../views/KnowledgeCorrectionTaskView.vue'
import { apiClient } from '../api/client'

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async () => ({
      data: {
        items: [],
      },
    })),
  },
}))

describe('KnowledgeCorrectionTaskView filters', () => {
  it('reloads tasks with server-side filter params', async () => {
    const wrapper = mount(KnowledgeCorrectionTaskView)
    await Promise.resolve()
    await nextTick()

    const selects = wrapper.findAll('select')
    await selects[0].setValue('open')
    await selects[1].setValue('document')
    await Promise.resolve()

    expect(apiClient.get).toHaveBeenLastCalledWith('/knowledge/correction-tasks', {
      params: {
        status: 'open',
        correction_type: 'document',
      },
    })
  })
})
