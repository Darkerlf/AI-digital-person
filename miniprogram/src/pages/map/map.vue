<template>
  <view class="page">
    <map
      class="map"
      :latitude="centerLat"
      :longitude="centerLng"
      :markers="markers"
      :include-points="includePoints"
      :scale="15"
      show-location
      @markertap="onMarkerTap"
    />
    <view class="locate-btn" @tap="locateCurrentUser">
      <text>定位我</text>
    </view>

    <view class="map-sheet">
      <view class="spot-panel">
        <view class="panel-head">
          <text class="panel-title">景点列表</text>
          <text class="panel-subtitle">点击后地图自动定位</text>
        </view>
        <scroll-view scroll-x class="spot-scroll">
          <view
            v-for="spot in spots"
            :key="spot.id"
            :class="['spot-chip', { active: selectedSpot === spot.id, uncalibrated: isUncalibratedSpot(spot) }]"
            @tap="selectSpot(spot)"
          >
            <text>{{ spot.name }}</text>
          </view>
        </scroll-view>

        <view v-if="selectedServiceInfo" class="spot-detail service-detail">
          <text class="detail-kicker">已定位服务点</text>
          <text class="detail-name">{{ selectedServiceInfo.name }}</text>
          <text class="detail-desc">{{ serviceDescriptionText }}</text>
          <text class="coord-note">
            坐标：{{ selectedServiceInfo.latitude }}，{{ selectedServiceInfo.longitude }}
          </text>
        </view>

        <view v-else-if="selectedSpotInfo" class="spot-detail">
          <text class="detail-name">{{ selectedSpotInfo.name }}</text>
          <scroll-view scroll-y class="detail-desc-scroll">
            <text class="detail-desc">{{ descriptionText }}</text>
          </scroll-view>
          <text v-if="isUncalibratedSpot(selectedSpotInfo)" class="coord-note">
            该点位当前使用预设坐标，后台录入精确坐标后会自动替换。
          </text>
          <view class="detail-actions">
            <view class="action-btn" @tap="askAboutSpot(selectedSpotInfo.name)">
              <text>询问 AI 导游</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getMapGuideData } from '../../api/tourist'
import type { MapGuideSpot, ServicePOI } from '../../types/api'

const DEFAULT_CENTER = { lat: 31.428076, lng: 120.098006 }
const SCENIC_CENTER = DEFAULT_CENTER
const MAX_LOCATION_DISTANCE_KM = 8
const centerLat = ref(DEFAULT_CENTER.lat)
const centerLng = ref(DEFAULT_CENTER.lng)
const spots = ref<MapGuideSpot[]>([])
const selectedSpot = ref<number | null>(null)
const targetPoi = ref<ServicePOI | null>(null)
const SERVICE_POI_MARKER_ID = 900000
const SERVICE_CATEGORY_LABELS: Record<string, string> = {
  toilet: '公共厕所',
  restaurant: '餐饮',
  parking: '停车场',
  service_center: '游客服务中心',
}

function getSpotCoords(spot: MapGuideSpot): { lat: number; lng: number } | null {
  if (typeof spot.latitude === 'number' && typeof spot.longitude === 'number') {
    return { lat: spot.latitude, lng: spot.longitude }
  }
  return null
}

function hasSpotCoords(spot: MapGuideSpot): boolean {
  return getSpotCoords(spot) !== null
}

function isUncalibratedSpot(spot: MapGuideSpot): boolean {
  return !(spot.coordinate_verified || spot.coordinate_source === 'database')
}

const markers = computed(() => {
  const scenicMarkers = spots.value.flatMap((spot) => {
    const coords = getSpotCoords(spot)
    if (!coords) return []
    const active = selectedSpot.value === spot.id
    const label = isUncalibratedSpot(spot) ? `${spot.name}（待校准）` : spot.name
    return {
      id: spot.id,
      latitude: coords.lat,
      longitude: coords.lng,
      title: spot.name,
      width: active ? 42 : 30,
      height: active ? 42 : 30,
      zIndex: active ? 99 : 1,
      callout: {
        content: markerCalloutText(label, active),
        display: 'ALWAYS',
        padding: 8,
        borderRadius: 6,
        fontSize: 12,
        bgColor: active ? '#238fa3' : '#ffffff',
        color: active ? '#ffffff' : '#17252b',
      },
    }
  })
  const serviceMarker = targetPoiMarker.value
  return serviceMarker ? [...scenicMarkers, serviceMarker] : scenicMarkers
})

