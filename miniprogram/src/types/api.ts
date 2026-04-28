export interface ChatRequest {
  session_id?: number | null
  message: string
  scenic_area_id?: number | null
}

export interface ChatResponse {
  session_id: number
  answer: string
  intent: string
  sources: Array<Record<string, unknown>>
}

export interface ScenicSpot {
  id: number
  spot_code: string
  name: string
  alias?: string
  location_text?: string
  detail_intro?: string
  highlights?: string
  suggested_duration_minutes?: number
  open_status: string
}

export interface ScenicArea {
  id: number
  code: string
  name: string
  description?: string
}

export interface Session {
  id: number
  session_key: string
  channel: string
  status: string
}

export interface ConversationTurn {
  id: number
  role: 'user' | 'assistant'
  content: string
  intent?: string
  created_at: string
}

export interface RouteRecommendRequest {
  scenic_area_id: number
  duration_minutes?: number
  interest_tags?: string[]
  audience_tags?: string[]
}

export interface RouteRecommendResponse {
  template_name: string
  summary?: string
  spots: Array<{
    name: string
    stay_minutes: number
    highlight?: string
  }>
  match_reason?: string
}
