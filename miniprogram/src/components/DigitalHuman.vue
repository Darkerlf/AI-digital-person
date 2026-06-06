<template>
  <view class="digital-human" :class="[{ speaking: isSpeaking, thinking: isThinking }, `emotion-${resolvedEmotion}`]">
    <view class="avatar-stage">
      <view class="avatar-rig">
        <image class="avatar-layer base-layer" :src="baseImage" mode="widthFix" />
        <view v-if="showBlinkClosed" class="blink-mask left-eye">
          <view class="blink-line" />
        </view>
        <view v-if="showBlinkClosed" class="blink-mask right-eye">
          <view class="blink-line" />
        </view>
        <image
          v-if="showMouthLayer"
          class="avatar-layer mouth-layer"
          :class="`mouth-${props.mouth}`"
          :src="mouthImage"
          :style="mouthStyle"
          mode="scaleToFill"
        />
      </view>
    </view>
    <view class="status-dot" :class="{ active: isSpeaking || isThinking }">
      <text>{{ statusText }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { digitalHumanAssetBase } from '../config/assets'
import { mouthVisualProfile } from '../utils/mouthSmoothing'

type MouthShape = 'closed' | 'small' | 'mid' | 'big' | 'round'
type AvatarEmotion = 'neutral' | 'smile' | 'enthusiastic' | 'thinking'

const realisticGuideImage = '/static/digital-human/realistic_guide.png'

const props = withDefaults(defineProps<{
  isSpeaking: boolean
  isThinking: boolean
  mouth?: MouthShape
  emotion?: AvatarEmotion
}>(), {
  mouth: 'closed',
  emotion: 'neutral',
})

const assetBase = digitalHumanAssetBase
const baseImage = realisticGuideImage
const isBlinking = ref(false)
let blinkTimer: ReturnType<typeof setInterval> | null = null
let blinkResetTimer: ReturnType<typeof setTimeout> | null = null

const mouthImages: Record<MouthShape, string> = {
  closed: `${assetBase}/mouth_closed.png`,
  small: `${assetBase}/mouth_small.png`,
  mid: `${assetBase}/mouth_mid.png`,
  big: `${assetBase}/mouth_big.png`,
  round: `${assetBase}/mouth_round.png`,
}

const mouthImage = computed(() => mouthImages[props.mouth] || mouthImages.closed)
const useRealisticStill = computed(() => baseImage === realisticGuideImage)
const resolvedEmotion = computed<AvatarEmotion>(() => {
  if (props.isThinking) return 'thinking'
  if (props.isSpeaking && props.emotion === 'neutral') return 'smile'
  return props.emotion
})
const showBlinkClosed = computed(() => !useRealisticStill.value && isBlinking.value)
const showMouthLayer = computed(() => !useRealisticStill.value && (props.isSpeaking || props.mouth !== 'closed'))
const mouthStyle = computed(() => {
  const profile = mouthVisualProfile(props.mouth)
  return `transform: translateY(${profile.translateY}rpx) scale(${profile.scaleX}, ${profile.scaleY});`
})
const statusText = computed(() => {
  if (props.isSpeaking) return '讲解中'
  if (props.isThinking) return '思考中'
  return '待机'
})

function blinkOnce() {
  if (props.mouth === 'big') return
  isBlinking.value = true
  blinkResetTimer = setTimeout(() => {
    isBlinking.value = false
  }, props.isSpeaking ? 90 : 120)
}

onMounted(() => {
  blinkTimer = setInterval(blinkOnce, 3600)
})

onUnmounted(() => {
  if (blinkTimer) clearInterval(blinkTimer)
  if (blinkResetTimer) clearTimeout(blinkResetTimer)
})

watch(
  () => props.isSpeaking,
  (speaking) => {
    if (speaking) {
      isBlinking.value = false
    }
  },
)
</script>

<style scoped>
.digital-human {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.avatar-stage {
  width: 250rpx;
  height: 385rpx;
  position: relative;
  overflow: hidden;
  transform-origin: bottom center;
}

.avatar-rig {
  position: absolute;
  inset: 0;
  transform-origin: 50% 72%;
}

.digital-human .avatar-rig {
  animation: idle-breathe 3600ms ease-in-out infinite;
}

.digital-human.thinking .avatar-rig {
  animation: think-nod 1300ms ease-in-out infinite;
}

.digital-human.speaking .avatar-rig {
  animation: speak-breathe 1500ms ease-in-out infinite;
}

.avatar-layer {
  position: absolute;
  display: block;
  pointer-events: none;
}

.base-layer {
  left: 0;
  top: 0;
  width: 100%;
  height: auto;
}

.blink-mask {
  position: absolute;
  top: 29.2%;
  width: 12.2%;
  height: 5.6%;
  border-radius: 999rpx;
  background: #f3c8b9;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.left-eye {
  left: 34%;
}

.right-eye {
  left: 54.5%;
}

.blink-line {
  width: 88%;
  height: 4rpx;
  border-radius: 999rpx;
  background: #2f1e1b;
}

.mouth-layer {
  left: 37.8%;
  top: 38%;
  width: 24.18%;
  height: 8.14%;
  z-index: 3;
  transform-origin: 50% 60%;
  transition: transform 70ms ease-out, opacity 90ms ease-out;
  will-change: transform;
}

.mouth-closed {
  opacity: 0.88;
}

.mouth-big,
.mouth-round {
  opacity: 1;
}

.status-dot {
  margin-top: 8rpx;
  min-width: 96rpx;
  height: 34rpx;
  border-radius: 17rpx;
  background: rgba(255, 255, 255, 0.82);
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-dot.active {
  background: rgba(229, 243, 246, 0.96);
}

.status-dot text {
  color: #238fa3;
  font-size: 20rpx;
  line-height: 1;
}

@keyframes idle-breathe {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-2rpx) scale(1.004); }
}

@keyframes speak-breathe {
  0%, 100% { transform: translateY(0) scale(1); }
  45% { transform: translateY(-3rpx) scale(1.006); }
}

@keyframes think-nod {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-3rpx) rotate(-0.45deg); }
}
</style>
