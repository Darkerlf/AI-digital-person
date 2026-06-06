<template>
  <section class="page-shell">
    <div class="page-shell__grid">
      <form class="page-shell__panel page-shell__form" @submit.prevent="handleSubmit">
        <h2>{{ editingId ? '编辑数字人' : '新增数字人' }}</h2>
        <select v-model="form.scenic_area_id" name="scenic_area_id">
          <option value="">全局配置</option>
          <option v-for="item in scenicAreas" :key="item.id" :value="String(item.id)">
            {{ item.name }}
          </option>
        </select>
        <input v-model="form.name" name="name" placeholder="数字人名称" type="text" />
        <input v-model="form.avatar_url" name="avatar_url" placeholder="外观资源 URL" type="url" />
        <input v-model="form.voice_style" name="voice_style" placeholder="音色风格" type="text" />
        <input v-model="form.default_mode" name="default_mode" placeholder="默认模式，如 guide/chat" type="text" />
        <select v-model="form.status" name="status">
          <option value="active">启用</option>
          <option value="inactive">停用</option>
        </select>
        <textarea v-model="form.welcome_text" name="welcome_text" placeholder="欢迎语" rows="4" />
        <textarea v-model="form.config_json" name="config_json" placeholder='配置 JSON，如 {"pose":"welcome"}' rows="6" />
        <p v-if="configError" class="page-shell__error">{{ configError }}</p>
        <button type="submit">{{ editingId ? '更新配置' : '创建配置' }}</button>
      </form>

      <section class="page-shell__panel">
        <h2>基础预览</h2>
        <div class="digital-preview">
          <img v-if="previewAvatarUrl" :src="previewAvatarUrl" alt="数字人外观预览" />
          <div v-else class="digital-preview__empty">未配置外观</div>
          <strong>{{ form.name || '未命名数字人' }}</strong>
          <p>{{ form.welcome_text || '暂无欢迎语' }}</p>
          <small>{{ form.default_mode || '未设置默认模式' }} · {{ form.status === 'active' ? '启用' : '停用' }}</small>
        </div>
      </section>

      <section class="page-shell__panel">
        <h2>数字人列表</h2>
        <ul class="page-shell__list">
          <li v-for="item in items" :key="item.id">
            <div>
              <strong>{{ item.name }}</strong>
              <p>{{ item.voice_style ?? '未设置音色' }} · {{ item.status === 'active' ? '启用' : '停用' }}</p>
            </div>
            <button type="button" @click="startEdit(item)">编辑</button>
          </li>
        </ul>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'

import { apiClient } from '../api/client'

type DigitalHumanItem = {
  id: number
  scenic_area_id: number | null
  name: string
  avatar_url: string | null
  voice_style: string | null
  welcome_text: string | null
  default_mode: string | null
  config_json: Record<string, unknown> | null
  status: string
}

const items = ref<DigitalHumanItem[]>([])
const scenicAreas = ref<Array<{ id: number; name: string }>>([])
const editingId = ref<number | null>(null)
const configError = ref('')
const form = reactive({
  scenic_area_id: '',
  name: '',
  avatar_url: '',
  voice_style: '',
  welcome_text: '',
  default_mode: '',
  config_json: '',
  status: 'active',
})

const previewAvatarUrl = computed(() => form.avatar_url.trim())

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
  form.avatar_url = item.avatar_url ?? ''
  form.voice_style = item.voice_style ?? ''
  form.welcome_text = item.welcome_text ?? ''
  form.default_mode = item.default_mode ?? ''
  form.config_json = item.config_json ? JSON.stringify(item.config_json, null, 2) : ''
  form.status = item.status
}

async function handleSubmit() {
  configError.value = ''
  let parsedConfig: Record<string, unknown> | null = null
  if (form.config_json.trim()) {
    try {
      parsedConfig = JSON.parse(form.config_json)
    } catch {
      configError.value = '配置 JSON 格式不正确'
      return
    }
  }

  const payload = {
    scenic_area_id: form.scenic_area_id ? Number(form.scenic_area_id) : null,
    name: form.name,
    avatar_url: form.avatar_url || null,
    voice_style: form.voice_style || null,
    welcome_text: form.welcome_text || null,
    default_mode: form.default_mode || null,
    config_json: parsedConfig,
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

<style scoped>
.digital-preview {
  display: grid;
  gap: 10px;
}

.digital-preview img,
.digital-preview__empty {
  width: 180px;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 8px;
  background: #e2e8f0;
}

.digital-preview__empty {
  display: grid;
  place-items: center;
  color: #64748b;
}

.page-shell__error {
  margin: 0;
  color: #dc2626;
}
</style>
