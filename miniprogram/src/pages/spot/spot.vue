<template>
  <view class="page">
    <view class="hero">
      <text class="eyebrow">景点讲解</text>
      <text class="title">{{ spot?.name || '景点讲解' }}</text>
      <text class="subtitle">{{ spot?.location_text || '灵山胜境' }}</text>
    </view>

    <view class="tabs">
      <view v-for="item in modes" :key="item.value" :class="['tab', { active: mode === item.value }]" @tap="loadNarration(item.value)">
        <text>{{ item.label }}</text>
      </view>
    </view>

    <view class="content-card">
      <text class="card-title">数字人讲解词</text>
      <text class="body-text">{{ narration?.narration || '正在准备讲解...' }}</text>
    </view>

    <view class="content-card" v-if="spot">
      <text class="card-title">基础信息</text>
      <text class="body-text">{{ spot.detail_intro || spot.highlights || '暂无详细资料' }}</text>
    </view>

    <view class="actions">
      <view class="secondary-btn" @tap="askAboutSpot"><text>继续问这个景点</text></view>
      <view class="primary-btn" @tap="goRoute"><text>加入路线推荐</text></view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'
import { getScenicSpot, getScenicSpotNarration } from '../../api/tourist'
import type { ScenicSpot, ScenicSpotNarration } from '../../types/api'

const modes = [
  { label: '简短版', value: 'brief' as const },
  { label: '深入版', value: 'deep' as const },
  { label: '亲子版', value: 'family' as const },
]

const spotId = ref(1)
const mode = ref<'brief' | 'deep' | 'family'>('brief')
const spot = ref<ScenicSpot | null>(null)
const narration = ref<ScenicSpotNarration | null>(null)

onLoad((query) => {
  const id = Number(query?.id || query?.spot_id || 1)
  spotId.value = Number.isFinite(id) && id > 0 ? id : 1
  loadSpot()
  loadNarration(mode.value)
})

async function loadSpot() {
  try {
    spot.value = await getScenicSpot(spotId.value)
  } catch {
    uni.showToast({ title: '景点加载失败', icon: 'none' })
  }
}

async function loadNarration(nextMode: 'brief' | 'deep' | 'family') {
  mode.value = nextMode
  narration.value = null
  try {
    narration.value = await getScenicSpotNarration(spotId.value, nextMode)
  } catch {
    uni.showToast({ title: '讲解加载失败', icon: 'none' })
  }
}

function askAboutSpot() {
  const name = spot.value?.name || ''
  uni.switchTab({ url: '/pages/guide/guide' })
  if (name) uni.setStorageSync('pending_question', `讲讲${name}`)
}

function goRoute() {
  uni.navigateTo({ url: '/pages/route/route' })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 24rpx;
  background: linear-gradient(180deg, #f7fdfb 0%, #effaf7 40%, #e9fbf7 100%);
}

.hero {
  padding: 34rpx 30rpx;
  border-radius: 18rpx;
  background:
    linear-gradient(135deg, rgba(239, 250, 247, 0.98), rgba(201, 241, 237, 0.96)),
    linear-gradient(160deg, rgba(42, 174, 192, 0.28), rgba(255, 255, 255, 0) 46%);
  box-shadow: 0 14rpx 34rpx rgba(35, 143, 163, 0.11);
}

.eyebrow {
  display: block;
  font-size: 22rpx;
  font-weight: 800;
  color: #b4533c;
}

.title {
  display: block;
  margin-top: 12rpx;
  font-size: 42rpx;
  line-height: 1.18;
  font-weight: 800;
  color: #123f49;
}

.subtitle {
  display: block;
  margin-top: 10rpx;
  font-size: 25rpx;
  color: #4f626a;
}

.tabs {
  display: flex;
  gap: 14rpx;
  margin: 22rpx 0;
}

.tab {
  flex: 1;
  height: 70rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  border: 1rpx solid #d7edf0;
}

.tab text {
  color: #64747d;
  font-size: 25rpx;
  font-weight: 700;
}

.tab.active {
  background: #238fa3;
  border-color: #238fa3;
  box-shadow: 0 8rpx 18rpx rgba(35, 143, 163, 0.15);
}

.tab.active text {
  color: #ffffff;
}

.content-card {
  margin-bottom: 18rpx;
  padding: 26rpx;
  border-radius: 18rpx;
  background: #ffffff;
  border: 1rpx solid rgba(35, 143, 163, 0.08);
  box-shadow: 0 8rpx 24rpx rgba(35, 143, 163, 0.07);
}

.card-title {
  display: block;
  margin-bottom: 12rpx;
  font-size: 29rpx;
  font-weight: 800;
  color: #17252b;
}

.body-text {
  display: block;
  font-size: 26rpx;
  color: #4f626a;
  line-height: 1.78;
}

.actions {
  display: flex;
  gap: 16rpx;
  padding-bottom: calc(18rpx + env(safe-area-inset-bottom));
}

.primary-btn,
.secondary-btn {
  flex: 1;
  min-width: 0;
  height: 84rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
}

.primary-btn {
  background: #238fa3;
}

.secondary-btn {
  background: #fff1ea;
}

.primary-btn text {
  color: #ffffff;
  font-size: 26rpx;
}

.secondary-btn text {
  color: #b4533c;
  font-size: 26rpx;
}
</style>
