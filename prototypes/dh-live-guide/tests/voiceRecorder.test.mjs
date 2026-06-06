import test from 'node:test'
import assert from 'node:assert/strict'
import { encodeMonoWav } from '../src/voiceRecorder.mjs'

test('encodes browser PCM samples as 16 kHz mono 16-bit wav', () => {
  const wav = encodeMonoWav([new Float32Array([0, 0.5, -0.5, 1, -1])], 48000, 16000)
  const view = new DataView(wav)
  const text = (offset, length) => String.fromCharCode(...new Uint8Array(wav, offset, length))

  assert.equal(text(0, 4), 'RIFF')
  assert.equal(text(8, 4), 'WAVE')
  assert.equal(view.getUint16(22, true), 1)
  assert.equal(view.getUint32(24, true), 16000)
  assert.equal(view.getUint16(34, true), 16)
  assert.equal(text(36, 4), 'data')
  assert.ok(view.getUint32(40, true) > 0)
})
