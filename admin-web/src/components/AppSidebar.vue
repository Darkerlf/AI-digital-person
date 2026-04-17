<template>
  <aside class="app-sidebar">
    <div class="app-sidebar__brand">Scenic Admin</div>
    <nav class="app-sidebar__nav">
      <RouterLink
        v-for="item in items"
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
import { RouterLink } from 'vue-router'

const items = [
  { to: '/', label: '工作台' },
  { to: '/scenic-areas', label: '景区管理' },
  { to: '/scenic-spots', label: '景点管理' },
  { to: '/route-templates', label: '路线模板' },
  { to: '/knowledge/documents', label: '知识管理' },
  { to: '/knowledge/faqs', label: 'FAQ 管理' },
  { to: '/sessions', label: '会话管理' },
  { to: '/imports', label: '数据导入' },
  { to: '/feedback-report', label: '感受度报告' },
  { to: '/digital-humans', label: '数字人配置' },
  { to: '/settings/ai-providers', label: 'AI 配置' },
  { to: '/operation-logs', label: '操作日志' },
]
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
