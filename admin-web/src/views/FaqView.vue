<template>
  <section class="page-shell">
    <div class="page-shell__grid">
      <el-card class="page-shell__panel">
        <template #header>
          <span>{{ editingId ? '编辑 FAQ' : '新增 FAQ' }}</span>
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
          <el-form-item label="问题">
            <el-input v-model="form.question" placeholder="问题" />
          </el-form-item>
          <el-form-item label="答案">
            <el-input v-model="form.answer" type="textarea" :rows="4" placeholder="答案" />
          </el-form-item>
          <el-form-item label="分类">
            <el-input v-model="form.category" placeholder="分类" />
          </el-form-item>
          <el-form-item label="优先级">
            <el-input-number v-model="form.priority" :min="0" :max="100" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" native-type="submit">
              {{ editingId ? '更新 FAQ' : '创建 FAQ' }}
            </el-button>
            <el-button v-if="editingId" @click="resetForm">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="page-shell__panel">
        <template #header>
          <span>FAQ 列表</span>
        </template>
        <el-table :data="faqs" stripe style="width: 100%">
          <el-table-column prop="question" label="问题" />
          <el-table-column label="分类" width="120">
            <template #default="{ row }">
              <el-tag>{{ row.category ?? '未分类' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="priority" label="优先级" width="80" />
          <el-table-column label="操作" width="160">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="startEdit(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="removeFaq(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'

import { apiClient } from '../api/client'

type FaqItem = {
  id: number
  scenic_area_id: number
  question: string
  answer: string
  category: string | null
  priority: number
}

const faqs = ref<FaqItem[]>([])
const scenicAreas = ref<Array<{ id: number; name: string }>>([])
const editingId = ref<number | null>(null)
const route = useRoute()
const form = reactive({
  scenic_area_id: '',
  question: '',
  answer: '',
  category: '',
  priority: 0,
  status: 'active',
  source: '',
})

async function loadPage() {
  const [faqsResponse, areasResponse] = await Promise.all([
    apiClient.get('/knowledge/faqs'),
    apiClient.get('/scenic-areas'),
  ])
  faqs.value = faqsResponse.data.items
  scenicAreas.value = areasResponse.data
}

function startEdit(item: FaqItem) {
  editingId.value = item.id
  form.scenic_area_id = String(item.scenic_area_id)
  form.question = item.question
  form.answer = item.answer
  form.category = item.category ?? ''
  form.priority = item.priority
}

function resetForm() {
  editingId.value = null
  form.scenic_area_id = ''
  form.question = ''
  form.answer = ''
  form.category = ''
  form.priority = 0
}

function applyTaskPrefill() {
  if (typeof route.query.scenicAreaId === 'string') {
    form.scenic_area_id = route.query.scenicAreaId
  }
  if (typeof route.query.question === 'string') {
    form.question = route.query.question
  }
}

function buildCreatePath() {
  if (typeof route.query.taskId !== 'string' || !route.query.taskId) {
    return '/knowledge/faqs'
  }
  const searchParams = new URLSearchParams({
    correction_task_id: route.query.taskId,
  })
  return `/knowledge/faqs?${searchParams.toString()}`
}

async function handleSubmit() {
  const payload = {
    scenic_area_id: Number(form.scenic_area_id),
    question: form.question,
    answer: form.answer,
    category: form.category || null,
    priority: form.priority,
    status: form.status,
    source: form.source || null,
  }
  if (editingId.value) {
    await apiClient.put(`/knowledge/faqs/${editingId.value}`, payload)
  } else {
    await apiClient.post(buildCreatePath(), payload)
  }
  resetForm()
  applyTaskPrefill()
  await loadPage()
}

async function removeFaq(id: number) {
  await apiClient.delete(`/knowledge/faqs/${id}`)
  await loadPage()
}

onMounted(() => {
  applyTaskPrefill()
  void loadPage()
})
</script>
