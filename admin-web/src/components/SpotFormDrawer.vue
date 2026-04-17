<template>
  <div v-if="open" class="spot-drawer">
    <div class="spot-drawer__panel">
      <header class="spot-drawer__header">
        <h3>{{ editingId ? '编辑景点' : '新增景点' }}</h3>
        <button type="button" @click="$emit('close')">关闭</button>
      </header>
      <div class="spot-drawer__form">
        <select v-model="form.scenic_area_id">
          <option value="">选择景区</option>
          <option v-for="item in scenicAreas" :key="item.id" :value="String(item.id)">
            {{ item.name }}
          </option>
        </select>
        <input v-model="form.spot_code" placeholder="景点编码" type="text" />
        <input v-model="form.name" placeholder="景点名称" type="text" />
        <input v-model="form.alias" placeholder="别名" type="text" />
        <input v-model="form.location_text" placeholder="位置描述" type="text" />
        <input v-model="form.tags" placeholder="标签，逗号分隔" type="text" />
        <select v-model="form.open_status">
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
  save: [
    payload: {
      scenic_area_id: number
      spot_code: string
      name: string
      alias: string | null
      location_text: string | null
      tags: string[]
      open_status: string
      id?: number
    },
  ]
}>()

const form = reactive({
  scenic_area_id: '',
  spot_code: '',
  name: '',
  alias: '',
  location_text: '',
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
    tags: form.tags
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean),
    open_status: form.open_status,
  })
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
  width: min(100%, 520px);
  padding: 24px;
  border-radius: 20px;
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

.spot-drawer__form input,
.spot-drawer__form select,
.spot-drawer__form button {
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
}

.spot-drawer__form button {
  color: #fff;
  background: #2563eb;
}
</style>
