<template>
  <view class="digital-human" :class="{ speaking: isSpeaking, thinking: isThinking }">
    <!-- 头部 -->
    <view class="dh-head">
      <!-- 眼睛 -->
      <view class="dh-eyes">
        <view class="dh-eye left" :class="{ blink: !isSpeaking }">
          <view class="dh-pupil" />
        </view>
        <view class="dh-eye right" :class="{ blink: !isSpeaking }">
          <view class="dh-pupil" />
        </view>
      </view>
      <!-- 嘴巴 -->
      <view class="dh-mouth" :class="{ talking: isSpeaking }">
        <view class="dh-lip" />
      </view>
      <!-- 脸颊 -->
      <view class="dh-cheeks">
        <view class="dh-cheek left" />
        <view class="dh-cheek right" />
      </view>
    </view>

    <!-- 身体 -->
    <view class="dh-body">
      <view class="dh-outfit" />
      <view class="dh-badge">
        <text class="badge-text">AI导游</text>
      </view>
    </view>

    <!-- 状态文字 -->
    <view class="dh-status">
      <text v-if="isThinking">思考中...</text>
      <text v-else-if="isSpeaking">说话中</text>
      <text v-else>等待提问</text>
    </view>
  </view>
</template>

<script setup lang="ts">
defineProps<{
  isSpeaking: boolean
  isThinking: boolean
}>()
</script>

<style scoped>
.digital-human {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx;
}

/* 头部 */
.dh-head {
  width: 180rpx;
  height: 200rpx;
  background: #ffecd2;
  border-radius: 90rpx 90rpx 80rpx 80rpx;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.1);
}

/* 眼睛 */
.dh-eyes {
  display: flex;
  gap: 40rpx;
  margin-top: -20rpx;
}

.dh-eye {
  width: 36rpx;
  height: 36rpx;
  background: #ffffff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid #333;
}

.dh-pupil {
  width: 16rpx;
  height: 16rpx;
  background: #333;
  border-radius: 50%;
}

.dh-eye.blink {
  animation: blink 3s infinite;
}

@keyframes blink {
  0%, 95%, 100% { height: 36rpx; }
  97% { height: 4rpx; }
}

/* 嘴巴 */
.dh-mouth {
  width: 40rpx;
  height: 20rpx;
  margin-top: 20rpx;
  position: relative;
  overflow: hidden;
}

.dh-lip {
  width: 40rpx;
  height: 20rpx;
  border-bottom: 4rpx solid #e8836b;
  border-radius: 0 0 20rpx 20rpx;
}

.dh-mouth.talking .dh-lip {
  animation: talk 0.3s infinite;
}

@keyframes talk {
  0%, 100% { height: 10rpx; }
  50% { height: 30rpx; }
}

/* 脸颊 */
.dh-cheeks {
  display: flex;
  gap: 100rpx;
  margin-top: 10rpx;
}

.dh-cheek {
  width: 24rpx;
  height: 12rpx;
  background: #ffb3b3;
  border-radius: 50%;
  opacity: 0.6;
}

/* 身体 */
.dh-body {
  width: 140rpx;
  height: 120rpx;
  background: #1a73e8;
  border-radius: 20rpx 20rpx 40rpx 40rpx;
  margin-top: -10rpx;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dh-outfit {
  width: 100rpx;
  height: 60rpx;
  background: rgba(255,255,255,0.2);
  border-radius: 10rpx;
}

.dh-badge {
  position: absolute;
  bottom: 10rpx;
  background: #ffffff;
  border-radius: 12rpx;
  padding: 4rpx 12rpx;
}

.badge-text {
  font-size: 18rpx;
  color: #1a73e8;
  font-weight: bold;
}

/* 思考状态 */
.digital-human.thinking .dh-head {
  animation: think-bob 1s infinite;
}

@keyframes think-bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8rpx); }
}

/* 说话状态 */
.digital-human.speaking .dh-head {
  animation: speak-bob 0.5s infinite;
}

@keyframes speak-bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4rpx); }
}

/* 状态文字 */
.dh-status {
  margin-top: 16rpx;
}

.dh-status text {
  font-size: 22rpx;
  color: #999;
}
</style>
