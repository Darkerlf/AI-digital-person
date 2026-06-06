<template>
  <view class="page">
    <view class="user-card">
      <image v-if="authStore.isLoggedIn && authStore.avatarUrl" class="user-avatar-img" :src="authStore.avatarUrl" mode="aspectFill" />
      <view v-else class="user-avatar"><text>{{ authStore.isLoggedIn ? '游' : '客' }}</text></view>
      <view class="user-info">
        <text class="user-name">{{ authStore.isLoggedIn ? displayName : '游客' }}</text>
        <text v-if="authStore.isLoggedIn" class="user-id">ID: {{ authStore.visitorDbId }}</text>
        <text v-else class="user-id">登录后可保存头像、昵称和反馈记录</text>
      </view>
      <view v-if="!authStore.isLoggedIn" class="login-btn" @tap="handleLogin">微信登录</view>
    </view>

    <view v-if="authStore.isLoggedIn" class="profile-section">
      <text class="section-title">个人资料</text>
      <view class="profile-row">
        <text class="profile-label">头像</text>
        <button class="avatar-picker" open-type="chooseAvatar" @chooseavatar="handleChooseAvatar">
          <image v-if="draftAvatarUrl" class="avatar-preview" :src="draftAvatarUrl" mode="aspectFill" />
          <text v-else>选择头像</text>
        </button>
      </view>
      <view class="profile-row">
        <text class="profile-label">昵称</text>
        <input
          v-model="draftNickname"
          class="nickname-input"
          type="nickname"
          placeholder="请输入微信昵称"
          @blur="syncNickname"
        />
      </view>
      <button class="save-profile-btn" @tap="saveProfile">保存资料</button>
    </view>

    <view class="menu-section">
      <view class="menu-item" @tap="goToHistory">
        <text class="menu-icon">话</text>
        <text class="menu-text">对话历史</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @tap="goToFeedback">
        <text class="menu-icon">评</text>
        <text class="menu-text">意见反馈</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @tap="goToAbout">
        <text class="menu-icon">景</text>
        <text class="menu-text">关于景区</text>
        <text class="menu-arrow">›</text>
      </view>
    </view>

    <view v-if="authStore.isLoggedIn" class="menu-section">
      <view class="menu-item" @tap="handleLogout">
        <text class="menu-icon warn">退</text>
        <text class="menu-text">退出登录</text>
        <text class="menu-arrow">›</text>
      </view>
    </view>

    <view class="danger-zone">
      <view class="menu-item" @tap="clearData">
        <text class="menu-icon danger">清</text>
        <text class="menu-text">清除对话记录</text>
        <text class="menu-arrow">›</text>
      </view>
    </view>

    <view class="footer">
      <text class="version">灵山胜境 AI 导游 v1.0.0</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { getRecentRecords } from '../../api/tourist'
import { useAuthStore } from '../../stores/auth'
import { useChatStore } from '../../stores/chat'

const authStore = useAuthStore()
const chatStore = useChatStore()
const draftNickname = ref(authStore.nickname || '')
const draftAvatarUrl = ref(authStore.avatarUrl || '')
const selectedAvatarPath = ref('')
const displayName = computed(() => authStore.nickname || '请完善昵称')

watch(
  () => [authStore.nickname, authStore.avatarUrl],
  () => {
    draftNickname.value = authStore.nickname || ''
    draftAvatarUrl.value = authStore.avatarUrl || ''
    selectedAvatarPath.value = ''
  },
)

async function handleLogin() {
  uni.showLoading({ title: '登录中...' })
  const ok = await authStore.wxLogin()
  uni.hideLoading()
  if (ok) {
    uni.showToast({ title: '登录成功，请完善资料', icon: 'none' })
  } else {
    uni.showToast({ title: '登录失败，请重试', icon: 'none' })
  }
}

function handleChooseAvatar(event: { detail?: { avatarUrl?: string } }) {
  const avatarUrl = event.detail?.avatarUrl
  if (avatarUrl) {
    draftAvatarUrl.value = avatarUrl
    selectedAvatarPath.value = avatarUrl
  }
}

function syncNickname(event: { detail?: { value?: string } }) {
  draftNickname.value = event.detail?.value || draftNickname.value
}

async function saveProfile() {
  if (!authStore.isLoggedIn) return
  const nickname = draftNickname.value.trim()
  if (!nickname) {
    uni.showToast({ title: '请先填写昵称', icon: 'none' })
    return
  }

  uni.showLoading({ title: '保存中...' })
  if (selectedAvatarPath.value) {
    const uploaded = await authStore.uploadAvatar(selectedAvatarPath.value)
    if (!uploaded) {
      uni.hideLoading()
      uni.showToast({ title: '头像上传失败，请稍后重试', icon: 'none' })
      return
    }
    selectedAvatarPath.value = ''
    draftAvatarUrl.value = authStore.avatarUrl
  }
  const ok = await authStore.saveProfile({
    nickname,
  })
  uni.hideLoading()
  uni.showToast({ title: ok ? '资料已更新' : '保存失败，请重试', icon: ok ? 'success' : 'none' })
}

function handleLogout() {
  uni.showModal({
    title: '确认退出',
    content: '退出登录后将清除本地会话状态。',
    success: (res) => {
      if (res.confirm) {
        authStore.logout()
        chatStore.clearMessages()
        uni.showToast({ title: '已退出', icon: 'success' })
      }
    },
  })
}

