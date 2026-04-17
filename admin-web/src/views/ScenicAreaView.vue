<template>
  <section class="page-shell">
    <div class="page-shell__grid">
      <form class="page-shell__panel page-shell__form" @submit.prevent="handleSubmit">
        <h2>{{ editingId ? '编辑景区' : '新增景区' }}</h2>
        <input v-model="form.code" placeholder="景区编码" type="text" />
        <input v-model="form.name" placeholder="景区名称" type="text" />
        <textarea v-model="form.description" placeholder="景区描述" rows="4" />
        <select v-model="form.status">
          <option value="active">启用</option>
          <option value="inactive">停用</option>
        </select>
        <button type="submit">{{ editingId ? '更新景区' : '创建景区' }}</button>
      </form>
      <section class="page-shell__panel">
        <h2>景区列表</h2>
        <ul class="page-shell__list">
          <li v-for="item in scenicAreas" :key="item.id">
            <div>
              <strong>{{ item.name }}</strong>
              <p>{{ item.code }}</p>
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

type ScenicArea = {
  id: number
  code: string
  name: string
  description: string | null
  status: string
}

const scenicAreas = ref<ScenicArea[]>([])
const editingId = ref<number | null>(null)
const form = reactive({
  code: '',
  name: '',
  description: '',
  status: 'active',
})

async function loadScenicAreas() {
  const response = await apiClient.get('/scenic-areas')
  scenicAreas.value = response.data
}

function startEdit(item: ScenicArea) {
  editingId.value = item.id
  form.code = item.code
  form.name = item.name
  form.description = item.description ?? ''
  form.status = item.status
}

function resetForm() {
  editingId.value = null
  form.code = ''
  form.name = ''
  form.description = ''
  form.status = 'active'
}

async function handleSubmit() {
  const payload = {
    code: form.code,
    name: form.name,
    description: form.description || null,
    status: form.status,
  }
  if (editingId.value) {
    await apiClient.put(`/scenic-areas/${editingId.value}`, payload)
  } else {
    await apiClient.post('/scenic-areas', payload)
  }
  resetForm()
  await loadScenicAreas()
}

onMounted(() => {
  void loadScenicAreas()
})
</script>

<style scoped>
.page-shell__grid {
  display: grid;
  grid-template-columns: minmax(280px, 360px) 1fr;
  gap: 20px;
}
</style>
