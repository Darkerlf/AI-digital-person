<template>
  <section class="page-shell">
    <div class="page-shell__grid">
      <form class="page-shell__panel page-shell__form" @submit.prevent="handleSubmit">
        <h2>{{ editingId ? '编辑数字人' : '新增数字人' }}</h2>
        <select v-model="form.scenic_area_id">
          <option value="">全局配置</option>
          <option v-for="item in scenicAreas" :key="item.id" :value="String(item.id)">
            {{ item.name }}
          </option>
        </select>
        <input v-model="form.name" placeholder="数字人名称" type="text" />
        <input v-model="form.voice_style" placeholder="音色风格" type="text" />
        <input v-model="form.default_mode" placeholder="默认模式" type="text" />
        <textarea v-model="form.welcome_text" placeholder="欢迎语" rows="4" />
        <button type="submit">{{ editingId ? '更新配置' : '创建配置' }}</button>
      </form>
      <section class="page-shell__panel">
        <h2>数字人列表</h2>
        <ul class="page-shell__list">
          <li v-for="item in items" :key="item.id">
            <div>
              <strong>{{ item.name }}</strong>
              <p>{{ item.voice_style ?? '未设置音色' }}</p>
            </div>
            <button type="button" @click="startEdit(item)">编辑</button>
          </li>
        </ul>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'

import { apiClient } from '../api/client'

type DigitalHumanItem = {
  id: number
  scenic_area_id: number | null
  name: string
  voice_style: string | null
  welcome_text: string | null
  default_mode: string | null
  status: string
}

const items = ref<DigitalHumanItem[]>([])
const scenicAreas = ref<Array<{ id: number; name: string }>>([])
const editingId = ref<number | null>(null)
const form = reactive({
  scenic_area_id: '',
  name: '',
  voice_style: '',
  welcome_text: '',
  default_mode: '',
  status: 'active',
})

async function loadPage() {
  const [itemsResponse, areasResponse] = await Promise.all([
    apiClient.get('/digital-humans'),
    apiClient.get('/scenic-areas'),
  ])
  items.value = itemsResponse.data.items
  scenicAreas.value = areasResponse.data
}

function startEdit(item: DigitalHumanItem) {
  editingId.value = item.id
  form.scenic_area_id = item.scenic_area_id ? String(item.scenic_area_id) : ''
  form.name = item.name
  form.voice_style = item.voice_style ?? ''
  form.welcome_text = item.welcome_text ?? ''
  form.default_mode = item.default_mode ?? ''
}

async function handleSubmit() {
  const payload = {
    scenic_area_id: form.scenic_area_id ? Number(form.scenic_area_id) : null,
    name: form.name,
    voice_style: form.voice_style || null,
    welcome_text: form.welcome_text || null,
    default_mode: form.default_mode || null,
    status: form.status,
  }
  if (editingId.value) {
    await apiClient.put(`/digital-humans/${editingId.value}`, payload)
  } else {
    await apiClient.post('/digital-humans', payload)
  }
  editingId.value = null
  await loadPage()
}

onMounted(() => {
  void loadPage()
})
</script>
