<template>
  <section class="page-shell">
    <div class="page-shell__grid service-poi-grid">
      <form class="page-shell__panel page-shell__form" @submit.prevent="handleSubmit">
        <h2>{{ editingId ? '编辑便民服务点' : '新增便民服务点' }}</h2>
        <select v-model.number="form.scenic_area_id">
          <option :value="null">不绑定景区</option>
          <option v-for="area in scenicAreas" :key="area.id" :value="area.id">{{ area.name }}</option>
        </select>
        <input v-model="form.name" placeholder="服务点名称" type="text" required />
        <select v-model="form.category" name="category" required>
          <option value="toilet">公共厕所</option>
          <option value="service_center">游客中心</option>
          <option value="restaurant">餐饮</option>
          <option value="parking">停车场</option>
          <option value="other">其他</option>
        </select>
        <input v-model="form.area_text" placeholder="所在区域" type="text" />
        <input v-model="form.open_hours" placeholder="开放时间" type="text" />
        <div class="coordinate-row">
          <input v-model="form.latitude" placeholder="纬度" type="number" step="0.000001" />
          <input v-model="form.longitude" placeholder="经度" type="number" step="0.000001" />
        </div>
        <textarea v-model="form.description" placeholder="服务说明" rows="4" />
        <select v-model="form.status">
          <option value="active">启用</option>
          <option value="inactive">停用</option>
        </select>
        <button type="submit">{{ editingId ? '更新服务点' : '创建服务点' }}</button>
        <button v-if="editingId" class="secondary-btn" type="button" @click="resetForm">取消编辑</button>
      </form>

      <section class="page-shell__panel">
        <h2>便民服务点管理</h2>
        <ul class="page-shell__list">
          <li v-for="item in pois" :key="item.id">
            <div>
              <strong>{{ item.name }}</strong>
              <p>{{ categoryLabel(item.category) }} · {{ item.area_text || '景区内' }}</p>
              <p>坐标：{{ formatCoordinate(item.latitude) }}，{{ formatCoordinate(item.longitude) }}</p>
            </div>
            <div class="page-shell__actions">
              <button type="button" @click="startEdit(item)">编辑</button>
              <button type="button" @click="deletePoi(item)">删除</button>
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

type ScenicAreaOption = {
  id: number
  name: string
}

type ServicePOI = {
  id: number
  scenic_area_id: number | null
  name: string
  category: string
  area_text: string | null
  description: string | null
  open_hours: string | null
  latitude: number | null
  longitude: number | null
  status: string
}

const categories: Record<string, string> = {
  toilet: '公共厕所',
  service_center: '游客中心',
  restaurant: '餐饮',
  parking: '停车场',
  other: '其他',
}

const pois = ref<ServicePOI[]>([])
const scenicAreas = ref<ScenicAreaOption[]>([])
const editingId = ref<number | null>(null)
const form = reactive({
  scenic_area_id: null as number | null,
  name: '',
  category: 'toilet',
  area_text: '',
  description: '',
  open_hours: '',
  latitude: '',
  longitude: '',
  status: 'active',
})

async function loadPage() {
  const [poisResponse, areasResponse] = await Promise.all([
    apiClient.get('/service-pois'),
    apiClient.get('/scenic-areas'),
  ])
  pois.value = poisResponse.data.items || []
  scenicAreas.value = areasResponse.data || []
}

function toOptionalNumber(value: string) {
  if (value === '') return null
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

function buildPayload() {
  return {
    scenic_area_id: form.scenic_area_id,
    name: form.name,
    category: form.category,
    area_text: form.area_text || null,
    description: form.description || null,
    open_hours: form.open_hours || null,
    latitude: toOptionalNumber(form.latitude),
    longitude: toOptionalNumber(form.longitude),
    status: form.status,
  }
}

async function handleSubmit() {
  const payload = buildPayload()
  if (editingId.value) {
    await apiClient.put(`/service-pois/${editingId.value}`, payload)
  } else {
    await apiClient.post('/service-pois', payload)
  }
  resetForm()
  await loadPage()
}

function startEdit(item: ServicePOI) {
  editingId.value = item.id
  form.scenic_area_id = item.scenic_area_id
  form.name = item.name
  form.category = item.category
  form.area_text = item.area_text || ''
  form.description = item.description || ''
  form.open_hours = item.open_hours || ''
  form.latitude = item.latitude == null ? '' : String(item.latitude)
  form.longitude = item.longitude == null ? '' : String(item.longitude)
  form.status = item.status
}

async function deletePoi(item: ServicePOI) {
  await apiClient.delete(`/service-pois/${item.id}`)
  if (editingId.value === item.id) {
    resetForm()
  }
  await loadPage()
}

function resetForm() {
  editingId.value = null
  form.scenic_area_id = null
  form.name = ''
  form.category = 'toilet'
  form.area_text = ''
  form.description = ''
  form.open_hours = ''
  form.latitude = ''
  form.longitude = ''
  form.status = 'active'
}

function categoryLabel(value: string) {
  return categories[value] || value
}

function formatCoordinate(value: number | null) {
  return value == null ? '未填写' : value.toFixed(6)
}

onMounted(() => {
  void loadPage()
})
</script>

<style scoped>
.service-poi-grid {
  grid-template-columns: minmax(320px, 420px) 1fr;
}

.coordinate-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.secondary-btn {
  background: #64748b;
}
</style>
