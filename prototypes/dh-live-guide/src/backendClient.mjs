export function createBackendClient(baseUrl, options = fetch) {
  const baseUrls = Array.isArray(baseUrl) ? baseUrl : [baseUrl]
  const fetchImpl = typeof options === 'function' ? options : options.fetchImpl || fetch
  const authToken = typeof options === 'function' ? '' : options.authToken || ''
  const digitalHumanVoice = typeof options === 'function' ? 'loongbella_v3' : options.digitalHumanVoice || 'loongbella_v3'

  return {
    async *streamAnswer(payload, signal, onMeta) {
      const response = await postWithFallback(
        baseUrls,
        '/tourist/chat/stream',
        payload,
        signal,
        fetchImpl,
        authToken,
      )
      if (response.status === 401 || response.status === 403) throw new Error('请先登录后再使用 AI 导游')
      if (!response.ok || !response.body) throw new Error('对话服务暂不可用')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { value, done } = await reader.read()
        buffer += decoder.decode(value || new Uint8Array(), { stream: !done })
        const frames = buffer.split('\n\n')
        buffer = frames.pop() || ''

        for (const frame of frames) {
          const data = frame.replace(/^data:\s*/, '').trim()
          if (!data || data === '[DONE]') continue
          const parsed = JSON.parse(data)
          const text = parsed.text || ''
          const normalized = text.trimStart()
          if (normalized.startsWith('__meta__:')) {
            onMeta?.(JSON.parse(normalized.slice('__meta__:'.length)))
            continue
          }
          if (text) yield text
        }

        if (done) return
      }
    },

    async synthesizeAvatar(text, signal) {
      const response = await postWithFallback(
        baseUrls,
        '/tourist/voice/avatar-tts',
        { text, voice: digitalHumanVoice },
        signal,
        fetchImpl,
        authToken,
      )
      if (!response.ok) throw new Error('语音生成失败')
      return new Uint8Array(await response.arrayBuffer())
    },

    async submitFeedback(payload, signal) {
      const response = await postWithFallback(
        baseUrls,
        '/tourist/feedback',
        payload,
        signal,
        fetchImpl,
        authToken,
      )
      if (!response.ok) throw new Error('评价提交失败，请稍后重试')
      return response.json()
    },

    async recognizeAudio(audio, signal) {
      const formData = new FormData()
      formData.append('audio', audio, 'voice.wav')
      const response = await postFormWithFallback(
        baseUrls,
        '/tourist/voice/asr',
        formData,
        signal,
        fetchImpl,
      )
      if (!response.ok) throw new Error('语音识别失败，请稍后重试')
      const result = await response.json()
      return String(result.text || '').trim()
    },
  }
}

async function postWithFallback(baseUrls, path, payload, signal, fetchImpl, authToken = '') {
  let lastResponse = null
  let lastError = null
  const headers = { 'Content-Type': 'application/json' }
  if (authToken) headers.Authorization = `Bearer ${authToken}`
  for (const baseUrl of baseUrls) {
    try {
      const response = await fetchImpl(`${baseUrl}${path}`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
        signal,
      })
      if (response.ok) return response
      lastResponse = response
    } catch (error) {
      lastError = error
      if (error?.name === 'AbortError') throw error
    }
  }
  if (!lastResponse && lastError) throw lastError
  return lastResponse || new Response('', { status: 503 })
}

async function postFormWithFallback(baseUrls, path, formData, signal, fetchImpl) {
  let lastResponse = null
  let lastError = null
  for (const baseUrl of baseUrls) {
    try {
      const response = await fetchImpl(`${baseUrl}${path}`, {
        method: 'POST',
        body: formData,
        signal,
      })
      if (response.ok) return response
      lastResponse = response
    } catch (error) {
      lastError = error
      if (error?.name === 'AbortError') throw error
    }
  }
  if (!lastResponse && lastError) throw lastError
  return lastResponse || new Response('', { status: 503 })
}
