export interface RecorderOptions {
  onStart?: () => void
  onStop?: (tempFilePath: string) => void
  onError?: (err: string) => void
}

export class VoiceRecorder {
  private recorderManager = uni.getRecorderManager()
  private options: RecorderOptions

  constructor(options: RecorderOptions = {}) {
    this.options = options
    this.recorderManager.onStart(() => {
      this.options.onStart?.()
    })
    this.recorderManager.onStop((res) => {
      this.options.onStop?.(res.tempFilePath)
    })
    this.recorderManager.onError((res) => {
      this.options.onError?.(res.errMsg || '录音失败')
    })
  }

  start(): void {
    this.recorderManager.start({
      format: 'mp3',
      sampleRate: 16000,
      numberOfChannels: 1,
      encodeBitRate: 48000,
      duration: 60000,
    })
  }

  stop(): void {
    this.recorderManager.stop()
  }
}
