export interface PlayerOptions {
  onPlay?: () => void
  onStop?: () => void
  onEnded?: () => void
  onTimeUpdate?: (currentTimeMs: number) => void
  onError?: (err: string) => void
}

export class TTSPlayer {
  private primaryContext: UniApp.InnerAudioContext
  private standbyContext: UniApp.InnerAudioContext
  private activeContext: UniApp.InnerAudioContext
  private options: PlayerOptions
  private timeUpdateTimer: ReturnType<typeof setInterval> | null = null
  private preparedUrl: string | null = null

  constructor(options: PlayerOptions = {}) {
    this.options = options
    this.primaryContext = uni.createInnerAudioContext()
    this.standbyContext = uni.createInnerAudioContext()
    this.activeContext = this.primaryContext
    this.bindContext(this.primaryContext)
    this.bindContext(this.standbyContext)
  }

  playFromUrl(url: string): void {
    const preparedContext = this.getPreparedContext(url)
    if (preparedContext) {
      this.activeContext = preparedContext
      this.preparedUrl = null
      this.activeContext.play()
      return
    }

    this.activeContext.src = url
    this.activeContext.play()
  }

  prepareNext(url: string): void {
    if (!url || this.preparedUrl === url) return
    const standbyContext = this.getStandbyContext()
    standbyContext.src = url
    this.preparedUrl = url
  }

  stop(): void {
    this.primaryContext.stop()
    this.standbyContext.stop()
    this.preparedUrl = null
  }

  destroy(): void {
    this.stopTimeUpdateTimer()
    this.primaryContext.destroy()
    this.standbyContext.destroy()
  }

  private bindContext(context: UniApp.InnerAudioContext): void {
    context.onPlay(() => {
      this.startTimeUpdateTimer()
      this.options.onPlay?.()
    })
    context.onStop(() => {
      this.stopTimeUpdateTimer()
      this.options.onStop?.()
    })
    context.onEnded(() => {
      this.stopTimeUpdateTimer()
      this.options.onEnded?.()
    })
    context.onTimeUpdate(() => {
      this.emitCurrentTime()
    })
    context.onError((res) => {
      this.stopTimeUpdateTimer()
      this.options.onError?.(res.errMsg || '播放失败')
    })
  }

  private emitCurrentTime(): void {
    this.options.onTimeUpdate?.(Math.floor(this.activeContext.currentTime * 1000))
  }

  private getPreparedContext(url: string): UniApp.InnerAudioContext | null {
    if (this.preparedUrl !== url) return null
    return this.getStandbyContext()
  }

  private getStandbyContext(): UniApp.InnerAudioContext {
    return this.activeContext === this.primaryContext ? this.standbyContext : this.primaryContext
  }

  private startTimeUpdateTimer(): void {
    this.stopTimeUpdateTimer()
    this.emitCurrentTime()
    this.timeUpdateTimer = setInterval(() => this.emitCurrentTime(), 60)
  }

  private stopTimeUpdateTimer(): void {
    if (!this.timeUpdateTimer) return
    clearInterval(this.timeUpdateTimer)
    this.timeUpdateTimer = null
  }
}
