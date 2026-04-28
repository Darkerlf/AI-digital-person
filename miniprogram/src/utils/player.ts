export interface PlayerOptions {
  onPlay?: () => void
  onStop?: () => void
  onEnded?: () => void
  onError?: (err: string) => void
}

export class TTSPlayer {
  private innerAudioContext: UniApp.InnerAudioContext
  private options: PlayerOptions

  constructor(options: PlayerOptions = {}) {
    this.options = options
    this.innerAudioContext = uni.createInnerAudioContext()
    this.innerAudioContext.onPlay(() => this.options.onPlay?.())
    this.innerAudioContext.onStop(() => this.options.onStop?.())
    this.innerAudioContext.onEnded(() => this.options.onEnded?.())
    this.innerAudioContext.onError((res) => this.options.onError?.(res.errMsg || '播放失败'))
  }

  playFromUrl(url: string): void {
    this.innerAudioContext.src = url
    this.innerAudioContext.play()
  }

  stop(): void {
    this.innerAudioContext.stop()
  }

  destroy(): void {
    this.innerAudioContext.destroy()
  }
}
