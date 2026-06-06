import { createBackendClient } from './backendClient.mjs'
import { createAvatarPresentation } from './avatarPresentation.mjs?v=idle-cover-1'
import { createDhLiveAudioBridge, waitForDhLiveModule } from './dhLiveAudioBridge.mjs'
import { SpeechPipeline } from './speechPipeline.mjs'
import { createBrowserWavRecorder } from './voiceRecorder.mjs'

const searchParams = new URLSearchParams(location.search)
const configuredApiBase = searchParams.get('api')
const requestedQuestion = searchParams.get('question')
const shouldAutoSubmit = searchParams.get('auto') === '1'
const apiBase = configuredApiBase ? [configuredApiBase] : buildLocalApiBaseUrls()
const client = createBackendClient(apiBase)
const form = document.getElementById('guide-form')
const input = document.getElementById('question')
const send = document.getElementById('send')
const textPromptMode = document.getElementById('text-prompt-mode')
const voicePromptMode = document.getElementById('voice-prompt-mode')
const voiceModeToggle = document.getElementById('voice-mode-toggle')
const textModeToggle = document.getElementById('text-mode-toggle')
const holdToTalk = document.getElementById('hold-to-talk')
const messages = document.getElementById('messages')
const state = document.getElementById('metric-state')
const avatarStatus = document.getElementById('avatar-status')
const latency = document.getElementById('metric-latency')
const quickQuestions = document.querySelectorAll('[data-question]')
const messageTemplate = document.getElementById('assistant-message-template')
const soundButton = document.querySelector('[data-stage-action="sound"]')
const fullscreenButton = document.querySelector('[data-stage-action="fullscreen"]')
const feedbackModal = document.getElementById('feedback-modal')
const feedbackForm = document.getElementById('feedback-form')
const feedbackComment = document.getElementById('feedback-comment')
const feedbackSubmit = document.getElementById('feedback-submit')
const starButtons = document.querySelectorAll('[data-star]')
const toast = document.getElementById('toast')
const presentation = createAvatarPresentation({
  stage: document.getElementById('avatar-stage'),
  dynamicCanvas: document.getElementById('canvas_video'),
  idleCanvas: document.getElementById('avatar-idle-frame'),
  idleImage: document.getElementById('avatar-idle-still'),
})
let bridge
let activeController
let audioMuted = false
let selectedScore = 5
let detailFeedbackCard = null
let toastTimer
let recorder
let voicePressActive = false
let voiceRecordingReady = false
let voiceFinishing = false
let voiceCancelling = false
let voiceStartY = 0
let voiceStartedAt = 0
let asrController

if (requestedQuestion) input.value = requestedQuestion

quickQuestions.forEach((button) => {
  button.addEventListener('click', () => {
    input.value = button.dataset.question || ''
    input.focus()
  })
})

voiceModeToggle.addEventListener('click', switchToVoiceMode)
textModeToggle.addEventListener('click', switchToTextMode)
holdToTalk.addEventListener('pointerdown', beginVoiceCapture)
holdToTalk.addEventListener('pointermove', updateVoiceCancellation)
holdToTalk.addEventListener('pointerup', finishVoiceCapture)
holdToTalk.addEventListener('pointercancel', cancelVoiceCapture)

soundButton.addEventListener('click', () => {
  audioMuted = !audioMuted
  bridge?.setMuted(audioMuted)
  soundButton.classList.toggle('is-muted', audioMuted)
  soundButton.setAttribute('aria-label', audioMuted ? '打开声音' : '关闭声音')
  soundButton.title = audioMuted ? '打开声音' : '关闭声音'
  showToast(audioMuted ? '声音已关闭' : '声音已打开')
})

fullscreenButton.addEventListener('click', async () => {
  try {
    if (document.fullscreenElement) {
      await document.exitFullscreen?.()
    } else {
      await document.querySelector('.stage-first-layout').requestFullscreen?.()
    }
  } catch {
    showToast('当前环境暂不支持全屏')
  }
})

messages.addEventListener('click', async (event) => {
  const button = event.target.closest('button')
  if (!button) return
  const card = button.closest('.message.assistant')
  if (!card?.dataset.messageId) return

  if (button.hasAttribute('data-feedback-detail')) {
    openDetailFeedback(card)
    return
  }

  const sentiment = button.dataset.feedbackSentiment
  if (!sentiment) return
  await submitFeedback(card, { sentiment }, button)
})

document.querySelectorAll('[data-feedback-close]').forEach((button) => {
  button.addEventListener('click', closeDetailFeedback)
})

starButtons.forEach((button) => {
  button.addEventListener('click', () => {
    selectedScore = Number(button.dataset.star)
    renderStars()
  })
})

