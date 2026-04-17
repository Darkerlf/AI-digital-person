<template>
  <header class="app-header">
    <div>
      <p class="app-header__eyebrow">Scenic Guide Admin</p>
      <h1>{{ title }}</h1>
      <p v-if="description" class="app-header__description">{{ description }}</p>
    </div>
    <button class="app-header__logout" type="button" @click="handleLogout">退出登录</button>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const title = computed(() => String(route.meta.title ?? '后台管理'))
const description = computed(() => String(route.meta.description ?? ''))

function handleLogout() {
  localStorage.removeItem('accessToken')
  router.push('/login')
}
</script>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: start;
  margin-bottom: 24px;
}

.app-header__eyebrow {
  margin: 0 0 8px;
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.app-header h1 {
  margin: 0 0 8px;
  font-size: 30px;
}

.app-header__description {
  margin: 0;
  color: #64748b;
}

.app-header__logout {
  padding: 10px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  background: #fff;
}
</style>
