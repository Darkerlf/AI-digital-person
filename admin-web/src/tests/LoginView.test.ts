import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import LoginView from '../views/LoginView.vue'

describe('LoginView', () => {
  it('renders username and password inputs', () => {
    const wrapper = mount(LoginView)

    expect(wrapper.text()).toContain('登录')
    expect(wrapper.find('input').exists()).toBe(true)
  })
})
