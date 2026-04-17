<template>
  <div class="admin-layout">
    <aside class="admin-layout__sidebar">
      <div class="admin-layout__brand">Scenic Admin</div>
      <nav class="admin-layout__nav">
        <RouterLink to="/">工作台</RouterLink>
      </nav>
    </aside>
    <main class="admin-layout__content">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.admin-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
}

.admin-layout__sidebar {
  padding: 24px;
  color: #e5eefc;
  background: linear-gradient(180deg, #1d3557 0%, #0b1320 100%);
}

.admin-layout__brand {
  margin-bottom: 24px;
  font-size: 20px;
  font-weight: 700;
}

.admin-layout__nav a {
  color: inherit;
  text-decoration: none;
}

.admin-layout__content {
  padding: 32px;
}

@media (max-width: 768px) {
  .admin-layout {
    grid-template-columns: 1fr;
  }
}
</style>
