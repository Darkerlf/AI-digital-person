<template>
  <section class="page-shell">
    <section class="page-shell__panel">
      <div class="report-heading">
        <div>
          <h2>游客感受度报告</h2>
          <p>汇总游客对 AI 导游回答、路线推荐和服务体验的评分与意见。</p>
        </div>
      </div>
      <form class="filter-bar" @submit.prevent="loadReport">
        <input v-model="filters.start_date" name="start_date" type="date" />
        <input v-model="filters.end_date" name="end_date" type="date" />
        <select v-model="filters.scenic_area_id" name="scenic_area_id">
          <option value="">全部景区</option>
          <option v-for="item in scenicAreas" :key="item.id" :value="String(item.id)">
            {{ item.name }}
          </option>
        </select>
        <select v-model="filters.source_type" name="source_type">
          <option value="">全部来源</option>
          <option value="chat">问答反馈</option>
          <option value="route">路线反馈</option>
          <option value="qa">知识问答</option>
        </select>
        <button type="submit">筛选</button>
      </form>
      <div class="feedback-grid">
        <article class="feedback-card">
          <span>反馈总量</span>
          <strong>{{ report.total_feedback }}</strong>
        </article>
        <article class="feedback-card">
          <span>平均评分</span>
          <strong>{{ report.average_score ?? '--' }}</strong>
        </article>
        <article class="feedback-card">
          <span>正向反馈</span>
          <strong>{{ report.sentiment_distribution.positive }}</strong>
        </article>
        <article class="feedback-card">
          <span>负向反馈</span>
          <strong>{{ report.sentiment_distribution.negative }}</strong>
        </article>
      </div>
    </section>

    <section class="page-shell__panel">
      <h2>运营建议</h2>
      <p class="feedback-summary">{{ report.suggestion_summary }}</p>
      <p v-if="errorMessage" class="feedback-error">{{ errorMessage }}</p>
    </section>

    <section class="analysis-grid">
      <article class="page-shell__panel">
        <h2>反馈趋势</h2>
        <ul class="metric-list">
          <li v-for="item in report.feedback_trend" :key="item.date">
            <strong>{{ item.date }}</strong>
            <span>{{ item.total_feedback }} 条 / 均分 {{ item.average_score ?? '--' }} / 差评 {{ item.negative_count }}</span>
          </li>
        </ul>
      </article>
      <article class="page-shell__panel">
        <h2>关注 TopN</h2>
        <ul class="metric-list">
          <li v-for="item in report.focus_top_n" :key="item.name">
            <strong>{{ item.name }}</strong>
            <span>{{ item.count }}</span>
          </li>
        </ul>
      </article>
      <article class="page-shell__panel">
        <h2>差评归因</h2>
        <ul class="metric-list">
          <li v-for="item in report.negative_reason_top_n" :key="item.reason">
            <strong>{{ item.reason }}</strong>
            <span>{{ item.count }}</span>
          </li>
        </ul>
      </article>
      <article class="page-shell__panel">
        <h2>路线反馈分析</h2>
        <ul class="metric-list">
          <li v-for="item in report.route_feedback_analysis" :key="item.route_name">
            <strong>{{ item.route_name }}</strong>
            <span>{{ item.total_feedback }} 条 / 均分 {{ item.average_score ?? '--' }} / 差评 {{ item.negative_count }}</span>
          </li>
        </ul>
      </article>
    </section>

    <section class="page-shell__panel">
      <div class="report-heading">
        <div>
          <h2>评价明细</h2>
          <p>优先查看差评和低星反馈，持续修正知识内容与讲解体验。</p>
        </div>
      </div>
      <div v-if="report.latest_feedback.length" class="feedback-table-wrap">
        <table class="feedback-table">
          <thead>
            <tr>
              <th>评价</th>
              <th>星级</th>
              <th>游客评论</th>
              <th>游客问题</th>
              <th>AI 回答摘要</th>
              <th>时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in report.latest_feedback" :key="item.id">
              <td>
                <span :class="['sentiment-tag', `sentiment-tag--${item.sentiment ?? 'neutral'}`]">
                  {{ sentimentLabel(item.sentiment) }}
                </span>
              </td>
              <td>{{ item.score ? `${item.score} 星` : '--' }}</td>
              <td>{{ item.content || '未填写详细评论' }}</td>
              <td>{{ item.question_text || '--' }}</td>
              <td>{{ item.answer_text || '--' }}</td>
              <td>{{ formatDate(item.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="feedback-empty">暂无评价明细。</p>
    </section>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'

import { apiClient } from '../api/client'

type FeedbackDetail = {
  id: number
  message_id: number | null
  session_id: number | null
  sentiment: string | null
  score: number | null
  content: string | null
  question_text: string | null
  answer_text: string | null
  created_at: string
}

type FeedbackTrendItem = {
  date: string
  total_feedback: number
  average_score: number | null
  negative_count: number
}

type FeedbackTopItem = {
  name: string
  count: number
}

type NegativeReasonItem = {
  reason: string
  count: number
}

type RouteFeedbackAnalysisItem = {
  route_name: string
  total_feedback: number
  average_score: number | null
  negative_count: number
}

const report = reactive({
  total_feedback: 0,
  average_score: null as number | null,
  sentiment_distribution: {
    positive: 0,
    neutral: 0,
    negative: 0,
  },
  suggestion_summary: '暂无游客反馈数据，建议先打通游客端反馈采集。',
  latest_feedback: [] as FeedbackDetail[],
  feedback_trend: [] as FeedbackTrendItem[],
  focus_top_n: [] as FeedbackTopItem[],
  complaint_top_n: [] as FeedbackTopItem[],
  negative_reason_top_n: [] as NegativeReasonItem[],
  route_feedback_analysis: [] as RouteFeedbackAnalysisItem[],
})

const filters = reactive({
  start_date: '',
  end_date: '',
  scenic_area_id: '',
  source_type: '',
})
const scenicAreas = ref<Array<{ id: number; name: string }>>([])
const errorMessage = ref('')

function sentimentLabel(sentiment: string | null) {
  if (sentiment === 'positive') return '点赞'
  if (sentiment === 'negative') return '点踩'
  return '中性'
}

function formatDate(value: string) {
  return value ? new Date(value).toLocaleString('zh-CN') : '--'
}

function buildParams() {
  return Object.fromEntries(
    Object.entries(filters).filter(([, value]) => value !== ''),
  )
}

async function loadReport() {
  try {
    const response = await apiClient.get('/dashboard/feedback-report', {
      params: buildParams(),
    })
    Object.assign(report, response.data)
  } catch {
    errorMessage.value = '暂时无法加载游客感受度报告。'
  }
}

async function loadScenicAreas() {
  const response = await apiClient.get('/scenic-areas')
  scenicAreas.value = response.data
}

onMounted(() => {
  void loadScenicAreas()
  void loadReport()
})
</script>

<style scoped>
.report-heading {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 16px;
}

.report-heading h2 {
  margin: 0;
}

.report-heading p {
  margin: 7px 0 0;
  color: #64748b;
}

.filter-bar {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
  margin-top: 18px;
}

.filter-bar input,
.filter-bar select,
.filter-bar button {
  min-width: 0;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
}

.filter-bar button {
  color: #fff;
  border-color: #2563eb;
  background: #2563eb;
}

.feedback-grid,
.analysis-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-top: 18px;
}

.analysis-grid {
  align-items: stretch;
}

.feedback-card {
  display: grid;
  gap: 8px;
  padding: 18px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fbff;
}

.feedback-card span {
  color: #64748b;
}

.feedback-card strong {
  font-size: 28px;
}

.feedback-summary {
  margin: 0;
  line-height: 1.7;
}

.feedback-error {
  margin: 12px 0 0;
  color: #b91c1c;
}

.metric-list {
  display: grid;
  gap: 10px;
  margin: 14px 0 0;
  padding: 0;
  list-style: none;
}

.metric-list li {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e2e8f0;
}

.feedback-table-wrap {
  margin-top: 18px;
  overflow-x: auto;
}

.feedback-table {
  width: 100%;
  min-width: 980px;
  border-collapse: collapse;
  table-layout: fixed;
}

.feedback-table th,
.feedback-table td {
  padding: 12px;
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
  vertical-align: top;
  line-height: 1.55;
}

.feedback-table th {
  color: #64748b;
  font-size: 13px;
  background: #f8fafc;
}

.feedback-table th:nth-child(1),
.feedback-table td:nth-child(1) {
  width: 84px;
}

.feedback-table th:nth-child(2),
.feedback-table td:nth-child(2) {
  width: 76px;
}

.feedback-table th:nth-child(3),
.feedback-table td:nth-child(3) {
  width: 220px;
}

.feedback-table th:nth-child(6),
.feedback-table td:nth-child(6) {
  width: 180px;
}

.sentiment-tag {
  display: inline-flex;
  padding: 4px 9px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.sentiment-tag--positive {
  color: #047857;
  background: #d1fae5;
}

.sentiment-tag--negative {
  color: #b91c1c;
  background: #fee2e2;
}

.sentiment-tag--neutral {
  color: #475569;
  background: #e2e8f0;
}

.feedback-empty {
  margin: 18px 0 0;
  color: #64748b;
}

@media (max-width: 900px) {
  .feedback-grid,
  .analysis-grid,
  .filter-bar {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
