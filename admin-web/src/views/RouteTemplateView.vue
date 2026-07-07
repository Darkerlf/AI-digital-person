<template>
  <section class="page-shell">
    <div class="route-template-grid">
      <form class="page-shell__panel page-shell__form" @submit.prevent="submitTemplate">
        <h2>路线模板管理</h2>
        <p v-if="formError" class="route-template-error">{{ formError }}</p>
        <input v-model="form.name" placeholder="模板名称" type="text" />
        <select v-model.number="form.scenic_area_id">
          <option :value="0">选择景区</option>
          <option v-for="item in scenicAreas" :key="item.id" :value="item.id">{{ item.name }}</option>
        </select>
        <select v-model="form.template_type">
          <option value="fixed">固定路线</option>
          <option value="hybrid">混合模板</option>
        </select>
        <input v-model="form.interest_tags_text" placeholder="兴趣标签，逗号分隔，如历史文化,拍照打卡" type="text" />
        <input v-model="form.audience_tags_text" placeholder="人群标签，逗号分隔，如亲子,老人,首次来访" type="text" />

        <div class="route-template-duration">
          <label class="route-template-field">
            <span>最短适用时长</span>
            <input v-model.number="form.duration_min_minutes" type="number" min="0" />
            <small>单位：分钟。游客可用时间低于该值时，通常不推荐此模板；例如 120 表示至少 2 小时。</small>
          </label>
          <label class="route-template-field">
            <span>最长适用时长</span>
            <input v-model.number="form.duration_max_minutes" type="number" min="0" />
            <small>单位：分钟。游客可用时间高于该值时，系统会优先考虑更长路线；例如 180 表示最多 3 小时。</small>
          </label>
        </div>

        <textarea v-model="form.summary" placeholder="路线摘要" rows="3" />

        <div class="route-template-duration">
          <select v-model="form.status">
            <option value="active">启用</option>
            <option value="inactive">停用</option>
          </select>
          <label class="route-template-field">
            <span>优先级</span>
            <input v-model.number="form.priority" type="number" />
            <small>数字越大越优先。多个模板都匹配时，优先推荐数值更大的模板；普通模板可填 0。</small>
          </label>
        </div>

        <textarea v-model="form.rule_notes" placeholder="规则说明，如适合上午入园、避开人流高峰等" rows="2" />

        <section class="route-template-stops">
          <div class="route-template-stops__header">
            <div>
              <h3>路线站点</h3>
              <p>按游客实际游览顺序配置景点，并为每个景点设置建议停留时间。</p>
            </div>
            <button class="app-button app-button--primary" type="button" @click="addSpotRow">新增站点</button>
          </div>
          <div v-for="(item, index) in form.spots" :key="index" class="route-template-stop">
            <label class="route-template-field">
              <span>景点</span>
              <select v-model.number="item.scenic_spot_id">
                <option :value="0">选择景点</option>
                <option v-for="spot in spotOptions" :key="spot.id" :value="spot.id">{{ spot.name }}</option>
              </select>
            </label>
            <label class="route-template-field">
              <span>站点顺序</span>
              <input v-model.number="item.sort_order" type="number" min="1" />
              <small>数字越小越靠前，如 1 表示第一站。</small>
            </label>
            <label class="route-template-field">
              <span>站点停留时间</span>
              <input v-model.number="item.stay_minutes" type="number" min="0" />
              <small>单位：分钟。用于路线总时长估算，如 30 表示建议讲解和游览 30 分钟。</small>
            </label>
            <label class="route-template-field">
              <span>亮点说明</span>
              <input v-model="item.highlight" placeholder="如核心地标、适合拍照" type="text" />
            </label>
            <button
              type="button"
              class="app-button app-button--danger route-template-stop__remove"
              @click="removeSpotRow(index)"
            >
              删除
            </button>
          </div>
        </section>

        <div class="page-shell__actions">
          <button class="app-button app-button--primary" type="submit">
            {{ editingId ? '更新模板' : '创建模板' }}
          </button>
          <button v-if="editingId" type="button" class="app-button app-button--ghost" @click="resetForm">取消编辑</button>
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
              <button class="app-button app-button--ghost" type="button" @click="startEdit(item)">编辑</button>
              <button class="app-button app-button--danger" type="button" @click="deleteTemplate(item.id)">删除</button>
            </div>
          </li>
        </ul>
      </section>
    </div>

    <section class="page-shell__panel">
      <h2>推荐预览</h2>
      <form class="route-preview-form" @submit.prevent="generatePreview">
        <p v-if="previewError" class="route-template-error route-template-error--wide">{{ previewError }}</p>
        <select v-model.number="preview.scenic_area_id">
          <option :value="0">选择景区</option>
          <option v-for="item in scenicAreas" :key="item.id" :value="item.id">{{ item.name }}</option>
        </select>
        <input v-model="preview.interest_tags_text" placeholder="兴趣标签，逗号分隔" type="text" />
        <input v-model="preview.audience_tags_text" placeholder="人群标签，逗号分隔" type="text" />
        <label class="route-template-field">
          <span>预览游玩时长</span>
          <input v-model.number="preview.duration_minutes" type="number" min="0" />
          <small>单位：分钟。模拟游客可用游玩时间，用来测试会命中哪条模板。</small>
        </label>
        <button class="app-button app-button--primary" type="submit">生成推荐路线</button>
      </form>

      <div class="route-preview-result">
        <template v-if="previewResult">
          <p>
            <strong>{{ previewResult.matched_template.name }}</strong>
            <span> · {{ previewResult.fallback_used ? '使用兜底匹配' : '精准命中' }}</span>
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

