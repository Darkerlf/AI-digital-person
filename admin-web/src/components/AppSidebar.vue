<template>
  <aside class="app-sidebar">
    <div class="app-sidebar__brand">Scenic Admin</div>
    <nav class="app-sidebar__nav">
      <RouterLink
        v-for="item in visibleItems"
        :key="item.to"
        :to="item.to"
        class="app-sidebar__link"
      >
        {{ item.label }}
      </RouterLink>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const items = [
  { to: '/', label: '工作台', roles: ['super_admin', 'ops_admin'] },
  { to: '/scenic-areas', label: '景区管理', roles: ['super_admin', 'content_admin'] },
  { to: '/scenic-spots', label: '景点管理', roles: ['super_admin', 'content_admin'] },
  { to: '/route-templates', label: '路线模板', roles: ['super_admin', 'content_admin'] },
  { to: '/knowledge/documents', label: '知识管理', roles: ['super_admin', 'content_admin'] },
  { to: '/knowledge/correction-tasks', label: '知识修正任务', roles: ['super_admin', 'content_admin'] },
  { to: '/knowledge/faqs', label: 'FAQ 管理', roles: ['super_admin', 'content_admin'] },
  { to: '/sessions', label: '会话管理', roles: ['super_admin', 'content_admin', 'ops_admin'] },
  { to: '/imports', label: '数据导入', roles: ['super_admin', 'content_admin'] },
  { to: '/feedback-report', label: '感受度报告', roles: ['super_admin', 'ops_admin'] },
  { to: '/digital-humans', label: '数字人配置', roles: ['super_admin', 'content_admin'] },
  { to: '/settings/ai-providers', label: 'AI 配置', roles: ['super_admin'] },
  { to: '/operation-logs', label: '操作日志', roles: ['super_admin', 'ops_admin'] },
]

const authStore = useAuthStore()
const visibleItems = computed(() => {
  if (!authStore.role) {
    return []
  }
  return items.filter((item) => item.roles.includes(authStore.role))
})
</script>

<style scoped>
.app-sidebar {
  height: 100%;
  padding: 24px 18px;
  color: #dfe8f7;
  background: linear-gradient(180deg, #17304f 0%, #09121f 100%);
}

.app-sidebar__brand {
  margin-bottom: 24px;
  font-size: 20px;
  font-weight: 700;
}

.app-sidebar__nav {
  display: grid;
  gap: 8px;
}

.app-sidebar__link {
  padding: 10px 12px;
  border-radius: 12px;
  color: inherit;
  text-decoration: none;
  transition: background 0.2s ease;
}

.app-sidebar__link.router-link-active {
  background: rgba(255, 255, 255, 0.12);
}
</style>
