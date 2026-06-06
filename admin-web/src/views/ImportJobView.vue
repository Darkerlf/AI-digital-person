<template>
  <section class="page-shell">
    <div class="page-shell__grid">
      <ImportUploadCard
        description="上传结构化景点文档，系统会自动解析并入库。"
        title="景点导入"
        @submit="submitScenicImport"
      />
      <ImportUploadCard
        description="上传知识文档，并绑定到指定景区。"
        require-scenic-area
        :scenic-areas="scenicAreas"
        title="知识文档导入"
        @submit="submitKnowledgeImport"
      />
      <ImportUploadCard
        description="上传游客行为分析 Excel 文件。"
        title="行为数据导入"
        @submit="submitBehaviorImport"
      />
    </div>
    <section class="page-shell__panel">
      <h2>导入任务</h2>
      <ul class="page-shell__list">
        <li v-for="item in jobs" :key="item.id">
          <div>
            <strong>{{ item.job_type }}</strong>
            <p>{{ item.status }} - {{ item.source_file_name }}</p>
          </div>
          <RouterLink :to="`/imports/${item.id}`">查看</RouterLink>
        </li>
      </ul>
    </section>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { apiClient } from '../api/client'
import ImportUploadCard from '../components/ImportUploadCard.vue'

type ImportJob = {
  id: number
  job_type: string
  status: string
  source_file_name: string
}

type UploadPayload = {
  file: File
  scenicAreaId: number | null
}

const jobs = ref<ImportJob[]>([])
const scenicAreas = ref<Array<{ id: number; name: string }>>([])

async function loadPage() {
  const [jobsResponse, areasResponse] = await Promise.all([
    apiClient.get('/imports/jobs'),
    apiClient.get('/scenic-areas'),
  ])
  jobs.value = jobsResponse.data.items
  scenicAreas.value = areasResponse.data
}

function buildFormData(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return formData
}

async function submitScenicImport(payload: UploadPayload) {
  await apiClient.post('/imports/scenic-spots/upload', buildFormData(payload.file))
  await loadPage()
}

async function submitKnowledgeImport(payload: UploadPayload) {
  await apiClient.post(
    `/imports/knowledge-docs/upload?scenic_area_id=${payload.scenicAreaId ?? ''}`,
    buildFormData(payload.file),
  )
  await loadPage()
}

async function submitBehaviorImport(payload: UploadPayload) {
  await apiClient.post('/imports/behavior-events/upload', buildFormData(payload.file))
  await loadPage()
}

onMounted(() => {
  void loadPage()
})
</script>
