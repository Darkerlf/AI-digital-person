import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'

import FaqView from '../views/FaqView.vue'

const { postMock, routeMock } = vi.hoisted(() => ({
  postMock: vi.fn(async (_path: string, _payload?: unknown) => ({ data: { id: 10 } })),
  routeMock: {
    query: {
      taskId: '9',
      question: '景区半日游路线怎么安排？',
      scenicAreaId: '1',
    },
  },
}))

vi.mock('vue-router', () => ({
  useRoute: () => routeMock,
}))

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async (path: string) => {
      if (path === '/knowledge/faqs') {
        return { data: { items: [] } }
      }
      if (path === '/scenic-areas') {
        return { data: [{ id: 1, name: '灵山胜境' }] }
      }
      return { data: {} }
    }),
    post: postMock,
    put: vi.fn(async () => ({ data: {} })),
    delete: vi.fn(async () => ({ data: {} })),
  },
}))

describe('FaqView', () => {
  it('prefills the FAQ form from correction task query params', async () => {
    const wrapper = mount(FaqView)
    await Promise.resolve()
    await nextTick()

    const questionInput = wrapper.find('input[placeholder="问题"]')
    expect((questionInput.element as HTMLInputElement).value).toContain('景区半日游路线怎么安排？')
  })

  it('submits correction_task_id when creating a FAQ from a task', async () => {
    postMock.mockClear()
    const wrapper = mount(FaqView)
    await Promise.resolve()
    await nextTick()

    await wrapper.find('textarea[placeholder="答案"]').setValue('建议先游览核心景点。')
    await wrapper.find('form').trigger('submit.prevent')
    await Promise.resolve()

    expect(postMock).toHaveBeenCalled()
    expect(String(postMock.mock.calls[0][0])).toContain('correction_task_id=9')
  })
})
