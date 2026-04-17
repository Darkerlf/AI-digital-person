<template>
  <section class="page-shell">
    <div class="page-shell__grid">
      <form class="page-shell__panel page-shell__form" @submit.prevent="handleSubmit">
        <h2>{{ editingId ? '编辑 AI 提供商' : '新增 AI 提供商' }}</h2>
        <input v-model="form.provider_name" placeholder="提供商名称" type="text" />
        <input v-model="form.model_type" placeholder="模型类型" type="text" />
        <input v-model="form.endpoint" placeholder="接口地址" type="text" />
        <input v-model="form.api_key_masked" placeholder="脱敏 API Key" type="text" />
        <select v-model="form.status">
          <option value="active">启用</option>
          <option value="inactive">停用</option>
        </select>
        <button type="submit">{{ editingId ? '更新配置' : '创建配置' }}</button>
      </form>
      <section class="page-shell__panel">
        <h2>AI 提供商列表</h2>
        <ul class="page-shell__list">
          <li v-for="item in items" :key="item.id">
            <div>
              <strong>{{ item.provider_name }}</strong>
              <p>{{ item.model_type }} · {{ item.status }}</p>
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

type Provider = {
  id: number
  provider_name: string
  model_type: string
  endpoint: string | null
  api_key_masked: string | null
  status: string
}

const items = ref<Provider[]>([])
const editingId = ref<number | null>(null)
const form = reactive({
  provider_name: '',
  model_type: '',
  endpoint: '',
  api_key_masked: '',
  status: 'inactive',
})

async function loadProviders() {
  const response = await apiClient.get('/settings/ai-providers')
  items.value = response.data.items
}

function startEdit(item: Provider) {
  editingId.value = item.id
  form.provider_name = item.provider_name
  form.model_type = item.model_type
  form.endpoint = item.endpoint ?? ''
  form.api_key_masked = item.api_key_masked ?? ''
  form.status = item.status
}

async function handleSubmit() {
  const payload = {
    provider_name: form.provider_name,
    model_type: form.model_type,
    endpoint: form.endpoint || null,
    api_key_masked: form.api_key_masked || null,
    status: form.status,
  }
  if (editingId.value) {
    await apiClient.put(`/settings/ai-providers/${editingId.value}`, payload)
  } else {
    await apiClient.post('/settings/ai-providers', payload)
  }
  editingId.value = null
  await loadProviders()
}

onMounted(() => {
  void loadProviders()
})
</script>
