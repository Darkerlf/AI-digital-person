<template>
  <section class="page-shell">
    <div class="route-template-grid">
      <form class="page-shell__panel page-shell__form" @submit.prevent="submitTemplate">
        <h2>路线模板管理</h2>
        <input v-model="form.name" placeholder="模板名称" type="text" />
        <select v-model.number="form.scenic_area_id">
          <option :value="0">选择景区</option>
          <option v-for="item in scenicAreas" :key="item.id" :value="item.id">{{ item.name }}</option>
        </select>
        <select v-model="form.template_type">
          <option value="fixed">固定路线</option>
          <option value="hybrid">混合模板</option>
        </select>
        <input v-model="form.interest_tags_text" placeholder="兴趣标签，逗号分隔" type="text" />
        <input v-model="form.audience_tags_text" placeholder="人群标签，逗号分隔" type="text" />
        <div class="route-template-duration">
          <input v-model.number="form.duration_min_minutes" placeholder="最短时长（分钟）" type="number" />
          <input v-model.number="form.duration_max_minutes" placeholder="最长时长（分钟）" type="number" />
        </div>
        <textarea v-model="form.summary" placeholder="路线摘要" rows="3" />
        <div class="route-template-duration">
          <select v-model="form.status">
            <option value="active">启用</option>
            <option value="inactive">停用</option>
          </select>
          <input v-model.number="form.priority" placeholder="优先级" type="number" />
        </div>
        <textarea v-model="form.rule_notes" placeholder="规则说明" rows="2" />

        <section class="route-template-stops">
          <div class="route-template-stops__header">
            <h3>路线站点</h3>
            <button type="button" @click="addSpotRow">新增站点</button>
          </div>
          <div v-for="(item, index) in form.spots" :key="index" class="route-template-stop">
            <select v-model.number="item.scenic_spot_id">
              <option :value="0">选择景点</option>
              <option v-for="spot in spotOptions" :key="spot.id" :value="spot.id">{{ spot.name }}</option>
            </select>
            <input v-model.number="item.sort_order" placeholder="顺序" type="number" />
            <input v-model.number="item.stay_minutes" placeholder="停留分钟" type="number" />
            <input v-model="item.highlight" placeholder="亮点说明" type="text" />
            <button type="button" class="route-template-stop__remove" @click="removeSpotRow(index)">删除</button>
          </div>
        </section>

        <div class="page-shell__actions">
          <button type="submit">{{ editingId ? '更新模板' : '创建模板' }}</button>
          <button v-if="editingId" type="button" class="route-template-secondary" @click="resetForm">取消编辑</button>
        </div>
      </form>

      <section class="page-shell__panel">
        <h2>模板列表</h2>
        <ul class="page-shell__list">
          <li v-for="item in templates" :key="item.id">
            <div>
              <strong>{{ item.name }}</strong>
              <p>{{ item.summary || '未填写摘要' }}</p>
              <p>景点数：{{ item.spots.length }} · 优先级：{{ item.priority }}</p>
            </div>
            <div class="page-shell__actions">
              <button type="button" @click="startEdit(item)">编辑</button>
              <button type="button" class="route-template-danger" @click="deleteTemplate(item.id)">删除</button>
            </div>
          </li>
        </ul>
      </section>
    </div>

    <section class="page-shell__panel">
      <h2>推荐预览</h2>
      <form class="route-preview-form" @submit.prevent="generatePreview">
        <select v-model.number="preview.scenic_area_id">
          <option :value="0">选择景区</option>
          <option v-for="item in scenicAreas" :key="item.id" :value="item.id">{{ item.name }}</option>
        </select>
        <input v-model="preview.interest_tags_text" placeholder="兴趣标签，逗号分隔" type="text" />
        <input v-model="preview.audience_tags_text" placeholder="人群标签，逗号分隔" type="text" />
        <input v-model.number="preview.duration_minutes" placeholder="游玩时长（分钟）" type="number" />
        <button type="submit">生成推荐路线</button>
      </form>

      <div class="route-preview-result">
        <template v-if="previewResult">
          <p>
            <strong>{{ previewResult.matched_template.name }}</strong>
            <span> · {{ previewResult.fallback_used ? '使用兜底匹配' : '精确命中' }}</span>
          </p>
          <p>{{ previewResult.match_reason }}</p>
          <p>{{ previewResult.summary || '未填写摘要' }}</p>
          <ul class="page-shell__list">
            <li v-for="item in previewResult.spots" :key="item.scenic_spot_id">
              <div>
                <strong>{{ item.name }}</strong>
                <p>建议停留：{{ item.stay_minutes ?? '--' }} 分钟</p>
              </div>
              <span>{{ item.highlight || '未填写亮点' }}</span>
            </li>
          </ul>
        </template>
        <p v-else>提交条件后查看推荐结果。</p>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'

