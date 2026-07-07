<template>
  <view class="voice-page">
    <view class="voice-panel">
      <text class="kicker">AI 导游语音输入</text>
      <text class="title">{{ title }}</text>
      <text class="copy">{{ copy }}</text>

      <button
        class="record-button"
        :class="{ recording: isRecording }"
        @touchstart.prevent="startRecord"
        @touchend.prevent="stopRecord"
        @mousedown.prevent="startRecord"
        @mouseup.prevent="stopRecord"
      >
        {{ isRecording ? '松开结束' : '按住说话' }}
      </button>

      <button class="text-button" @tap="returnToGuide">返回 AI 导游</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { onLoad, onUnload } from '@dcloudio/uni-app'
import { ref } from 'vue'
import { API_BASE_URL } from '../../api/request'

const recorderManager = uni.getRecorderManager()
const isRecording = ref(false)
const isUploading = ref(false)
const title = ref('请按住按钮说话')
const copy = ref('录音会在小程序原生层完成，识别后自动回到数字人导游继续提问。')

onLoad(() => {
  recorderManager.onStart(() => {
    isRecording.value = true
    title.value = '正在聆听'
    copy.value = '说完后松开按钮，我会帮你识别成文字。'
  })
  recorderManager.onStop((res) => {
    isRecording.value = false
    if (!res.tempFilePath) {
      showToast('录音失败，请重试')
      return
    }
    uploadForAsr(res.tempFilePath)
  })
  recorderManager.onError((res) => {
    isRecording.value = false
    showToast(res.errMsg || '录音失败，请重试')
  })
})

onUnload(() => {
  if (isRecording.value) recorderManager.stop()
})

function startRecord() {
  if (isRecording.value || isUploading.value) return
  recorderManager.start({
    format: 'mp3',
    sampleRate: 16000,
    numberOfChannels: 1,
    encodeBitRate: 48000,
    duration: 60000,
  })
}

function stopRecord() {
  if (!isRecording.value) return
  recorderManager.stop()
}

function uploadForAsr(filePath: string) {
  const token = String(uni.getStorageSync('token') || '').trim()
  isUploading.value = true
  title.value = '正在识别'
  copy.value = '马上回到数字人导游。'
  uni.uploadFile({
    url: `${API_BASE_URL}/tourist/voice/asr`,
    filePath,
    name: 'audio',
    header: token ? { Authorization: `Bearer ${token}` } : {},
    success: (res) => {
      if (res.statusCode !== 200) {
        showToast('语音识别失败，请重试')
        return
      }
      const data = JSON.parse(res.data || '{}') as { text?: string }
      const text = String(data.text || '').trim()
      if (!text) {
        showToast('没有听清，请再说一次')
        return
      }
      uni.setStorageSync('pending_question', text)
      uni.switchTab({ url: '/pages/guide/guide' })
    },
    fail: (err) => {
      showToast(err.errMsg || '语音识别失败，请重试')
    },
    complete: () => {
      isUploading.value = false
      if (!isRecording.value) {
        title.value = '请按住按钮说话'
        copy.value = '录音会在小程序原生层完成，识别后自动回到数字人导游继续提问。'
      }
    },
  })
}

function returnToGuide() {
  uni.switchTab({ url: '/pages/guide/guide' })
}

function showToast(titleText: string) {
  uni.showToast({ title: titleText, icon: 'none' })
}
</script>

<style scoped>
.voice-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40rpx;
  background: #f7fdfb;
}

.voice-panel {
  width: 100%;
  padding: 44rpx 34rpx;
  border-radius: 20rpx;
  background: #ffffff;
  box-shadow: 0 18rpx 46rpx rgba(35, 143, 163, 0.13);
}

.kicker,
.title,
.copy {
  display: block;
}

.kicker {
  color: #238fa3;
  font-size: 24rpx;
  font-weight: 800;
}

.title {
  margin-top: 16rpx;
  color: #17252b;
  font-size: 40rpx;
  font-weight: 900;
}

.copy {
  margin-top: 18rpx;
  color: #667880;
  font-size: 28rpx;
  line-height: 1.65;
}

.record-button {
  width: 100%;
  height: 116rpx;
  margin-top: 42rpx;
  border-radius: 999rpx;
  color: #ffffff;
  background: #238fa3;
  font-size: 32rpx;
  font-weight: 900;
}

.record-button.recording {
  background: #d94c48;
}

.text-button {
  width: 100%;
  height: 82rpx;
  margin-top: 22rpx;
  border-radius: 999rpx;
  color: #238fa3;
  background: #e9f8f6;
  font-size: 28rpx;
  font-weight: 800;
}
</style>
