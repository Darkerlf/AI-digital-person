import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'

import FaqView from '../views/FaqView.vue'

const elementPlusStubs = {
  'el-button': { template: '<button><slot /></button>' },
  'el-card': { template: '<section><slot name="header" /><slot /></section>' },
  'el-form': { template: '<form><slot /></form>' },
  'el-form-item': { template: '<label><slot /></label>' },
  'el-input': {
    props: ['modelValue', 'placeholder', 'type'],
    emits: ['update:modelValue'],
    template:
      '<textarea v-if="type === \'textarea\'" :placeholder="placeholder" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />' +
      '<input v-else :placeholder="placeholder" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
  },
  'el-input-number': {
    props: ['modelValue'],
    emits: ['update:modelValue'],
    template: '<input type="number" :value="modelValue" @input="$emit(\'update:modelValue\', Number($event.target.value))" />',
  },
  'el-option': { template: '<option><slot /></option>' },
  'el-select': {
    props: ['modelValue'],
    emits: ['update:modelValue'],
    template: '<select :value="modelValue" @change="$emit(\'update:modelValue\', $event.target.value)"><slot /></select>',
  },
  'el-table': { template: '<div><slot /></div>' },
  'el-table-column': { template: '<div><slot :row="{}" /></div>' },
  'el-tag': { template: '<span><slot /></span>' },
}

const { postMock, routeMock } = vi.hoisted(() => ({
  postMock: vi.fn(async (_path: string, _payload?: unknown) => ({ data: { id: 10 } })),
  routeMock: {
    query: {
      taskId: '9',
      question: '景区半日游路线怎么安排？',
      scenicAreaId: '1',
    },
  },
}))

vi.mock('vue-router', () => ({
  useRoute: () => routeMock,
}))

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async (path: string) => {
      if (path === '/knowledge/faqs') {
        return { data: { items: [] } }
      }
      if (path === '/scenic-areas') {
        return { data: [{ id: 1, name: '灵山胜境' }] }
      }
      return { data: {} }
    }),
    post: postMock,
    put: vi.fn(async () => ({ data: {} })),
    delete: vi.fn(async () => ({ data: {} })),
  },
}))

describe('FaqView', () => {
  it('prefills the FAQ form from correction task query params', async () => {
    const wrapper = mount(FaqView, { global: { stubs: elementPlusStubs } })
    await Promise.resolve()
    await nextTick()

    const questionInput = wrapper.find('input[placeholder="问题"]')
    expect((questionInput.element as HTMLInputElement).value).toContain('景区半日游路线怎么安排？')
  })

  it('submits correction_task_id when creating a FAQ from a task', async () => {
    postMock.mockClear()
    const wrapper = mount(FaqView, { global: { stubs: elementPlusStubs } })
    await Promise.resolve()
    await nextTick()

    await wrapper.find('textarea[placeholder="答案"]').setValue('建议先游览核心景点。')
    await wrapper.find('form').trigger('submit.prevent')
    await Promise.resolve()

    expect(postMock).toHaveBeenCalled()
    expect(String(postMock.mock.calls[0][0])).toContain('correction_task_id=9')
  })
})