import { apiClient } from '../api/client'

type ScenicArea = {
  id: number
  code: string
  name: string
  description: string | null
  status: string
}

type ScenicSpot = {
  id: number
  scenic_area_id: number
  spot_code: string
  name: string
}

type RouteTemplateSpot = {
  id?: number
  scenic_spot_id: number
  name?: string
  sort_order: number
  stay_minutes: number | null
  highlight: string
}

type RouteTemplate = {
  id: number
  scenic_area_id: number
  name: string
  template_type: string
  interest_tags: string[]
  audience_tags: string[]
  duration_min_minutes: number
  duration_max_minutes: number
  summary: string | null
  status: string
  priority: number
  rule_notes: string | null
  spots: RouteTemplateSpot[]
}

type RecommendationResult = {
  matched_template: {
    id: number
    name: string
    template_type: string
    scenic_area_id: number
    priority: number
  }
  fallback_used: boolean
  match_reason: string
  summary: string | null
  spots: Array<{
    scenic_spot_id: number
    name: string
    stay_minutes: number | null
    highlight: string | null
  }>
}

const scenicAreas = ref<ScenicArea[]>([])
const scenicSpots = ref<ScenicSpot[]>([])
const templates = ref<RouteTemplate[]>([])
const editingId = ref<number | null>(null)
const previewResult = ref<RecommendationResult | null>(null)

const form = reactive({
  scenic_area_id: 0,
  name: '',
  template_type: 'fixed',
  interest_tags_text: '',
  audience_tags_text: '',
  duration_min_minutes: 120,
  duration_max_minutes: 180,
  summary: '',
  status: 'active',
  priority: 0,
  rule_notes: '',
  spots: [createEmptySpotRow()],
})

const preview = reactive({
  scenic_area_id: 0,
  interest_tags_text: '',
  audience_tags_text: '',
  duration_minutes: 180,
})

const spotOptions = computed(() => {
  if (!form.scenic_area_id) {
    return scenicSpots.value
  }
  return scenicSpots.value.filter((item) => item.scenic_area_id === form.scenic_area_id)
})

function createEmptySpotRow(): RouteTemplateSpot {
  return {
    scenic_spot_id: 0,
    sort_order: 1,
    stay_minutes: null,
    highlight: '',
  }
}

function parseTags(rawText: string): string[] {
  return rawText
    .split(/[，,]/)
    .map((item) => item.trim())
    .filter(Boolean)
}

function buildTemplatePayload() {
  return {
    scenic_area_id: form.scenic_area_id,
    name: form.name,
    template_type: form.template_type,
    interest_tags: parseTags(form.interest_tags_text),
    audience_tags: parseTags(form.audience_tags_text),
    duration_min_minutes: Number(form.duration_min_minutes || 0),
    duration_max_minutes: Number(form.duration_max_minutes || 0),
    summary: form.summary || null,
    status: form.status,
    priority: Number(form.priority || 0),
    rule_notes: form.rule_notes || null,
    spots: form.spots
      .filter((item) => item.scenic_spot_id > 0)
      .map((item) => ({
        scenic_spot_id: item.scenic_spot_id,
        sort_order: Number(item.sort_order || 0),
        stay_minutes: item.stay_minutes ? Number(item.stay_minutes) : null,
        highlight: item.highlight || null,
      })),
  }
}

async function loadScenicAreas() {
  const response = await apiClient.get('/scenic-areas')
  scenicAreas.value = response.data
}

