<template>
  <section class="dashboard-charts">
    <div class="chart-card">
      <h3>热门景点 TOP5</h3>
      <div ref="barChartRef" class="chart-container" />
    </div>
    <div class="chart-card">
      <h3>游客行为趋势</h3>
      <div ref="lineChartRef" class="chart-container" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  hotSpots: Array<Record<string, unknown>>
  trends: Array<Record<string, unknown>>
}>()

const barChartRef = ref<HTMLDivElement>()
const lineChartRef = ref<HTMLDivElement>()
let barChart: echarts.ECharts | null = null
let lineChart: echarts.ECharts | null = null

function renderBarChart() {
  if (!barChartRef.value || !props.hotSpots?.length) return
  if (!barChart) barChart = echarts.init(barChartRef.value)

  const sorted = [...props.hotSpots]
    .map(s => ({
      name: String(s.spot_name ?? s.name ?? '未命名'),
      count: Number(s.event_count ?? s.value ?? 0),
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5)

  barChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '8%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: { type: 'value' },
    yAxis: {
      type: 'category',
      data: sorted.map(s => s.name),
      axisLabel: { fontSize: 12 },
    },
    series: [{
      type: 'bar',
      data: sorted.map(s => s.count),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#1a73e8' },
          { offset: 1, color: '#4fc3f7' },
        ]),
      },
      barWidth: '60%',
    }],
  })
}

function renderLineChart() {
  if (!lineChartRef.value || !props.trends?.length) return
  if (!lineChart) lineChart = echarts.init(lineChartRef.value)

  const sorted = [...props.trends]
    .map(s => ({
      date: String(s.stat_date ?? s.date ?? ''),
      count: Number(s.total_events ?? s.value ?? 0),
    }))
    .sort((a, b) => a.date.localeCompare(b.date))

  lineChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '5%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: sorted.map(s => s.date),
      axisLabel: { rotate: 30, fontSize: 11 },
    },
    yAxis: { type: 'value' },
    series: [{
      type: 'line',
      data: sorted.map(s => s.count),
      smooth: true,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(26,115,232,0.3)' },
          { offset: 1, color: 'rgba(26,115,232,0.02)' },
        ]),
      },
      lineStyle: { color: '#1a73e8', width: 2 },
      itemStyle: { color: '#1a73e8' },
    }],
  })
}

function handleResize() {
  barChart?.resize()
  lineChart?.resize()
}

watch(() => props.hotSpots, renderBarChart, { deep: true })
watch(() => props.trends, renderLineChart, { deep: true })

onMounted(() => {
  renderBarChart()
  renderLineChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  barChart?.dispose()
  lineChart?.dispose()
})
</script>

<style scoped>
.dashboard-charts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.chart-card {
  padding: 20px;
  border: 1px solid #dbe4f0;
  border-radius: 20px;
  background: #fff;
}

.chart-card h3 {
  margin: 0 0 16px;
  font-size: 16px;
  color: #333;
}

.chart-container {
  width: 100%;
  height: 300px;
}

@media (max-width: 900px) {
  .dashboard-charts {
    grid-template-columns: 1fr;
  }
}
</style>
