<template>
  <section class="login-page">
    <div class="login-card">
      <p class="login-card__eyebrow">景区导览服务 AI 数字人</p>
      <h1>后台登录</h1>
      <form class="login-form">
        <label class="login-form__field">
          <span>用户名</span>
          <input v-model="form.username" autocomplete="username" type="text" />
        </label>
        <label class="login-form__field">
          <span>密码</span>
          <input v-model="form.password" autocomplete="current-password" type="password" />
        </label>
        <button type="button">登录</button>
      </form>
    </div>
  </section>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

const form = reactive({
  username: '',
  password: '',
})
</script>

<style scoped>
.login-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at top, rgba(51, 94, 234, 0.18), transparent 35%),
    linear-gradient(135deg, #f8fbff 0%, #eef3fb 48%, #e3ebf8 100%);
}

.login-card {
  width: min(100%, 420px);
  padding: 32px;
  border: 1px solid rgba(29, 53, 87, 0.12);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 24px 60px rgba(29, 53, 87, 0.14);
}

.login-card__eyebrow {
  margin: 0 0 8px;
  color: #335eea;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.login-card h1 {
  margin: 0 0 24px;
  font-size: 32px;
}

.login-form {
  display: grid;
  gap: 16px;
}

.login-form__field {
  display: grid;
  gap: 8px;
}

.login-form__field span {
  font-size: 14px;
  font-weight: 600;
}

.login-form__field input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  background: #fff;
}

.login-form button {
  padding: 12px 16px;
  border: 0;
  border-radius: 12px;
  color: #fff;
  background: #1d4ed8;
}
</style>
