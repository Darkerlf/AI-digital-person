<template>
  <view class="page">
    <map
      class="map"
      :latitude="centerLat"
      :longitude="centerLng"
      :markers="markers"
      :scale="15"
      show-location
      @markertap="onMarkerTap"
    />

    <view class="spot-panel">
      <text class="panel-title">景点列表</text>
      <scroll-view scroll-x class="spot-scroll">
        <view
          v-for="spot in spots"
          :key="spot.id"
          :class="['spot-chip', { active: selectedSpot === spot.id }]"
          @tap="selectSpot(spot)"
        >
          <text>{{ spot.name }}</text>
        </view>
      </scroll-view>

      <view v-if="selectedSpotInfo" class="spot-detail">
        <text class="detail-name">{{ selectedSpotInfo.name }}</text>
        <text class="detail-desc">{{ selectedSpotInfo.detail_intro || '暂无详细介绍' }}</text>
        <view class="detail-actions">
          <view class="action-btn" @tap="askAboutSpot(selectedSpotInfo.name)">
            <text>问问AI导游</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getScenicSpots } from '../../api/tourist'
import type { ScenicSpot } from '../../types/api'

const centerLat = ref(31.4256)
const centerLng = ref(120.0946)
const spots = ref<ScenicSpot[]>([])
const selectedSpot = ref<number | null>(null)

const spotCoordinates: Record<string, { lat: number; lng: number }> = {
  '灵山大佛': { lat: 31.4276, lng: 120.0936 },
  '灵山梵宫': { lat: 31.4246, lng: 120.0956 },
  '五印坛城': { lat: 31.4236, lng: 120.0966 },
  '九龙灌浴': { lat: 31.4266, lng: 120.0946 },
  '祥符禅寺': { lat: 31.4286, lng: 120.0926 },
}

const markers = computed(() => {
  return spots.value.map((spot, index) => {
    const coords = spotCoordinates[spot.name] || {
      lat: centerLat.value + (index - 2) * 0.001,
      lng: centerLng.value + (index - 2) * 0.001,
    }
    return {
      id: spot.id,
      latitude: coords.lat,
      longitude: coords.lng,
      title: spot.name,
      width: 30,
      height: 30,
      callout: {
        content: spot.name,
        display: 'ALWAYS',
        padding: 8,
        borderRadius: 4,
        fontSize: 12,
      },
    }
  })
})

const selectedSpotInfo = computed(() => {
  if (!selectedSpot.value) return null
  return spots.value.find((s) => s.id === selectedSpot.value) || null
})

onMounted(async () => {
  try {
    const res = await getScenicSpots()
    spots.value = res.items || []
  } catch {
    spots.value = [
      { id: 1, spot_code: 'LSDF', name: '灵山大佛', detail_intro: '世界上最高的青铜佛像', open_status: 'open' },
      { id: 2, spot_code: 'LSFG', name: '灵山梵宫', detail_intro: '金碧辉煌的佛教艺术殿堂', open_status: 'open' },
      { id: 3, spot_code: 'WYTC', name: '五印坛城', detail_intro: '藏式风格建筑群', open_status: 'open' },
    ]
  }
})

function onMarkerTap(e: { detail: { markerId: number } }) {
  selectedSpot.value = e.detail.markerId
}

function selectSpot(spot: ScenicSpot) {
  selectedSpot.value = spot.id
  const coords = spotCoordinates[spot.name]
  if (coords) {
    centerLat.value = coords.lat
    centerLng.value = coords.lng
  }
}

function askAboutSpot(name: string) {
  uni.switchTab({ url: '/pages/guide/guide' })
}
</script>

<style scoped>
.page { height: 100vh; display: flex; flex-direction: column; }
.map { flex: 1; width: 100%; }
.spot-panel { background: #ffffff; padding: 20rpx; border-top-left-radius: 24rpx; border-top-right-radius: 24rpx; box-shadow: 0 -4rpx 16rpx rgba(0,0,0,0.08); }
.panel-title { font-size: 28rpx; font-weight: bold; color: #333; display: block; margin-bottom: 16rpx; }
.spot-scroll { white-space: nowrap; }
.spot-chip { display: inline-block; background: #f0f2f5; border-radius: 32rpx; padding: 12rpx 24rpx; margin-right: 16rpx; }
.spot-chip.active { background: #1a73e8; }
.spot-chip text { font-size: 24rpx; color: #666; }
.spot-chip.active text { color: #ffffff; }
.spot-detail { margin-top: 20rpx; padding-top: 20rpx; border-top: 1rpx solid #e5e5e5; }
.detail-name { font-size: 30rpx; font-weight: bold; color: #333; display: block; }
.detail-desc { font-size: 24rpx; color: #666; margin-top: 8rpx; line-height: 1.6; display: block; }
.detail-actions { margin-top: 16rpx; }
.action-btn { display: inline-block; background: #e8f0fe; border-radius: 32rpx; padding: 12rpx 24rpx; }
.action-btn text { font-size: 24rpx; color: #1a73e8; }
</style>
