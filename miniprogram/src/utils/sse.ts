const BASE_URL = 'http://localhost:8000/api'

export interface SSEOptions {
  url: string
  data: Record<string, unknown>
  onMessage: (text: string) => void
  onDone: () => void
  onError: (err: Error) => void
}

export function sseRequest(options: SSEOptions): void {
  const token = uni.getStorageSync('token')
  const header: Record<string, string> = {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
  }
  if (token) {
    header['Authorization'] = `Bearer ${token}`
  }

  uni.request({
    url: `${BASE_URL}${options.url}`,
    method: 'POST',
    data: options.data,
    header,
    timeout: 60000,
    enableChunked: true,
    success: (res) => {
      if (res.statusCode === 200) {
        const text = typeof res.data === 'string' ? res.data : JSON.stringify(res.data)
        const lines = text.split('\n')
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const payload = line.slice(6)
            if (payload === '[DONE]') {
              options.onDone()
              return
            }
            try {
              const parsed = JSON.parse(payload)
              if (parsed.text) {
                options.onMessage(parsed.text)
              }
            } catch {
              // ignore parse errors
            }
          }
        }
        options.onDone()
      } else {
        options.onError(new Error(`HTTP ${res.statusCode}`))
      }
    },
    fail: (err) => {
      options.onError(new Error(err.errMsg || 'request failed'))
    },
  })
}

export function chatWithProgressiveDisplay(
  data: { message: string; session_id?: number | null; scenic_area_id?: number | null },
  onChunk: (text: string) => void,
  onDone: (fullText: string) => void,
  onError: (err: Error) => void,
): void {
  const token = uni.getStorageSync('token')
  const header: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (token) {
    header['Authorization'] = `Bearer ${token}`
  }

  uni.request({
    url: `${BASE_URL}/tourist/chat`,
    method: 'POST',
    data,
    header,
    timeout: 30000,
    success: (res) => {
      if (res.statusCode === 200) {
        const chatRes = res.data as { answer: string; session_id: number; intent: string }
        const answer = chatRes.answer
        let index = 0
        const interval = setInterval(() => {
          if (index < answer.length) {
            const chunkSize = Math.min(3, answer.length - index)
            onChunk(answer.slice(index, index + chunkSize))
            index += chunkSize
          } else {
            clearInterval(interval)
            onDone(answer)
          }
        }, 30)
      } else {
        onError(new Error(`HTTP ${res.statusCode}`))
      }
    },
    fail: (err) => {
      onError(new Error(err.errMsg || 'request failed'))
    },
  })
}
