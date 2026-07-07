import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'

import KnowledgeCorrectionTaskView from '../views/KnowledgeCorrectionTaskView.vue'

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async () => ({
      data: {
        items: [],
      },
    })),
  },
}))

describe('KnowledgeCorrectionTaskView empty state', () => {
  it('explains why the task list is empty', async () => {
    const wrapper = mount(KnowledgeCorrectionTaskView)
    await Promise.resolve()
    await nextTick()

    expect(wrapper.text()).toContain('暂无知识修正任务')
    expect(wrapper.text()).toContain('会话管理')
    expect(wrapper.text()).toContain('未命中问题')
  })
})
