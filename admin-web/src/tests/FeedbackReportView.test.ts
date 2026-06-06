import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import FeedbackReportView from '../views/FeedbackReportView.vue'

const { getMock } = vi.hoisted(() => ({
  getMock: vi.fn(async (path: string) => {
    if (path === '/scenic-areas') {
      return { data: [{ id: 3, name: '灵山胜境' }] }
    }
    return {
      data: {
        total_feedback: 1,
        average_score: 2,
        sentiment_distribution: {
          positive: 0,
          neutral: 0,
          negative: 1,
        },
        suggestion_summary: '优先补充门票价格知识。',
        latest_feedback: [
          {
            id: 9,
            message_id: 18,
            session_id: 7,
            sentiment: 'negative',
            score: 2,
            content: '门票价格回答不够准确。',
            question_text: '门票多少钱？',
            answer_text: '请以景区公告为准。',
            created_at: '2026-05-31T10:00:00',
          },
        ],
        feedback_trend: [
          { date: '2026-05-31', total_feedback: 1, average_score: 2, negative_count: 1 },
        ],
        focus_top_n: [{ name: '门票', count: 2 }],
        complaint_top_n: [{ name: '价格', count: 1 }],
        negative_reason_top_n: [{ reason: '价格', count: 1 }],
        route_feedback_analysis: [
          { route_name: '经典路线', total_feedback: 1, average_score: 2, negative_count: 1 },
        ],
      },
    }
  }),
}))

vi.mock('../api/client', () => ({
  apiClient: {
    get: getMock,
  },
}))

describe('FeedbackReportView', () => {
  it('renders detailed report analysis and submits filters as query params', async () => {
    const wrapper = mount(FeedbackReportView)
    await flushPromises()

    expect(wrapper.text()).toContain('游客感受度报告')
    expect(wrapper.text()).toContain('评价明细')
    expect(wrapper.text()).toContain('反馈趋势')
    expect(wrapper.text()).toContain('差评归因')
    expect(wrapper.text()).toContain('路线反馈分析')
    expect(wrapper.text()).toContain('门票价格回答不够准确。')
    expect(wrapper.text()).toContain('门票多少钱？')
    expect(wrapper.text()).toContain('2 星')
    expect(wrapper.text()).toContain('经典路线')

    await wrapper.find('input[name="start_date"]').setValue('2026-05-01')
    await wrapper.find('select[name="source_type"]').setValue('route')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(getMock).toHaveBeenLastCalledWith('/dashboard/feedback-report', {
      params: {
        start_date: '2026-05-01',
        source_type: 'route',
      },
    })
  })
})
