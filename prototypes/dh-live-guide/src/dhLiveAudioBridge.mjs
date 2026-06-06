export function createDhLiveAudioBridge({
  module,
  AudioContextClass = window.AudioContext || window.webkitAudioContext,
}) {
  const audioContext = new AudioContextClass()
  const gainNode = audioContext.createGain?.()
  if (gainNode) gainNode.connect(audioContext.destination)
  const outputNode = gainNode || audioContext.destination

  return {
    setMuted(isMuted) {
      if (gainNode) gainNode.gain.value = isMuted ? 0 : 1
    },

    async play(bytes) {
      if (audioContext.state === 'suspended' && audioContext.resume) {
        await audioContext.resume()
      }

      const pointer = module._malloc(bytes.byteLength)
      module.HEAPU8.set(bytes, pointer)
      module._setAudioBuffer(pointer, bytes.byteLength)
      module._free(pointer)

      const arrayBuffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength)
      const decoded = await audioContext.decodeAudioData(arrayBuffer)
      await new Promise((resolve) => {
        const source = audioContext.createBufferSource()
        source.buffer = decoded
        source.connect(outputNode)
        source.onended = resolve
        source.start(0)
      })
    },
  }
}

export async function waitForDhLiveModule(scope = window, timeoutMs = 15000) {
  const started = Date.now()
  while (Date.now() - started < timeoutMs) {
    const module = scope.Module
    if (module?._malloc && module?._setAudioBuffer && module?.HEAPU8) return module
    await new Promise((resolve) => setTimeout(resolve, 80))
  }
  throw new Error('动态人物引擎加载超时')
}
