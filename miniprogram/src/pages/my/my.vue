<template>
  <view class="page">
    <view class="user-card">
      <view class="user-avatar">😊</view>
      <view class="user-info">
        <text class="user-name">游客</text>
        <text class="user-id">ID: {{ authStore.visitorId.slice(0, 12) }}...</text>
      </view>
    </view>

    <view class="menu-section">
      <view class="menu-item" @tap="goToHistory">
        <text class="menu-icon">💬</text>
        <text class="menu-text">对话历史</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @tap="goToFeedback">
        <text class="menu-icon">⭐</text>
        <text class="menu-text">意见反馈</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @tap="goToAbout">
        <text class="menu-icon">ℹ️</text>
        <text class="menu-text">关于景区</text>
        <text class="menu-arrow">›</text>
      </view>
    </view>

    <view class="danger-zone">
      <view class="menu-item" @tap="clearData">
        <text class="menu-icon">🗑️</text>
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
import { useAuthStore } from '../../stores/auth'
import { useChatStore } from '../../stores/chat'

const authStore = useAuthStore()
const chatStore = useChatStore()

function goToHistory() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function goToFeedback() {
  uni.showToast({ title: '功能开发中', icon: 'none' })
}

function goToAbout() {
  uni.showModal({
    title: '关于灵山胜境',
    content: '灵山胜境位于江苏省无锡市，是国家5A级旅游景区。景区以灵山大佛为核心，汇集梵宫、五印坛城等著名景点。',
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
.page { min-height: 100vh; background: #f5f5f5; }
.user-card { display: flex; align-items: center; gap: 24rpx; padding: 40rpx 30rpx; background: linear-gradient(135deg, #1a73e8, #0d47a1); }
.user-avatar { width: 100rpx; height: 100rpx; border-radius: 50%; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-size: 48rpx; }
.user-info { display: flex; flex-direction: column; gap: 8rpx; }
.user-name { font-size: 32rpx; font-weight: bold; color: #ffffff; }
.user-id { font-size: 22rpx; color: rgba(255,255,255,0.7); }
.menu-section { margin-top: 20rpx; background: #ffffff; border-radius: 12rpx; margin-left: 20rpx; margin-right: 20rpx; overflow: hidden; }
.danger-zone { margin-top: 20rpx; background: #ffffff; border-radius: 12rpx; margin-left: 20rpx; margin-right: 20rpx; overflow: hidden; }
.menu-item { display: flex; align-items: center; padding: 28rpx 24rpx; border-bottom: 1rpx solid #f0f0f0; }
.menu-item:last-child { border-bottom: none; }
.menu-icon { font-size: 36rpx; margin-right: 20rpx; }
.menu-text { flex: 1; font-size: 28rpx; color: #333; }
.menu-arrow { font-size: 32rpx; color: #ccc; }
.footer { text-align: center; margin-top: 60rpx; padding-bottom: 40rpx; }
.version { font-size: 22rpx; color: #ccc; }
</style>
