import { API_BASE_URLS } from '../api/request'
import { extractStreamingTtsChunk, splitTtsText } from './ttsChunking'

export interface SSEOptions {
  url: string
  data: Record<string, unknown>
  onMessage: (text: string) => void
  onDone: () => void
  onError: (err: Error) => void
}

export interface ChatMeta {
  session_id: number
  intent: string
}

export type MouthShape = 'closed' | 'small' | 'mid' | 'big' | 'round'

export interface MouthCue {
  start_ms: number
  end_ms: number
  mouth: MouthShape
}

export interface TTSSyncResponse {
  audio_url: string
  duration_ms: number
  mouth_cues: MouthCue[]
  chunk_index?: number
  chunk_total?: number
  skipped?: boolean
}

export function sseRequest(options: SSEOptions): void {
  const token = uni.getStorageSync('token')
  const header: Record<string, string> = {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
  }
  if (token) {
    header.Authorization = `Bearer ${token}`
  }

  postWithFallback({
    path: options.url,
    data: options.data,
    header,
    timeout: 60000,
    success: (res) => {
      const text = typeof res.data === 'string' ? res.data : JSON.stringify(res.data)
      const lines = text.split('\n')
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const payload = line.slice(6)
        if (payload === '[DONE]') {
          options.onDone()
          return
        }
        try {
          const parsed = JSON.parse(payload) as { text?: string }
          if (parsed.text) options.onMessage(parsed.text)
        } catch {
          // Ignore malformed chunks; the non-stream fallback handles normal chat.
        }
      }
      options.onDone()
    },
    fail: options.onError,
  })
}

export function chatWithProgressiveDisplay(
  data: { message: string; session_id?: number | null; scenic_area_id?: number | null; visitor_id?: string },
  onChunk: (text: string) => void,
  onDone: (fullText: string, meta: ChatMeta) => void,
  onError: (err: Error) => void,
  onTtsSync?: (sync: TTSSyncResponse) => void,
): void {
  const token = uni.getStorageSync('token')
  const header: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (token) {
    header.Authorization = `Bearer ${token}`
  }

  if (tryStreamingChat(data, header, onChunk, onDone, onError, onTtsSync)) {
    return
  }

  fallbackChat(data, header, onChunk, onDone, onError, onTtsSync)
}

function fallbackChat(
  data: { message: string; session_id?: number | null; scenic_area_id?: number | null; visitor_id?: string },
  header: Record<string, string>,
  onChunk: (text: string) => void,
  onDone: (fullText: string, meta: ChatMeta) => void,
  onError: (err: Error) => void,
  onTtsSync?: (sync: TTSSyncResponse) => void,
): void {
  postWithFallback({
    path: '/tourist/chat',
    data,
    header,
    timeout: 30000,
    success: (res) => {
      const chatRes = res.data as { answer: string; session_id: number; intent: string }
      const answer = chatRes.answer || ''
      const meta: ChatMeta = { session_id: chatRes.session_id, intent: chatRes.intent }
      if (onTtsSync && answer.length > 0) {
        fetchTtsSyncChunks(answer, onTtsSync)
      }
      let index = 0
      const interval = setInterval(() => {
        if (index < answer.length) {
          const chunkSize = Math.min(3, answer.length - index)
          onChunk(answer.slice(index, index + chunkSize))
          index += chunkSize
          return
        }
        clearInterval(interval)
        onDone(answer, meta)
      }, 30)
    },
    fail: onError,
  })
}

