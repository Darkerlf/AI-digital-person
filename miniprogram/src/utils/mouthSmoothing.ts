export type MouthShape = 'closed' | 'small' | 'mid' | 'big' | 'round'

export interface MouthSmoothingState {
  mouth: MouthShape
  changedAtMs: number
}

export interface MouthVisualProfile {
  scaleX: number
  scaleY: number
  translateY: number
}

const DEFAULT_MIN_HOLD_MS = 75

const VISUAL_PROFILES: Record<MouthShape, MouthVisualProfile> = {
  closed: { scaleX: 0.96, scaleY: 0.86, translateY: 0 },
  small: { scaleX: 0.98, scaleY: 0.96, translateY: 1 },
  mid: { scaleX: 1.04, scaleY: 1.08, translateY: 2 },
  big: { scaleX: 1.12, scaleY: 1.28, translateY: 4 },
  round: { scaleX: 0.92, scaleY: 1.12, translateY: 2 },
}

export function createMouthSmoothingState(mouth: MouthShape = 'closed', nowMs = 0): MouthSmoothingState {
  return {
    mouth,
    changedAtMs: nowMs,
  }
}

export function smoothMouthState(
  state: MouthSmoothingState,
  requestedMouth: MouthShape,
  nowMs: number,
  minHoldMs = DEFAULT_MIN_HOLD_MS,
): MouthSmoothingState {
  if (state.mouth === requestedMouth) {
    return state
  }

  if (nowMs - state.changedAtMs < minHoldMs) {
    return state
  }

  return {
    mouth: requestedMouth,
    changedAtMs: nowMs,
  }
}

export function mouthVisualProfile(mouth: MouthShape): MouthVisualProfile {
  return VISUAL_PROFILES[mouth] || VISUAL_PROFILES.closed
}
