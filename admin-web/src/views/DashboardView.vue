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
    <p v-if="chartMessage" class="dashboard-view__notice">{{ chartMessage }}</p>
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
const chartMessage = ref('')

async function loadOverview() {
  const response = await apiClient.get('/dashboard/overview')
  Object.assign(overview, response.data)
}

async function loadCharts() {
  const [hotSpotsResult, behaviorResult] = await Promise.allSettled([
    apiClient.get('/dashboard/hot-spots'),
    apiClient.get('/dashboard/behavior-trends'),
  ])

  if (hotSpotsResult.status === 'fulfilled') {
    hotSpots.value = hotSpotsResult.value.data.items ?? hotSpotsResult.value.data
  } else {
    hotSpots.value = []
  }

  if (behaviorResult.status === 'fulfilled') {
    behaviorTrends.value = behaviorResult.value.data.items ?? behaviorResult.value.data
  } else {
    behaviorTrends.value = []
  }

  chartMessage.value =
    hotSpotsResult.status === 'rejected' || behaviorResult.status === 'rejected'
      ? '图表数据暂时无法加载，概览数据仍可正常查看。'
      : ''
}

async function loadDashboard() {
  errorMessage.value = ''
  chartMessage.value = ''
  try {
    await loadOverview()
  } catch {
    errorMessage.value = '暂时无法加载运营概览数据。'
    return
  }
  await loadCharts()
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

.dashboard-view__notice {
  margin: 0;
  color: #936520;
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
