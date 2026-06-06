const DEFAULT_TARGET_SAMPLE_RATE = 16000

export function createBrowserWavRecorder({
  mediaDevices = navigator.mediaDevices,
  AudioContextClass = window.AudioContext || window.webkitAudioContext,
  targetSampleRate = DEFAULT_TARGET_SAMPLE_RATE,
} = {}) {
  let stream
  let context
  let source
  let processor
  let silentGain
  let chunks = []

  async function start() {
    if (!mediaDevices?.getUserMedia || !AudioContextClass) {
      throw new Error('当前浏览器不支持语音输入')
    }
    if (context) throw new Error('录音已经开始')

    stream = await mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    })
    context = new AudioContextClass()
    if (context.state === 'suspended') await context.resume?.()
    source = context.createMediaStreamSource(stream)
    processor = context.createScriptProcessor(4096, 1, 1)
    silentGain = context.createGain()
    silentGain.gain.value = 0
    chunks = []
    processor.onaudioprocess = (event) => {
      chunks.push(new Float32Array(event.inputBuffer.getChannelData(0)))
    }
    source.connect(processor)
    processor.connect(silentGain)
    silentGain.connect(context.destination)
  }

  async function stop() {
    if (!context) return null
    const sampleRate = context.sampleRate
    const wav = encodeMonoWav(chunks, sampleRate, targetSampleRate)
    await cleanup()
    return new Blob([wav], { type: 'audio/wav' })
  }

  async function cancel() {
    await cleanup()
  }

  async function cleanup() {
    processor?.disconnect()
    source?.disconnect()
    silentGain?.disconnect()
    stream?.getTracks().forEach((track) => track.stop())
    await context?.close?.()
    stream = undefined
    context = undefined
    source = undefined
    processor = undefined
    silentGain = undefined
    chunks = []
  }

  return { start, stop, cancel }
}

export function encodeMonoWav(chunks, inputSampleRate, targetSampleRate = DEFAULT_TARGET_SAMPLE_RATE) {
  const samples = mergeSamples(chunks)
  const resampled = resampleLinear(samples, inputSampleRate, targetSampleRate)
  const buffer = new ArrayBuffer(44 + resampled.length * 2)
  const view = new DataView(buffer)

  writeAscii(view, 0, 'RIFF')
  view.setUint32(4, 36 + resampled.length * 2, true)
  writeAscii(view, 8, 'WAVE')
  writeAscii(view, 12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true)
  view.setUint16(22, 1, true)
  view.setUint32(24, targetSampleRate, true)
  view.setUint32(28, targetSampleRate * 2, true)
  view.setUint16(32, 2, true)
  view.setUint16(34, 16, true)
  writeAscii(view, 36, 'data')
  view.setUint32(40, resampled.length * 2, true)

  for (let index = 0; index < resampled.length; index += 1) {
    const sample = Math.max(-1, Math.min(1, resampled[index]))
    view.setInt16(44 + index * 2, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true)
  }
  return buffer
}

function mergeSamples(chunks) {
  const length = chunks.reduce((total, chunk) => total + chunk.length, 0)
  const merged = new Float32Array(length)
  let offset = 0
  for (const chunk of chunks) {
    merged.set(chunk, offset)
    offset += chunk.length
  }
  return merged
}

function resampleLinear(samples, inputRate, outputRate) {
  if (!samples.length || inputRate === outputRate) return samples
  const outputLength = Math.max(1, Math.round(samples.length * outputRate / inputRate))
  const result = new Float32Array(outputLength)
  const ratio = inputRate / outputRate
  for (let index = 0; index < outputLength; index += 1) {
    const sourceIndex = index * ratio
    const left = Math.floor(sourceIndex)
    const right = Math.min(samples.length - 1, left + 1)
    const weight = sourceIndex - left
    result[index] = samples[left] * (1 - weight) + samples[right] * weight
  }
  return result
}

function writeAscii(view, offset, text) {
  for (let index = 0; index < text.length; index += 1) {
    view.setUint8(offset + index, text.charCodeAt(index))
  }
}
