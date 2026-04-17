<template>
  <section class="page-shell">
    <section class="page-shell__panel">
      <h2>游客感受度报告</h2>
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
      <h2>情绪分布</h2>
      <ul class="page-shell__list">
        <li>
          <div>
            <strong>正向</strong>
            <p>积极评价与满意反馈</p>
          </div>
          <span>{{ report.sentiment_distribution.positive }}</span>
        </li>
        <li>
          <div>
            <strong>中性</strong>
            <p>一般评价与待补充内容</p>
          </div>
          <span>{{ report.sentiment_distribution.neutral }}</span>
        </li>
        <li>
          <div>
            <strong>负向</strong>
            <p>抱怨、路线偏差或讲解不满足预期</p>
          </div>
          <span>{{ report.sentiment_distribution.negative }}</span>
        </li>
      </ul>
    </section>

    <section class="page-shell__panel">
      <h2>运营建议</h2>
      <p class="feedback-summary">{{ report.suggestion_summary }}</p>
      <p v-if="errorMessage" class="feedback-error">{{ errorMessage }}</p>
    </section>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'

import { apiClient } from '../api/client'

const report = reactive({
  total_feedback: 0,
  average_score: null as number | null,
  sentiment_distribution: {
    positive: 0,
    neutral: 0,
    negative: 0,
  },
  suggestion_summary: '暂无游客反馈数据，建议先打通游客端反馈采集。',
})

const errorMessage = ref('')

async function loadReport() {
  try {
    const response = await apiClient.get('/dashboard/feedback-report')
    Object.assign(report, response.data)
  } catch (error) {
    errorMessage.value = '暂时无法加载游客感受度报告。'
  }
}

onMounted(() => {
  void loadReport()
})
</script>

<style scoped>
.feedback-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
}

.feedback-card {
  display: grid;
  gap: 8px;
  padding: 18px;
  border-radius: 18px;
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

@media (max-width: 900px) {
  .feedback-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
