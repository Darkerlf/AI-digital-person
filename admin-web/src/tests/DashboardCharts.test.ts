import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

const echartsMock = vi.hoisted(() => ({
  options: [] as Array<Record<string, unknown>>,
}))

vi.mock('echarts', () => ({
  init: vi.fn(() => ({
    setOption: vi.fn((option: Record<string, unknown>) => {
      echartsMock.options.push(option)
    }),
    resize: vi.fn(),
    dispose: vi.fn(),
  })),
  graphic: {
    LinearGradient: vi.fn(function LinearGradient() {
      return 'linear-gradient'
    }),
  },
}))

import DashboardCharts from '../components/DashboardCharts.vue'

describe('DashboardCharts', () => {
  it('explains chart axes and data meaning in Chinese', () => {
    echartsMock.options = []

    const wrapper = mount(DashboardCharts, {
      props: {
        hotSpots: [['灵山大佛', 24]],
        trends: [{ date: '2026-05-01', count: 12 }],
      },
      attachTo: document.body,
    })

    expect(wrapper.text()).toContain('横轴：行为事件次数')
    expect(wrapper.text()).toContain('纵轴：行为事件次数')
    expect(wrapper.text()).toContain('统计口径')
    expect(echartsMock.options[0]).toMatchObject({
      xAxis: { name: '行为事件次数' },
    })
    expect(echartsMock.options[1]).toMatchObject({
      yAxis: { name: '行为事件次数' },
    })

    wrapper.unmount()
  })
})
