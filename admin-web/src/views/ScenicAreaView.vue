<template>
  <section class="page-shell">
    <div class="page-shell__grid scenic-area-grid">
      <form class="page-shell__panel page-shell__form" @submit.prevent="handleSubmit">
        <h2>{{ editingId ? '编辑景区' : '新增景区' }}</h2>
        <p v-if="formError" class="form-error">{{ formError }}</p>
        <input v-model="form.code" placeholder="景区编码" type="text" />
        <input v-model="form.name" placeholder="景区名称" type="text" />
        <textarea v-model="form.description" placeholder="景区描述" rows="4" />
        <select v-model="form.status">
          <option value="active">启用</option>
          <option value="inactive">停用</option>
        </select>
        <div class="page-shell__actions">
          <button class="app-button app-button--primary" type="submit">
            {{ editingId ? '更新景区' : '创建景区' }}
          </button>
          <button v-if="editingId" class="app-button app-button--ghost" type="button" @click="resetForm">
            取消编辑
          </button>
        </div>
      </form>
      <section class="page-shell__panel">
        <h2>景区列表</h2>
        <ul class="page-shell__list">
          <li v-for="item in scenicAreas" :key="item.id">
            <div class="scenic-area-item__main">
              <strong>{{ item.name || '未命名景区' }}</strong>
              <p>{{ item.code || '未设置编码' }}</p>
            </div>
            <div class="page-shell__actions">
              <button class="app-button app-button--ghost" type="button" @click="startEdit(item)">编辑</button>
              <button
                class="app-button app-button--danger"
                name="delete-scenic-area"
                type="button"
                @click="deleteScenicArea(item)"
              >
                删除
              </button>
            </div>
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
const formError = ref('')
const form = reactive({
  code: '',
  name: '',
  description: '',
  status: 'active',
})

function cleanText(value: string) {
  return value.trim()
}

async function loadScenicAreas() {
  const response = await apiClient.get('/scenic-areas')
  scenicAreas.value = response.data
}

function startEdit(item: ScenicArea) {
  formError.value = ''
  editingId.value = item.id
  form.code = item.code || ''
  form.name = item.name || ''
  form.description = item.description ?? ''
  form.status = item.status || 'active'
}

function resetForm() {
  editingId.value = null
  formError.value = ''
  form.code = ''
  form.name = ''
  form.description = ''
  form.status = 'active'
}

function buildPayload() {
  const code = cleanText(form.code)
  const name = cleanText(form.name)
  if (!code || !name) {
    formError.value = '请填写景区编码和景区名称'
    return null
  }
  formError.value = ''
  const description = cleanText(form.description)
  return {
    code,
    name,
    description: description || null,
    status: form.status,
  }
}

async function handleSubmit() {
  const payload = buildPayload()
  if (!payload) return
  if (editingId.value) {
    await apiClient.put(`/scenic-areas/${editingId.value}`, payload)
  } else {
    await apiClient.post('/scenic-areas', payload)
  }
  resetForm()
  await loadScenicAreas()
}

async function deleteScenicArea(item: ScenicArea) {
  const label = item.name || item.code || '该景区'
  if (!window.confirm(`确认删除“${label}”？删除后不可恢复。`)) return
  await apiClient.delete(`/scenic-areas/${item.id}`)
  if (editingId.value === item.id) {
    resetForm()
  }
  await loadScenicAreas()
}

onMounted(() => {
  void loadScenicAreas()
})
</script>

<style scoped>
.scenic-area-grid {
  grid-template-columns: minmax(280px, 360px) 1fr;
}

.form-error {
  margin: 0;
  color: #b91c1c;
  font-size: 14px;
}

.scenic-area-item__main {
  min-width: 0;
}
</style>
