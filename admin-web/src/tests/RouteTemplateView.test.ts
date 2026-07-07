import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import RouteTemplateView from '../views/RouteTemplateView.vue'

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async (path: string) => {
      if (path === '/scenic-areas') {
        return { data: [{ id: 1, code: 'LS', name: '灵山胜境', description: null, status: 'active' }] }
      }
      if (path === '/scenic-spots') {
        return { data: { items: [{ id: 1, scenic_area_id: 1, spot_code: 'LS-001', name: '灵山大佛' }] } }
      }
      if (path === '/route-templates') {
        return { data: { items: [] } }
      }
      return { data: {} }
    }),
    post: vi.fn(async () => ({
      data: {
        matched_template: { id: 1, name: '经典半日游', template_type: 'fixed', scenic_area_id: 1, priority: 10 },
        fallback_used: false,
        match_reason: '命中时长与兴趣标签条件，返回最佳路线模板。',
        summary: '覆盖核心文化景点的半日路线。',
        spots: [{ scenic_spot_id: 1, name: '灵山大佛', stay_minutes: 90, highlight: '核心地标' }],
      },
    })),
    put: vi.fn(async () => ({ data: {} })),
    delete: vi.fn(async () => ({ data: {} })),
  },
}))

async function flushPromises() {
  await Promise.resolve()
  await Promise.resolve()
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('RouteTemplateView', () => {
  it('renders template management and preview areas', async () => {
    const wrapper = mount(RouteTemplateView)
    await flushPromises()

    expect(wrapper.text()).toContain('路线模板管理')
    expect(wrapper.text()).toContain('推荐预览')
  })

  it('explains numeric fields with labels, units and examples', async () => {
    const wrapper = mount(RouteTemplateView)
    await flushPromises()

    const text = wrapper.text()
    expect(text).toContain('最短适用时长')
    expect(text).toContain('最长适用时长')
    expect(text).toContain('单位：分钟')
    expect(text).toContain('优先级')
    expect(text).toContain('数字越大越优先')
    expect(text).toContain('站点顺序')
    expect(text).toContain('站点停留时间')
    expect(text).toContain('预览游玩时长')
  })
})
