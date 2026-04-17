<template>
  <section class="page-shell">
    <section class="page-shell__panel">
      <h2>导入任务详情</h2>
      <pre class="page-shell__pre">{{ JSON.stringify(job, null, 2) }}</pre>
    </section>
    <section class="page-shell__panel">
      <h2>任务明细</h2>
      <pre class="page-shell__pre">{{ JSON.stringify(items, null, 2) }}</pre>
    </section>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { apiClient } from '../api/client'

const route = useRoute()
const jobId = Number(route.params.id)

const job = ref<Record<string, unknown>>({})
const items = ref<Array<Record<string, unknown>>>([])

async function loadPage() {
  const [jobResponse, itemsResponse] = await Promise.all([
    apiClient.get(`/imports/jobs/${jobId}`),
    apiClient.get(`/imports/jobs/${jobId}/items`),
  ])
  job.value = jobResponse.data
  items.value = itemsResponse.data.items
}

onMounted(() => {
  void loadPage()
})
</script>
