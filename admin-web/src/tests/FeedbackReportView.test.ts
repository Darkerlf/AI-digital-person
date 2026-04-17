import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import FeedbackReportView from '../views/FeedbackReportView.vue'

describe('FeedbackReportView', () => {
  it('renders the feedback report title', () => {
    const wrapper = mount(FeedbackReportView)

    expect(wrapper.text()).toContain('游客感受度报告')
  })
})
