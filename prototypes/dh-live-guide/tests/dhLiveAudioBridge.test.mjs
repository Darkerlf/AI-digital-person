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

test('plays wav through an HTML audio element before falling back to Web Audio', async () => {
  const events = []
  const module = {
    HEAPU8: { set() {} },
    _malloc() { return 32 },
    _setAudioBuffer() {},
    _free() {},
  }
  class FakeAudioContext {
    decodeAudioData() {
      events.push('web-audio-decode')
      return Promise.resolve({ decoded: true })
    }
    createBufferSource() {
      return {
        connect() {},
        start() { queueMicrotask(() => this.onended()) },
      }
    }
    get destination() { return {} }
  }
  class FakeAudioElement {
    set src(value) {
      events.push(`src:${value}`)
    }
    play() {
      events.push('html-audio-play')
      queueMicrotask(() => {
        if (typeof this.onended === 'function') this.onended()
      })
      return Promise.resolve()
    }
  }
  const fakeUrl = {
    createObjectURL() {
      events.push('create-object-url')
      return 'blob:audio'
    },
    revokeObjectURL(url) {
      events.push(`revoke:${url}`)
    },
  }

  const bridge = createDhLiveAudioBridge({
    module,
    AudioContextClass: FakeAudioContext,
    AudioElementClass: FakeAudioElement,
    URLApi: fakeUrl,
    BlobClass: Blob,
  })
  await bridge.play(new Uint8Array([82, 73, 70, 70]))

  assert.equal(events.includes('html-audio-play'), true)
  assert.equal(events.includes('web-audio-decode'), false)
  assert.equal(events.includes('revoke:blob:audio'), true)
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

test('unlocks browser audio output from a user gesture before async TTS playback', async () => {
  const events = []
  const module = {
    HEAPU8: { set() {} },
    _malloc() { return 32 },
    _setAudioBuffer() {},
    _free() {},
  }
  class FakeAudioContext {
    constructor() {
      this.state = 'suspended'
    }
    resume() {
      events.push('resume')
      this.state = 'running'
      return Promise.resolve()
    }
    createGain() {
      return { gain: { value: 1 }, connect() {} }
    }
    createBuffer() {
      events.push('create-silent-buffer')
      return { silent: true }
    }
    createBufferSource() {
      return {
        connect() { events.push('connect-silent-source') },
        start() { events.push('start-silent-source') },
      }
    }
    get destination() { return {} }
  }
  class FakeAudioElement {
    set src(value) {
      events.push(value.startsWith('data:audio/wav') ? 'set-silent-html-audio' : `src:${value}`)
    }
    play() {
      events.push('play-silent-html-audio')
      return Promise.resolve()
    }
    pause() {
      events.push('pause-silent-html-audio')
    }
  }

  const bridge = createDhLiveAudioBridge({
    module,
    AudioContextClass: FakeAudioContext,
    AudioElementClass: FakeAudioElement,
  })
  await bridge.unlock()

  assert.deepEqual(events, [
    'set-silent-html-audio',
    'play-silent-html-audio',
    'pause-silent-html-audio',
    'resume',
    'create-silent-buffer',
    'connect-silent-source',
    'start-silent-source',
  ])
})
