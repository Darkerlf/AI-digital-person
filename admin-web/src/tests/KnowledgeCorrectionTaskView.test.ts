import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'

import KnowledgeCorrectionTaskView from '../views/KnowledgeCorrectionTaskView.vue'

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async () => ({
      data: {
        items: [
          {
            id: 9,
            question_text: '景区半日游路线怎么安排？',
            correction_type: 'faq',
            status: 'open',
            linked_faq_id: null,
            linked_document_id: null,
          },
        ],
      },
    })),
  },
}))

describe('KnowledgeCorrectionTaskView', () => {
  it('renders the correction task title', async () => {
    const wrapper = mount(KnowledgeCorrectionTaskView)
    await Promise.resolve()
    await nextTick()

    expect(wrapper.text()).toContain('知识修正任务')
    expect(wrapper.text()).toContain('景区半日游路线怎么安排？')
  })
})
