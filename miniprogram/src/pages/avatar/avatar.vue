<template>
  <view class="avatar-page">
    <web-view v-if="canOpenWebView" :src="url" @message="handleMessage" @error="handleError" />
    <view v-else class="blocked-panel">
      <text class="blocked-title">数字人页面暂时无法打开</text>
      <text class="blocked-copy">{{ blockedReason }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { dhLiveGuideUrl } from '../../config/assets'
import { isSafeDhLiveWebViewUrl, webViewBlockedReason } from '../../utils/dhLiveWebView.js'

const url = computed(() => dhLiveGuideUrl)
const canOpenWebView = computed(() => isSafeDhLiveWebViewUrl(url.value))
const blockedReason = computed(() => webViewBlockedReason(url.value))

function handleMessage(event: unknown) {
  console.log('DH_live web-view message:', event)
}

function handleError() {
  uni.showToast({
    title: '数字人页面加载失败',
    icon: 'none',
  })
}
</script>

<style scoped>
.avatar-page {
  width: 100vw;
  height: 100vh;
  background: #f7fdfb;
}

.blocked-panel {
  min-height: 100vh;
  padding: 72rpx 42rpx;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: #f7fdfb;
}

.blocked-title,
.blocked-copy {
  display: block;
}

.blocked-title {
  color: #17252b;
  font-size: 36rpx;
  font-weight: 900;
}

.blocked-copy {
  margin-top: 18rpx;
  color: #64747d;
  font-size: 27rpx;
  line-height: 1.65;
}
</style>
