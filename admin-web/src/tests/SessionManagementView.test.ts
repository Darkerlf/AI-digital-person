import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import SessionManagementView from '../views/SessionManagementView.vue'

const { pushMock } = vi.hoisted(() => ({
  pushMock: vi.fn(),
}))

vi.mock('vue-router', () => ({
  RouterLink: {
    template: '<a><slot /></a>',
  },
  useRouter: () => ({
    push: pushMock,
  }),
}))

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async (path: string) => {
      if (path === '/sessions') {
        return { data: { items: [] } }
      }
      if (path === '/sessions/unresolved') {
        return {
          data: {
            items: [
              {
                id: 11,
                session_id: 1,
                scenic_area_id: 3,
                session_key: 'session-001',
                question_text: '景区半日游路线怎么安排？',
                recognized_text: '景区半日游路线怎么安排',
                feedback_status: 'disliked',
                resolution_status: 'pending',
                correction_task: null,
              },
            ],
          },
        }
      }
      return { data: { id: 1, session_key: 'session-001', messages: [] } }
    }),
    post: vi.fn(async () => ({ data: { id: 9, correction_type: 'faq', status: 'open' } })),
    put: vi.fn(async () => ({ data: {} })),
  },
}))

describe('SessionManagementView', () => {
  it('renders the session management title', () => {
    const wrapper = mount(SessionManagementView, {
    })

    expect(wrapper.text()).toContain('会话记录与问题修正')
  })

  it('renders correction task creation actions for unresolved questions', async () => {
    const wrapper = mount(SessionManagementView)

    await Promise.resolve()
    await Promise.resolve()

    expect(wrapper.text()).toContain('创建 FAQ 修正任务')
    expect(wrapper.text()).toContain('创建文档修正任务')
  })

  it('passes scenicAreaId when starting a correction task flow', async () => {
    pushMock.mockReset()
    const wrapper = mount(SessionManagementView)

    await Promise.resolve()
    await Promise.resolve()

    await wrapper.find('button').trigger('click')
    await Promise.resolve()
    await Promise.resolve()

    expect(pushMock).toHaveBeenCalledWith({
      path: '/knowledge/faqs',
      query: {
        taskId: '9',
        question: '景区半日游路线怎么安排？',
        recognizedText: '景区半日游路线怎么安排',
        scenicAreaId: '3',
      },
    })
  })
})
