import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import KnowledgeDocumentDetailView from '../views/KnowledgeDocumentDetailView.vue'

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { id: '12' } }),
}))

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async (path: string) => {
      if (path === '/knowledge/documents/12') {
        return {
          data: {
            id: 12,
            scenic_area_id: 1,
            title: '灵山胜境导览',
            doc_type: 'docx',
            source_name: 'guide.docx',
            content_text: '这里是完整文档正文。'.repeat(40),
            status: 'active',
            version: 1,
          },
        }
      }
      if (path === '/knowledge/documents/12/chunks') {
        throw new Error('chunk api failed')
      }
      return { data: {} }
    }),
  },
}))

async function flushPromises() {
  await Promise.resolve()
  await Promise.resolve()
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('KnowledgeDocumentDetailView', () => {
  it('shows document content even when chunk preview fails', async () => {
    const wrapper = mount(KnowledgeDocumentDetailView)
    await flushPromises()

    expect(wrapper.text()).toContain('灵山胜境导览')
    expect(wrapper.text()).toContain('这里是完整文档正文。')
    expect(wrapper.text()).toContain('后端分块接口暂时无法加载')
    expect(wrapper.text()).toContain('已按正文临时分段展示')
    expect(wrapper.text()).not.toContain('暂无知识分块')
  })
})
