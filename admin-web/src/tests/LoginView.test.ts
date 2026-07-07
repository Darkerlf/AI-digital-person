import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { describe, expect, it, vi } from 'vitest'

import LoginView from '../views/LoginView.vue'

const { pushMock, postMock, getMock } = vi.hoisted(() => ({
  pushMock: vi.fn(),
  postMock: vi.fn(async () => ({ data: { access_token: 'token-1', token_type: 'bearer' } })),
  getMock: vi.fn(async () => ({ data: { username: 'content_admin', role: 'content_admin' } })),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: pushMock,
  }),
}))

vi.mock('../api/client', () => ({
  apiClient: {
    post: postMock,
    get: getMock,
  },
}))

function mountLoginView() {
  return mount(LoginView, {
    global: {
      plugins: [createPinia()],
    },
  })
}

describe('LoginView', () => {
  it('renders username and password inputs', () => {
    vi.stubGlobal('localStorage', {
      getItem: vi.fn(() => ''),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    })

    const wrapper = mountLoginView()

    expect(wrapper.text()).toContain('后台登录')
    expect(wrapper.find('input[autocomplete="username"]').exists()).toBe(true)
    expect(wrapper.find('input[autocomplete="current-password"]').exists()).toBe(true)
  })

  it('renders the scenic branded login composition', () => {
    vi.stubGlobal('localStorage', {
      getItem: vi.fn(() => ''),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    })

    const wrapper = mountLoginView()

    expect(wrapper.find('.login-page').attributes('style')).toContain('--login-bg')
    expect(wrapper.text()).toContain('灵山胜境')
    expect(wrapper.text()).toContain('AI 数字人运营后台')
  })

  it('fetches profile and redirects to the role default page after login', async () => {
    const localStorageMock = {
      getItem: vi.fn((key: string) => (key === 'accessToken' ? '' : null)),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    }
    vi.stubGlobal('localStorage', localStorageMock)
    pushMock.mockReset()
    postMock.mockClear()
    getMock.mockClear()

    const wrapper = mountLoginView()

    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('content_admin')
    await inputs[1].setValue('content123')
    await wrapper.find('form').trigger('submit.prevent')
    await Promise.resolve()
    await Promise.resolve()

    expect(postMock).toHaveBeenCalledWith('/auth/login', {
      username: 'content_admin',
      password: 'content123',
    })
    expect(getMock).toHaveBeenCalledWith('/auth/me')
    expect(localStorageMock.setItem).toHaveBeenCalledWith('role', 'content_admin')
    expect(pushMock).toHaveBeenCalledWith('/knowledge/documents')
  })
})
