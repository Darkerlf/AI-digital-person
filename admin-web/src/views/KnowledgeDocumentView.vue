<template>
  <section class="page-shell">
    <div class="page-shell__grid">
      <form class="page-shell__panel page-shell__form" @submit.prevent="handleSubmit">
        <h2>新增知识文档</h2>
        <select v-model="form.scenic_area_id">
          <option value="">选择景区</option>
          <option v-for="item in scenicAreas" :key="item.id" :value="String(item.id)">
            {{ item.name }}
          </option>
        </select>
        <input v-model="form.title" placeholder="文档标题" type="text" />
        <input v-model="form.doc_type" placeholder="文档类型" type="text" />
        <input v-model="form.source_name" placeholder="来源名称" type="text" />
        <textarea v-model="form.content_text" placeholder="文档内容" rows="6" />
        <button type="submit">上传文档</button>
      </form>
      <section class="page-shell__panel">
        <h2>文档列表</h2>
        <ul class="page-shell__list">
          <li v-for="item in documents" :key="item.id">
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.doc_type }} · {{ item.source_name }}</p>
            </div>
            <RouterLink :to="`/knowledge/documents/${item.id}`">查看</RouterLink>
          </li>
        </ul>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { apiClient } from '../api/client'

type KnowledgeDocumentItem = {
  id: number
  title: string
  doc_type: string
  source_name: string
}

const documents = ref<KnowledgeDocumentItem[]>([])
const scenicAreas = ref<Array<{ id: number; name: string }>>([])
const form = reactive({
  scenic_area_id: '',
  title: '',
  doc_type: 'markdown',
  source_name: '',
  content_text: '',
})

async function loadPage() {
  const [documentsResponse, areasResponse] = await Promise.all([
    apiClient.get('/knowledge/documents'),
    apiClient.get('/scenic-areas'),
  ])
  documents.value = documentsResponse.data
  scenicAreas.value = areasResponse.data
}

async function handleSubmit() {
  await apiClient.post('/knowledge/documents/upload', {
    scenic_area_id: Number(form.scenic_area_id),
    title: form.title,
    doc_type: form.doc_type,
    source_name: form.source_name,
    content_text: form.content_text,
  })
  form.title = ''
  form.source_name = ''
  form.content_text = ''
  await loadPage()
}

onMounted(() => {
  void loadPage()
})
</script>