async function loadScenicSpots() {
  const response = await apiClient.get('/scenic-spots')
  scenicSpots.value = response.data.items
}

async function loadTemplates() {
  const response = await apiClient.get('/route-templates')
  templates.value = response.data.items
}

function addSpotRow() {
  form.spots.push({
    ...createEmptySpotRow(),
    sort_order: form.spots.length + 1,
  })
}

function removeSpotRow(index: number) {
  if (form.spots.length === 1) {
    form.spots.splice(0, 1, createEmptySpotRow())
    return
  }
  form.spots.splice(index, 1)
}

function resetForm() {
  editingId.value = null
  form.scenic_area_id = 0
  form.name = ''
  form.template_type = 'fixed'
  form.interest_tags_text = ''
  form.audience_tags_text = ''
  form.duration_min_minutes = 120
  form.duration_max_minutes = 180
  form.summary = ''
  form.status = 'active'
  form.priority = 0
  form.rule_notes = ''
  form.spots = [createEmptySpotRow()]
}

function startEdit(item: RouteTemplate) {
  editingId.value = item.id
  form.scenic_area_id = item.scenic_area_id
  form.name = item.name
  form.template_type = item.template_type
  form.interest_tags_text = item.interest_tags.join('，')
  form.audience_tags_text = item.audience_tags.join('，')
  form.duration_min_minutes = item.duration_min_minutes
  form.duration_max_minutes = item.duration_max_minutes
  form.summary = item.summary ?? ''
  form.status = item.status
  form.priority = item.priority
  form.rule_notes = item.rule_notes ?? ''
  form.spots = item.spots.length
    ? item.spots.map((spot) => ({
        scenic_spot_id: spot.scenic_spot_id,
        sort_order: spot.sort_order,
        stay_minutes: spot.stay_minutes,
        highlight: spot.highlight ?? '',
      }))
    : [createEmptySpotRow()]
}

async function submitTemplate() {
  const payload = buildTemplatePayload()
  if (editingId.value) {
    await apiClient.put(`/route-templates/${editingId.value}`, payload)
  } else {
    await apiClient.post('/route-templates', payload)
  }
  resetForm()
  await loadTemplates()
}

async function deleteTemplate(templateId: number) {
  await apiClient.delete(`/route-templates/${templateId}`)
  if (editingId.value === templateId) {
    resetForm()
  }
  await loadTemplates()
}

async function generatePreview() {
  const response = await apiClient.post('/route-recommendations/generate', {
    scenic_area_id: preview.scenic_area_id || null,
    interest_tags: parseTags(preview.interest_tags_text),
    audience_tags: parseTags(preview.audience_tags_text),
    duration_minutes: Number(preview.duration_minutes || 0),
  })
  previewResult.value = response.data
}

onMounted(async () => {
  await Promise.all([loadScenicAreas(), loadScenicSpots(), loadTemplates()])
})
</script>

<style scoped>
.route-template-grid {
  display: grid;
  grid-template-columns: minmax(360px, 520px) 1fr;
  gap: 20px;
}

.route-template-duration {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.route-template-stops {
  display: grid;
  gap: 12px;
}

.route-template-stops__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.route-template-stops__header h3 {
  margin: 0;
}

.route-template-stop {
  display: grid;
  grid-template-columns: 1.4fr 90px 120px 1fr auto;
  gap: 10px;
  padding: 12px;
  border-radius: 16px;
  background: #f8fbff;
}

.route-template-stop__remove,
.route-template-danger {
  color: #fff;
  background: #dc2626;
  border: 0;
}

.route-template-secondary {
  color: #1f2937;
  background: #e2e8f0;
}

.route-preview-form {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.route-preview-form select,
.route-preview-form input,
.route-preview-form button {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
}

.route-preview-form button {
  color: #fff;
  background: #2563eb;
  border: 0;
}

.route-preview-result {
  display: grid;
  gap: 12px;
}

.route-preview-result p {
  margin: 0;
}

@media (max-width: 1100px) {
  .route-template-grid {
    grid-template-columns: 1fr;
  }

  .route-preview-form {
    grid-template-columns: 1fr;
  }

  .route-template-stop {
    grid-template-columns: 1fr;
  }
}
</style>
