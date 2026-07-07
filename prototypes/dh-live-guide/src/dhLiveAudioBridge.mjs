export function createDhLiveAudioBridge({
  module,
  AudioContextClass = window.AudioContext || window.webkitAudioContext,
  AudioElementClass = typeof Audio !== 'undefined' ? Audio : null,
  URLApi = typeof URL !== 'undefined' ? URL : null,
  BlobClass = typeof Blob !== 'undefined' ? Blob : null,
}) {
  const audioContext = new AudioContextClass()
  const gainNode = audioContext.createGain?.()
  if (gainNode) gainNode.connect(audioContext.destination)
  const outputNode = gainNode || audioContext.destination
  const audioElement = AudioElementClass ? new AudioElementClass() : null
  if (audioElement) {
    audioElement.preload = 'auto'
    audioElement.playsInline = true
  }
  let audioMuted = false
  let unlocked = false

  async function unlock() {
    if (unlocked) return
    await unlockHtmlAudio()
    if (audioContext.state === 'suspended' && audioContext.resume) {
      await audioContext.resume()
    }
    try {
      const silent = audioContext.createBuffer?.(1, 1, 16000)
      const source = audioContext.createBufferSource?.()
      if (silent && source) {
        source.buffer = silent
        source.connect(outputNode)
        source.start(0)
      }
    } catch {
      // Some embedded web-view runtimes allow resume but not a synthetic silent buffer.
    }
    unlocked = true
  }

  async function unlockHtmlAudio() {
    if (!audioElement) return
    try {
      const previousMuted = audioElement.muted
      audioElement.muted = true
      audioElement.src = SILENT_WAV_DATA_URL
      const playPromise = audioElement.play?.()
      if (playPromise?.then) await playPromise
      audioElement.pause?.()
      audioElement.muted = audioMuted || previousMuted
    } catch {
      audioElement.muted = audioMuted
    }
  }

  return {
    unlock,

    setMuted(isMuted) {
      audioMuted = isMuted
      if (gainNode) gainNode.gain.value = isMuted ? 0 : 1
      if (audioElement) audioElement.muted = isMuted
    },

    async play(bytes) {
      await unlock()

      const pointer = module._malloc(bytes.byteLength)
      module.HEAPU8.set(bytes, pointer)
      module._setAudioBuffer(pointer, bytes.byteLength)
      module._free(pointer)

      try {
        await playHtmlAudio(bytes)
        return
      } catch {
        await playWebAudio(bytes)
      }
    },
  }

  async function playHtmlAudio(bytes) {
    if (!audioElement || !URLApi?.createObjectURL || !BlobClass) throw new Error('HTML audio unavailable')
    const blobUrl = URLApi.createObjectURL(new BlobClass([bytes], { type: 'audio/wav' }))
    try {
      await new Promise((resolve, reject) => {
        audioElement.onended = resolve
        audioElement.onerror = () => reject(new Error('HTML audio playback failed'))
        audioElement.src = blobUrl
        const playPromise = audioElement.play?.()
        if (playPromise?.catch) playPromise.catch(reject)
      })
    } finally {
      audioElement.onended = null
      audioElement.onerror = null
      URLApi.revokeObjectURL?.(blobUrl)
    }
  }

  async function playWebAudio(bytes) {
    const arrayBuffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength)
    const decoded = await audioContext.decodeAudioData(arrayBuffer)
    await new Promise((resolve) => {
      const source = audioContext.createBufferSource()
      source.buffer = decoded
      source.connect(outputNode)
      source.onended = resolve
      source.start(0)
    })
  }
}

const SILENT_WAV_DATA_URL = 'data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAgD4AAAB9AAACABAAZGF0YQAAAAA='

export async function waitForDhLiveModule(scope = window, timeoutMs = 15000) {
  const started = Date.now()
  while (Date.now() - started < timeoutMs) {
    const module = scope.Module
    if (module?._malloc && module?._setAudioBuffer && module?.HEAPU8) return module
    await new Promise((resolve) => setTimeout(resolve, 80))
  }
  throw new Error('动态人物引擎加载超时')
}
