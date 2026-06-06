import { extractPhrase, flushPhrase } from './phraseChunker.mjs'

export class SpeechPipeline {
  constructor({ synthesize, play, onSpeakingStart = () => {}, onError = () => {} }) {
    this.synthesize = synthesize
    this.play = play
    this.onSpeakingStart = onSpeakingStart
    this.onError = onError
    this.buffer = ''
    this.requestCount = 0
    this.nextPlayIndex = 0
    this.pending = new Map()
    this.playing = false
    this.first = true
    this.waiters = []
    this.stopped = false
    this.synthesizing = false
  }

  append(text) {
    if (this.stopped) return
    this.buffer += text
    let extracted = extractPhrase(this.buffer, this.first)

    while (extracted) {
      this.queue(extracted.phrase)
      this.buffer = extracted.rest
      this.first = false
      extracted = extractPhrase(this.buffer, false)
    }
  }

  complete() {
    if (this.stopped) return this.finishIfIdle()
    const remaining = flushPhrase(this.buffer)
    if (remaining) this.queue(remaining.phrase)
    this.buffer = ''
    this.finishIfIdle()
  }

  queue(text) {
    if (this.stopped) return
    const index = this.requestCount++
    const state = { text, audio: null, ready: false, requested: false }
    this.pending.set(index, state)
    this.pumpSynthesis()
  }

  pumpSynthesis() {
    if (this.stopped || this.synthesizing) return
    const state = [...this.pending.values()].find((candidate) => !candidate.requested)
    if (!state) return

    state.requested = true
    this.synthesizing = true
    Promise.resolve(this.synthesize(state.text))
      .then((audio) => {
        if (this.stopped) return
        state.audio = audio
        state.ready = true
        this.synthesizing = false
        return this.drain()
      })
      .catch((error) => this.fail(error))
  }

  async drain() {
    if (this.stopped) return this.finishIfIdle()
    if (this.playing) return
    const state = this.pending.get(this.nextPlayIndex)
    if (!state || !state.ready) return this.finishIfIdle()

    this.playing = true
    if (this.nextPlayIndex === 0) this.onSpeakingStart()
    this.pumpSynthesis()
    try {
      await this.play({ text: state.text, audio: state.audio })
    } finally {
      this.pending.delete(this.nextPlayIndex++)
      this.playing = false
      await this.drain()
    }
  }

  fail(error) {
    this.stopped = true
    this.buffer = ''
    this.pending.clear()
    this.onError(error)
    this.finishIfIdle()
  }

  whenIdle() {
    if (!this.playing && this.pending.size === 0) return Promise.resolve()
    return new Promise((resolve) => this.waiters.push(resolve))
  }

  finishIfIdle() {
    if (this.playing || this.pending.size > 0) return
    this.waiters.splice(0).forEach((resolve) => resolve())
  }
}
