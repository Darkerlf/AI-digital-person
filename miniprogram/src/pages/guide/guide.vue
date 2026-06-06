<template>
  <view class="guide-live-shell">
    <view v-if="!loaded || failed" class="live-fallback">
      <view class="fallback-card">
        <text class="fallback-kicker">灵山胜境 AI 导游</text>
        <text class="fallback-title">{{ fallbackTitle }}</text>
        <text class="fallback-copy">
          {{ fallbackCopy }}
        </text>
        <view v-if="failed" class="retry-btn" @tap="reloadGuide">
          <text>重新加载</text>
        </view>
      </view>
    </view>

    <web-view
      v-if="canOpenWebView"
      class="live-webview"
      :src="url"
      @load="handleLoad"
      @message="handleMessage"
      @error="handleError"
    />
  </view>
</template>

<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { computed, onUnmounted, ref } from 'vue'
import { API_BASE_URL } from '../../api/request'
import { dhLiveGuideUrl } from '../../config/assets'
import { isSafeDhLiveWebViewUrl, webViewBlockedReason } from '../../utils/dhLiveWebView.js'

const url = ref(buildGuideUrl())
const loaded = ref(false)
const canOpenWebView = ref(isSafeDhLiveWebViewUrl(url.value))
const failed = ref(!canOpenWebView.value)
const fallbackTitle = computed(() => (failed.value ? '动态导游暂时无法打开' : '正在进入动态导游'))
const fallbackCopy = computed(() => {
  if (!failed.value) return '马上为您加载语音、表情和口型同步的数字人讲解体验。'
  return webViewBlockedReason(url.value) || '请确认 DH_live 服务已启动，或稍后重新进入。'
})
let loadTimer: ReturnType<typeof setTimeout> | undefined

if (canOpenWebView.value) {
  startLoadTimeout()
}

onShow(() => {
  const pending = uni.getStorageSync('pending_question')
  if (pending && typeof pending === 'string') {
    uni.removeStorageSync('pending_question')
    url.value = buildGuideUrl(pending, true)
    canOpenWebView.value = isSafeDhLiveWebViewUrl(url.value)
    loaded.value = false
    failed.value = !canOpenWebView.value
    if (canOpenWebView.value) {
      startLoadTimeout()
    } else {
      showBlockedReason()
    }
  }
})

onUnmounted(clearLoadTimeout)

function buildGuideUrl(question = '', auto = false) {
  const separator = dhLiveGuideUrl.includes('?') ? '&' : '?'
  const params = [`source=mini-guide`, `v=${Date.now()}`, `api=${encodeURIComponent(API_BASE_URL)}`]
  if (question) params.push(`question=${encodeURIComponent(question)}`)
  if (auto) params.push('auto=1')
  return `${dhLiveGuideUrl}${separator}${params.join('&')}`
}

function handleLoad() {
  clearLoadTimeout()
  loaded.value = true
  failed.value = false
}

function handleMessage(event: unknown) {
  console.log('DH_live guide message:', event)
}

function handleError() {
  clearLoadTimeout()
  loaded.value = false
  failed.value = true
  uni.showToast({
    title: '动态导游加载失败',
    icon: 'none',
  })
}

function reloadGuide() {
  url.value = buildGuideUrl()
  canOpenWebView.value = isSafeDhLiveWebViewUrl(url.value)
  loaded.value = false
  failed.value = !canOpenWebView.value
  if (canOpenWebView.value) {
    startLoadTimeout()
  } else {
    showBlockedReason()
  }
}

function startLoadTimeout() {
  clearLoadTimeout()
  loadTimer = setTimeout(handleTimeout, 8000)
}

function clearLoadTimeout() {
  if (loadTimer === undefined) return
  clearTimeout(loadTimer)
  loadTimer = undefined
}

function handleTimeout() {
  loadTimer = undefined
  if (loaded.value) return
  failed.value = true
  uni.showToast({
    title: '动态导游连接超时',
    icon: 'none',
  })
}

function showBlockedReason() {
  uni.showToast({
    title: webViewBlockedReason(url.value),
    icon: 'none',
  })
}
</script>

<style scoped>
.guide-live-shell {
  width: 100vw;
  height: 100vh;
  position: relative;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.86), rgba(237, 249, 246, 0.9)),
    linear-gradient(135deg, #f8fefd 0%, #e5f6f3 100%);
}

.live-webview {
  width: 100%;
  height: 100%;
}

.live-fallback {
  position: absolute;
  inset: 0;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 42rpx;
  background:
    linear-gradient(180deg, rgba(247, 253, 251, 0.92), rgba(229, 246, 243, 0.96)),
    linear-gradient(135deg, rgba(42, 174, 192, 0.14), rgba(255, 255, 255, 0));
}

.fallback-card {
  width: 100%;
  padding: 42rpx 36rpx;
  border-radius: 22rpx;
  background: rgba(255, 255, 255, 0.96);
  border: 1rpx solid rgba(35, 143, 163, 0.12);
  box-shadow: 0 18rpx 42rpx rgba(35, 143, 163, 0.12);
}

.fallback-kicker,
.fallback-title,
.fallback-copy {
  display: block;
}

.fallback-kicker {
  color: #238fa3;
  font-size: 24rpx;
  font-weight: 800;
}

.fallback-title {
  margin-top: 14rpx;
  color: #17252b;
  font-size: 38rpx;
  font-weight: 900;
  line-height: 1.25;
}

.fallback-copy {
  margin-top: 18rpx;
  color: #64747d;
  font-size: 27rpx;
  line-height: 1.65;
}

.retry-btn {
  height: 76rpx;
  margin-top: 28rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #238fa3;
}

.retry-btn text {
  color: #ffffff;
  font-size: 27rpx;
  font-weight: 800;
}
</style>
