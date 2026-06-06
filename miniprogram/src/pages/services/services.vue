<template>
  <view class="page">
    <view class="header">
      <text class="eyebrow">便民服务</text>
      <text class="title">快速查询厕所、餐饮、停车与服务中心。</text>
      <text class="subtitle">点击服务点可跳转到地图导览。</text>
    </view>

    <scroll-view scroll-x class="category-scroll">
      <view
        v-for="item in categories"
        :key="item.value"
        :class="['chip', { active: category === item.value }]"
        @tap="selectCategory(item.value)"
      >
        <text>{{ item.label }}</text>
      </view>
    </scroll-view>

    <view class="poi-card" v-for="poi in pois" :key="poi.name" @tap="openOnMap(poi)">
      <view class="poi-main">
        <text class="poi-name">{{ poi.name }}</text>
        <text class="poi-meta">{{ categoryLabel(poi.category) }} · {{ poi.area_text || '景区内' }}</text>
      </view>
      <text class="poi-desc">{{ poi.description || '暂无说明' }}</text>
      <view class="poi-foot">
        <text class="poi-hours">开放：{{ poi.open_hours || '以现场为准' }}</text>
        <text class="poi-action">查看地图</text>
      </view>
    </view>

    <view v-if="pois.length === 0" class="empty">
      <text>暂无服务点数据</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getServicePois } from '../../api/tourist'
import type { ServicePOI } from '../../types/api'

const categories = [
  { label: '全部', value: '' },
  { label: '厕所', value: 'toilet' },
  { label: '餐饮', value: 'restaurant' },
  { label: '停车', value: 'parking' },
  { label: '服务中心', value: 'service_center' },
]

const category = ref('')
const pois = ref<ServicePOI[]>([])

onMounted(loadPois)

async function loadPois() {
  try {
    const res = await getServicePois(category.value || undefined)
    pois.value = res.items || []
  } catch {
    uni.showToast({ title: '服务点加载失败', icon: 'none' })
  }
}

function selectCategory(value: string) {
  category.value = value
  loadPois()
}

function categoryLabel(value: string) {
  return categories.find((item) => item.value === value)?.label || value
}

function openOnMap(poi: ServicePOI) {
  if (typeof poi.latitude !== 'number' || typeof poi.longitude !== 'number') {
    uni.showToast({ title: '暂无精确点位', icon: 'none' })
    return
  }
  uni.setStorageSync('target_poi', poi)
  uni.switchTab({ url: '/pages/map/map' })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 24rpx;
  background: linear-gradient(180deg, #f7fdfb 0%, #effaf7 38%, #e9fbf7 100%);
}

.header {
  padding: 32rpx 30rpx;
  border-radius: 18rpx;
  background: #ffffff;
  border: 1rpx solid rgba(35, 143, 163, 0.08);
  box-shadow: 0 8rpx 24rpx rgba(35, 143, 163, 0.07);
}

.eyebrow {
  display: block;
  color: #b4533c;
  font-size: 23rpx;
  font-weight: 800;
}

.title {
  display: block;
  margin-top: 10rpx;
  color: #17252b;
  font-size: 34rpx;
  line-height: 1.35;
  font-weight: 800;
}

.subtitle {
  display: block;
  margin-top: 10rpx;
  color: #64747d;
  font-size: 25rpx;
}

.category-scroll {
  margin: 20rpx 0;
  white-space: nowrap;
}

.chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 60rpx;
  margin-right: 12rpx;
  padding: 0 22rpx;
  border-radius: 999rpx;
  background: #ffffff;
  border: 1rpx solid #d7edf0;
}

.chip text {
  font-size: 24rpx;
  color: #64747d;
  font-weight: 700;
}

.chip.active {
  background: #238fa3;
  border-color: #238fa3;
}

.chip.active text {
  color: #ffffff;
}

.poi-card {
  margin-bottom: 16rpx;
  padding: 24rpx;
  border-radius: 18rpx;
  background: #ffffff;
  border: 1rpx solid rgba(35, 143, 163, 0.08);
  box-shadow: 0 8rpx 24rpx rgba(35, 143, 163, 0.07);
}

.poi-main {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20rpx;
}

.poi-name {
  flex: 1;
  min-width: 0;
  font-size: 30rpx;
  font-weight: 800;
  color: #17252b;
}

.poi-meta {
  flex-shrink: 0;
  padding: 6rpx 12rpx;
  border-radius: 999rpx;
  background: #e9fbf7;
  font-size: 21rpx;
  color: #238fa3;
}

.poi-desc {
  display: block;
  margin-top: 10rpx;
  font-size: 25rpx;
  color: #4f626a;
  line-height: 1.55;
}

.poi-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18rpx;
  margin-top: 16rpx;
  padding-top: 14rpx;
  border-top: 1rpx solid #edf3f4;
}

.poi-hours {
  font-size: 23rpx;
  color: #7a8a91;
}

.poi-action {
  font-size: 23rpx;
  color: #b4533c;
  font-weight: 800;
}

.empty {
  margin-top: 80rpx;
  text-align: center;
}

.empty text {
  font-size: 25rpx;
  color: #7a8a91;
}
</style>
