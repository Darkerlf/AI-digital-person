import test from 'node:test'
import assert from 'node:assert/strict'
import { createBackendClient } from '../src/backendClient.mjs'

test('reports streamed answer metadata to the guide page', async () => {
  const encoder = new TextEncoder()
  const client = createBackendClient('http://localhost:8000/api', async () => (
    new Response(new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode(
          'data: {"text":"Welcome"}\n\n'
            + 'data: {"text":"\\n__meta__:{\\"session_id\\":7,\\"message_id\\":19,\\"intent\\":\\"scenic_qa\\"}"}\n\n'
            + 'data: [DONE]\n\n',
        ))
        controller.close()
      },
    }))
  ))
  let receivedMeta = null
  const chunks = []

  for await (const chunk of client.streamAnswer({ message: 'hello' }, undefined, (meta) => {
    receivedMeta = meta
  })) {
    chunks.push(chunk)
  }

  assert.deepEqual(chunks, ['Welcome'])
  assert.deepEqual(receivedMeta, { session_id: 7, message_id: 19, intent: 'scenic_qa' })
})

test('submits per-answer feedback to the tourist API', async () => {
  const requests = []
  const client = createBackendClient('http://localhost:8000/api', async (url, options) => {
    requests.push({ url, options })
    return Response.json({ id: 5, status: 'ok' })
  })

  const response = await client.submitFeedback({
    session_id: 7,
    message_id: 19,
    sentiment: 'positive',
  })

  assert.equal(response.status, 'ok')
  assert.equal(requests[0].url, 'http://localhost:8000/api/tourist/feedback')
  assert.deepEqual(JSON.parse(requests[0].options.body), {
    session_id: 7,
    message_id: 19,
    sentiment: 'positive',
  })
})