feedbackForm.addEventListener('submit', async (event) => {
  event.preventDefault()
  if (!detailFeedbackCard) return
  feedbackSubmit.disabled = true
  const sentiment = selectedScore >= 4 ? 'positive' : selectedScore <= 2 ? 'negative' : 'neutral'
  try {
    await submitFeedback(detailFeedbackCard, {
      sentiment,
      score: selectedScore,
      content: feedbackComment.value.trim() || null,
    })
    closeDetailFeedback()
  } finally {
    feedbackSubmit.disabled = false
  }
})

setStatus('加载动态人物')
waitForDhLiveModule()
  .then((module) => {
    bridge = createDhLiveAudioBridge({ module })
    bridge.setMuted(audioMuted)
    captureIdleFrameWhenRendered()
    setStatus('待机')
    if (requestedQuestion && shouldAutoSubmit) window.setTimeout(requestGuideSubmit, 120)
  })
  .catch((error) => setStatus(error.message, true))

form.addEventListener('submit', async (event) => {
  event.preventDefault()
  const question = input.value.trim()
  if (!bridge || !question) return

  activeController?.abort()
  activeController = new AbortController()
  send.disabled = true
  latency.textContent = '--'
  appendUserMessage(question)
  const assistant = appendAssistantMessage()
  const firstTextAt = { value: 0 }
  let answerMeta = null
  let speechFailed = false
  input.value = ''
  const pipeline = new SpeechPipeline({
    synthesize: (text) => client.synthesizeAvatar(text, activeController.signal),
    play: ({ audio }) => bridge.play(audio),
    onSpeakingStart: () => {
      setStatus('讲解中')
      latency.textContent = `${Date.now() - firstTextAt.value} ms`
    },
    onError: () => {
      speechFailed = true
      setStatus('语音生成失败', true)
    },
  })

  try {
    setStatus('思考中')
    for await (const chunk of client.streamAnswer(
      { message: question },
      activeController.signal,
      (meta) => { answerMeta = meta },
    )) {
      if (!firstTextAt.value) firstTextAt.value = Date.now()
      assistant.content.textContent += chunk
      messages.scrollTop = messages.scrollHeight
      pipeline.append(chunk)
    }
    enableFeedback(assistant.card, answerMeta)
    pipeline.complete()
    await pipeline.whenIdle()
    if (!speechFailed) setStatus('待机')
  } catch (error) {
    if (error.name !== 'AbortError') setStatus(error.message || '讲解失败', true)
  } finally {
    send.disabled = false
  }
})

function setStatus(label, failed = false) {
  state.textContent = label
  avatarStatus.textContent = label
  avatarStatus.classList.toggle('failed', failed)
  presentation.setSpeaking(label === '讲解中')
}

function appendUserMessage(text) {
  const node = document.createElement('div')
  node.className = 'message user'
  node.textContent = text
  messages.appendChild(node)
  messages.scrollTop = messages.scrollHeight
}

function appendAssistantMessage() {
  const fragment = messageTemplate.content.cloneNode(true)
  const card = fragment.querySelector('.message.assistant')
  const content = fragment.querySelector('.message-content')
  card.querySelectorAll('.feedback-actions button').forEach((button) => {
    button.disabled = true
  })
  messages.appendChild(fragment)
  messages.scrollTop = messages.scrollHeight
  return { card, content }
}

function enableFeedback(card, meta) {
  if (!meta?.message_id) return
  card.dataset.messageId = String(meta.message_id)
  card.dataset.sessionId = String(meta.session_id)
  card.querySelectorAll('.feedback-actions button').forEach((button) => {
    button.disabled = false
  })
}

async function submitFeedback(card, detail, selectedButton = null) {
  const actions = card.querySelector('.feedback-actions')
  actions.querySelectorAll('button').forEach((button) => {
    button.disabled = true
  })
  try {
    await client.submitFeedback({
      session_id: Number(card.dataset.sessionId),
      message_id: Number(card.dataset.messageId),
      ...detail,
    })
    actions.querySelectorAll('button').forEach((button) => button.classList.remove('is-selected'))
    selectedButton?.classList.add('is-selected')
    actions.dataset.submitted = 'true'
    showToast('感谢您的评价')
  } catch (error) {
    showToast(error.message || '评价提交失败')
  } finally {
    actions.querySelectorAll('button').forEach((button) => {
      button.disabled = false
    })
  }
}

function openDetailFeedback(card) {
  detailFeedbackCard = card
  selectedScore = 5
  feedbackComment.value = ''
  renderStars()
  feedbackModal.hidden = false
}

