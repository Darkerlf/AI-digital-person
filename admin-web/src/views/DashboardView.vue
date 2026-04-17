<template>
  <section class="dashboard-view">
    <h2>运营概览</h2>
    <div class="dashboard-view__stats">
      <article class="dashboard-view__card">
        <span>总事件量</span>
        <strong>{{ overview.total_events }}</strong>
      </article>
      <article class="dashboard-view__card">
        <span>景点数量</span>
        <strong>{{ overview.total_spots }}</strong>
      </article>
      <article class="dashboard-view__card">
        <span>知识文档</span>
        <strong>{{ overview.total_documents }}</strong>
      </article>
      <article class="dashboard-view__card">
        <span>最近导入任务</span>
        <strong>{{ overview.recent_import_jobs.length }}</strong>
      </article>
    </div>
    <DashboardCharts :hot-spots="hotSpots" :trends="behaviorTrends" />
    <p v-if="errorMessage" class="dashboard-view__error">{{ errorMessage }}</p>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'

import { apiClient } from '../api/client'
import DashboardCharts from '../components/DashboardCharts.vue'

const overview = reactive({
  total_events: 0,
  total_spots: 0,
  total_documents: 0,
  recent_import_jobs: [] as Array<Record<string, unknown>>,
})

const hotSpots = ref<Array<Record<string, unknown>>>([])
const behaviorTrends = ref<Array<Record<string, unknown>>>([])
const errorMessage = ref('')

async function loadDashboard() {
  try {
    const [overviewResponse, hotSpotsResponse, behaviorResponse] = await Promise.all([
      apiClient.get('/dashboard/overview'),
      apiClient.get('/dashboard/hot-spots'),
      apiClient.get('/dashboard/behavior-trends'),
    ])
    Object.assign(overview, overviewResponse.data)
    hotSpots.value = hotSpotsResponse.data.items ?? hotSpotsResponse.data
    behaviorTrends.value = behaviorResponse.data.items ?? behaviorResponse.data
  } catch (error) {
    errorMessage.value = '暂时无法加载运营概览数据。'
  }
}

onMounted(() => {
  void loadDashboard()
})
</script>

<style scoped>
.dashboard-view {
  display: grid;
  gap: 24px;
}

.dashboard-view h2 {
  margin: 0;
  font-size: 30px;
}

.dashboard-view__stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
}

.dashboard-view__card {
  display: grid;
  gap: 8px;
  padding: 20px;
  border: 1px solid #dbe4f0;
  border-radius: 20px;
  background: #fff;
}

.dashboard-view__card span {
  color: #64748b;
}

.dashboard-view__card strong {
  font-size: 28px;
}

.dashboard-view__error {
  margin: 0;
  color: #b91c1c;
}

@media (max-width: 900px) {
  .dashboard-view__stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