function goToHistory() {
  const visitorId = authStore.isLoggedIn ? String(authStore.visitorDbId) : undefined
  getRecentRecords(visitorId)
    .then((res) => {
      const first = res.items?.[0]?.messages?.[0]
      if (!first) {
        uni.showToast({ title: '暂无对话记录', icon: 'none' })
        return
      }
      uni.showModal({
        title: '最近对话',
        content: `问：${first.question_text}\n答：${first.answer_text || '暂无回答'}`,
        showCancel: false,
      })
    })
    .catch(() => {
      uni.showToast({ title: '记录加载失败', icon: 'none' })
    })
}

function goToFeedback() {
  uni.navigateTo({ url: '/pages/feedback/feedback' })
}

function goToAbout() {
  uni.showModal({
    title: '关于灵山胜境',
    content: '灵山胜境位于江苏省无锡市，是国家5A旅游景区。景区以灵山大佛为核心，汇集梵宫、五印坛城等著名景点。',
    showCancel: false,
  })
}

function clearData() {
  uni.showModal({
    title: '确认清除',
    content: '清除所有对话记录？此操作不可恢复。',
    success: (res) => {
      if (res.confirm) {
        chatStore.clearMessages()
        uni.showToast({ title: '已清除', icon: 'success' })
      }
    },
  })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 24rpx;
  background: linear-gradient(180deg, #f7fdfb 0%, #effaf7 36%, #e9fbf7 100%);
}

.user-card {
  display: flex;
  align-items: center;
  gap: 22rpx;
  padding: 34rpx 28rpx;
  border-radius: 20rpx;
  background:
    linear-gradient(135deg, rgba(239, 250, 247, 0.98), rgba(201, 241, 237, 0.96)),
    linear-gradient(160deg, rgba(42, 174, 192, 0.28), rgba(255, 255, 255, 0) 46%);
  box-shadow: 0 14rpx 34rpx rgba(35, 143, 163, 0.11);
}

.user-avatar,
.user-avatar-img {
  width: 104rpx;
  height: 104rpx;
  flex-shrink: 0;
  border-radius: 50%;
  border: 2rpx solid rgba(35, 143, 163, 0.24);
}

.user-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.58);
}

.user-avatar text {
  color: #238fa3;
  font-size: 36rpx;
  font-weight: 800;
}

.user-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.user-name {
  font-size: 32rpx;
  font-weight: 800;
  color: #123f49;
}

.user-id {
  font-size: 23rpx;
  line-height: 1.35;
  color: #4f626a;
}

.login-btn {
  height: 62rpx;
  padding: 0 22rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #238fa3;
  color: #ffffff;
  font-size: 24rpx;
  font-weight: 800;
}

.profile-section,
.menu-section,
.danger-zone {
  margin-top: 20rpx;
  padding: 0 24rpx;
  border-radius: 18rpx;
  background: #ffffff;
  border: 1rpx solid rgba(35, 143, 163, 0.08);
  box-shadow: 0 8rpx 24rpx rgba(35, 143, 163, 0.07);
}

.profile-section {
  padding-top: 24rpx;
  padding-bottom: 24rpx;
}

.section-title {
  display: block;
  margin-bottom: 14rpx;
  font-size: 29rpx;
  color: #17252b;
  font-weight: 800;
}

.profile-row,
.menu-item {
  display: flex;
  align-items: center;
  min-height: 88rpx;
  border-top: 1rpx solid #edf3f4;
}

.profile-row:first-of-type,
.menu-item:first-child {
  border-top: none;
}

.profile-label {
  width: 130rpx;
  font-size: 26rpx;
  color: #64747d;
}

.avatar-picker {
  min-width: 168rpx;
  height: 68rpx;
  padding: 0 20rpx;
  border-radius: 999rpx;
  background: #e9fbf7;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-picker text {
  color: #238fa3;
  font-size: 24rpx;
  font-weight: 700;
}

.avatar-preview {
  width: 58rpx;
  height: 58rpx;
  border-radius: 50%;
}

.nickname-input {
  flex: 1;
  min-width: 0;
  height: 72rpx;
  font-size: 28rpx;
  color: #17252b;
}

.save-profile-btn {
  margin-top: 18rpx;
  height: 76rpx;
  border-radius: 999rpx;
  background: #238fa3;
  color: #ffffff;
  font-size: 27rpx;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}

.menu-icon {
  width: 46rpx;
  height: 46rpx;
  flex-shrink: 0;
  margin-right: 18rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e9fbf7;
  color: #238fa3;
  font-size: 22rpx;
  font-weight: 800;
}

.menu-icon.warn,
.menu-icon.danger {
  background: #fff1ea;
  color: #b4533c;
}

.menu-text {
  flex: 1;
  min-width: 0;
  font-size: 28rpx;
  color: #17252b;
}

.menu-arrow {
  color: #93a5ac;
  font-size: 40rpx;
  line-height: 1;
}

.footer {
  text-align: center;
  margin-top: 56rpx;
  padding-bottom: 36rpx;
}

.version {
  font-size: 22rpx;
  color: #93a5ac;
}
</style>
