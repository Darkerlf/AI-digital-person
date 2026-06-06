import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'

import AdminUserView from '../views/AdminUserView.vue'

const { getMock, postMock, putMock } = vi.hoisted(() => ({
  getMock: vi.fn(async () => ({
    data: {
      items: [
        {
          id: 2,
          username: 'content_admin',
          role: 'content_admin',
          status: 'active',
          last_login_at: null,
        },
      ],
    },
  })),
  postMock: vi.fn(async () => ({ data: { id: 3 } })),
  putMock: vi.fn(async () => ({ data: { id: 2 } })),
}))

vi.mock('../api/client', () => ({
  apiClient: {
    get: getMock,
    post: postMock,
    put: putMock,
  },
}))

describe('AdminUserView', () => {
  it('renders admin user management copy in Chinese', async () => {
    const wrapper = mount(AdminUserView)
    await Promise.resolve()
    await nextTick()

    expect(wrapper.text()).toContain('新增管理员')
    expect(wrapper.text()).toContain('管理员列表')
    expect(wrapper.text()).toContain('内容管理员 / 启用')
    expect(wrapper.text()).toContain('创建用户')
    expect(wrapper.find('input[placeholder="用户名"]').exists()).toBe(true)
    expect(wrapper.find('input[placeholder="密码"]').exists()).toBe(true)
    expect(wrapper.text()).not.toContain('Create Admin User')
    expect(wrapper.text()).not.toContain('Admin Users')
  })

  it('loads admin users and creates a new user', async () => {
    const wrapper = mount(AdminUserView)
    await Promise.resolve()
    await nextTick()

    expect(getMock).toHaveBeenCalledWith('/settings/admin-users')
    expect(wrapper.text()).toContain('content_admin')

    await wrapper.find('input[placeholder="用户名"]').setValue('ops_admin')
    await wrapper.find('input[placeholder="密码"]').setValue('ops123456')
    await wrapper.find('select[name="role"]').setValue('ops_admin')
    await wrapper.find('select[name="status"]').setValue('active')
    await wrapper.find('form').trigger('submit.prevent')

    expect(postMock).toHaveBeenCalledWith('/settings/admin-users', {
      username: 'ops_admin',
      password: 'ops123456',
      role: 'ops_admin',
      status: 'active',
    })
  })

  it('edits an existing user role status and password', async () => {
    const wrapper = mount(AdminUserView)
    await Promise.resolve()
    await nextTick()

    await wrapper.find('button[data-test="edit-user-2"]').trigger('click')
    await wrapper.find('select[name="role"]').setValue('ops_admin')
    await wrapper.find('select[name="status"]').setValue('inactive')
    await wrapper.find('input[placeholder="密码"]').setValue('newpass123')
    await wrapper.find('form').trigger('submit.prevent')

    expect(putMock).toHaveBeenCalledWith('/settings/admin-users/2', {
      role: 'ops_admin',
      status: 'inactive',
      password: 'newpass123',
    })
  })
})
