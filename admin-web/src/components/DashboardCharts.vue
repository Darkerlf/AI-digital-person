<template>
  <section class="dashboard-charts">
    <div class="chart-card">
      <h3>热门景点 TOP5</h3>
      <p class="chart-card__desc">
        横轴：行为事件次数，表示游客在对应景点产生的浏览、咨询、路线等行为记录数量；纵轴：景点名称。
      </p>
      <div ref="barChartRef" class="chart-container" />
    </div>
    <div class="chart-card">
      <h3>游客行为趋势</h3>
      <p class="chart-card__desc">
        横轴：日期；纵轴：行为事件次数，用于观察游客交互活跃度随时间的变化。
      </p>
      <div ref="lineChartRef" class="chart-container" />
    </div>
    <p class="dashboard-charts__note">
      统计口径：当前图表来自行为分析数据，统计的是系统记录到的游客行为事件次数，不等同于真实入园人数或门票销量。
    </p>
  </section>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

type ChartRecord = Record<string, unknown> | [string, number]

const props = defineProps<{
  hotSpots: ChartRecord[]
  trends: ChartRecord[]
}>()

const barChartRef = ref<HTMLDivElement>()
const lineChartRef = ref<HTMLDivElement>()
let barChart: echarts.ECharts | null = null
let lineChart: echarts.ECharts | null = null

function normalizeHotSpot(item: ChartRecord) {
  if (Array.isArray(item)) {
    return {
      name: String(item[0] || '未命名'),
      count: Number(item[1] || 0),
    }
  }
  return {
    name: String(item.spot_name ?? item.name ?? '未命名'),
    count: Number(item.event_count ?? item.count ?? item.value ?? 0),
  }
}

function normalizeTrend(item: ChartRecord) {
  if (Array.isArray(item)) {
    return {
      date: String(item[0] || ''),
      count: Number(item[1] || 0),
    }
  }
  return {
    date: String(item.stat_date ?? item.date ?? ''),
    count: Number(item.total_events ?? item.count ?? item.value ?? 0),
  }
}

function renderBarChart() {
  if (!barChartRef.value || !props.hotSpots?.length) return
  if (!barChart) barChart = echarts.init(barChartRef.value)

  const sorted = [...props.hotSpots]
    .map(normalizeHotSpot)
    .sort((a, b) => b.count - a.count)
    .slice(0, 5)

  barChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '8%', bottom: '12%', top: '10%', containLabel: true },
    xAxis: {
      type: 'value',
      name: '行为事件次数',
      nameLocation: 'middle',
      nameGap: 28,
    },
    yAxis: {
      type: 'category',
      name: '景点名称',
      data: sorted.map((item) => item.name),
      axisLabel: { fontSize: 12 },
    },
    series: [
      {
        type: 'bar',
        data: sorted.map((item) => item.count),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#1a73e8' },
            { offset: 1, color: '#4fc3f7' },
          ]),
        },
        barWidth: '60%',
      },
    ],
  })
}

function renderLineChart() {
  if (!lineChartRef.value || !props.trends?.length) return
  if (!lineChart) lineChart = echarts.init(lineChartRef.value)

  const sorted = [...props.trends]
    .map(normalizeTrend)
    .sort((a, b) => a.date.localeCompare(b.date))

  lineChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '5%', bottom: '14%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      name: '日期',
      nameLocation: 'middle',
      nameGap: 42,
      data: sorted.map((item) => item.date),
      axisLabel: { rotate: 30, fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      name: '行为事件次数',
    },
    series: [
      {
        type: 'line',
        data: sorted.map((item) => item.count),
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(26,115,232,0.3)' },
            { offset: 1, color: 'rgba(26,115,232,0.02)' },
          ]),
        },
        lineStyle: { color: '#1a73e8', width: 2 },
        itemStyle: { color: '#1a73e8' },
      },
    ],
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
  margin: 0 0 8px;
  font-size: 16px;
  color: #333;
}

.chart-card__desc,
.dashboard-charts__note {
  margin: 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.6;
}

.chart-card__desc {
  min-height: 42px;
}

.dashboard-charts__note {
  grid-column: 1 / -1;
  padding: 12px 14px;
  border: 1px solid #dbe4f0;
  border-radius: 12px;
  background: #f8fafc;
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
