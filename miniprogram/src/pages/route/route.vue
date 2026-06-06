<template>
  <view class="page">
    <view class="hero">
      <text class="eyebrow">个性化路线</text>
      <text class="title">按你的时间和兴趣，生成可执行游览顺序。</text>
      <text class="subtitle">路线会优先参考知识库内容，也会结合当前偏好做灵活推荐。</text>
    </view>

    <view class="preference-card">
      <view class="card-head">
        <text class="label">兴趣</text>
        <text class="hint">可多选</text>
      </view>
      <view class="chips">
        <view
          v-for="item in interestOptions"
          :key="item.value"
          :class="['chip', { active: interestTags.includes(item.value) }]"
          @tap="toggleInterest(item.value)"
        >
          <text>{{ item.label }}</text>
        </view>
      </view>
    </view>

    <view class="preference-card">
      <view class="card-head">
        <text class="label">时长</text>
        <text class="hint">单选</text>
      </view>
      <view class="chips">
        <view
          v-for="item in durationOptions"
          :key="item.value"
          :class="['chip', { active: durationMinutes === item.value }]"
          @tap="durationMinutes = item.value"
        >
          <text>{{ item.label }}</text>
        </view>
      </view>
    </view>

    <view class="preference-card">
      <view class="card-head">
        <text class="label">起终点</text>
        <text class="hint">可留空</text>
      </view>
      <view class="field-stack">
        <input v-model="startSpotName" class="text-input" placeholder="从哪里出发，如南门入口" />
        <input v-model="endSpotName" class="text-input" placeholder="希望在哪里结束，如出口/停车场" />
        <view v-if="rerouteFromSpotName" class="reroute-note">
          <text>将从 {{ rerouteFromSpotName }} 继续规划</text>
        </view>
      </view>
    </view>

    <view class="preference-card">
      <view class="card-head">
        <text class="label">人群</text>
        <text class="hint">可多选</text>
      </view>
      <view class="chips">
        <view
          v-for="item in audienceOptions"
          :key="item.value"
          :class="['chip', { active: audienceTags.includes(item.value) }]"
          @tap="toggleAudience(item.value)"
        >
          <text>{{ item.label }}</text>
        </view>
      </view>
    </view>

    <view class="preference-card">
      <view class="card-head">
        <text class="label">节奏</text>
        <text class="hint">单选</text>
      </view>
      <view class="chips">
        <view
          v-for="item in paceOptions"
          :key="item.value"
          :class="['chip', { active: pace === item.value }]"
          @tap="pace = item.value"
        >
          <text>{{ item.label }}</text>
        </view>
      </view>
    </view>

    <view class="preference-card">
      <view class="card-head">
        <text class="label">行动需求</text>
        <text class="hint">可多选</text>
      </view>
      <view class="chips">
        <view
          v-for="item in mobilityOptions"
          :key="item.value"
          :class="['chip', { active: mobilityTags.includes(item.value) }]"
          @tap="toggleMobility(item.value)"
        >
          <text>{{ item.label }}</text>
        </view>
      </view>
    </view>

    <view class="preference-card">
      <view class="card-head">
        <text class="label">服务点</text>
        <text class="hint">可多选</text>
      </view>
      <view class="chips">
        <view
          v-for="item in serviceNeedOptions"
          :key="item.value"
          :class="['chip', { active: serviceNeeds.includes(item.value) }]"
          @tap="toggleServiceNeed(item.value)"
        >
          <text>{{ item.label }}</text>
        </view>
      </view>
    </view>

    <view :class="['primary-btn', { loading }]" @tap="generateRoute">
      <text>{{ loading ? '生成中...' : '生成路线' }}</text>
    </view>

    <view v-if="routeResult" class="result-card">
      <view class="result-head">
        <text class="route-name">{{ routeResult.matched_template?.name || routeResult.template_name || '推荐路线' }}</text>
        <text class="route-summary">{{ routeResult.summary || routeResult.match_reason }}</text>
      </view>
      <view class="timeline">
        <view class="spot-step" v-for="(spot, index) in routeResult.spots" :key="index">
          <text class="step-index">{{ index + 1 }}</text>
          <view class="step-body">
            <text class="step-name">{{ spot.name }}</text>
            <text class="step-desc">{{ spot.stay_minutes || 30 }}分钟 · {{ spot.highlight || '重点讲解站点' }}</text>
          </view>
        </view>
      </view>
      <view class="secondary-btn" @tap="startMapGuide">
        <text>开始步行导览</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import { recommendRoute } from '../../api/tourist'
import type { RouteRecommendRequest, RouteRecommendResponse } from '../../types/api'

