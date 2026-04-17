<template>
  <div class="admin-layout">
    <AppSidebar />
    <main class="admin-layout__content">
      <AppHeader />
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'

import AppHeader from '../components/AppHeader.vue'
import AppSidebar from '../components/AppSidebar.vue'
</script>

<style scoped>
.admin-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
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
