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
        <li v-for="item in filteredTasks" :key="item.id">
          <div>
            <strong>{{ item.question_text }}</strong>
            <p>{{ item.correction_type }} · {{ item.status }}</p>
            <p v-if="item.linked_faq_id">关联 FAQ：#{{ item.linked_faq_id }}</p>
            <p v-if="item.linked_document_id">关联文档：#{{ item.linked_document_id }}</p>
          </div>
        </li>
      </ul>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

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

const filteredTasks = computed(() => {
  return tasks.value.filter((item) => {
    if (statusFilter.value && item.status !== statusFilter.value) {
      return false
    }
    if (typeFilter.value && item.correction_type !== typeFilter.value) {
      return false
    }
    return true
  })
})

async function loadTasks() {
  const response = await apiClient.get('/knowledge/correction-tasks')
  tasks.value = response.data.items
}

onMounted(() => {
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
</style>
