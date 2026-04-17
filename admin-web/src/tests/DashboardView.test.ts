import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import DashboardView from '../views/DashboardView.vue'

describe('DashboardView', () => {
  it('renders the overview title', () => {
    const wrapper = mount(DashboardView, {
      global: {
        stubs: {
          RouterLink: {
            template: '<a><slot /></a>',
          },
        },
      },
    })

    expect(wrapper.text()).toContain('运营概览')
  })
})