const targetPoiCoords = computed(() => {
  const poi = targetPoi.value
  if (!poi || typeof poi.latitude !== 'number' || typeof poi.longitude !== 'number') return null
  return { lat: poi.latitude, lng: poi.longitude }
})

const targetPoiMarker = computed(() => {
  const poi = targetPoi.value
  const coords = targetPoiCoords.value
  if (!poi || !coords) return null
  return {
    id: SERVICE_POI_MARKER_ID + Number(poi.id || 0),
    latitude: coords.lat,
    longitude: coords.lng,
    title: poi.name,
    width: 44,
    height: 44,
    zIndex: 120,
    callout: {
      content: `服务点：${poi.name}`,
      display: 'ALWAYS',
      padding: 8,
      borderRadius: 6,
      fontSize: 12,
      bgColor: '#b4533c',
      color: '#ffffff',
    },
  }
})

const includePoints = computed(() => {
  const points: Array<{ latitude: number; longitude: number }> = []
  if (targetPoiCoords.value) {
    points.push({ latitude: targetPoiCoords.value.lat, longitude: targetPoiCoords.value.lng })
  }
  const selected = selectedSpotInfo.value
  const coords = selected ? getSpotCoords(selected) : null
  if (coords) {
    points.push({ latitude: coords.lat, longitude: coords.lng })
  }
  return uniqueMapPoints(points)
})

const selectedSpotInfo = computed(() => {
  if (!selectedSpot.value) return null
  return spots.value.find((s) => s.id === selectedSpot.value) || null
})

const selectedServiceInfo = computed(() => targetPoi.value)
const serviceDescriptionText = computed(() => {
  const poi = targetPoi.value
  if (!poi) return ''
  const category = serviceCategoryLabel(poi.category)
  const area = poi.area_text || '景区内'
  return poi.description || `${category} · ${area}`
})
const descriptionText = computed(() => selectedSpotInfo.value?.detail_intro || '暂无详细介绍')

function consumeTargetPoiFromStorage() {
  const storedTargetPoi = uni.getStorageSync('target_poi') as ServicePOI | ''
  if (!storedTargetPoi || typeof storedTargetPoi !== 'object') {
    return false
  }
  uni.removeStorageSync('target_poi')
  if (typeof storedTargetPoi.latitude !== 'number' || typeof storedTargetPoi.longitude !== 'number') {
    uni.showToast({ title: '该服务点暂无精确点位', icon: 'none' })
    return false
  }
  targetPoi.value = storedTargetPoi
  selectedSpot.value = null
  centerLat.value = storedTargetPoi.latitude
  centerLng.value = storedTargetPoi.longitude
  return true
}

onMounted(async () => {
  consumeTargetPoiFromStorage()
  try {
    const res = await getMapGuideData(1, true)
    spots.value = res.spots || []
    if (!targetPoi.value && res.center) {
      centerLat.value = res.center.latitude
      centerLng.value = res.center.longitude
    }
    const firstSpotWithCoords = spots.value.find(hasSpotCoords)
    if (!targetPoi.value && firstSpotWithCoords) {
      selectedSpot.value = firstSpotWithCoords.id
    }
  } catch {
    spots.value = [
      { id: 1, name: '灵山大佛', latitude: 31.430266, longitude: 120.096427, sort_order: 1, narration_url: '/api/tourist/scenic-spots/1/narration', detail_intro: '世界著名露天青铜佛像，是灵山胜境的核心景观。' },
      { id: 2, name: '灵山梵宫', latitude: 31.428867, longitude: 120.102472, sort_order: 2, narration_url: '/api/tourist/scenic-spots/2/narration', detail_intro: '金碧辉煌的佛教艺术殿堂，适合深度讲解。' },
      { id: 3, name: '五印坛城', latitude: 31.424856, longitude: 120.103041, sort_order: 3, narration_url: '/api/tourist/scenic-spots/3/narration', detail_intro: '藏式风格建筑群，适合了解藏传佛教文化。' },
    ]
  }
})

