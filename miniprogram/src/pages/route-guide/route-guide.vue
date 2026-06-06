<template>
  <view class="page">
    <map
      class="map"
      :latitude="centerLat"
      :longitude="centerLng"
      :markers="markers"
      :polyline="routePolyline"
      :include-points="includePoints"
      :scale="16"
      show-location
      @markertap="onMarkerTap"
    />

    <view class="top-actions">
      <view class="pill-btn" @tap="locateCurrentUser">
        <text>定位我</text>
      </view>
      <view class="pill-btn warning" v-if="walkGuide?.fallback_used">
        <text>含兜底路线</text>
      </view>
    </view>

    <view class="guide-sheet">
      <view class="guide-head">
        <view>
          <text class="guide-title">{{ routeTitle }}</text>
          <text class="guide-subtitle">{{ progressLabel }} · {{ distanceLabel }} · {{ durationLabel }}</text>
        </view>
        <text class="guide-badge">{{ offRouteCount >= 2 ? '已偏航' : '导览中' }}</text>
      </view>

      <view v-if="loading" class="loading-card">
        <text>正在生成可走路线...</text>
      </view>

      <view v-else-if="nextStop" class="next-card">
        <view class="next-main">
          <text class="kicker">下一站</text>
          <text class="next-name">{{ nextStop.name }}</text>
          <text class="next-note">{{ nextLegLabel }}</text>
        </view>
        <view class="next-actions">
          <view class="action primary" @tap="arriveAtNextStop"><text>已到达</text></view>
          <view class="action" @tap="skipNextStop"><text>跳过</text></view>
        </view>
      </view>

      <view v-else class="next-card">
        <view class="next-main">
          <text class="kicker">路线完成</text>
          <text class="next-name">已完成本次步行导览</text>
          <text class="next-note">可以返回路线页重新生成，或继续浏览景点。</text>
        </view>
      </view>

      <view class="tool-row">
        <view class="tool-btn" @tap="rerouteFromCurrentLocation"><text>从当前位置重算</text></view>
        <view class="tool-btn" @tap="backToRoute"><text>调整路线</text></view>
      </view>

      <scroll-view v-if="servicePois.length" scroll-x class="service-scroll">
        <view
          v-for="poi in servicePois"
          :key="poi.name"
          class="service-chip"
          @tap="focusServicePoi(poi)"
        >
          <text>{{ serviceLabel(poi.category) }} · {{ poi.name }}</text>
        </view>
      </scroll-view>

      <view v-if="warnings.length" class="warning-list">
        <text v-for="item in warnings" :key="item">{{ item }}</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { onLoad, onUnload } from '@dcloudio/uni-app'
import { buildWalkGuide } from '../../api/tourist'
import type { MapPoint, RouteRecommendRequest, RouteRecommendResponse, ServicePOI, WalkGuideResponse } from '../../types/api'
import {
  DEFAULT_SCENIC_CENTER,
  isNearScenicArea,
  isOffRoute,
  isValidMapPoint,
  nextPendingStop,
  routeProgressText,
} from '../../utils/routeGuide'

const DEFAULT_CENTER = DEFAULT_SCENIC_CENTER
const SERVICE_MARKER_ID = 800000
const CURRENT_MARKER_ID = 999999
const OFF_ROUTE_THRESHOLD_METERS = 80

const activeRoute = ref<RouteRecommendResponse | null>(null)
const lastRouteRequest = ref<RouteRecommendRequest | null>(null)
const walkGuide = ref<WalkGuideResponse | null>(null)
const currentLocation = ref<MapPoint | null>(null)
const selectedServicePoi = ref<ServicePOI | null>(null)
const progressIndex = ref(0)
const skippedIndexes = ref<number[]>([])
const offRouteCount = ref(0)
const loading = ref(false)
let locationTimer: ReturnType<typeof setInterval> | null = null

