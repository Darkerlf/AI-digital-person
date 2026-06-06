<template>
  <view class="page">
    <view class="header-card">
      <text class="eyebrow">游客反馈</text>
      <text class="title">你的反馈会帮助我们优化讲解、路线和服务体验。</text>
    </view>

    <view class="form-card">
      <text class="label">整体感受</text>
      <view class="chips">
        <view :class="['chip', { active: sentiment === 'positive' }]" @tap="sentiment = 'positive'"><text>满意</text></view>
        <view :class="['chip', { active: sentiment === 'negative' }]" @tap="sentiment = 'negative'"><text>不满意</text></view>
      </view>
    </view>

    <view class="form-card">
      <text class="label">评分</text>
      <view class="score-row">
        <view v-for="item in [1,2,3,4,5]" :key="item" :class="['score', { active: score === item }]" @tap="score = item">
          <text>{{ item }}</text>
        </view>
      </view>
    </view>

    <view class="form-card">
      <text class="label">补充说明</text>
      <textarea v-model="content" class="textarea" placeholder="可以写下讲解、路线或服务体验的问题" />
    </view>

    <view class="submit" @tap="submit"><text>提交反馈</text></view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { submitFeedback } from '../../api/tourist'

const sentiment = ref<'positive' | 'negative'>('positive')
const score = ref(5)
const content = ref('')

async function submit() {
  try {
    await submitFeedback({
      sentiment: sentiment.value,
      score: score.value,
      content: content.value,
      scenic_area_id: 1,
    })
    uni.showToast({ title: '感谢反馈', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 600)
  } catch {
    uni.showToast({ title: '提交失败', icon: 'none' })
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 24rpx;
  background: linear-gradient(180deg, #f7fdfb 0%, #effaf7 38%, #e9fbf7 100%);
}

.header-card,
.form-card {
  margin-bottom: 18rpx;
  padding: 26rpx;
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
  line-height: 1.4;
  font-weight: 800;
}

.label {
  display: block;
  margin-bottom: 16rpx;
  font-size: 29rpx;
  font-weight: 800;
  color: #17252b;
}

.chips,
.score-row {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
}

.chip,
.score {
  height: 64rpx;
  min-width: 64rpx;
  padding: 0 24rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e9fbf7;
  border: 1rpx solid #d7edf0;
}

.chip text,
.score text {
  font-size: 25rpx;
  color: #64747d;
  font-weight: 700;
}

.chip.active,
.score.active {
  background: #238fa3;
  border-color: #238fa3;
}

.chip.active text,
.score.active text {
  color: #ffffff;
}

.textarea {
  width: 100%;
  min-height: 190rpx;
  padding: 18rpx;
  border-radius: 14rpx;
  background: #f7faf9;
  border: 1rpx solid #d7edf0;
  font-size: 26rpx;
  color: #17252b;
  line-height: 1.55;
}

.submit {
  height: 88rpx;
  border-radius: 16rpx;
  background: #238fa3;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 12rpx 28rpx rgba(35, 143, 163, 0.18);
}

.submit text {
  color: #ffffff;
  font-weight: 800;
  font-size: 28rpx;
}
</style>