type ApiErrorLike = {
  response?: {
    status?: number
    data?: {
      detail?: string
    }
  }
  message?: string
}

const scenicAreas = ref<ScenicArea[]>([])
const scenicSpots = ref<ScenicSpot[]>([])
const templates = ref<RouteTemplate[]>([])
const editingId = ref<number | null>(null)
const previewResult = ref<RecommendationResult | null>(null)
const formError = ref('')
const previewError = ref('')

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
    .split(/[,，]/)
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

function validateTemplatePayload(payload: ReturnType<typeof buildTemplatePayload>): string {
  if (!payload.name.trim()) {
    return '请填写模板名称。'
  }
  if (!payload.scenic_area_id) {
    return '请选择所属景区。'
  }
  if (payload.duration_min_minutes <= 0 || payload.duration_max_minutes <= 0) {
    return '适用时长必须大于 0 分钟。'
  }
  if (payload.duration_min_minutes > payload.duration_max_minutes) {
    return '最短适用时长不能大于最长适用时长。'
  }
  if (!payload.spots.length) {
    return '请至少配置一个路线站点。'
  }
  const invalidSpot = payload.spots.find((item) => item.sort_order <= 0)
  if (invalidSpot) {
    return '站点顺序必须大于 0。'
  }
  return ''
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
  form.interest_tags_text = item.interest_tags.join(',')
  form.audience_tags_text = item.audience_tags.join(',')
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
  formError.value = validateTemplatePayload(payload)
  if (formError.value) {
    return
  }
  if (editingId.value) {
    await apiClient.put(`/route-templates/${editingId.value}`, payload)
  } else {
    await apiClient.post('/route-templates', payload)
  }
  resetForm()
  await loadTemplates()
}

async function deleteTemplate(templateId: number) {
  if (!window.confirm('确认删除该路线模板吗？删除后无法恢复。')) {
    return
  }
  await apiClient.delete(`/route-templates/${templateId}`)
  if (editingId.value === templateId) {
    resetForm()
  }
  await loadTemplates()
}

async function generatePreview() {
  previewError.value = ''
  if (preview.duration_minutes <= 0) {
    previewError.value = '预览游玩时长必须大于 0 分钟。'
    previewResult.value = null
    return
  }
  try {
    const response = await apiClient.post('/route-recommendations/generate', {
      scenic_area_id: preview.scenic_area_id || null,
      interest_tags: parseTags(preview.interest_tags_text),
      audience_tags: parseTags(preview.audience_tags_text),
      duration_minutes: Number(preview.duration_minutes || 0),
    })
    previewResult.value = response.data
  } catch (error) {
    previewResult.value = null
    previewError.value = getPreviewErrorMessage(error)
  }
}

function getPreviewErrorMessage(error: unknown): string {
  const apiError = error as ApiErrorLike
  if (apiError.response?.status === 404) {
    return '当前条件没有可用的启用路线模板，请先创建并启用对应景区的路线模板。'
  }
  if (apiError.response?.status === 422) {
    return '预览条件不完整或格式不正确，请检查景区、标签和游玩时长。'
  }
  if (apiError.response?.data?.detail) {
    return apiError.response.data.detail
  }
  return apiError.message || '生成推荐路线失败，请稍后重试。'
}

onMounted(async () => {
  await Promise.all([loadScenicAreas(), loadScenicSpots(), loadTemplates()])
})
</script>

<style scoped>
.route-template-grid {
  display: grid;
  grid-template-columns: minmax(360px, 560px) 1fr;
  gap: 20px;
}

.route-template-duration {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.route-template-field {
  display: grid;
  gap: 6px;
  min-width: 0;
}

.route-template-field span {
  color: #334155;
  font-size: 14px;
  font-weight: 700;
}

.route-template-field small,
.route-template-stops__header p {
  margin: 0;
  color: #64748b;
  font-size: 12px;
  line-height: 1.45;
}

.route-template-error {
  margin: 0;
  padding: 10px 12px;
  color: #b42318;
  background: #fff4ed;
  border: 1px solid #ffd6ae;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.5;
}

.route-template-error--wide {
  grid-column: 1 / -1;
}

.route-template-stops {
  display: grid;
  gap: 12px;
}

.route-template-stops__header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.route-template-stops__header h3 {
  margin: 0;
}

.route-template-stop {
  display: grid;
  grid-template-columns: 1.35fr 110px 150px 1fr auto;
  gap: 10px;
  align-items: start;
  padding: 12px;
  border-radius: 16px;
  background: #f8fbff;
}

.route-template-stop__remove {
  align-self: end;
}

.route-preview-form {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
  align-items: start;
}

.route-preview-form select,
.route-preview-form input,
.route-preview-form button {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
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
