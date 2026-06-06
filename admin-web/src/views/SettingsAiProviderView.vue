<template>
  <section class="page-shell">
    <div class="page-shell__grid">
      <form class="page-shell__panel page-shell__form" @submit.prevent="handleSubmit">
        <h2>{{ editingId ? '编辑 AI 提供商' : '新增 AI 提供商' }}</h2>
        <input v-model="form.provider_name" placeholder="提供商名称" type="text" />
        <input v-model="form.model_type" placeholder="模型类型" type="text" />
        <input v-model="form.endpoint" placeholder="接口地址" type="text" />
        <input v-model="form.api_key_masked" placeholder="脱敏 API Key" type="text" />
        <textarea
          v-model="form.extra_config_json"
          name="extra_config_json"
          placeholder='扩展配置 JSON，例如 {"temperature":0.7}'
          rows="7"
        />
        <p v-if="jsonError" class="form-error">{{ jsonError }}</p>
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
              <p>{{ item.model_type }} - {{ item.status }}</p>
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
  extra_config_json: Record<string, unknown> | null
  status: string
}

const items = ref<Provider[]>([])
const editingId = ref<number | null>(null)
const jsonError = ref('')
const form = reactive({
  provider_name: '',
  model_type: '',
  endpoint: '',
  api_key_masked: '',
  extra_config_json: '',
  status: 'inactive',
})

async function loadProviders() {
  const response = await apiClient.get('/settings/ai-providers')
  items.value = response.data.items
}

function formatExtraConfig(value: Record<string, unknown> | null) {
  return value ? JSON.stringify(value, null, 2) : ''
}

function parseExtraConfig() {
  jsonError.value = ''
  if (!form.extra_config_json.trim()) {
    return null
  }
  try {
    const parsed = JSON.parse(form.extra_config_json)
    if (parsed === null || Array.isArray(parsed) || typeof parsed !== 'object') {
      jsonError.value = '扩展配置必须是 JSON 对象'
      return undefined
    }
    return parsed as Record<string, unknown>
  } catch {
    jsonError.value = '扩展配置不是合法 JSON'
    return undefined
  }
}

function startEdit(item: Provider) {
  editingId.value = item.id
  jsonError.value = ''
  form.provider_name = item.provider_name
  form.model_type = item.model_type
  form.endpoint = item.endpoint ?? ''
  form.api_key_masked = item.api_key_masked ?? ''
  form.extra_config_json = formatExtraConfig(item.extra_config_json)
  form.status = item.status
}

async function handleSubmit() {
  const extraConfig = parseExtraConfig()
  if (extraConfig === undefined) {
    return
  }
  const payload = {
    provider_name: form.provider_name,
    model_type: form.model_type,
    endpoint: form.endpoint || null,
    api_key_masked: form.api_key_masked || null,
    extra_config_json: extraConfig,
    status: form.status,
  }
  if (editingId.value) {
    await apiClient.put(`/settings/ai-providers/${editingId.value}`, payload)
  } else {
    await apiClient.post('/settings/ai-providers', payload)
  }
  editingId.value = null
  form.provider_name = ''
  form.model_type = ''
  form.endpoint = ''
  form.api_key_masked = ''
  form.extra_config_json = ''
  form.status = 'inactive'
  await loadProviders()
}

onMounted(() => {
  void loadProviders()
})
</script>

<style scoped>
.form-error {
  margin: 0;
  color: #b91c1c;
  font-size: 14px;
}
</style>
