<template>
  <view class="page">
    <view class="banner">
      <view class="banner-overlay">
        <text class="banner-title">灵山胜境</text>
        <text class="banner-subtitle">AI 数字人导游 · 智慧游览</text>
      </view>
    </view>

    <view class="section">
      <text class="section-title">快速入口</text>
      <view class="quick-actions">
        <view class="action-item" @tap="goToGuide">
          <text class="action-icon">💬</text>
          <text class="action-text">AI对话</text>
        </view>
        <view class="action-item" @tap="goToMap">
          <text class="action-icon">🗺️</text>
          <text class="action-text">导览地图</text>
        </view>
        <view class="action-item" @tap="goToRoute">
          <text class="action-icon">📍</text>
          <text class="action-text">推荐路线</text>
        </view>
        <view class="action-item" @tap="goToMy">
          <text class="action-icon">👤</text>
          <text class="action-text">我的</text>
        </view>
      </view>
    </view>

    <view class="section">
      <text class="section-title">热门景点</text>
      <view class="spot-list">
        <view
          v-for="spot in hotSpots"
          :key="spot.id"
          class="spot-card"
          @tap="goToSpot(spot.id)"
        >
          <view class="spot-info">
            <text class="spot-name">{{ spot.name }}</text>
            <text class="spot-desc">{{ spot.detail_intro?.slice(0, 60) || '暂无介绍' }}...</text>
          </view>
        </view>
      </view>
    </view>

    <view class="section">
      <text class="section-title">关于灵山胜境</text>
      <view class="about-card">
        <text class="about-text">
          灵山胜境位于江苏省无锡市滨湖区，是国家5A级旅游景区。景区以灵山大佛为核心，汇集梵宫、五印坛城、九龙灌浴等著名景点，是一处集佛教文化、自然风光于一体的综合性景区。
        </text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getScenicSpots } from '../../api/tourist'
import type { ScenicSpot } from '../../types/api'

const hotSpots = ref<ScenicSpot[]>([])

onMounted(async () => {
  try {
    const res = await getScenicSpots()
    hotSpots.value = (res.items || []).slice(0, 5)
  } catch {
    hotSpots.value = [
      { id: 1, spot_code: 'LSDF', name: '灵山大佛', detail_intro: '世界上最高的青铜佛像，高88米', open_status: 'open' },
      { id: 2, spot_code: 'LSFG', name: '灵山梵宫', detail_intro: '东方卢浮宫，金碧辉煌的佛教艺术殿堂', open_status: 'open' },
      { id: 3, spot_code: 'WYTC', name: '五印坛城', detail_intro: '藏式风格建筑群，感受藏传佛教文化', open_status: 'open' },
    ]
  }
})

function goToGuide() { uni.switchTab({ url: '/pages/guide/guide' }) }
function goToMap() { uni.switchTab({ url: '/pages/map/map' }) }
function goToRoute() { uni.switchTab({ url: '/pages/guide/guide' }) }
function goToMy() { uni.switchTab({ url: '/pages/my/my' }) }
function goToSpot(id: number) { uni.navigateTo({ url: `/pages/guide/guide?spot_id=${id}` }) }
</script>

<style scoped>
.page { min-height: 100vh; background: #f5f5f5; }
.banner { height: 360rpx; background: linear-gradient(135deg, #1a73e8, #0d47a1); display: flex; align-items: flex-end; padding: 40rpx; }
.banner-overlay { display: flex; flex-direction: column; }
.banner-title { font-size: 48rpx; font-weight: bold; color: #ffffff; }
.banner-subtitle { font-size: 28rpx; color: rgba(255,255,255,0.8); margin-top: 12rpx; }
.section { padding: 30rpx; }
.section-title { font-size: 32rpx; font-weight: bold; color: #333; margin-bottom: 20rpx; display: block; }
.quick-actions { display: flex; justify-content: space-around; background: #ffffff; border-radius: 16rpx; padding: 30rpx 0; }
.action-item { display: flex; flex-direction: column; align-items: center; gap: 12rpx; }
.action-icon { font-size: 48rpx; }
.action-text { font-size: 24rpx; color: #666; }
.spot-list { display: flex; flex-direction: column; gap: 16rpx; }
.spot-card { background: #ffffff; border-radius: 12rpx; padding: 24rpx; }
.spot-name { font-size: 30rpx; font-weight: bold; color: #333; display: block; }
.spot-desc { font-size: 24rpx; color: #999; margin-top: 8rpx; display: block; }
.about-card { background: #ffffff; border-radius: 12rpx; padding: 24rpx; }
.about-text { font-size: 26rpx; color: #666; line-height: 1.8; }
</style>
