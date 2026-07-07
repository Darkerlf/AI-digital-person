import test from 'node:test'
import assert from 'node:assert/strict'
import { createBackendClient } from '../src/backendClient.mjs'

test('parses current tourist SSE frames and requests avatar wav audio', async () => {
  const requests = []
  const encoder = new TextEncoder()
  const client = createBackendClient('http://localhost:8000/api', async (url, options) => {
    requests.push({ url, options })
    if (url.endsWith('/tourist/chat/stream')) {
      return new Response(new ReadableStream({
        start(controller) {
          controller.enqueue(encoder.encode(
            'data: {"text":"欢迎"}\n\n'
              + 'data: {"text":"来到灵山"}\n\n'
              + 'data: {"text":"\\n__meta__:{\\"session_id\\":51,\\"intent\\":\\"scenic_qa\\"}"}\n\n'
              + 'data: [DONE]\n\n',
          ))
          controller.close()
        },
      }))
    }
    return new Response(new Uint8Array([82, 73, 70, 70]), {
      headers: { 'Content-Type': 'audio/wav' },
    })
  })

  const text = []
  for await (const chunk of client.streamAnswer({ message: '介绍灵山大佛' })) text.push(chunk)
  const audio = await client.synthesizeAvatar('欢迎来到灵山')

  assert.deepEqual(text, ['欢迎', '来到灵山'])
  assert.deepEqual([...audio], [82, 73, 70, 70])
  assert.equal(requests[1].url, 'http://localhost:8000/api/tourist/voice/avatar-tts')
})

test('falls back to the next API base when local loopback speech fails', async () => {
  const requests = []
  const client = createBackendClient(
    ['http://localhost:8000/api', 'http://172.27.35.118:8000/api'],
    async (url) => {
      requests.push(url)
      if (url.startsWith('http://localhost:8000')) {
        return new Response('Internal Server Error', { status: 500 })
      }
      return new Response(new Uint8Array([82, 73, 70, 70]), {
        headers: { 'Content-Type': 'audio/wav' },
      })
    },
  )

  const audio = await client.synthesizeAvatar('欢迎来到灵山胜境')

  assert.deepEqual([...audio], [82, 73, 70, 70])
  assert.deepEqual(requests, [
    'http://localhost:8000/api/tourist/voice/avatar-tts',
    'http://172.27.35.118:8000/api/tourist/voice/avatar-tts',
  ])
})

test('uses configured digital human voice for avatar speech', async () => {
  const requests = []
  const client = createBackendClient('http://localhost:8000/api', {
    digitalHumanVoice: 'lingling_voice',
    fetchImpl: async (url, options) => {
      requests.push({ url, options })
      return new Response(new Uint8Array([82, 73, 70, 70]), {
        headers: { 'Content-Type': 'audio/wav' },
      })
    },
  })

  await client.synthesizeAvatar('你好，我是灵灵')

  assert.equal(requests[0].url, 'http://localhost:8000/api/tourist/voice/avatar-tts')
  assert.equal(JSON.parse(requests[0].options.body).voice, 'lingling_voice')
})

test('reports login-required errors for unauthenticated chat stream', async () => {
  const client = createBackendClient('http://localhost:8000/api', async () => {
    return new Response(JSON.stringify({ detail: 'Not authenticated' }), { status: 403 })
  })

  await assert.rejects(
    async () => {
      for await (const _chunk of client.streamAnswer({ message: '你好' })) {
        // drain stream
      }
    },
    /请先登录后再使用 AI 导游/,
  )
})

test('falls back to the next API base when browser fetch throws before a response', async () => {
  const requests = []
  const client = createBackendClient(
    ['http://blocked-localhost:8000/api', 'http://172.27.35.118:8000/api'],
    async (url) => {
      requests.push(url)
      if (url.startsWith('http://blocked-localhost:8000')) {
        throw new TypeError('Failed to fetch')
      }
      return new Response(new Uint8Array([82, 73, 70, 70]), {
        headers: { 'Content-Type': 'audio/wav' },
      })
    },
  )

  const audio = await client.synthesizeAvatar('welcome')

  assert.deepEqual([...audio], [82, 73, 70, 70])
  assert.deepEqual(requests, [
    'http://blocked-localhost:8000/api/tourist/voice/avatar-tts',
    'http://172.27.35.118:8000/api/tourist/voice/avatar-tts',
  ])
})

test('uploads recorded wav audio for speech recognition', async () => {
  const requests = []
  const client = createBackendClient('http://localhost:8000/api', async (url, options) => {
    requests.push({ url, options })
    return Response.json({ text: '灵山大佛在哪里' })
  })

  const text = await client.recognizeAudio(new Blob(['RIFF'], { type: 'audio/wav' }))

  assert.equal(text, '灵山大佛在哪里')
  assert.equal(requests[0].url, 'http://localhost:8000/api/tourist/voice/asr')
  assert.equal(requests[0].options.method, 'POST')
  assert.equal(requests[0].options.body instanceof FormData, true)
  assert.equal(requests[0].options.body.get('audio').name, 'voice.wav')
})

test('sends visitor token to authenticated tourist interaction endpoints', async () => {
  const requests = []
  const client = createBackendClient('http://localhost:8000/api', {
    authToken: 'visitor-token-001',
    fetchImpl: async (url, options) => {
      requests.push({ url, options })
      if (url.endsWith('/tourist/chat/stream')) {
        return new Response(new ReadableStream({
          start(controller) {
            controller.enqueue(new TextEncoder().encode('data: [DONE]\n\n'))
            controller.close()
          },
        }))
      }
      return Response.json({ status: 'ok' })
    },
  })

  for await (const _chunk of client.streamAnswer({ message: '你好' })) {
    // drain stream
  }
  await client.submitFeedback({ session_id: 1, message_id: 2, sentiment: 'positive' })

  assert.equal(requests[0].url, 'http://localhost:8000/api/tourist/chat/stream')
  assert.equal(requests[0].options.headers.Authorization, 'Bearer visitor-token-001')
  assert.equal(requests[1].url, 'http://localhost:8000/api/tourist/feedback')
  assert.equal(requests[1].options.headers.Authorization, 'Bearer visitor-token-001')
})
