<template>
  <section class="login-page" :style="{ '--login-bg': `url(${loginBackground})` }">
    <div class="login-page__shade"></div>
    <main class="login-shell" aria-label="后台登录">
      <section class="login-hero" aria-label="灵山胜境后台">
        <p class="login-hero__kicker">SCENIC GUIDE ADMIN</p>
        <h1>灵山胜境 AI 数字人运营后台</h1>
        <p class="login-hero__summary">
          汇聚景区内容、路线、知识库与数字人配置，让导览服务保持清晰、准确和可运营。
        </p>
        <div class="login-hero__meta" aria-label="后台能力">
          <span>知识库</span>
          <span>路线推荐</span>
          <span>数字人配置</span>
        </div>
      </section>

      <section class="login-card" aria-label="登录表单">
        <div class="login-card__header">
          <p>安全入口</p>
          <h2>后台登录</h2>
        </div>
        <form class="login-form" @submit.prevent="handleLogin">
          <label class="login-form__field">
            <span>用户名</span>
            <input v-model="form.username" autocomplete="username" type="text" />
          </label>
          <label class="login-form__field">
            <span>密码</span>
            <input v-model="form.password" autocomplete="current-password" type="password" />
          </label>
          <p v-if="errorMessage" class="login-form__error">{{ errorMessage }}</p>
          <button :disabled="isSubmitting" type="submit">
            {{ isSubmitting ? '登录中...' : '登录' }}
          </button>
        </form>
      </section>
    </main>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { apiClient } from '../api/client'
import { loginBackground } from '../config/loginBackground'
import { getDefaultRouteByRole, useAuthStore } from '../stores/auth'

const form = reactive({
  username: '',
  password: '',
})

const router = useRouter()
const authStore = useAuthStore()
const errorMessage = ref('')
const isSubmitting = ref(false)

async function handleLogin() {
  errorMessage.value = ''
  isSubmitting.value = true
  try {
    const response = await apiClient.post('/auth/login', form)
    authStore.setToken(response.data.access_token)
    await authStore.fetchProfile()
    await router.push(getDefaultRouteByRole(authStore.role))
  } catch (error) {
    errorMessage.value = '登录失败，请检查用户名和密码。'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  display: grid;
  min-height: 100dvh;
  overflow: hidden;
  padding: clamp(24px, 4vw, 64px);
  background:
    linear-gradient(90deg, rgba(5, 14, 24, 0.22), rgba(5, 14, 24, 0.62)),
    var(--login-bg) center / cover no-repeat;
  color: #f8fafc;
}

.login-page__shade {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 22% 18%, rgba(255, 218, 150, 0.22), transparent 28%),
    linear-gradient(180deg, rgba(5, 14, 24, 0.08), rgba(5, 14, 24, 0.7));
  pointer-events: none;
}

.login-shell {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 440px);
  gap: clamp(32px, 7vw, 120px);
  width: min(1180px, 100%);
  margin: auto;
  align-items: center;
}

.login-hero {
  max-width: 640px;
  padding-block: 32px;
}

.login-hero__kicker,
.login-card__header p {
  margin: 0;
  color: #a7f3d0;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.14em;
}

.login-hero h1 {
  max-width: 12ch;
  margin: 18px 0 18px;
  color: #ffffff;
  font-size: clamp(44px, 6vw, 76px);
  line-height: 1.02;
  letter-spacing: 0;
  text-shadow: 0 18px 60px rgba(0, 0, 0, 0.36);
}

.login-hero__summary {
  max-width: 34em;
  margin: 0;
  color: rgba(248, 250, 252, 0.86);
  font-size: 17px;
  line-height: 1.8;
}

.login-hero__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 28px;
}

.login-hero__meta span {
  padding: 9px 13px;
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: 999px;
  background: rgba(12, 22, 32, 0.32);
  color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(14px);
}

.login-card {
  width: 100%;
  padding: clamp(28px, 4vw, 40px);
  border: 1px solid rgba(255, 255, 255, 0.36);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 28px 80px rgba(5, 14, 24, 0.34);
  color: #0f172a;
  backdrop-filter: blur(24px);
}

.login-card__header {
  margin-bottom: 28px;
}

.login-card__header p {
  color: #047857;
}

.login-card__header h2 {
  margin: 8px 0 0;
  font-size: 34px;
  line-height: 1.15;
  letter-spacing: 0;
}

.login-form {
  display: grid;
  gap: 18px;
}

.login-form__field {
  display: grid;
  gap: 9px;
}

.login-form__field span {
  color: #172033;
  font-size: 14px;
  font-weight: 800;
}

.login-form__field input {
  width: 100%;
  min-height: 52px;
  padding: 13px 15px;
  border: 1px solid rgba(71, 85, 105, 0.28);
  border-radius: 14px;
  outline: none;
  background: rgba(255, 255, 255, 0.94);
  color: #0f172a;
  font-size: 16px;
  transition:
    border-color 160ms ease,
    box-shadow 160ms ease,
    background 160ms ease;
}

.login-form__field input:focus {
  border-color: #047857;
  background: #ffffff;
  box-shadow: 0 0 0 4px rgba(4, 120, 87, 0.16);
}

.login-form button {
  min-height: 54px;
  margin-top: 4px;
  border: 0;
  border-radius: 14px;
  color: #ffffff;
  background: linear-gradient(135deg, #047857, #0f766e);
  box-shadow: 0 16px 32px rgba(4, 120, 87, 0.26);
  font-size: 17px;
  font-weight: 800;
  cursor: pointer;
  transition:
    transform 140ms ease,
    box-shadow 140ms ease,
    filter 140ms ease;
}

.login-form button:hover {
  filter: brightness(1.05);
  box-shadow: 0 18px 38px rgba(4, 120, 87, 0.34);
}

.login-form button:active {
  transform: translateY(1px) scale(0.99);
}

.login-form button:disabled {
  cursor: not-allowed;
  filter: grayscale(0.25);
  opacity: 0.72;
}

.login-form__error {
  margin: 0;
  padding: 10px 12px;
  border: 1px solid rgba(185, 28, 28, 0.2);
  border-radius: 12px;
  background: rgba(254, 242, 242, 0.9);
  color: #991b1b;
  font-size: 14px;
}

@media (max-width: 860px) {
  .login-page {
    padding: 20px;
  }

  .login-shell {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .login-hero {
    max-width: 100%;
    padding-block: 12px 0;
  }

  .login-hero h1 {
    max-width: 14ch;
    font-size: clamp(34px, 12vw, 48px);
  }

  .login-hero__summary {
    font-size: 15px;
  }

  .login-card {
    border-radius: 18px;
  }
}
</style>
