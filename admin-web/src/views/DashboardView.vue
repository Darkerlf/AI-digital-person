<template>
  <AdminLayout>
    <section class="dashboard-view">
      <p class="dashboard-view__eyebrow">Admin Dashboard</p>
      <h1>后台工作台</h1>
      <p>Task 9 前端壳已建立，后续页面将在 Task 10 中继续接入真实接口。</p>
    </section>
  </AdminLayout>
</template>

<script setup lang="ts">
import AdminLayout from '../layouts/AdminLayout.vue'
</script>

<style scoped>
.dashboard-view__eyebrow {
  margin: 0 0 8px;
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.dashboard-view h1 {
  margin: 0 0 16px;
  font-size: 32px;
}

.dashboard-view p {
  margin: 0;
  max-width: 720px;
  line-height: 1.6;
}
</style>