function closeDetailFeedback() {
  feedbackModal.hidden = true
  detailFeedbackCard = null
}

function renderStars() {
  starButtons.forEach((button) => {
    button.classList.toggle('is-active', Number(button.dataset.star) <= selectedScore)
  })
}

function showToast(message) {
  window.clearTimeout(toastTimer)
  toast.textContent = message
  toast.hidden = false
  toastTimer = window.setTimeout(() => {
    toast.hidden = true
  }, 1800)
}

function switchToVoiceMode() {
  textPromptMode.hidden = true
  voicePromptMode.hidden = false
}

async function switchToTextMode() {
  if (voicePressActive || voiceRecordingReady) {
    voiceCancelling = true
    voicePressActive = false
    await finishVoiceCapture()
  }
  voicePromptMode.hidden = true
  textPromptMode.hidden = false
  input.focus()
}

async function beginVoiceCapture(event) {
  if (voicePressActive || voiceFinishing) return
  event.preventDefault()
  try {
    holdToTalk.setPointerCapture?.(event.pointerId)
  } catch {
    // Synthetic pointer events and a few embedded browsers do not expose an active pointer.
  }
  asrController?.abort()
  recorder = createBrowserWavRecorder()
  voicePressActive = true
  voiceRecordingReady = false
  voiceCancelling = false
  voiceStartY = event.clientY
  voiceStartedAt = Date.now()
  renderVoiceState()
  try {
    await recorder.start()
    voiceRecordingReady = true
    if (!voicePressActive) await finishVoiceCapture()
  } catch (error) {
    resetVoiceCapture()
    showToast(describeMicrophoneError(error))
  }
}

function updateVoiceCancellation(event) {
  if (!voicePressActive) return
  const nextCancelling = voiceStartY - event.clientY > 60
  if (nextCancelling === voiceCancelling) return
  voiceCancelling = nextCancelling
  renderVoiceState()
}

async function cancelVoiceCapture(event) {
  voiceCancelling = true
  await finishVoiceCapture(event)
}

async function finishVoiceCapture(event) {
  event?.preventDefault()
  voicePressActive = false
  if (!voiceRecordingReady || voiceFinishing) return
  voiceFinishing = true
  const duration = Date.now() - voiceStartedAt
  try {
    if (voiceCancelling) {
      await recorder.cancel()
      showToast('已取消录音')
      return
    }
    const audio = await recorder.stop()
    if (!audio || duration < 500 || audio.size <= 44) {
      showToast('说话时间太短')
      return
    }
    holdToTalk.textContent = '正在识别...'
    asrController = new AbortController()
    const text = await client.recognizeAudio(audio, asrController.signal)
    if (!text) {
      showToast('没有听清，请再说一次')
      return
    }
    input.value = text
    await switchToTextMode()
    showToast('识别完成，请确认后输入')
  } catch (error) {
    if (error.name !== 'AbortError') showToast(error.message || '语音识别失败')
  } finally {
    resetVoiceCapture()
  }
}

function renderVoiceState() {
  holdToTalk.classList.toggle('is-recording', voicePressActive && !voiceCancelling)
  holdToTalk.classList.toggle('is-cancelling', voiceCancelling)
  holdToTalk.textContent = voiceCancelling ? '松开取消' : voicePressActive ? '松开结束' : '按住说话'
}

function resetVoiceCapture() {
  voicePressActive = false
  voiceRecordingReady = false
  voiceFinishing = false
  voiceCancelling = false
  recorder = undefined
  renderVoiceState()
}

function describeMicrophoneError(error) {
  if (!window.isSecureContext) return '语音输入需要 HTTPS 或 localhost'
  if (error?.name === 'NotAllowedError') return '请允许使用麦克风后重试'
  if (error?.name === 'NotFoundError') return '未检测到可用麦克风'
  return error?.message || '无法启动录音'
}

function requestGuideSubmit() {
  if (typeof form.requestSubmit === 'function') {
    form.requestSubmit()
    return
  }
  form.dispatchEvent(new Event('submit', { cancelable: true }))
}

function captureIdleFrameWhenRendered(attempt = 0) {
  if (presentation.captureIdleFrame() || attempt >= 40) return
  window.setTimeout(() => captureIdleFrameWhenRendered(attempt + 1), 50)
}

function buildLocalApiBaseUrls() {
  const currentHost = window.location.hostname || 'localhost'
  return unique([
    `http://${currentHost}:8000/api`,
    'http://localhost:8000/api',
    'http://127.0.0.1:8000/api',
    'http://172.22.115.100:8000/api',
  ])
}

function unique(items) {
  return [...new Set(items)]
}
