<template>
  <section class="dashboard-charts">
    <div class="dashboard-panel">
      <h3>热门景点</h3>
      <ul v-if="hotSpots.length" class="dashboard-list">
        <li v-for="item in hotSpots" :key="String(item.spot_name ?? item.name ?? item.id)">
          <span>{{ item.spot_name ?? item.name ?? '未命名景点' }}</span>
          <strong>{{ item.event_count ?? item.value ?? 0 }}</strong>
        </li>
      </ul>
      <p v-else>暂无热门景点数据。</p>
    </div>
    <div class="dashboard-panel">
      <h3>行为趋势</h3>
      <ul v-if="trends.length" class="dashboard-list">
        <li v-for="item in trends" :key="String(item.stat_date ?? item.date ?? item.id)">
          <span>{{ item.stat_date ?? item.date ?? '未知日期' }}</span>
          <strong>{{ item.total_events ?? item.value ?? 0 }}</strong>
        </li>
      </ul>
      <p v-else>暂无行为趋势数据。</p>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  hotSpots: Array<Record<string, unknown>>
  trends: Array<Record<string, unknown>>
}>()
</script>

<style scoped>
.dashboard-charts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.dashboard-panel {
  padding: 20px;
  border: 1px solid #dbe4f0;
  border-radius: 20px;
  background: #fff;
}

.dashboard-panel h3 {
  margin: 0 0 16px;
}

.dashboard-list {
  display: grid;
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.dashboard-list li {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

@media (max-width: 900px) {
  .dashboard-charts {
    grid-template-columns: 1fr;
  }
}
</style>