const routeTitle = computed(() => activeRoute.value?.matched_template?.name || activeRoute.value?.template_name || '步行导览')
const stops = computed(() => walkGuide.value?.stops || [])
const legs = computed(() => walkGuide.value?.legs || [])
const servicePois = computed(() => (walkGuide.value?.service_pois || []).filter(poiHasValidPoint))
const warnings = computed(() => walkGuide.value?.warnings || [])
const safePolylinePoints = computed(() => (walkGuide.value?.polyline || []).filter(isValidMapPoint))
const safeCurrentLocation = computed(() => (isValidMapPoint(currentLocation.value) ? currentLocation.value : null))
const safeSelectedServicePoi = computed(() => (
  selectedServicePoi.value && poiHasValidPoint(selectedServicePoi.value) ? selectedServicePoi.value : null
))
const nextStop = computed(() => nextPendingStop(stops.value, progressIndex.value))
const progressLabel = computed(() => routeProgressText(stops.value, progressIndex.value))
const distanceLabel = computed(() => formatDistance(walkGuide.value?.total_distance_meters || 0))
const durationLabel = computed(() => formatDuration(walkGuide.value?.total_duration_minutes || 0))
const nextLegLabel = computed(() => {
  const legIndex = Math.max(0, Math.min(progressIndex.value, legs.value.length - 1))
  const leg = legs.value[legIndex]
  if (!leg) return '按地图路线继续前往'
  return `${formatDistance(leg.distance_meters)} · 约${formatDuration(leg.duration_minutes)}`
})

const routePolyline = computed(() => {
  const points = safePolylinePoints.value
  if (points.length < 2) return []
  return [{ points, color: '#238fa3', width: 6, dottedLine: false, arrowLine: true }]
})

const centerLat = computed(() => safeSelectedServicePoi.value?.latitude || safeCurrentLocation.value?.latitude || safePolylinePoints.value[0]?.latitude || DEFAULT_CENTER.latitude)
const centerLng = computed(() => safeSelectedServicePoi.value?.longitude || safeCurrentLocation.value?.longitude || safePolylinePoints.value[0]?.longitude || DEFAULT_CENTER.longitude)
const includePoints = computed(() => {
  const points = [...safePolylinePoints.value]
  if (safeCurrentLocation.value) points.push(safeCurrentLocation.value)
  return points
})

const markers = computed(() => {
  const stopMarkers = stops.value.filter(isValidMapPoint).map((stop, index) => ({
    id: index + 1,
    latitude: stop.latitude,
    longitude: stop.longitude,
    title: stop.name,
    width: index === progressIndex.value ? 42 : 30,
    height: index === progressIndex.value ? 42 : 30,
    zIndex: index === progressIndex.value ? 90 : 20,
    callout: {
      content: index === progressIndex.value ? `下一站：${stop.name}` : stop.name,
      display: 'ALWAYS',
      padding: 8,
      borderRadius: 6,
      fontSize: 12,
      bgColor: index === progressIndex.value ? '#238fa3' : '#ffffff',
      color: index === progressIndex.value ? '#ffffff' : '#17252b',
    },
  }))
  const poiMarkers = servicePois.value.flatMap((poi, index) => (
    typeof poi.latitude === 'number' && typeof poi.longitude === 'number'
      ? [{
          id: SERVICE_MARKER_ID + index,
          latitude: poi.latitude,
          longitude: poi.longitude,
          title: poi.name,
          width: selectedServicePoi.value?.name === poi.name ? 40 : 28,
          height: selectedServicePoi.value?.name === poi.name ? 40 : 28,
          zIndex: 70,
          callout: {
            content: `${serviceLabel(poi.category)}：${poi.name}`,
            display: selectedServicePoi.value?.name === poi.name ? 'ALWAYS' : 'BYCLICK',
            padding: 8,
            borderRadius: 6,
            fontSize: 12,
            bgColor: '#fff1ea',
            color: '#b4533c',
          },
        }]
      : []
  ))
  const currentMarker = safeCurrentLocation.value
    ? [{
        id: CURRENT_MARKER_ID,
        latitude: safeCurrentLocation.value.latitude,
        longitude: safeCurrentLocation.value.longitude,
        title: '当前位置',
        width: 34,
        height: 34,
        zIndex: 100,
      }]
    : []
  return [...stopMarkers, ...poiMarkers, ...currentMarker]
})

onLoad(() => {
  loadStoredRoute()
})

onMounted(() => {
  buildGuide()
  locateCurrentUser(false)
  locationTimer = setInterval(() => locateCurrentUser(false), 10000)
})

