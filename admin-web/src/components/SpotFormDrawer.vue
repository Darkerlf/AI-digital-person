<template>
  <div v-if="open" class="spot-drawer">
    <div class="spot-drawer__panel">
      <header class="spot-drawer__header">
        <h3>{{ editingId ? '编辑景点' : '新增景点' }}</h3>
        <button type="button" @click="$emit('close')">关闭</button>
      </header>
      <div class="spot-drawer__form">
        <select v-model="form.scenic_area_id" name="scenic_area_id">
          <option value="">选择景区</option>
          <option v-for="item in scenicAreas" :key="item.id" :value="String(item.id)">
            {{ item.name }}
          </option>
        </select>
        <input v-model="form.spot_code" name="spot_code" placeholder="景点编码" type="text" />
        <input v-model="form.name" name="name" placeholder="景点名称" type="text" />
        <input v-model="form.alias" name="alias" placeholder="别名" type="text" />
        <input v-model="form.cover_image_url" name="cover_image_url" placeholder="封面图片 URL" type="url" />
        <input v-model="form.location_text" name="location_text" placeholder="位置描述" type="text" />
        <div class="spot-drawer__coords">
          <input v-model="form.latitude" name="latitude" placeholder="GCJ-02 纬度" type="number" step="0.000001" />
          <input v-model="form.longitude" name="longitude" placeholder="GCJ-02 经度" type="number" step="0.000001" />
        </div>
        <input v-model="form.target_audience" name="target_audience" placeholder="适配人群" type="text" />
        <input
          v-model="form.suggested_duration_minutes"
          name="suggested_duration_minutes"
          placeholder="建议停留分钟数"
          type="number"
          min="0"
        />
        <input v-model="form.tags" name="tags" placeholder="标签，逗号分隔" type="text" />
        <textarea v-model="form.guide_text" name="guide_text" placeholder="讲解词" rows="4" />
        <textarea v-model="form.detail_intro" name="detail_intro" placeholder="详细介绍" rows="3" />
        <textarea v-model="form.highlights" name="highlights" placeholder="亮点" rows="3" />
        <textarea v-model="form.parameters_text" name="parameters_text" placeholder="参数信息" rows="3" />
        <textarea v-model="form.core_function" name="core_function" placeholder="核心功能" rows="3" />
        <textarea v-model="form.cultural_value" name="cultural_value" placeholder="文化价值" rows="3" />
        <textarea v-model="form.performance_info" name="performance_info" placeholder="演艺/开放信息" rows="3" />
        <textarea v-model="form.remarks" name="remarks" placeholder="备注" rows="3" />
        <select v-model="form.open_status" name="open_status">
          <option value="open">开放</option>
          <option value="closed">关闭</option>
        </select>
        <button type="button" @click="handleSave">保存</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'

type ScenicAreaOption = {
  id: number
  name: string
}

type SpotPayload = {
  id?: number
  scenic_area_id?: number
  spot_code?: string
  name?: string
  alias?: string | null
  location_text?: string | null
  latitude?: number | null
  longitude?: number | null
  cover_image_url?: string | null
  guide_text?: string | null
  target_audience?: string | null
  parameters_text?: string | null
  core_function?: string | null
  cultural_value?: string | null
  detail_intro?: string | null
  highlights?: string | null
  performance_info?: string | null
  remarks?: string | null
  suggested_duration_minutes?: number | null
  tags?: string[]
  open_status?: string
}

const props = defineProps<{
  open: boolean
  scenicAreas: ScenicAreaOption[]
  spot?: SpotPayload | null
}>()

const emit = defineEmits<{
  close: []
  save: [payload: SpotPayload & { scenic_area_id: number; spot_code: string; name: string; open_status: string }]
}>()

const form = reactive({
  scenic_area_id: '',
  spot_code: '',
  name: '',
  alias: '',
  location_text: '',
  latitude: '',
  longitude: '',
  cover_image_url: '',
  guide_text: '',
  target_audience: '',
  parameters_text: '',
  core_function: '',
  cultural_value: '',
  detail_intro: '',
  highlights: '',
  performance_info: '',
  remarks: '',
  suggested_duration_minutes: '',
  tags: '',
  open_status: 'open',
})

const editingId = defineModel<number | null>('editingId', { default: null })

watch(
  () => props.spot,
  (spot) => {
    form.scenic_area_id = spot?.scenic_area_id ? String(spot.scenic_area_id) : ''
    form.spot_code = spot?.spot_code ?? ''
    form.name = spot?.name ?? ''
    form.alias = spot?.alias ?? ''
    form.location_text = spot?.location_text ?? ''
    form.latitude = spot?.latitude != null ? String(spot.latitude) : ''
    form.longitude = spot?.longitude != null ? String(spot.longitude) : ''
    form.cover_image_url = spot?.cover_image_url ?? ''
    form.guide_text = spot?.guide_text ?? ''
    form.target_audience = spot?.target_audience ?? ''
    form.parameters_text = spot?.parameters_text ?? ''
    form.core_function = spot?.core_function ?? ''
    form.cultural_value = spot?.cultural_value ?? ''
    form.detail_intro = spot?.detail_intro ?? ''
    form.highlights = spot?.highlights ?? ''
    form.performance_info = spot?.performance_info ?? ''
    form.remarks = spot?.remarks ?? ''
    form.suggested_duration_minutes =
      spot?.suggested_duration_minutes != null ? String(spot.suggested_duration_minutes) : ''
    form.tags = spot?.tags?.join(', ') ?? ''
    form.open_status = spot?.open_status ?? 'open'
    editingId.value = spot?.id ?? null
  },
  { immediate: true },
)

function handleSave() {
  emit('save', {
    id: editingId.value ?? undefined,
    scenic_area_id: Number(form.scenic_area_id),
    spot_code: form.spot_code,
    name: form.name,
    alias: form.alias || null,
    location_text: form.location_text || null,
    latitude: parseOptionalNumber(form.latitude),
    longitude: parseOptionalNumber(form.longitude),
    cover_image_url: form.cover_image_url || null,
    guide_text: form.guide_text || null,
    target_audience: form.target_audience || null,
    parameters_text: form.parameters_text || null,
    core_function: form.core_function || null,
    cultural_value: form.cultural_value || null,
    detail_intro: form.detail_intro || null,
    highlights: form.highlights || null,
    performance_info: form.performance_info || null,
    remarks: form.remarks || null,
    suggested_duration_minutes: parseOptionalNumber(form.suggested_duration_minutes),
    tags: form.tags
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean),
    open_status: form.open_status,
  })
}

function parseOptionalNumber(value: string | number | null | undefined) {
  if (value == null) return null
  const normalized = String(value).trim()
  if (!normalized) return null
  const parsed = Number(normalized)
  return Number.isFinite(parsed) ? parsed : null
}
</script>

<style scoped>
.spot-drawer {
  position: fixed;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgba(15, 23, 42, 0.45);
}

.spot-drawer__panel {
  width: min(100%, 720px);
  max-height: 92vh;
  overflow: auto;
  padding: 24px;
  border-radius: 8px;
  background: #fff;
}

.spot-drawer__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.spot-drawer__header h3 {
  margin: 0;
}

.spot-drawer__form {
  display: grid;
  gap: 12px;
}

.spot-drawer__coords {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.spot-drawer__form input,
.spot-drawer__form select,
.spot-drawer__form textarea,
.spot-drawer__form button {
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
}

.spot-drawer__form textarea {
  resize: vertical;
}

.spot-drawer__form button {
  color: #fff;
  background: #2563eb;
}
</style>
