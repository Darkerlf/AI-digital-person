import test from 'node:test'
import assert from 'node:assert/strict'
import { createDhLiveAudioBridge } from '../src/dhLiveAudioBridge.mjs'

test('copies wav bytes into DH_live wasm before audible playback resolves', async () => {
  const written = []
  const module = {
    HEAPU8: { set(bytes, pointer) { written.push({ bytes: [...bytes], pointer }) } },
    _malloc() { return 32 },
    _setAudioBuffer(pointer, length) { written.push({ pointer, length }) },
    _free(pointer) { written.push({ freed: pointer }) },
  }
  class FakeAudioContext {
    decodeAudioData() { return Promise.resolve({ decoded: true }) }
    createBufferSource() {
      return {
        connect() {},
        start() { queueMicrotask(() => this.onended()) },
      }
    }
    get destination() { return {} }
  }

  const bridge = createDhLiveAudioBridge({ module, AudioContextClass: FakeAudioContext })
  await bridge.play(new Uint8Array([82, 73, 70, 70]))

  assert.deepEqual(written[0], { bytes: [82, 73, 70, 70], pointer: 32 })
  assert.deepEqual(written[1], { pointer: 32, length: 4 })
  assert.deepEqual(written[2], { freed: 32 })
})

test('mutes and restores audible playback without stopping DH_live mouth driving', () => {
  const gain = { value: 1 }
  const module = {
    HEAPU8: { set() {} },
    _malloc() { return 32 },
    _setAudioBuffer() {},
    _free() {},
  }
  class FakeAudioContext {
    createGain() {
      return {
        gain,
        connect() {},
      }
    }
    get destination() { return {} }
  }

  const bridge = createDhLiveAudioBridge({ module, AudioContextClass: FakeAudioContext })
  bridge.setMuted(true)
  assert.equal(gain.value, 0)
  bridge.setMuted(false)
  assert.equal(gain.value, 1)
})
