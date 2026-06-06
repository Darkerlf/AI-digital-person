export interface StreamingTtsChunk {
  chunk: string
  rest: string
}

const HARD_BREAK_RE = /[。！？!?；;]/
const SOFT_BREAK_RE = /[，、,：:]/

interface ChunkLimits {
  minPhrase: number
  softLimit: number
  hardLimit: number
}

function limitsFor(isFirst: boolean): ChunkLimits {
  return isFirst
    ? { minPhrase: 18, softLimit: 24, hardLimit: 38 }
    : { minPhrase: 36, softLimit: 72, hardLimit: 104 }
}

export function extractStreamingTtsChunk(text: string, isFirst: boolean, force: boolean): StreamingTtsChunk | null {
  const source = text.trimStart()
  if (!source) return null

  const limits = limitsFor(isFirst)
  const naturalBreak = findNaturalTtsBreak(source, limits)
  if (naturalBreak > -1) {
    return {
      chunk: source.slice(0, naturalBreak + 1).trim(),
      rest: source.slice(naturalBreak + 1),
    }
  }

  if (source.length >= limits.hardLimit) {
    const fallbackBreak = findBackwardBreak(source, limits.minPhrase, limits.hardLimit)
    const end = fallbackBreak > -1 ? fallbackBreak + 1 : limits.hardLimit
    return {
      chunk: source.slice(0, end).trim(),
      rest: source.slice(end),
    }
  }

  if (force) {
    return {
      chunk: source.trim(),
      rest: '',
    }
  }

  return null
}

export function splitTtsText(text: string): string[] {
  let rest = text.replace(/\s+/g, ' ').trim()
  if (!rest) return []

  const chunks: string[] = []
  while (rest) {
    const extracted = extractStreamingTtsChunk(rest, chunks.length === 0, false)
    if (!extracted) break
    chunks.push(extracted.chunk)
    rest = extracted.rest.trimStart()
  }

  if (rest) {
    if (chunks.length > 0 && rest.length < 18) {
      chunks[chunks.length - 1] += rest
    } else {
      chunks.push(rest)
    }
  }

  return chunks
}

function findNaturalTtsBreak(text: string, limits: ChunkLimits): number {
  let softCandidate = -1
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index]
    if (SOFT_BREAK_RE.test(char) && index >= limits.minPhrase) {
      softCandidate = index
      if (index >= limits.softLimit) return index
    }
    if (HARD_BREAK_RE.test(char) && index >= limits.minPhrase) {
      return index
    }
    if (index >= limits.hardLimit && softCandidate > -1) {
      return softCandidate
    }
  }
  return -1
}

function findBackwardBreak(text: string, minLength: number, hardLimit: number): number {
  const end = Math.min(hardLimit, text.length - 1)
  for (let index = end; index >= minLength; index -= 1) {
    if (HARD_BREAK_RE.test(text[index]) || SOFT_BREAK_RE.test(text[index]) || text[index] === ' ') {
      return index
    }
  }
  return -1
}