function tryStreamingChat(
  data: { message: string; session_id?: number | null; scenic_area_id?: number | null; visitor_id?: string },
  header: Record<string, string>,
  onChunk: (text: string) => void,
  onDone: (fullText: string, meta: ChatMeta) => void,
  onError: (err: Error) => void,
  onTtsSync?: (sync: TTSSyncResponse) => void,
): boolean {
  // #ifdef H5
  return false
  // #endif
  // #ifndef H5
  const baseUrl = API_BASE_URLS[0]
  let fullText = ''
  let meta: ChatMeta = { session_id: data.session_id || 0, intent: '' }
  let sseBuffer = ''
  let receivedChunk = false
  let done = false
  let ttsBuffer = ''
  let ttsChunkIndex = 0
  const decoder = typeof TextDecoder !== 'undefined' ? new TextDecoder('utf-8') : null

  function finish() {
    if (done) return
    done = true
    flushTtsBuffer(true)
    if (onTtsSync) {
      onTtsSync({
        audio_url: '',
        duration_ms: 0,
        mouth_cues: [],
        chunk_index: ttsChunkIndex,
        chunk_total: ttsChunkIndex,
        skipped: true,
      })
    }
    onDone(fullText, meta)
  }

  function queueTtsChunk(text: string) {
    if (!onTtsSync || !text.trim()) return
    const currentIndex = ttsChunkIndex
    ttsChunkIndex += 1
    fetchTtsSync(
      text,
      (sync) => {
        onTtsSync({
          ...sync,
          chunk_index: currentIndex,
        })
      },
      () => {
        onTtsSync({
          audio_url: '',
          duration_ms: 0,
          mouth_cues: [],
          chunk_index: currentIndex,
          skipped: true,
        })
      },
    )
  }

  function flushTtsBuffer(force = false) {
    if (!onTtsSync) return
    while (ttsBuffer.trim()) {
      const extracted = extractStreamingTtsChunk(ttsBuffer, ttsChunkIndex === 0, force)
      if (!extracted) return
      queueTtsChunk(extracted.chunk)
      ttsBuffer = extracted.rest
    }
  }

  function handlePayload(text: string) {
    if (text.startsWith('\n__meta__:') || text.startsWith('__meta__:')) {
      const rawMeta = text.replace(/^\n?__meta__:/, '')
      try {
        meta = JSON.parse(rawMeta) as ChatMeta
      } catch {
        // Keep the existing metadata fallback.
      }
      return
    }
    fullText += text
    ttsBuffer += text
    onChunk(text)
    flushTtsBuffer(false)
  }

  function processSse(raw: string) {
    sseBuffer += raw
    const events = sseBuffer.split('\n\n')
    sseBuffer = events.pop() || ''
    for (const event of events) {
      const line = event.split('\n').find((item) => item.startsWith('data: '))
      if (!line) continue
      const payload = line.slice(6)
      if (payload === '[DONE]') {
        finish()
        return
      }
      try {
        const parsed = JSON.parse(payload) as { text?: string }
        if (parsed.text) handlePayload(parsed.text)
      } catch {
        // Ignore malformed stream frames.
      }
    }
  }

  const requestTask = uni.request({
    url: `${baseUrl}/tourist/chat/stream`,
    method: 'POST',
    data,
    header,
    timeout: 60000,
    enableChunked: true,
    success: () => {
      if (receivedChunk) {
        finish()
        return
      }
      fallbackChat(data, header, onChunk, onDone, onError, onTtsSync)
    },
    fail: (err) => {
      if (receivedChunk) {
        finish()
        return
      }
      onError(new Error(err.errMsg || 'stream request failed'))
    },
  } as UniApp.RequestOptions & { enableChunked: boolean })

  const task = requestTask as UniApp.RequestTask & {
    onChunkReceived?: (callback: (res: { data: ArrayBuffer }) => void) => void
  }
  if (!task.onChunkReceived) {
    task.abort()
    fallbackChat(data, header, onChunk, onDone, onError, onTtsSync)
    return true
  }
  task.onChunkReceived((res) => {
    receivedChunk = true
    const raw = decoder
      ? decoder.decode(res.data, { stream: true })
      : String.fromCharCode(...new Uint8Array(res.data))
    processSse(raw)
  })
  return true
  // #endif
}

export function fetchTtsSync(
  text: string,
  onSuccess: (sync: TTSSyncResponse) => void,
  onFailure?: () => void,
): void {
  const token = uni.getStorageSync('token')
  const header: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (token) {
    header.Authorization = `Bearer ${token}`
  }

  postWithFallback({
    path: '/tourist/voice/tts-sync',
    data: { text },
    header,
    timeout: 45000,
    success: (res) => {
      if (res.data) {
        onSuccess(res.data as TTSSyncResponse)
      }
    },
    fail: () => {
      // TTS failure is non-critical; text is already displayed.
      onFailure?.()
    },
  })
}

export function fetchTtsSyncChunks(text: string, onSuccess: (sync: TTSSyncResponse) => void): void {
  const chunks = splitTtsText(text)
  const results: Array<TTSSyncResponse | null | undefined> = new Array(chunks.length)
  let nextToRequest = 0
  let nextToEmit = 0
  let activeRequests = 0
  const concurrency = Math.min(3, Math.max(1, chunks.length))

  function flushReady() {
    while (nextToEmit < results.length && results[nextToEmit] !== undefined) {
      const result = results[nextToEmit]
      if (result) {
        onSuccess({
          ...result,
          chunk_index: nextToEmit,
          chunk_total: chunks.length,
        })
      } else {
        onSuccess({
          audio_url: '',
          duration_ms: 0,
          mouth_cues: [],
          chunk_index: nextToEmit,
          chunk_total: chunks.length,
          skipped: true,
        })
      }
      nextToEmit += 1
    }
  }

  function pump() {
    while (activeRequests < concurrency && nextToRequest < chunks.length) {
      const currentIndex = nextToRequest
      const chunk = chunks[currentIndex]
      nextToRequest += 1
      activeRequests += 1
      fetchTtsSync(
        chunk,
        (sync) => {
          results[currentIndex] = sync
          activeRequests -= 1
          flushReady()
          pump()
        },
        () => {
          results[currentIndex] = null
          activeRequests -= 1
          flushReady()
          pump()
        },
      )
    }
  }

  pump()
}

interface FallbackPostOptions {
  path: string
  data: Record<string, unknown>
  header: Record<string, string>
  timeout: number
  success: (res: UniApp.RequestSuccessCallbackResult) => void
  fail: (err: Error) => void
}

function postWithFallback(options: FallbackPostOptions): void {
  function tryPost(baseIndex: number) {
    const baseUrl = API_BASE_URLS[baseIndex]
    uni.request({
      url: `${baseUrl}${options.path}`,
      method: 'POST',
      data: options.data,
      header: options.header,
      timeout: options.timeout,
      success: (res) => {
        if (res.statusCode === 200) {
          options.success(res)
          return
        }
        if (baseIndex + 1 < API_BASE_URLS.length) {
          tryPost(baseIndex + 1)
          return
        }
        options.fail(new Error(`HTTP ${res.statusCode}`))
      },
      fail: (err) => {
        if (baseIndex + 1 < API_BASE_URLS.length) {
          tryPost(baseIndex + 1)
          return
        }
        options.fail(new Error(err.errMsg || 'request failed'))
      },
    })
  }

  tryPost(0)
}
