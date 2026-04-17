<template>
  <section class="page-shell">
    <section class="page-shell__panel">
      <h2>会话记录与问题修正</h2>
      <div class="session-toolbar">
        <input v-model="keyword" placeholder="搜索问题关键词" type="text" />
        <RouterLink class="session-toolbar__link" to="/knowledge/documents">前往知识修正</RouterLink>
      </div>
    </section>

    <div class="session-grid">
      <section class="page-shell__panel">
        <h2>会话列表</h2>
        <ul class="page-shell__list">
          <li v-for="item in filteredSessions" :key="item.id">
            <button class="session-list__button" type="button" @click="selectSession(item.id)">
              <strong>{{ item.session_key }}</strong>
              <p>{{ item.channel }} · 未修复 {{ item.unresolved_count }} 条</p>
            </button>
          </li>
        </ul>
      </section>

      <section class="page-shell__panel">
        <h2>会话详情</h2>
        <ul v-if="selectedSession.messages.length" class="page-shell__list">
          <li v-for="item in selectedSession.messages" :key="item.id">
            <div>
              <strong>{{ item.question_text }}</strong>
              <p>识别文本：{{ item.recognized_text ?? '无' }}</p>
              <p>回答：{{ item.answer_text ?? '无回答' }}</p>
              <p>命中文档：{{ item.matched_document_title ?? '未命中' }}</p>
              <p>耗时：{{ item.latency_ms ?? '-' }} ms · 反馈：{{ item.feedback_status ?? '未反馈' }}</p>
            </div>
          </li>
        </ul>
        <p v-else class="session-empty">请选择一条会话查看详情。</p>
      </section>
    </div>

    <section class="page-shell__panel">
      <h2>未命中问题</h2>
      <ul class="page-shell__list">
        <li v-for="item in filteredUnresolved" :key="item.id" class="session-unresolved">
          <div>
            <strong>{{ item.question_text }}</strong>
            <p>会话：{{ item.session_key }}</p>
            <p>识别文本：{{ item.recognized_text ?? '无' }}</p>
            <p>反馈：{{ item.feedback_status ?? '未反馈' }}</p>
          </div>
          <div class="session-unresolved__actions">
            <textarea
              v-model="resolutionNotes[item.id]"
              placeholder="填写修正说明，例如：已补充 FAQ / 已更新讲解文档"
              rows="3"
            />
            <button type="button" @click="resolveMessage(item.id)">标记已修复</button>
          </div>
        </li>
      </ul>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { apiClient } from '../api/client'

type SessionListItem = {
  id: number
  session_key: string
  channel: string
  visitor_id: string | null
  status: string
  message_count: number
  unresolved_count: number
}

type SessionMessage = {
  id: number
  question_text: string
  recognized_text: string | null
  answer_text: string | null
  matched_document_title: string | null
  latency_ms: number | null
  feedback_status: string | null
}

type SessionDetail = {
  id: number | null
  session_key: string
  messages: SessionMessage[]
}

type UnresolvedItem = {
  id: number
  session_id: number
  session_key: string
  question_text: string
  recognized_text: string | null
  feedback_status: string | null
  resolution_status: string
}

const keyword = ref('')
const sessions = ref<SessionListItem[]>([])
const unresolvedItems = ref<UnresolvedItem[]>([])
const selectedSession = reactive<SessionDetail>({
  id: null,
  session_key: '',
  messages: [],
})
const resolutionNotes = reactive<Record<number, string>>({})

const filteredSessions = computed(() => {
  const normalized = keyword.value.trim()
  if (!normalized) {
    return sessions.value
  }
  return sessions.value.filter((item) => item.session_key.includes(normalized))
})

const filteredUnresolved = computed(() => {
  const normalized = keyword.value.trim()
  if (!normalized) {
    return unresolvedItems.value
  }
  return unresolvedItems.value.filter(
    (item) => item.question_text.includes(normalized) || (item.recognized_text ?? '').includes(normalized),
  )
})

async function loadSessions() {
  const response = await apiClient.get('/sessions')
  sessions.value = response.data.items
}

async function loadUnresolved() {
  const response = await apiClient.get('/sessions/unresolved')
  unresolvedItems.value = response.data.items
}

async function selectSession(sessionId: number) {
  const response = await apiClient.get(`/sessions/${sessionId}`)
  selectedSession.id = response.data.id
  selectedSession.session_key = response.data.session_key
  selectedSession.messages = response.data.messages
}

async function resolveMessage(messageId: number) {
  const resolutionNote = resolutionNotes[messageId] || '已完成知识修正。'
  const currentSessionId = unresolvedItems.value.find((item) => item.id === messageId)?.session_id
  await apiClient.put(`/sessions/messages/${messageId}/resolve`, { resolution_note: resolutionNote })
  await Promise.all([loadSessions(), loadUnresolved()])
  if (currentSessionId && selectedSession.id === currentSessionId) {
    await selectSession(currentSessionId)
  }
}

onMounted(async () => {
  await Promise.all([loadSessions(), loadUnresolved()])
  if (sessions.value[0]) {
    await selectSession(sessions.value[0].id)
  }
})
</script>

<style scoped>
.session-toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
}

.session-toolbar input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
}

.session-toolbar__link {
  color: #2563eb;
  text-decoration: none;
}

.session-grid {
  display: grid;
  grid-template-columns: minmax(260px, 360px) 1fr;
  gap: 20px;
}

.session-list__button {
  width: 100%;
  padding: 0;
  text-align: left;
  color: inherit;
  background: transparent;
  border: 0;
}

.session-empty {
  margin: 0;
  color: #64748b;
}

.session-unresolved {
  align-items: start;
}

.session-unresolved__actions {
  display: grid;
  gap: 10px;
  width: min(320px, 100%);
}

.session-unresolved__actions textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
}

.session-unresolved__actions button {
  width: fit-content;
  padding: 10px 14px;
  border: 0;
  border-radius: 12px;
  color: #fff;
  background: #2563eb;
}

@media (max-width: 960px) {
  .session-grid {
    grid-template-columns: 1fr;
  }

  .session-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
