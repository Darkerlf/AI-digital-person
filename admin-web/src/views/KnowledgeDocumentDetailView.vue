<template>
  <section class="page-shell">
    <section class="page-shell__panel">
      <h2>{{ document.title }}</h2>
      <p>{{ document.doc_type }} · {{ document.source_name }}</p>
      <pre class="page-shell__pre">{{ document.content_text }}</pre>
    </section>
    <KnowledgeChunkPreview :items="chunks" />
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'

import { apiClient } from '../api/client'
import KnowledgeChunkPreview from '../components/KnowledgeChunkPreview.vue'

const route = useRoute()
const documentId = Number(route.params.id)

const document = reactive({
  title: '',
  doc_type: '',
  source_name: '',
  content_text: '',
})
const chunks = ref<Array<{ id: number; chunk_index: number; chunk_text: string }>>([])

async function loadPage() {
  const [documentResponse, chunksResponse] = await Promise.all([
    apiClient.get(`/knowledge/documents/${documentId}`),
    apiClient.get(`/knowledge/documents/${documentId}/chunks`),
  ])
  Object.assign(document, documentResponse.data)
  chunks.value = chunksResponse.data.items
}

onMounted(() => {
  void loadPage()
})
</script>
