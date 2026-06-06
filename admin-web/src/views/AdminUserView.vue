<template>
  <section class="page-shell">
    <div class="page-shell__grid">
      <form class="page-shell__panel page-shell__form" @submit.prevent="handleSubmit">
        <h2>{{ editingId ? '编辑管理员' : '新增管理员' }}</h2>
        <input v-model="form.username" :disabled="Boolean(editingId)" placeholder="用户名" type="text" />
        <input v-model="form.password" placeholder="密码" type="password" />
        <select v-model="form.role" name="role">
          <option value="super_admin">超级管理员</option>
          <option value="content_admin">内容管理员</option>
          <option value="ops_admin">运营管理员</option>
        </select>
        <select v-model="form.status" name="status">
          <option value="active">启用</option>
          <option value="inactive">停用</option>
        </select>
        <div class="admin-user-view__actions">
          <button type="submit">{{ editingId ? '更新用户' : '创建用户' }}</button>
          <button v-if="editingId" type="button" @click="resetForm">取消</button>
        </div>
      </form>

      <section class="page-shell__panel">
        <h2>管理员列表</h2>
        <ul class="page-shell__list">
          <li v-for="item in items" :key="item.id">
            <div>
              <strong>{{ item.username }}</strong>
              <p>{{ roleLabel(item.role) }} / {{ statusLabel(item.status) }}</p>
              <p v-if="item.last_login_at">最近登录：{{ item.last_login_at }}</p>
            </div>
            <button :data-test="`edit-user-${item.id}`" type="button" @click="startEdit(item)">编辑</button>
          </li>
        </ul>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'

import { apiClient } from '../api/client'

type AdminUser = {
  id: number
  username: string
  role: string
  status: string
  last_login_at: string | null
}

const items = ref<AdminUser[]>([])
const editingId = ref<number | null>(null)
const form = reactive({
  username: '',
  password: '',
  role: 'content_admin',
  status: 'active',
})

async function loadUsers() {
  const response = await apiClient.get('/settings/admin-users')
  items.value = response.data.items
}

function resetForm() {
  editingId.value = null
  form.username = ''
  form.password = ''
  form.role = 'content_admin'
  form.status = 'active'
}

function startEdit(item: AdminUser) {
  editingId.value = item.id
  form.username = item.username
  form.password = ''
  form.role = item.role
  form.status = item.status
}

async function handleSubmit() {
  if (editingId.value) {
    const payload: { role: string; status: string; password?: string } = {
      role: form.role,
      status: form.status,
    }
    if (form.password) {
      payload.password = form.password
    }
    await apiClient.put(`/settings/admin-users/${editingId.value}`, payload)
  } else {
    await apiClient.post('/settings/admin-users', {
      username: form.username,
      password: form.password,
      role: form.role,
      status: form.status,
    })
  }
  resetForm()
  await loadUsers()
}

function roleLabel(role: string) {
  const labels: Record<string, string> = {
    super_admin: '超级管理员',
    content_admin: '内容管理员',
    ops_admin: '运营管理员',
  }
  return labels[role] ?? role
}

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    active: '启用',
    inactive: '停用',
  }
  return labels[status] ?? status
}

onMounted(() => {
  void loadUsers()
})
</script>

<style scoped>
.admin-user-view__actions {
  display: flex;
  gap: 8px;
}
</style>
