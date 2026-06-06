import test from 'node:test'
import assert from 'node:assert/strict'
import { extractPhrase, flushPhrase } from '../src/phraseChunker.mjs'

test('waits for a useful first phrase instead of speaking a greeting alone', () => {
  assert.equal(extractPhrase('您好。', true), null)
})

test('releases a short natural first narration phrase quickly', () => {
  const result = extractPhrase('您好。现在请随我向前看，灵山大佛庄严矗立。后续仍在生成', true)
  assert.deepEqual(result, {
    phrase: '您好。现在请随我向前看，灵山大佛庄严矗立。',
    rest: '后续仍在生成',
  })
})

test('releases an informative first clause at an early hard break', () => {
  const result = extractPhrase('灵山胜境成人票为210元；半价票为105元，适用于6-18周岁未成年人、', true)
  assert.deepEqual(result, {
    phrase: '灵山胜境成人票为210元；',
    rest: '半价票为105元，适用于6-18周岁未成年人、',
  })
})

test('flushes the final remaining answer', () => {
  assert.deepEqual(flushPhrase('最后我们前往九龙灌浴。'), {
    phrase: '最后我们前往九龙灌浴。',
    rest: '',
  })
})
