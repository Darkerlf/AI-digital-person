<template>
  <section class="page-shell">
    <div class="page-shell__grid">
      <form class="page-shell__panel page-shell__form" @submit.prevent="handleSubmit">
        <h2>{{ editingId ? '编辑 FAQ' : '新增 FAQ' }}</h2>
        <select v-model="form.scenic_area_id">
          <option value="">选择景区</option>
          <option v-for="item in scenicAreas" :key="item.id" :value="String(item.id)">
            {{ item.name }}
          </option>
        </select>
        <input v-model="form.question" placeholder="问题" type="text" />
        <textarea v-model="form.answer" placeholder="答案" rows="4" />
        <input v-model="form.category" placeholder="分类" type="text" />
        <input v-model.number="form.priority" placeholder="优先级" type="number" />
        <button type="submit">{{ editingId ? '更新 FAQ' : '创建 FAQ' }}</button>
      </form>
      <section class="page-shell__panel">
        <h2>FAQ 列表</h2>
        <ul class="page-shell__list">
          <li v-for="item in faqs" :key="item.id">
            <div>
              <strong>{{ item.question }}</strong>
              <p>{{ item.category ?? '未分类' }}</p>
            </div>
            <div class="page-shell__actions">
              <button type="button" @click="startEdit(item)">编辑</button>
              <button type="button" @click="removeFaq(item.id)">删除</button>
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
    await apiClient.post('/knowledge/faqs', payload)
  }
  resetForm()
  await loadPage()
}

async function removeFaq(id: number) {
  await apiClient.delete(`/knowledge/faqs/${id}`)
  await loadPage()
}

onMounted(() => {
  void loadPage()
})
</script>
