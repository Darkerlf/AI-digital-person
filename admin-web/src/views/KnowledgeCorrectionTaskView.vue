<template>
  <section class="page-shell">
    <section class="page-shell__panel">
      <h2>知识修正任务</h2>
      <div class="correction-task-toolbar">
        <select v-model="statusFilter">
          <option value="">全部状态</option>
          <option value="open">open</option>
          <option value="resolved">resolved</option>
        </select>
        <select v-model="typeFilter">
          <option value="">全部类型</option>
          <option value="faq">faq</option>
          <option value="document">document</option>
        </select>
      </div>
      <ul class="page-shell__list">
        <li v-for="item in tasks" :key="item.id">
          <div>
            <strong>{{ item.question_text }}</strong>
            <p>{{ item.correction_type }} · {{ item.status }}</p>
            <p v-if="item.linked_faq_id">关联 FAQ：#{{ item.linked_faq_id }}</p>
            <p v-if="item.linked_document_id">关联文档：#{{ item.linked_document_id }}</p>
          </div>
        </li>
      </ul>
      <p v-if="loadError" class="correction-task-message correction-task-message--error">{{ loadError }}</p>
      <div v-else-if="!isLoading && tasks.length === 0" class="correction-task-empty">
        <strong>暂无知识修正任务</strong>
        <p>
          当前没有待处理任务。知识修正任务通常从“会话管理”中的未命中问题创建，
          也会在补充 FAQ 或知识文档并关联任务后变为已解决。
        </p>
      </div>
      <p v-if="isLoading" class="correction-task-message">正在加载知识修正任务...</p>
    </section>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

import { apiClient } from '../api/client'

type CorrectionTask = {
  id: number
  question_text: string
  correction_type: string
  status: string
  linked_faq_id: number | null
  linked_document_id: number | null
}

const tasks = ref<CorrectionTask[]>([])
const statusFilter = ref('')
const typeFilter = ref('')
const isLoading = ref(false)
const loadError = ref('')

async function loadTasks() {
  isLoading.value = true
  loadError.value = ''
  const params: Record<string, string> = {}
  if (statusFilter.value) {
    params.status = statusFilter.value
  }
  if (typeFilter.value) {
    params.correction_type = typeFilter.value
  }
  try {
    const response = Object.keys(params).length
      ? await apiClient.get('/knowledge/correction-tasks', { params })
      : await apiClient.get('/knowledge/correction-tasks')
    tasks.value = response.data.items
  } catch {
    tasks.value = []
    loadError.value = '知识修正任务暂时无法加载，请稍后重试。'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  void loadTasks()
})

watch([statusFilter, typeFilter], () => {
  void loadTasks()
})
</script>

<style scoped>
.correction-task-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.correction-task-toolbar select {
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
}

.correction-task-empty,
.correction-task-message {
  margin: 0;
  padding: 16px;
  color: #475569;
  background: #f8fafc;
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  line-height: 1.7;
}

.correction-task-empty strong {
  display: block;
  margin-bottom: 6px;
  color: #0f172a;
}

.correction-task-empty p {
  margin: 0;
}

.correction-task-message--error {
  color: #b42318;
  background: #fff4ed;
  border-style: solid;
  border-color: #ffd6ae;
}
</style>
