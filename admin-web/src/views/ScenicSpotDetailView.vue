<template>
  <section class="page-shell">
    <form class="page-shell__panel page-shell__form" @submit.prevent="handleSubmit">
      <h2>景点详情</h2>
      <input v-model="form.spot_code" placeholder="景点编码" type="text" />
      <input v-model="form.name" placeholder="景点名称" type="text" />
      <input v-model="form.alias" placeholder="别名" type="text" />
      <input v-model="form.location_text" placeholder="位置描述" type="text" />
      <input v-model="form.tags" placeholder="标签，逗号分隔" type="text" />
      <select v-model="form.open_status">
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
  location_text: '',
  tags: '',
  open_status: 'open',
})

async function loadSpot() {
  const response = await apiClient.get(`/scenic-spots/${spotId}`)
  form.scenic_area_id = response.data.scenic_area_id
  form.spot_code = response.data.spot_code
  form.name = response.data.name
  form.alias = response.data.alias ?? ''
  form.location_text = response.data.location_text ?? ''
  form.tags = response.data.tags.join(', ')
  form.open_status = response.data.open_status
}

async function handleSubmit() {
  await apiClient.put(`/scenic-spots/${spotId}`, {
    scenic_area_id: form.scenic_area_id,
    spot_code: form.spot_code,
    name: form.name,
    alias: form.alias || null,
    location_text: form.location_text || null,
    tags: form.tags
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean),
    open_status: form.open_status,
  })
}

onMounted(() => {
  void loadSpot()
})
</script>
