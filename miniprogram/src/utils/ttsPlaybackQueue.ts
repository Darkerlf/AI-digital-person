export interface QueuedTTSSync {
  audio_url: string
  skipped?: boolean
  chunk_index?: number
  chunk_total?: number
}

export interface ReadyTTSSegment<T extends QueuedTTSSync> {
  messageId: string
  sync: T
}

export class TTSPlaybackQueue<T extends QueuedTTSSync> {
  private segments: Array<T | null | undefined> = []
  private nextIndex = 0
  private expectedCount = 0
  private activeMessageId: string | null = null
  private playbackBusy = false

  enqueue(messageId: string, sync: T): ReadyTTSSegment<T> | null {
    this.activeMessageId = messageId
    const index = sync.chunk_index ?? this.segments.length
    if (typeof sync.chunk_total === 'number') {
      this.expectedCount = Math.max(this.expectedCount, sync.chunk_total)
    }
    this.segments[index] = sync.skipped ? null : sync
    return this.takeReady()
  }

  markPlaybackEnded(): ReadyTTSSegment<T> | null {
    this.playbackBusy = false
    return this.takeReady()
  }

  peekNextReady(): ReadyTTSSegment<T> | null {
    if (!this.playbackBusy || !this.activeMessageId) return null

    let index = this.nextIndex
    let sync = this.segments[index]
    while (sync === null) {
      index += 1
      sync = this.segments[index]
    }

    if (!sync) return null
    return {
      messageId: this.activeMessageId,
      sync,
    }
  }

  reset(): void {
    this.segments = []
    this.nextIndex = 0
    this.expectedCount = 0
    this.activeMessageId = null
    this.playbackBusy = false
  }

  private takeReady(): ReadyTTSSegment<T> | null {
    if (this.playbackBusy || !this.activeMessageId) return null

    let sync = this.segments[this.nextIndex]
    while (sync === null) {
      this.nextIndex += 1
      sync = this.segments[this.nextIndex]
    }

    if (sync) {
      this.nextIndex += 1
      this.playbackBusy = true
      return {
        messageId: this.activeMessageId,
        sync,
      }
    }

    if (this.expectedCount > 0 && this.nextIndex >= this.expectedCount) {
      this.reset()
    }
    return null
  }
}
