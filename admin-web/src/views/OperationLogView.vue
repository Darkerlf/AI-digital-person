<template>
  <section class="page-shell">
    <section class="page-shell__panel">
      <h2>操作日志</h2>
      <ul class="page-shell__list">
        <li v-for="item in items" :key="item.id">
          <div>
            <strong>{{ item.module }} / {{ item.action }}</strong>
            <p>{{ item.target_type }} #{{ item.target_id ?? '-' }}</p>
          </div>
        </li>
      </ul>
    </section>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { apiClient } from '../api/client'

type OperationLogItem = {
  id: number
  module: string
  action: string
  target_type: string | null
  target_id: number | null
}

const items = ref<OperationLogItem[]>([])

async function loadLogs() {
  const response = await apiClient.get('/operation-logs')
  items.value = response.data.items
}

onMounted(() => {
  void loadLogs()
})
</script>
