<template>
  <section class="import-card">
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
    <div class="import-card__form">
      <input v-model="sourcePath" :placeholder="placeholder" type="text" />
      <select v-if="requireScenicArea" v-model="scenicAreaId">
        <option value="">选择景区</option>
        <option v-for="item in scenicAreas" :key="item.id" :value="String(item.id)">
          {{ item.name }}
        </option>
      </select>
      <button :disabled="loading" type="button" @click="handleSubmit">
        {{ loading ? '提交中...' : buttonText }}
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = withDefaults(
  defineProps<{
    title: string
    description: string
    buttonText?: string
    placeholder?: string
    requireScenicArea?: boolean
    scenicAreas?: Array<{ id: number; name: string }>
    loading?: boolean
  }>(),
  {
    buttonText: '提交导入',
    placeholder: '输入源文件路径',
    requireScenicArea: false,
    scenicAreas: () => [],
    loading: false,
  },
)

const emit = defineEmits<{
  submit: [payload: { sourcePath: string; scenicAreaId: number | null }]
}>()

const sourcePath = ref('')
const scenicAreaId = ref('')

function handleSubmit() {
  emit('submit', {
    sourcePath: sourcePath.value,
    scenicAreaId: scenicAreaId.value ? Number(scenicAreaId.value) : null,
  })
}
</script>

<style scoped>
.import-card {
  padding: 20px;
  border: 1px solid #dbe4f0;
  border-radius: 20px;
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
  border-radius: 12px;
}

.import-card__form button {
  width: fit-content;
  padding: 10px 14px;
  border: 0;
  border-radius: 12px;
  color: #fff;
  background: #2563eb;
}
</style>