onUnload(() => {
  if (locationTimer) {
    clearInterval(locationTimer)
    locationTimer = null
  }
})

function loadStoredRoute() {
  const storedRoute = uni.getStorageSync('active_route') as RouteRecommendResponse | ''
  const storedRequest = uni.getStorageSync('last_route_request') as RouteRecommendRequest | ''
  activeRoute.value = storedRoute && typeof storedRoute === 'object' ? storedRoute : null
  lastRouteRequest.value = storedRequest && typeof storedRequest === 'object' ? storedRequest : null
}

async function buildGuide(startLocation?: MapPoint | null) {
  if (!activeRoute.value?.spots?.length) {
    uni.showToast({ title: '暂无可导览路线', icon: 'none' })
    return
  }
  const guideStartLocation = isValidMapPoint(startLocation) && isNearScenicArea(startLocation)
    ? startLocation
    : null
  loading.value = true
  try {
    walkGuide.value = await buildWalkGuide({
      scenic_area_id: lastRouteRequest.value?.scenic_area_id || 1,
      spots: remainingRouteSpots(guideStartLocation),
      start_location: guideStartLocation || undefined,
      service_needs: lastRouteRequest.value?.service_needs || [],
    })
    progressIndex.value = 0
    skippedIndexes.value = []
    offRouteCount.value = 0
  } catch {
    uni.showToast({ title: '暂时无法生成步行导览', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function remainingRouteSpots(startLocation?: MapPoint | null) {
  const spots = activeRoute.value?.spots || []
  if (!startLocation) return spots
  return spots.slice(Math.min(progressIndex.value, spots.length - 1))
}

function locateCurrentUser(showToast = true) {
  uni.getLocation({
    type: 'gcj02',
    isHighAccuracy: true,
    success: (res) => {
      const point = { latitude: Number(res.latitude), longitude: Number(res.longitude) }
      if (!isValidMapPoint(point)) {
        currentLocation.value = null
        offRouteCount.value = 0
        if (showToast) uni.showToast({ title: '定位坐标异常，已使用路线范围显示', icon: 'none' })
        return
      }
      if (!isNearScenicArea(point)) {
        currentLocation.value = null
        offRouteCount.value = 0
        if (showToast) uni.showToast({ title: '当前位置不在景区附近，已使用路线范围显示', icon: 'none' })
        return
      }
      currentLocation.value = point
      checkOffRoute(point)
      if (showToast) uni.showToast({ title: '已定位到当前位置', icon: 'none' })
    },
    fail: () => {
      if (showToast) uni.showToast({ title: '定位失败，可继续按路线导览', icon: 'none' })
    },
  })
}

function checkOffRoute(point: MapPoint) {
  const polyline = safePolylinePoints.value
  if (!isOffRoute(point, polyline, OFF_ROUTE_THRESHOLD_METERS)) {
    offRouteCount.value = 0
    return
  }
  offRouteCount.value += 1
  if (offRouteCount.value === 2) {
    uni.showModal({
      title: '可能已偏离路线',
      content: '当前位置已连续偏离推荐步行线，是否从当前位置重新规划？',
      confirmText: '重算',
      success: (res) => {
        if (res.confirm) rerouteFromCurrentLocation()
      },
    })
  }
}

function arriveAtNextStop() {
  if (!nextStop.value) {
    uni.showToast({ title: '路线已完成', icon: 'none' })
    return
  }
  progressIndex.value = Math.min(progressIndex.value + 1, stops.value.length)
}

function skipNextStop() {
  if (!nextStop.value) {
    uni.showToast({ title: '路线已完成', icon: 'none' })
    return
  }
  skippedIndexes.value = [...skippedIndexes.value, progressIndex.value]
  progressIndex.value = Math.min(progressIndex.value + 1, stops.value.length)
}

function rerouteFromCurrentLocation() {
  const point = safeCurrentLocation.value
  if (!point || !isNearScenicArea(point)) {
    locateCurrentUser()
    return
  }
  buildGuide(point)
}

function focusServicePoi(poi: ServicePOI) {
  if (!poiHasValidPoint(poi)) return
  selectedServicePoi.value = poi
  uni.showToast({ title: poi.name, icon: 'none' })
}

function onMarkerTap(e: { detail: { markerId: number } }) {
  if (e.detail.markerId >= SERVICE_MARKER_ID && e.detail.markerId < CURRENT_MARKER_ID) {
    const poi = servicePois.value[e.detail.markerId - SERVICE_MARKER_ID]
    if (poi) selectedServicePoi.value = poi
  }
}

function backToRoute() {
  uni.navigateTo({ url: '/pages/route/route' })
}

function formatDistance(value: number) {
  if (value >= 1000) return `${(value / 1000).toFixed(1)}公里`
  return `${Math.round(value)}米`
}

function formatDuration(value: number) {
  if (value >= 60) return `${Math.floor(value / 60)}小时${value % 60}分钟`
  return `${Math.max(1, Math.round(value))}分钟`
}

function serviceLabel(category: string) {
  const labels: Record<string, string> = {
    toilet: '厕所',
    restaurant: '餐饮',
    service_center: '服务',
    parking: '停车',
  }
  return labels[category] || category
}
function poiHasValidPoint(poi: ServicePOI): boolean {
  return typeof poi.latitude === 'number' &&
    typeof poi.longitude === 'number' &&
    isValidMapPoint({ latitude: poi.latitude, longitude: poi.longitude })
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

.top-actions {
  position: absolute;
  top: 24rpx;
  right: 24rpx;
  display: flex;
  gap: 12rpx;
}

.pill-btn {
  height: 58rpx;
  padding: 0 22rpx;
  border-radius: 999rpx;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1rpx solid rgba(35, 143, 163, 0.12);
}

.pill-btn.warning {
  background: #fff1ea;
}

.pill-btn text {
  color: #238fa3;
  font-size: 24rpx;
  font-weight: 800;
}

.pill-btn.warning text {
  color: #b4533c;
}

.guide-sheet {
  position: absolute;
  left: 16rpx;
  right: 16rpx;
  bottom: calc(18rpx + env(safe-area-inset-bottom));
  padding: 20rpx;
  border-radius: 22rpx;
  background: rgba(255, 255, 255, 0.96);
  border: 1rpx solid rgba(35, 143, 163, 0.1);
}

.guide-head,
.next-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18rpx;
}

.guide-title,
.next-name {
  display: block;
  color: #17252b;
  font-size: 31rpx;
  font-weight: 800;
}

.guide-subtitle,
.next-note {
  display: block;
  margin-top: 6rpx;
  color: #64747d;
  font-size: 23rpx;
  line-height: 1.45;
}

.guide-badge {
  flex-shrink: 0;
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  color: #238fa3;
  background: #e9fbf7;
  font-size: 22rpx;
  font-weight: 800;
}

.loading-card,
.next-card {
  margin-top: 18rpx;
  padding: 16rpx;
  border-radius: 16rpx;
  background: #f7fdfb;
  border: 1rpx solid #d7edf0;
}

.loading-card text,
.kicker {
  color: #b4533c;
  font-size: 22rpx;
  font-weight: 800;
}

.next-main {
  min-width: 0;
  flex: 1;
}

.next-actions,
.tool-row {
  display: flex;
  gap: 10rpx;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.action,
.tool-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 52rpx;
  padding: 0 18rpx;
  border-radius: 999rpx;
  background: #e9fbf7;
}

.action.primary {
  background: #238fa3;
}

.action text,
.tool-btn text {
  color: #238fa3;
  font-size: 22rpx;
  font-weight: 800;
}

.action.primary text {
  color: #ffffff;
}

.tool-row {
  margin-top: 16rpx;
  justify-content: flex-start;
}

.service-scroll {
  margin-top: 16rpx;
  white-space: nowrap;
}

.service-chip {
  display: inline-flex;
  align-items: center;
  height: 54rpx;
  margin-right: 12rpx;
  padding: 0 18rpx;
  border-radius: 999rpx;
  background: #fff1ea;
}

.service-chip text {
  color: #b4533c;
  font-size: 22rpx;
  font-weight: 800;
}

.warning-list {
  margin-top: 12rpx;
}

.warning-list text {
  display: block;
  color: #a05a1c;
  font-size: 21rpx;
  line-height: 1.45;
}
</style>
