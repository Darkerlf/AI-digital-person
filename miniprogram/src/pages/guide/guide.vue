<template>
  <view class="page">
    <!-- Avatar area -->
    <view class="avatar-area">
      <view class="avatar-placeholder">
        <text class="avatar-emoji">🧑‍🏫</text>
        <text class="avatar-label">灵山导游</text>
      </view>
    </view>

    <!-- Message list -->
    <scroll-view
      class="message-list"
      scroll-y
      :scroll-into-view="scrollTarget"
      scroll-with-animation
    >
      <!-- Welcome -->
      <view v-if="chatStore.messages.length === 0" class="welcome">
        <text class="welcome-title">你好！我是灵山胜境AI导游 👋</text>
        <text class="welcome-desc">有什么想了解的，尽管问我吧！</text>
        <view class="quick-questions">
          <view v-for="q in quickQuestions" :key="q" class="quick-q" @tap="sendQuickQuestion(q)">
            <text>{{ q }}</text>
          </view>
        </view>
      </view>

      <!-- Messages -->
      <view
        v-for="msg in chatStore.messages"
        :key="msg.id"
        :id="'msg-' + msg.id"
        :class="['message-item', msg.role]"
      >
        <view v-if="msg.role === 'assistant'" class="msg-avatar">🧑‍🏫</view>
        <view :class="['msg-bubble', msg.role]">
          <text v-if="msg.loading" class="loading-dots">思考中...</text>
          <text v-else class="msg-text">{{ msg.content }}</text>
          <text v-if="msg.intent && msg.role === 'assistant'" class="msg-intent">
            {{ intentLabels[msg.intent] || msg.intent }}
          </text>
        </view>
        <view v-if="msg.role === 'user'" class="msg-avatar">😊</view>
      </view>

      <view id="msg-bottom" style="height: 20rpx;" />
    </scroll-view>

    <!-- Input area -->
    <view class="input-area">
      <input
        v-model="inputText"
        class="msg-input"
        placeholder="输入你的问题..."
        :disabled="chatStore.isGenerating"
        confirm-type="send"
        @confirm="sendMessage"
      />
      <view :class="['send-btn', { disabled: !inputText.trim() || chatStore.isGenerating }]" @tap="sendMessage">
        <text>发送</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from '../../stores/chat'
import { useAuthStore } from '../../stores/auth'
import { chatWithProgressiveDisplay } from '../../utils/sse'

const chatStore = useChatStore()
const authStore = useAuthStore()

const inputText = ref('')
const scrollTarget = ref('msg-bottom')

const quickQuestions = [
  '灵山大佛多高？',
  '门票多少钱？',
  '推荐游览路线',
  '附近有餐厅吗？',
]

const intentLabels: Record<string, string> = {
  scenic_qa: '景区问答',
  route_recommend: '路线推荐',
  service_query: '便民服务',
  chitchat: '闲聊',
}

watch(
  () => chatStore.messages.length,
  () => {
    nextTick(() => {
      scrollTarget.value = ''
      setTimeout(() => {
        scrollTarget.value = 'msg-bottom'
      }, 50)
    })
  }
)

function sendQuickQuestion(q: string) {
  inputText.value = q
  sendMessage()
}

function sendMessage() {
  const text = inputText.value.trim()
  if (!text || chatStore.isGenerating) return

  authStore.ensureVisitor()
  chatStore.addUserMessage(text)
  inputText.value = ''

  const placeholderId = chatStore.addAssistantPlaceholder()
  chatStore.isGenerating = true

  nextTick(() => {
    scrollTarget.value = `msg-${placeholderId}`
  })

  chatWithProgressiveDisplay(
    {
      message: text,
      session_id: chatStore.sessionId,
      scenic_area_id: 1,
    },
    (chunk: string) => {
      chatStore.appendToMessage(placeholderId, chunk)
    },
    (fullText: string) => {
      chatStore.updateAssistantMessage(placeholderId, fullText)
      chatStore.isGenerating = false
    },
    (err: Error) => {
      chatStore.updateAssistantMessage(placeholderId, '抱歉，暂时无法回答，请稍后再试。')
      chatStore.isGenerating = false
      console.error('Chat error:', err)
    },
  )
}
</script>

<style scoped>
.page { height: 100vh; display: flex; flex-direction: column; background: #f0f2f5; }
.avatar-area { height: 160rpx; background: linear-gradient(135deg, #1a73e8, #0d47a1); display: flex; align-items: center; justify-content: center; }
.avatar-placeholder { display: flex; flex-direction: column; align-items: center; gap: 8rpx; }
.avatar-emoji { font-size: 64rpx; }
.avatar-label { font-size: 24rpx; color: rgba(255,255,255,0.9); }
.message-list { flex: 1; padding: 20rpx; overflow-y: auto; }
.welcome { text-align: center; padding: 60rpx 30rpx; }
.welcome-title { font-size: 32rpx; font-weight: bold; color: #333; display: block; }
.welcome-desc { font-size: 26rpx; color: #999; margin-top: 12rpx; display: block; }
.quick-questions { display: flex; flex-wrap: wrap; gap: 16rpx; justify-content: center; margin-top: 30rpx; }
.quick-q { background: #e8f0fe; border-radius: 32rpx; padding: 12rpx 24rpx; }
.quick-q text { font-size: 24rpx; color: #1a73e8; }
.message-item { display: flex; margin-bottom: 24rpx; gap: 12rpx; }
.message-item.user { justify-content: flex-end; }
.message-item.assistant { justify-content: flex-start; }
.msg-avatar { width: 64rpx; height: 64rpx; border-radius: 50%; background: #e8f0fe; display: flex; align-items: center; justify-content: center; font-size: 32rpx; flex-shrink: 0; }
.msg-bubble { max-width: 70%; padding: 20rpx 24rpx; border-radius: 16rpx; word-break: break-all; }
.msg-bubble.user { background: #1a73e8; border-bottom-right-radius: 4rpx; }
.msg-bubble.assistant { background: #ffffff; border-bottom-left-radius: 4rpx; }
.msg-text { font-size: 28rpx; line-height: 1.6; }
.msg-bubble.user .msg-text { color: #ffffff; }
.msg-bubble.assistant .msg-text { color: #333; }
.loading-dots { font-size: 28rpx; color: #999; }
.msg-intent { display: block; font-size: 20rpx; color: #1a73e8; margin-top: 8rpx; opacity: 0.7; }
.input-area { display: flex; align-items: center; gap: 16rpx; padding: 16rpx 24rpx; background: #ffffff; border-top: 1rpx solid #e5e5e5; padding-bottom: calc(16rpx + env(safe-area-inset-bottom)); }
.msg-input { flex: 1; height: 72rpx; background: #f5f5f5; border-radius: 36rpx; padding: 0 30rpx; font-size: 28rpx; }
.send-btn { width: 120rpx; height: 72rpx; background: #1a73e8; border-radius: 36rpx; display: flex; align-items: center; justify-content: center; }
.send-btn text { color: #ffffff; font-size: 28rpx; }
.send-btn.disabled { opacity: 0.5; }
</style>