onShow(() => {
  consumeTargetPoiFromStorage()
})

function onMarkerTap(e: { detail: { markerId: number } }) {
  if (e.detail.markerId >= SERVICE_POI_MARKER_ID) {
    selectedSpot.value = null
    return
  }
  selectedSpot.value = e.detail.markerId
  targetPoi.value = null
}

function selectSpot(spot: MapGuideSpot) {
  targetPoi.value = null
  selectedSpot.value = spot.id
  const coords = getSpotCoords(spot)
  if (coords) {
    centerLat.value = coords.lat
    centerLng.value = coords.lng
    return
  }
  uni.showToast({ title: '该景点暂无精确点位', icon: 'none' })
}

function serviceCategoryLabel(value: string) {
  return SERVICE_CATEGORY_LABELS[value] || value
}

function markerCalloutText(label: string, active: boolean) {
  if (active) return `当前：${label}`
  return label
}

function uniqueMapPoints(points: Array<{ latitude: number; longitude: number }>) {
  const seen = new Set<string>()
  return points.filter((point) => {
    const key = `${point.latitude},${point.longitude}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}

function locateCurrentUser(showToast = true) {
  uni.getLocation({
    type: 'gcj02',
    isHighAccuracy: true,
    success: (res) => {
      const distance = distanceKm(res.latitude, res.longitude, SCENIC_CENTER.lat, SCENIC_CENTER.lng)
      if (distance > MAX_LOCATION_DISTANCE_KM) {
        centerLat.value = SCENIC_CENTER.lat
        centerLng.value = SCENIC_CENTER.lng
        if (showToast) {
          uni.showModal({
            title: '当前位置不在景区附近',
            content: `当前定位距离灵山胜境约 ${Math.round(distance)} 公里，已保持景区导览视角。请在开发者工具中把模拟定位设置到无锡灵山胜境附近，或使用真机测试。`,
            showCancel: false,
          })
        }
        return
      }
      centerLat.value = res.latitude
      centerLng.value = res.longitude
      if (showToast) {
        uni.showToast({ title: '已定位到当前位置', icon: 'none' })
      }
    },
    fail: () => {
      if (showToast) {
        uni.showToast({ title: '定位失败，可继续使用列表导览', icon: 'none' })
      }
    },
  })
}

function distanceKm(lat1: number, lng1: number, lat2: number, lng2: number) {
  const earthRadiusKm = 6371
  const dLat = toRadians(lat2 - lat1)
  const dLng = toRadians(lng2 - lng1)
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) *
      Math.sin(dLng / 2) * Math.sin(dLng / 2)
  return earthRadiusKm * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

function toRadians(value: number) {
  return (value * Math.PI) / 180
}

function askAboutSpot(name: string) {
  uni.setStorageSync('pending_question', `请讲解${name}`)
  uni.switchTab({ url: '/pages/guide/guide' })
}
</script>

<style scoped>
.page {
  height: 100vh;
  position: relative;
  overflow: hidden;
  background: #e5f6f3;
}

.map {
  width: 100%;
  height: 100%;
}

.locate-btn {
  position: absolute;
  right: 24rpx;
  top: 24rpx;
  height: 58rpx;
  padding: 0 22rpx;
  border-radius: 999rpx;
  background: #ffffff;
  border: 1rpx solid rgba(35, 143, 163, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
}

.locate-btn text {
  color: #238fa3;
  font-size: 24rpx;
  font-weight: 800;
}

.map-sheet {
  position: absolute;
  left: 16rpx;
  right: 16rpx;
  bottom: calc(18rpx + env(safe-area-inset-bottom));
  max-height: 52vh;
  padding: 18rpx;
  border-radius: 22rpx;
  background: rgba(255, 255, 255, 0.96);
  border: 1rpx solid rgba(35, 143, 163, 0.1);
}

.route-panel {
  padding-bottom: 18rpx;
  margin-bottom: 16rpx;
  border-bottom: 1rpx solid #d7edf0;
}

.panel-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18rpx;
  margin-bottom: 14rpx;
}

.route-title,
.panel-title {
  font-size: 29rpx;
  font-weight: 800;
  color: #17252b;
}

.route-subtitle,
.panel-subtitle {
  font-size: 21rpx;
  color: #7a8a91;
  flex-shrink: 0;
}

.route-scroll,
.spot-scroll {
  white-space: nowrap;
}

.next-stop-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  margin-bottom: 14rpx;
  padding: 14rpx;
  border-radius: 16rpx;
  background: #f7fdfb;
  border: 1rpx solid #d7edf0;
}

.next-stop-main {
  min-width: 0;
  flex: 1;
}

.next-stop-name {
  display: block;
  color: #17252b;
  font-size: 28rpx;
  font-weight: 800;
}

.next-stop-note {
  display: block;
  margin-top: 5rpx;
  color: #64747d;
  font-size: 21rpx;
  line-height: 1.45;
}

.route-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8rpx;
  max-width: 260rpx;
}

.route-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 72rpx;
  height: 48rpx;
  padding: 0 12rpx;
  border-radius: 999rpx;
  background: #e9fbf7;
}

.route-action.primary {
  background: #238fa3;
}

.route-action text {
  color: #238fa3;
  font-size: 21rpx;
  font-weight: 800;
}

.route-action.primary text {
  color: #ffffff;
}

.route-step {
  display: inline-flex;
  align-items: center;
  gap: 9rpx;
  margin-right: 14rpx;
  padding: 9rpx 16rpx 9rpx 10rpx;
  border-radius: 999rpx;
  background: #e9fbf7;
}

.route-step.arrived {
  background: #edf3f4;
}

.route-step.skipped,
.route-step.unlocated {
  opacity: 0.68;
}

.route-step.next {
  background: #238fa3;
}

.route-index {
  width: 32rpx;
  height: 32rpx;
  border-radius: 50%;
  background: #238fa3;
  color: #ffffff;
  text-align: center;
  line-height: 32rpx;
  font-size: 20rpx;
  font-weight: 800;
}

.route-name {
  font-size: 23rpx;
  color: #238fa3;
  font-weight: 700;
}

.route-step.next .route-index {
  background: #ffffff;
  color: #238fa3;
}

.route-step.next .route-name {
  color: #ffffff;
}

.spot-chip {
  display: inline-flex;
  align-items: center;
  height: 58rpx;
  margin-right: 12rpx;
  padding: 0 22rpx;
  border-radius: 999rpx;
  background: #e9fbf7;
  border: 1rpx solid transparent;
}

.spot-chip.active {
  background: #238fa3;
}

.spot-chip.uncalibrated {
  opacity: 0.68;
}

.spot-chip text {
  font-size: 24rpx;
  color: #64747d;
  font-weight: 700;
}

.spot-chip.active text {
  color: #ffffff;
}

.spot-detail {
  margin-top: 18rpx;
  padding-top: 16rpx;
  border-top: 1rpx solid #edf3f4;
}

.detail-kicker {
  display: block;
  margin-bottom: 6rpx;
  color: #b4533c;
  font-size: 22rpx;
  font-weight: 800;
}

.detail-name {
  display: block;
  font-size: 31rpx;
  font-weight: 800;
  color: #17252b;
}

.detail-desc {
  display: block;
  font-size: 25rpx;
  color: #4f626a;
  line-height: 1.65;
}

.detail-desc-scroll {
  display: block;
  height: 176rpx;
  margin-top: 9rpx;
  padding-right: 8rpx;
  box-sizing: border-box;
}

.service-detail .detail-desc {
  margin-top: 9rpx;
}

.coord-note {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: #a05a1c;
  line-height: 1.5;
}

.detail-actions {
  margin-top: 16rpx;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 58rpx;
  padding: 0 24rpx;
  border-radius: 999rpx;
  background: #fff1ea;
}

.action-btn text {
  font-size: 24rpx;
  color: #b4533c;
  font-weight: 800;
}
</style>
