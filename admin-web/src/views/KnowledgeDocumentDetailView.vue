<template>
  <section class="page-shell">
    <section class="page-shell__panel">
      <h2>{{ document.title || '知识文档详情' }}</h2>
      <p class="document-meta">{{ document.doc_type }} · {{ document.source_name }}</p>
      <p v-if="documentError" class="document-error">{{ documentError }}</p>
      <pre v-else class="page-shell__pre">{{ document.content_text || '暂无文档正文。' }}</pre>
    </section>
    <p v-if="chunkError" class="document-warning">{{ chunkError }}</p>
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
const documentError = ref('')
const chunkError = ref('')

function buildFallbackChunks(content: string) {
  const normalized = content.trim()
  if (!normalized) return []
  const chunkSize = 800
  const result: Array<{ id: number; chunk_index: number; chunk_text: string }> = []
  for (let start = 0; start < normalized.length; start += chunkSize) {
    result.push({
      id: -(result.length + 1),
      chunk_index: result.length,
      chunk_text: normalized.slice(start, start + chunkSize),
    })
  }
  return result
}

async function loadDocument() {
  try {
    const response = await apiClient.get(`/knowledge/documents/${documentId}`)
    Object.assign(document, response.data)
  } catch {
    documentError.value = '知识文档详情暂时无法加载。'
  }
}

async function loadChunks() {
  try {
    const response = await apiClient.get(`/knowledge/documents/${documentId}/chunks`)
    chunks.value = response.data.items ?? []
    chunkError.value = ''
  } catch {
    chunks.value = buildFallbackChunks(document.content_text)
    chunkError.value = chunks.value.length
      ? '后端分块接口暂时无法加载，已按正文临时分段展示。'
      : '知识分块暂时无法加载，文档正文仍可查看。'
  }
}

async function loadPage() {
  await loadDocument()
  await loadChunks()
}

onMounted(() => {
  void loadPage()
})
</script>

<style scoped>
.document-meta {
  color: #64748b;
}

.document-error {
  color: #b91c1c;
}

.document-warning {
  margin: 0;
  padding: 12px 16px;
  border: 1px solid #fde68a;
  border-radius: 12px;
  color: #92400e;
  background: #fffbeb;
}
</style>
