import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ImportUploadCard from '../components/ImportUploadCard.vue'

describe('ImportUploadCard', () => {
  it('emits the selected browser file and scenic area id', async () => {
    const wrapper = mount(ImportUploadCard, {
      props: {
        title: 'Knowledge import',
        description: 'Upload a local file from browser',
        requireScenicArea: true,
        scenicAreas: [{ id: 3, name: 'Area 3' }],
      },
    })
    const file = new File(['guide content'], 'guide.txt', { type: 'text/plain' })
    const fileInput = wrapper.find('input[type="file"]')

    Object.defineProperty(fileInput.element, 'files', {
      value: [file],
      configurable: true,
    })
    await fileInput.trigger('change')
    await wrapper.find('select').setValue('3')
    await wrapper.find('button').trigger('click')

    expect(wrapper.emitted('submit')?.[0][0]).toEqual({
      file,
      scenicAreaId: 3,
    })
  })
})
