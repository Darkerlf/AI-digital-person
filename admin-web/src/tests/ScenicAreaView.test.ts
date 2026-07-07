import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import ScenicAreaView from '../views/ScenicAreaView.vue'
import { apiClient } from '../api/client'

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async () => ({
      data: [
        {
          id: 1,
          code: 'LS',
          name: '灵山胜境',
          description: '示范景区',
          status: 'active',
        },
      ],
    })),
    post: vi.fn(async () => ({ data: {} })),
    put: vi.fn(async () => ({ data: {} })),
    delete: vi.fn(async () => ({ data: {} })),
  },
}))

async function flushPromises() {
  await Promise.resolve()
  await Promise.resolve()
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('ScenicAreaView', () => {
  it('blocks blank create submissions and shows a validation message', async () => {
    const wrapper = mount(ScenicAreaView)
    await flushPromises()

    await wrapper.find('form').trigger('submit.prevent')

    expect(apiClient.post).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('请填写景区编码和景区名称')
  })

  it('deletes a scenic area after confirmation', async () => {
    vi.spyOn(window, 'confirm').mockReturnValueOnce(true)
    const wrapper = mount(ScenicAreaView)
    await flushPromises()

    await wrapper.find('button[name="delete-scenic-area"]').trigger('click')

    expect(apiClient.delete).toHaveBeenCalledWith('/scenic-areas/1')
  })

  it('uses shared interactive button classes for clear hover and active states', async () => {
    const wrapper = mount(ScenicAreaView)
    await flushPromises()

    expect(wrapper.find('button[type="submit"]').classes()).toContain('app-button')
    expect(wrapper.find('button[name="delete-scenic-area"]').classes()).toContain('app-button--danger')
  })
})
