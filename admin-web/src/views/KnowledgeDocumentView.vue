<template>
  <section class="page-shell">
    <div class="page-shell__grid">
      <el-card class="page-shell__panel">
        <template #header>
          <span>{{ editingId ? '编辑知识文档' : '新增知识文档' }}</span>
        </template>
        <el-form :model="form" label-position="top" @submit.prevent="handleSubmit">
          <el-form-item label="景区">
            <el-select v-model="form.scenic_area_id" placeholder="选择景区" style="width: 100%">
              <el-option
                v-for="item in scenicAreas"
                :key="item.id"
                :label="item.name"
                :value="String(item.id)"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="文档标题">
            <el-input v-model="form.title" placeholder="文档标题" />
          </el-form-item>
          <el-form-item label="文档类型">
            <el-input v-model="form.doc_type" placeholder="文档类型" />
          </el-form-item>
          <el-form-item label="来源名称">
            <el-input v-model="form.source_name" placeholder="来源名称" />
          </el-form-item>
          <el-form-item label="文档内容">
            <el-input v-model="form.content_text" type="textarea" :rows="6" placeholder="文档内容" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" native-type="submit">
              {{ editingId ? '保存修改' : '上传文档' }}
            </el-button>
            <el-button v-if="editingId" type="default" @click="resetForm">取消编辑</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="page-shell__panel">
        <template #header>
          <span>文档列表</span>
        </template>
        <el-table :data="documents" stripe style="width: 100%">
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="doc_type" label="类型" width="120" />
          <el-table-column prop="source_name" label="来源" width="150" />
          <el-table-column prop="status" label="状态" width="100" />
          <el-table-column label="操作" width="220">
            <template #default="{ row }">
              <RouterLink :to="`/knowledge/documents/${row.id}`">
                <el-button size="small" type="primary" link>查看</el-button>
              </RouterLink>
              <el-button size="small" type="primary" link @click="startEdit(row)">编辑</el-button>
              <el-button size="small" type="warning" link @click="toggleDocumentStatus(row)">
                {{ row.status === 'active' ? '停用' : '启用' }}
              </el-button>
              <el-button size="small" type="danger" link @click="deleteDocument(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import { apiClient } from '../api/client'

type KnowledgeDocumentItem = {
  id: number
  scenic_area_id: number
  title: string
  doc_type: string
  source_name: string
  content_text: string
  status: string
}

const documents = ref<KnowledgeDocumentItem[]>([])
const scenicAreas = ref<Array<{ id: number; name: string }>>([])
const route = useRoute()
const editingId = ref<number | null>(null)
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

function applyTaskPrefill() {
  if (typeof route.query.scenicAreaId === 'string') {
    form.scenic_area_id = route.query.scenicAreaId
  }
  if (typeof route.query.question === 'string') {
    form.title = route.query.question
  }
  if (typeof route.query.recognizedText === 'string') {
    form.content_text = route.query.recognizedText
  }
}

function buildCreatePath() {
  if (typeof route.query.taskId !== 'string' || !route.query.taskId) {
    return '/knowledge/documents/upload'
  }
  const searchParams = new URLSearchParams({
    correction_task_id: route.query.taskId,
  })
  return `/knowledge/documents/upload?${searchParams.toString()}`
}

function buildPayload() {
  return {
    scenic_area_id: Number(form.scenic_area_id),
    title: form.title,
    doc_type: form.doc_type,
    source_name: form.source_name,
    content_text: form.content_text,
  }
}

function resetForm() {
  editingId.value = null
  form.scenic_area_id = ''
  form.title = ''
  form.doc_type = 'markdown'
  form.source_name = ''
  form.content_text = ''
  applyTaskPrefill()
}

function startEdit(item: KnowledgeDocumentItem) {
  editingId.value = item.id
  form.scenic_area_id = String(item.scenic_area_id)
  form.title = item.title
  form.doc_type = item.doc_type
  form.source_name = item.source_name
  form.content_text = item.content_text
}

async function handleSubmit() {
  if (editingId.value) {
    await apiClient.put(`/knowledge/documents/${editingId.value}`, buildPayload())
  } else {
    await apiClient.post(buildCreatePath(), buildPayload())
  }
  resetForm()
  await loadPage()
}

async function toggleDocumentStatus(item: { id: number; status: string }) {
  await apiClient.put(`/knowledge/documents/${item.id}`, {
    status: item.status === 'active' ? 'inactive' : 'active',
  })
  await loadPage()
}

async function deleteDocument(item: { id: number }) {
  await apiClient.delete(`/knowledge/documents/${item.id}`)
  await loadPage()
}

onMounted(() => {
  applyTaskPrefill()
  void loadPage()
})

defineExpose({
  deleteDocument,
  startEdit,
  toggleDocumentStatus,
})
</script>