const interestOptions = [
  { label: '历史文化', value: '文化' },
  { label: '佛教艺术', value: '艺术' },
  { label: '拍照打卡', value: '拍照' },
  { label: '轻松游', value: '休闲' },
  { label: '自然风光', value: '自然' },
]
const durationOptions = [
  { label: '1小时', value: 60 },
  { label: '半天', value: 180 },
  { label: '全天', value: 360 },
]
const audienceOptions = [
  { label: '亲子', value: '亲子' },
  { label: '老人', value: '老人' },
  { label: '首次来访', value: '首次' },
]
const paceOptions = [
  { label: '轻松慢游', value: 'relaxed' },
  { label: '常规节奏', value: 'standard' },
  { label: '高效打卡', value: 'fast' },
]
const mobilityOptions = [
  { label: '少台阶', value: '少台阶' },
  { label: '少排队', value: '少排队' },
  { label: '轮椅友好', value: '轮椅友好' },
]
const serviceNeedOptions = [
  { label: '卫生间', value: '卫生间' },
  { label: '餐饮', value: '餐饮' },
  { label: '游客服务中心', value: '游客服务中心' },
]

const interestTags = ref<string[]>(['文化'])
const audienceTags = ref<string[]>([])
const durationMinutes = ref(180)
const startSpotName = ref('')
const endSpotName = ref('')
const pace = ref('standard')
const mobilityTags = ref<string[]>([])
const serviceNeeds = ref<string[]>([])
const rerouteFromSpotName = ref('')
const loading = ref(false)
const routeResult = ref<RouteRecommendResponse | null>(null)
const lastRouteRequest = ref<RouteRecommendRequest | null>(null)

function toggleInterest(value: string) {
  interestTags.value = interestTags.value.includes(value)
    ? interestTags.value.filter((item) => item !== value)
    : [...interestTags.value, value]
}

function toggleAudience(value: string) {
  audienceTags.value = audienceTags.value.includes(value)
    ? audienceTags.value.filter((item) => item !== value)
    : [...audienceTags.value, value]
}

function toggleMobility(value: string) {
  mobilityTags.value = mobilityTags.value.includes(value)
    ? mobilityTags.value.filter((item) => item !== value)
    : [...mobilityTags.value, value]
}

function toggleServiceNeed(value: string) {
  serviceNeeds.value = serviceNeeds.value.includes(value)
    ? serviceNeeds.value.filter((item) => item !== value)
    : [...serviceNeeds.value, value]
}

function cleanText(value: string) {
  const text = value.trim()
  return text.length > 0 ? text : undefined
}

function buildRouteRequest(): RouteRecommendRequest {
  return {
    scenic_area_id: 1,
    duration_minutes: durationMinutes.value,
    interest_tags: [...interestTags.value],
    audience_tags: [...audienceTags.value],
    start_spot_name: cleanText(startSpotName.value),
    end_spot_name: cleanText(endSpotName.value),
    pace: pace.value,
    mobility_tags: [...mobilityTags.value],
    service_needs: [...serviceNeeds.value],
    reroute_from_spot_name: cleanText(rerouteFromSpotName.value),
  }
}

function applyStoredRequest(payload: RouteRecommendRequest) {
  if (typeof payload.duration_minutes === 'number') {
    durationMinutes.value = payload.duration_minutes
  }
  if (Array.isArray(payload.interest_tags)) {
    interestTags.value = [...payload.interest_tags]
  }
  if (Array.isArray(payload.audience_tags)) {
    audienceTags.value = [...payload.audience_tags]
  }
  if (Array.isArray(payload.mobility_tags)) {
    mobilityTags.value = [...payload.mobility_tags]
  }
  if (Array.isArray(payload.service_needs)) {
    serviceNeeds.value = [...payload.service_needs]
  }
  startSpotName.value = payload.start_spot_name || startSpotName.value
  endSpotName.value = payload.end_spot_name || endSpotName.value
  pace.value = payload.pace || pace.value
  rerouteFromSpotName.value = payload.reroute_from_spot_name || rerouteFromSpotName.value
}

function readQueryValue(query: Record<string, unknown>, ...keys: string[]) {
  for (const key of keys) {
    const value = query[key]
    if (typeof value === 'string' && value.trim()) {
      return decodeURIComponent(value)
    }
  }
  return ''
}

function applyReroutePrefill(query: Record<string, unknown> = {}) {
  const storedRequest = uni.getStorageSync('last_route_request') as RouteRecommendRequest | ''
  if (storedRequest && typeof storedRequest === 'object') {
    applyStoredRequest(storedRequest)
    lastRouteRequest.value = storedRequest
  }

  const storedRerouteSpot = uni.getStorageSync('reroute_from_spot_name') as string | ''
  const queryRerouteSpot = readQueryValue(query, 'reroute_from_spot_name', 'rerouteFromSpotName')
  const queryStartSpot = readQueryValue(query, 'start_spot_name', 'startSpotName')
  const queryEndSpot = readQueryValue(query, 'end_spot_name', 'endSpotName')

  if (queryStartSpot) {
    startSpotName.value = queryStartSpot
  }
  if (queryEndSpot) {
    endSpotName.value = queryEndSpot
  }
  if (queryRerouteSpot || storedRerouteSpot) {
    rerouteFromSpotName.value = queryRerouteSpot || storedRerouteSpot
    startSpotName.value = startSpotName.value || rerouteFromSpotName.value
    uni.removeStorageSync('reroute_from_spot_name')
  }
}

