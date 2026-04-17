import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'

import KnowledgeDocumentView from '../views/KnowledgeDocumentView.vue'

const { postMock, routeMock } = vi.hoisted(() => ({
  postMock: vi.fn(async (_path: string, _payload?: unknown) => ({ data: { id: 20 } })),
  routeMock: {
    query: {
      taskId: '9',
      question: '景区半日游路线怎么安排？',
      recognizedText: '景区半日游路线怎么安排',
      scenicAreaId: '1',
    },
  },
}))

vi.mock('vue-router', () => ({
  RouterLink: {
    template: '<a><slot /></a>',
  },
  useRoute: () => routeMock,
}))

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async (path: string) => {
      if (path === '/knowledge/documents') {
        return { data: [] }
      }
      if (path === '/scenic-areas') {
        return { data: [{ id: 1, name: '灵山胜境' }] }
      }
      return { data: {} }
    }),
    post: postMock,
  },
}))

describe('KnowledgeDocumentView', () => {
  it('prefills the knowledge document form from correction task query params', async () => {
    const wrapper = mount(KnowledgeDocumentView)
    await Promise.resolve()
    await nextTick()

    expect((wrapper.find('input[placeholder="文档标题"]').element as HTMLInputElement).value).toContain(
      '景区半日游路线怎么安排？',
    )
    expect((wrapper.find('textarea[placeholder="文档内容"]').element as HTMLTextAreaElement).value).toContain(
      '景区半日游路线怎么安排',
    )
  })

  it('submits correction_task_id when creating a knowledge document from a task', async () => {
    postMock.mockClear()
    const wrapper = mount(KnowledgeDocumentView)
    await Promise.resolve()
    await nextTick()

    await wrapper.find('input[placeholder="来源名称"]').setValue('manual-entry')
    await wrapper.find('form').trigger('submit.prevent')
    await Promise.resolve()

    expect(postMock).toHaveBeenCalled()
    expect(String(postMock.mock.calls[0][0])).toContain('correction_task_id=9')
  })
})
