<template>
  <section class="chunk-preview">
    <h3>分块预览</h3>
    <ul v-if="items.length" class="chunk-preview__list">
      <li v-for="item in items" :key="item.id">
        <strong>#{{ item.chunk_index }}</strong>
        <p>{{ item.chunk_text }}</p>
      </li>
    </ul>
    <p v-else>暂无知识分块。</p>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  items: Array<{
    id: number
    chunk_index: number
    chunk_text: string
  }>
}>()
</script>

<style scoped>
.chunk-preview {
  padding: 20px;
  border: 1px solid #dbe4f0;
  border-radius: 20px;
  background: #fff;
}

.chunk-preview h3 {
  margin: 0 0 16px;
}

.chunk-preview__list {
  display: grid;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.chunk-preview__list li {
  padding: 14px;
  border-radius: 14px;
  background: #f8fbff;
}

.chunk-preview__list p {
  margin: 8px 0 0;
  white-space: pre-wrap;
}
</style>