onLoad((query = {}) => {
  applyReroutePrefill(query)
})

onShow(() => {
  applyReroutePrefill()
})

async function generateRoute() {
  if (loading.value) return
  loading.value = true
  const payload = buildRouteRequest()
  try {
    routeResult.value = await recommendRoute(payload)
    lastRouteRequest.value = payload
    uni.setStorageSync('last_route_request', payload)
    uni.setStorageSync('active_route', routeResult.value)
  } catch {
    uni.showToast({ title: '暂时无法生成路线', icon: 'none' })
  } finally {
    loading.value = false
  }
}

function startMapGuide() {
  if (!routeResult.value) return
  const payload = lastRouteRequest.value || buildRouteRequest()
  uni.setStorageSync('active_route', routeResult.value)
  uni.setStorageSync('last_route_request', payload)
  uni.navigateTo({ url: '/pages/route-guide/route-guide' })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 24rpx;
  background: linear-gradient(180deg, #f7fdfb 0%, #effaf7 38%, #e9fbf7 100%);
}

.hero {
  padding: 34rpx 30rpx;
  border-radius: 18rpx;
  background:
    linear-gradient(135deg, rgba(239, 250, 247, 0.98), rgba(201, 241, 237, 0.96)),
    linear-gradient(160deg, rgba(42, 174, 192, 0.28), rgba(255, 255, 255, 0) 46%);
  border: 1rpx solid rgba(35, 143, 163, 0.12);
}

.eyebrow {
  display: block;
  color: #b4533c;
  font-size: 23rpx;
  font-weight: 800;
}

.title {
  display: block;
  margin-top: 12rpx;
  color: #123f49;
  font-size: 36rpx;
  line-height: 1.35;
  font-weight: 800;
}

.subtitle {
  display: block;
  margin-top: 12rpx;
  color: #4f626a;
  font-size: 25rpx;
  line-height: 1.55;
}

.preference-card,
.result-card {
  margin-top: 18rpx;
  padding: 24rpx;
  border-radius: 18rpx;
  background: #ffffff;
  border: 1rpx solid rgba(35, 143, 163, 0.08);
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.label {
  font-size: 29rpx;
  font-weight: 800;
  color: #17252b;
}

.hint {
  font-size: 22rpx;
  color: #7a8a91;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
}

.chip {
  height: 60rpx;
  padding: 0 22rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e9fbf7;
  border: 1rpx solid #d7edf0;
}

.chip text {
  font-size: 24rpx;
  color: #4f626a;
  font-weight: 700;
}

.chip.active {
  background: #238fa3;
  border-color: #238fa3;
}

.chip.active text {
  color: #ffffff;
}

.field-stack {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.text-input {
  height: 68rpx;
  padding: 0 20rpx;
  border-radius: 14rpx;
  background: #f7fbfa;
  border: 1rpx solid #d7edf0;
  color: #17252b;
  font-size: 25rpx;
}

.reroute-note {
  padding: 14rpx 18rpx;
  border-radius: 14rpx;
  background: #fff1ea;
}

.reroute-note text {
  color: #b4533c;
  font-size: 24rpx;
  font-weight: 700;
}

.primary-btn,
.secondary-btn {
  height: 88rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
}

.primary-btn {
  margin-top: 20rpx;
  background: #238fa3;
}

.primary-btn.loading {
  opacity: 0.68;
}

.primary-btn text,
.secondary-btn text {
  color: #ffffff;
  font-size: 28rpx;
}

.result-head {
  padding-bottom: 18rpx;
  border-bottom: 1rpx solid #edf3f4;
}

.route-name {
  display: block;
  font-size: 32rpx;
  font-weight: 800;
  color: #17252b;
}

.route-summary {
  display: block;
  margin-top: 10rpx;
  color: #64747d;
  font-size: 25rpx;
  line-height: 1.65;
}

.timeline {
  padding-top: 4rpx;
}

.spot-step {
  display: flex;
  gap: 18rpx;
  margin-top: 22rpx;
}

.step-index {
  width: 44rpx;
  height: 44rpx;
  flex-shrink: 0;
  border-radius: 50%;
  background: #e9fbf7;
  color: #238fa3;
  text-align: center;
  line-height: 44rpx;
  font-size: 23rpx;
  font-weight: 800;
}

.step-body {
  flex: 1;
  min-width: 0;
}

.step-name {
  display: block;
  font-size: 28rpx;
  font-weight: 800;
  color: #17252b;
}

.step-desc {
  display: block;
  margin-top: 6rpx;
  color: #64747d;
  font-size: 24rpx;
  line-height: 1.45;
}

.secondary-btn {
  margin-top: 24rpx;
  background: #b4533c;
}
</style>
