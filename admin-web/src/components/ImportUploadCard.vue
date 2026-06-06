<template>
  <section class="import-card">
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
    <div class="import-card__form">
      <input type="file" @change="handleFileChange" />
      <p v-if="selectedFile" class="import-card__file">{{ selectedFile.name }}</p>
      <select v-if="requireScenicArea" v-model="scenicAreaId">
        <option value="">选择景区</option>
        <option v-for="item in scenicAreas" :key="item.id" :value="String(item.id)">
          {{ item.name }}
        </option>
      </select>
      <button :disabled="loading || !selectedFile" type="button" @click="handleSubmit">
        {{ loading ? '提交中...' : buttonText }}
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

withDefaults(
  defineProps<{
    title: string
    description: string
    buttonText?: string
    requireScenicArea?: boolean
    scenicAreas?: Array<{ id: number; name: string }>
    loading?: boolean
  }>(),
  {
    buttonText: '提交导入',
    requireScenicArea: false,
    scenicAreas: () => [],
    loading: false,
  },
)

const emit = defineEmits<{
  submit: [payload: { file: File; scenicAreaId: number | null }]
}>()

const selectedFile = ref<File | null>(null)
const scenicAreaId = ref('')

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  selectedFile.value = input.files?.[0] ?? null
}

function handleSubmit() {
  if (!selectedFile.value) {
    return
  }
  emit('submit', {
    file: selectedFile.value,
    scenicAreaId: scenicAreaId.value ? Number(scenicAreaId.value) : null,
  })
}
</script>

<style scoped>
.import-card {
  padding: 20px;
  border: 1px solid #dbe4f0;
  border-radius: 8px;
  background: #fff;
}

.import-card h3,
.import-card p {
  margin: 0 0 12px;
}

.import-card__form {
  display: grid;
  gap: 12px;
}

.import-card__form input,
.import-card__form select {
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
}

.import-card__file {
  color: #475569;
  font-size: 14px;
}

.import-card__form button {
  width: fit-content;
  padding: 10px 14px;
  border: 0;
  border-radius: 8px;
  color: #fff;
  background: #2563eb;
}

.import-card__form button:disabled {
  opacity: 0.55;
}
</style>
