<template>
  <view class="page">
    <view class="hero">
      <view class="hero-copy">
        <text class="eyebrow">灵山胜境智慧导览</text>
        <text class="hero-title">{{ scenicName }}</text>
        <text class="guide-name">AI 导游 {{ guideName }}</text>
        <text class="hero-subtitle">{{ welcomeMessage }}</text>
        <view class="hero-actions">
          <view class="primary-cta" @tap="goToGuide">
            <text class="cta-icon">问</text>
            <text>进入 AI 导游</text>
          </view>
        </view>
      </view>
      <view class="hero-portrait">
        <image src="/static/digital-human/realistic_guide.png" mode="aspectFill" />
      </view>
    </view>

    <view class="quick-grid">
      <view class="tool-card accent" @tap="goToGuide">
        <text class="tool-mark">AI</text>
        <text class="tool-title">智能问答</text>
        <text class="tool-desc">门票、讲解、服务随时问</text>
      </view>
      <view class="tool-card" @tap="goToMap">
        <text class="tool-mark">图</text>
        <text class="tool-title">地图导览</text>
        <text class="tool-desc">景点定位与路线查看</text>
      </view>
      <view class="tool-card" @tap="goToRoute">
        <text class="tool-mark">线</text>
        <text class="tool-title">推荐路线</text>
        <text class="tool-desc">按兴趣生成游览顺序</text>
      </view>
      <view class="tool-card" @tap="goToServices">
        <text class="tool-mark">服</text>
        <text class="tool-title">便民服务</text>
        <text class="tool-desc">厕所、餐饮、停车查询</text>
      </view>
    </view>

    <view class="section">
      <view class="section-heading">
        <text class="section-title">常问问题</text>
        <text class="section-note">一键发送给 AI 导游</text>
      </view>
      <view class="question-list">
        <view v-for="question in quickQuestions" :key="question" class="question-chip" @tap="askQuickQuestion(question)">
          <text>{{ question }}</text>
        </view>
      </view>
    </view>

    <view class="section">
      <view class="section-heading">
        <text class="section-title">热门景点</text>
        <text class="section-note">先看亮点，再去现场</text>
      </view>
      <view class="spot-list">
        <view
          v-for="spot in hotSpots"
          :key="spot.id"
          class="spot-card"
          @tap="goToSpot(spot.id)"
        >
          <view class="spot-index">
            <text>{{ spot.sort_order || spot.id }}</text>
          </view>
          <view class="spot-info">
            <text class="spot-name">{{ spot.name }}</text>
            <text class="spot-desc">{{ shortIntro(spot.detail_intro || spot.highlights) }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="about-band">
      <text class="about-title">关于灵山胜境</text>
      <text class="about-text">
        灵山胜境位于江苏无锡滨湖区，以灵山大佛为核心，融合佛教文化、自然风光和沉浸式游览体验，适合文化参访、亲子游和轻松休闲。
      </text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getActiveDigitalHumanConfig, getTouristHomeConfig } from '../../api/tourist'
import type { ScenicSpot } from '../../types/api'

const hotSpots = ref<ScenicSpot[]>([])
const scenicName = ref('灵山胜境')
const guideName = ref('灵灵')
const welcomeMessage = ref('AI 数字人导游 · 智慧游览')
const quickQuestions = ref<string[]>(['灵山大佛多高？', '门票多少钱？', '推荐游览路线', '附近有餐厅吗？'])

onMounted(async () => {
  try {
    const res = await getTouristHomeConfig(1)
    scenicName.value = res.scenic_name || scenicName.value
    welcomeMessage.value = res.welcome_message || welcomeMessage.value
    quickQuestions.value = res.quick_questions?.length ? res.quick_questions : quickQuestions.value
    hotSpots.value = (res.hot_spots || []) as ScenicSpot[]
  } catch {
    hotSpots.value = [
      { id: 1, spot_code: 'LSDF', name: '灵山大佛', detail_intro: '世界著名露天青铜佛像，是灵山胜境的核心景观。', open_status: 'open' },
      { id: 2, spot_code: 'LSFG', name: '灵山梵宫', detail_intro: '以佛教艺术、建筑空间和文化展陈见长的代表性景点。', open_status: 'open' },
      { id: 3, spot_code: 'WYTC', name: '五印坛城', detail_intro: '藏式建筑风格鲜明，适合了解藏传佛教文化。', open_status: 'open' },
    ]
  }

  try {
    const digitalHuman = await getActiveDigitalHumanConfig(1)
    guideName.value = digitalHuman.name || guideName.value
    welcomeMessage.value = digitalHuman.welcome_text || welcomeMessage.value
  } catch {
    // 首页仍可使用默认导游名展示，不阻塞游客进入其他功能。
  }
})

function shortIntro(value?: string) {
  const text = value || '暂无介绍'
  return text.length > 52 ? `${text.slice(0, 52)}...` : text
}

