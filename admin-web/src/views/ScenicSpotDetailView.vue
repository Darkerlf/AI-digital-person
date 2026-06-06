<template>
  <section class="page-shell">
    <form class="page-shell__panel page-shell__form" @submit.prevent="handleSubmit">
      <h2>景点详情</h2>
      <input v-model="form.spot_code" name="spot_code" placeholder="景点编码" type="text" />
      <input v-model="form.name" name="name" placeholder="景点名称" type="text" />
      <input v-model="form.alias" name="alias" placeholder="别名" type="text" />
      <input v-model="form.cover_image_url" name="cover_image_url" placeholder="封面图片 URL" type="url" />
      <input v-model="form.location_text" name="location_text" placeholder="位置描述" type="text" />
      <input v-model="form.target_audience" name="target_audience" placeholder="适配人群" type="text" />
      <input
        v-model="form.suggested_duration_minutes"
        name="suggested_duration_minutes"
        placeholder="建议停留分钟数"
        type="number"
      />
      <input v-model="form.tags" name="tags" placeholder="标签，逗号分隔" type="text" />
      <textarea v-model="form.guide_text" name="guide_text" placeholder="讲解词" rows="4" />
      <textarea v-model="form.detail_intro" name="detail_intro" placeholder="详细介绍" rows="4" />
      <textarea v-model="form.highlights" name="highlights" placeholder="亮点" rows="3" />
      <textarea v-model="form.parameters_text" name="parameters_text" placeholder="参数信息" rows="3" />
      <textarea v-model="form.core_function" name="core_function" placeholder="核心功能" rows="3" />
      <textarea v-model="form.cultural_value" name="cultural_value" placeholder="文化价值" rows="3" />
      <textarea v-model="form.performance_info" name="performance_info" placeholder="演艺/开放信息" rows="3" />
      <textarea v-model="form.remarks" name="remarks" placeholder="备注" rows="3" />
      <select v-model="form.open_status" name="open_status">
        <option value="open">开放</option>
        <option value="closed">关闭</option>
      </select>
      <button type="submit">保存景点</button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'

import { apiClient } from '../api/client'

const route = useRoute()
const spotId = Number(route.params.id)

const form = reactive({
  scenic_area_id: 0,
  spot_code: '',
  name: '',
  alias: '',
  cover_image_url: '',
  location_text: '',
  target_audience: '',
  suggested_duration_minutes: '',
  guide_text: '',
  detail_intro: '',
  highlights: '',
  parameters_text: '',
  core_function: '',
  cultural_value: '',
  performance_info: '',
  remarks: '',
  tags: '',
  open_status: 'open',
})

async function loadSpot() {
  const response = await apiClient.get(`/scenic-spots/${spotId}`)
  form.scenic_area_id = response.data.scenic_area_id
  form.spot_code = response.data.spot_code
  form.name = response.data.name
  form.alias = response.data.alias ?? ''
  form.cover_image_url = response.data.cover_image_url ?? ''
  form.location_text = response.data.location_text ?? ''
  form.target_audience = response.data.target_audience ?? ''
  form.suggested_duration_minutes =
    response.data.suggested_duration_minutes != null ? String(response.data.suggested_duration_minutes) : ''
  form.guide_text = response.data.guide_text ?? ''
  form.detail_intro = response.data.detail_intro ?? ''
  form.highlights = response.data.highlights ?? ''
  form.parameters_text = response.data.parameters_text ?? ''
  form.core_function = response.data.core_function ?? ''
  form.cultural_value = response.data.cultural_value ?? ''
  form.performance_info = response.data.performance_info ?? ''
  form.remarks = response.data.remarks ?? ''
  form.tags = response.data.tags.join(', ')
  form.open_status = response.data.open_status
}

async function handleSubmit() {
  await apiClient.put(`/scenic-spots/${spotId}`, {
    scenic_area_id: form.scenic_area_id,
    spot_code: form.spot_code,
    name: form.name,
    alias: form.alias || null,
    cover_image_url: form.cover_image_url || null,
    location_text: form.location_text || null,
    target_audience: form.target_audience || null,
    suggested_duration_minutes: parseOptionalNumber(form.suggested_duration_minutes),
    guide_text: form.guide_text || null,
    detail_intro: form.detail_intro || null,
    highlights: form.highlights || null,
    parameters_text: form.parameters_text || null,
    core_function: form.core_function || null,
    cultural_value: form.cultural_value || null,
    performance_info: form.performance_info || null,
    remarks: form.remarks || null,
    tags: form.tags
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean),
    open_status: form.open_status,
  })
}

function parseOptionalNumber(value: string) {
  const normalized = value.trim()
  if (!normalized) return null
  const parsed = Number(normalized)
  return Number.isFinite(parsed) ? parsed : null
}

onMounted(() => {
  void loadSpot()
})
</script>
