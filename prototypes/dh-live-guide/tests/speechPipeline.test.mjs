import test from 'node:test'
import assert from 'node:assert/strict'
import { SpeechPipeline } from '../src/speechPipeline.mjs'

test('starts the first synthesis alone and prefetches one next phrase during playback', async () => {
  const synthRequests = []
  const resolvers = []
  const played = []
  const playResolvers = []
  const pipeline = new SpeechPipeline({
    synthesize: (text) => new Promise((resolve) => {
      synthRequests.push(text)
      resolvers.push(resolve)
    }),
    play: (segment) => new Promise((resolve) => {
      played.push(segment.text)
      playResolvers.push(resolve)
    }),
  })

  pipeline.append('您好。现在请随我向前看，灵山大佛庄严矗立。')
  pipeline.append('随后我们继续前往九龙灌浴，观看动态演出。')
  pipeline.complete()
  assert.equal(synthRequests.length, 1)

  resolvers[0](new Uint8Array([1]))
  await Promise.resolve()
  await Promise.resolve()
  assert.deepEqual(played, [synthRequests[0]])
  assert.equal(synthRequests.length, 2)

  resolvers[1](new Uint8Array([2]))
  await Promise.resolve()
  assert.deepEqual(played, [synthRequests[0]])

  playResolvers[0]()
  await Promise.resolve()
  await Promise.resolve()
  assert.deepEqual(played, synthRequests)

  playResolvers[1]()
  await pipeline.whenIdle()
  assert.deepEqual(played, synthRequests)
})

test('stops the narration queue when one speech segment fails', async () => {
  const resolvers = []
  const rejectors = []
  const played = []
  const errors = []
  const pipeline = new SpeechPipeline({
    synthesize: () => new Promise((resolve, reject) => {
      resolvers.push(resolve)
      rejectors.push(reject)
    }),
    play: async (segment) => played.push(segment.text),
    onError: (error) => errors.push(error.message),
  })

  pipeline.append('您好。现在请随我向前看，灵山大佛庄严矗立。')
  pipeline.append('随后我们继续前往九龙灌浴，观看动态演出。')
  pipeline.complete()
  rejectors[0](new Error('speech failed'))

  const settled = await Promise.race([
    pipeline.whenIdle().then(() => true),
    new Promise((resolve) => setTimeout(() => resolve(false), 20)),
  ])

  assert.equal(settled, true)
  assert.deepEqual(errors, ['speech failed'])
  assert.deepEqual(played, [])
  assert.equal(resolvers.length, 1)
})