function goToGuide() { uni.switchTab({ url: '/pages/guide/guide' }) }
function goToMap() { uni.switchTab({ url: '/pages/map/map' }) }
function goToRoute() { uni.navigateTo({ url: '/pages/route/route' }) }
function goToServices() { uni.navigateTo({ url: '/pages/services/services' }) }
function goToSpot(id: number) { uni.navigateTo({ url: `/pages/spot/spot?id=${id}` }) }
function askQuickQuestion(question: string) {
  uni.setStorageSync('pending_question', question)
  uni.switchTab({ url: '/pages/guide/guide' })
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  padding: 24rpx 24rpx 42rpx;
  background:
    linear-gradient(180deg, #f7fdfb 0%, #effaf7 34%, #e9fbf7 100%);
}

.hero {
  min-height: 392rpx;
  position: relative;
  display: flex;
  overflow: hidden;
  border-radius: 18rpx;
  background:
    linear-gradient(135deg, rgba(239, 250, 247, 0.98), rgba(201, 241, 237, 0.96)),
    linear-gradient(160deg, rgba(42, 174, 192, 0.34), rgba(255, 255, 255, 0) 44%),
    linear-gradient(24deg, rgba(180, 83, 60, 0.08), rgba(255, 255, 255, 0) 42%);
  box-shadow: 0 18rpx 42rpx rgba(35, 143, 163, 0.12);
}

.hero-copy {
  width: 62%;
  padding: 42rpx 0 34rpx 34rpx;
  z-index: 2;
}

.eyebrow {
  display: block;
  font-size: 22rpx;
  color: #238fa3;
  letter-spacing: 0;
  font-weight: 800;
}

.hero-title {
  display: block;
  margin-top: 16rpx;
  font-size: 52rpx;
  line-height: 1.08;
  font-weight: 800;
  color: #123f49;
}

.guide-name {
  display: inline-flex;
  margin-top: 12rpx;
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: rgba(35, 143, 163, 0.12);
  color: #238fa3;
  font-size: 23rpx;
  font-weight: 800;
}

.hero-subtitle {
  display: block;
  margin-top: 14rpx;
  max-width: 360rpx;
  font-size: 25rpx;
  line-height: 1.45;
  color: #3f6470;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 14rpx;
  margin-top: 28rpx;
}

.primary-cta {
  height: 68rpx;
  border-radius: 999rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 25rpx;
  font-weight: 700;
}

.primary-cta {
  gap: 10rpx;
  padding: 0 24rpx;
  color: #ffffff;
  background: #238fa3;
}

.cta-icon {
  width: 34rpx;
  height: 34rpx;
  border-radius: 50%;
  text-align: center;
  line-height: 34rpx;
  font-size: 20rpx;
  color: #ffffff;
  background: #b4533c;
}

.hero-portrait {
  position: absolute;
  right: -18rpx;
  bottom: -8rpx;
  width: 292rpx;
  height: 382rpx;
  overflow: hidden;
  opacity: 0.98;
}

.hero-portrait image {
  width: 100%;
  height: 100%;
  object-position: center top;
}

.quick-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 18rpx;
  margin-top: 22rpx;
}

.tool-card {
  width: calc((100% - 18rpx) / 2);
  min-height: 156rpx;
  padding: 24rpx;
  border: 1rpx solid rgba(35, 143, 163, 0.08);
  border-radius: 16rpx;
  background: #ffffff;
  box-shadow: 0 10rpx 26rpx rgba(35, 143, 163, 0.08);
}

.tool-card.accent {
  background: linear-gradient(135deg, #fff8f4, #ffffff 70%);
}

.tool-mark {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 22rpx;
  font-weight: 800;
  background: #238fa3;
}

.tool-card.accent .tool-mark {
  background: #b4533c;
}

.tool-title {
  display: block;
  margin-top: 18rpx;
  font-size: 29rpx;
  font-weight: 800;
  color: #17252b;
}

.tool-desc {
  display: block;
  margin-top: 8rpx;
  font-size: 23rpx;
  line-height: 1.35;
  color: #64747d;
}

.section {
  margin-top: 28rpx;
}

.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 800;
  color: #17252b;
}

.section-note {
  font-size: 22rpx;
  color: #7a8a91;
}

.question-list {
  display: flex;
  flex-wrap: wrap;
  gap: 14rpx;
}

.question-chip {
  max-width: 100%;
  padding: 14rpx 22rpx;
  border-radius: 999rpx;
  background: #ffffff;
  border: 1rpx solid #d7edf0;
}

.question-chip text {
  font-size: 24rpx;
  color: #238fa3;
}

.spot-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.spot-card {
  display: flex;
  gap: 18rpx;
  padding: 22rpx;
  border-radius: 16rpx;
  background: #ffffff;
  box-shadow: 0 8rpx 22rpx rgba(35, 143, 163, 0.07);
}

.spot-index {
  width: 48rpx;
  height: 48rpx;
  flex-shrink: 0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e9fbf7;
}

.spot-index text {
  font-size: 22rpx;
  font-weight: 800;
  color: #238fa3;
}

.spot-info {
  flex: 1;
  min-width: 0;
}

.spot-name {
  display: block;
  font-size: 29rpx;
  font-weight: 800;
  color: #17252b;
}

.spot-desc {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  line-height: 1.5;
  color: #64747d;
}

.about-band {
  margin-top: 28rpx;
  padding: 26rpx;
  border-radius: 16rpx;
  background: #eef6f3;
  border: 1rpx solid rgba(35, 143, 163, 0.1);
}

.about-title {
  display: block;
  font-size: 28rpx;
  font-weight: 800;
  color: #238fa3;
}

.about-text {
  display: block;
  margin-top: 10rpx;
  font-size: 25rpx;
  line-height: 1.7;
  color: #4f626a;
}
</style>
