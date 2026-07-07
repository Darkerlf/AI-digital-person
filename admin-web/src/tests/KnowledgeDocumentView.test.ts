import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'

import KnowledgeDocumentView from '../views/KnowledgeDocumentView.vue'

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
  'el-option': {
    props: ['label', 'value'],
    template: '<option :value="value"><slot>{{ label }}</slot></option>',
  },
  'el-select': {
    props: ['modelValue'],
    emits: ['update:modelValue'],
    template: '<select :value="modelValue" @change="$emit(\'update:modelValue\', $event.target.value)"><slot /></select>',
  },
  'el-table': { template: '<div><slot /></div>' },
  'el-table-column': { template: '<div><slot :row="{}" /></div>' },
}

const { deleteMock, postMock, putMock, routeMock } = vi.hoisted(() => ({
  deleteMock: vi.fn(async (_path: string) => ({ data: {} })),
  postMock: vi.fn(async (_path: string, _payload?: unknown) => ({ data: { id: 20 } })),
  putMock: vi.fn(async (_path: string, _payload?: unknown) => ({ data: {} })),
  routeMock: {
    query: {
      taskId: '9',
      question: '景区半日游路线怎么安排？',
      recognizedText: '景区半日游路线怎么安排',
      scenicAreaId: '1',
    },
  },
}))

vi.mock('vue-router', () => ({
  RouterLink: {
    template: '<a><slot /></a>',
  },
  useRoute: () => routeMock,
}))

vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(async (path: string) => {
      if (path === '/knowledge/documents') {
        return {
          data: [
            {
              id: 12,
              scenic_area_id: 1,
              title: 'Route Guide',
              doc_type: 'markdown',
              source_name: 'manual',
              content_text: 'Existing route guide',
              status: 'active',
            },
          ],
        }
      }
      if (path === '/scenic-areas') {
        return { data: [{ id: 1, name: '灵山胜境' }] }
      }
      return { data: {} }
    }),
    delete: deleteMock,
    post: postMock,
    put: putMock,
  },
}))

async function flushForm() {
  await Promise.resolve()
  await nextTick()
}

describe('KnowledgeDocumentView', () => {
  it('prefills the knowledge document form from correction task query params', async () => {
    const wrapper = mount(KnowledgeDocumentView, { global: { stubs: elementPlusStubs } })
    await flushForm()

    expect((wrapper.find('input[placeholder="文档标题"]').element as HTMLInputElement).value).toContain(
      '景区半日游路线怎么安排？',
    )
    expect((wrapper.find('textarea[placeholder="文档内容"]').element as HTMLTextAreaElement).value).toContain(
      '景区半日游路线怎么安排',
    )
  })

  it('uses a select list for document type instead of free text input', async () => {
    const wrapper = mount(KnowledgeDocumentView, { global: { stubs: elementPlusStubs } })
    await flushForm()

    const text = wrapper.text()
    expect(text).toContain('Markdown 文档')
    expect(text).toContain('Word 文档')
    expect(text).toContain('Excel 表格')
    expect(text).toContain('纯文本')
    expect(wrapper.find('input[placeholder="文档类型"]').exists()).toBe(false)
  })

  it('submits correction_task_id when creating a knowledge document from a task', async () => {
    postMock.mockClear()
    const wrapper = mount(KnowledgeDocumentView, { global: { stubs: elementPlusStubs } })
    await flushForm()

    await wrapper.find('input[placeholder^="来源名称"]').setValue('manual-entry')
    await wrapper.find('form').trigger('submit.prevent')
    await Promise.resolve()

    expect(postMock).toHaveBeenCalled()
    expect(String(postMock.mock.calls[0][0])).toContain('correction_task_id=9')
  })

  it('updates, disables, and deletes existing knowledge documents', async () => {
    putMock.mockClear()
    deleteMock.mockClear()
    const wrapper = mount(KnowledgeDocumentView, { global: { stubs: elementPlusStubs } })
    await flushForm()

    const viewModel = wrapper.vm as unknown as {
      startEdit: (item: unknown) => void
      toggleDocumentStatus: (item: { id: number; status: string }) => Promise<void>
      deleteDocument: (item: { id: number }) => Promise<void>
    }
    viewModel.startEdit({
      id: 12,
      scenic_area_id: 1,
      title: 'Route Guide',
      doc_type: 'markdown',
      source_name: 'manual',
      content_text: 'Existing route guide',
      status: 'active',
    })
    await nextTick()
    await wrapper.find('input[placeholder="文档标题"]').setValue('Updated Route Guide')
    await wrapper.find('form').trigger('submit.prevent')
    await Promise.resolve()

    expect(putMock).toHaveBeenCalledWith('/knowledge/documents/12', expect.objectContaining({
      title: 'Updated Route Guide',
    }))

    await viewModel.toggleDocumentStatus({ id: 12, status: 'active' })
    expect(putMock).toHaveBeenCalledWith('/knowledge/documents/12', { status: 'inactive' })

    await viewModel.deleteDocument({ id: 12 })
    expect(deleteMock).toHaveBeenCalledWith('/knowledge/documents/12')
  })
})
