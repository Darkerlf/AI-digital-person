export interface ChatRequest {
  session_id?: number | null
  message: string
  scenic_area_id?: number | null
  visitor_id?: string | null
}

export interface WxLoginRequest {
  code: string
  user_info?: WxUserInfo
}

export interface WxUserInfo {
  nickName?: string
  avatarUrl?: string
}

export interface WxLoginResponse {
  token: string
  visitor_id: number
  nickname: string
  avatar_url: string
}

export interface UpdateProfileRequest {
  nickname?: string
  avatar_url?: string
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
  latitude?: number
  longitude?: number
  location_text?: string
  detail_intro?: string
  highlights?: string
  suggested_duration_minutes?: number
  open_status: string
}

export interface ScenicSpotNarration {
  spot_id: number
  title: string
  mode: 'brief' | 'deep' | 'family'
  narration: string
  source: string
}

export interface ServicePOI {
  id?: number | null
  name: string
  category: string
  area_text?: string | null
  description?: string | null
  open_hours?: string | null
  latitude?: number | null
  longitude?: number | null
}

export interface MapPoint {
  latitude: number
  longitude: number
}

export interface ServiceCategory {
  label: string
  value: string
}

export interface TouristHomeConfig {
  scenic_area_id?: number | null
  scenic_name: string
  welcome_message: string
  quick_questions: string[]
  hot_spots: Array<Partial<ScenicSpot> & { id: number; name: string }>
  service_categories: ServiceCategory[]
  today_route: {
    title: string
    duration_minutes: number
    interest_tags: string[]
    audience_tags: string[]
  }
}

export interface MapGuideSpot {
  id: number
  name: string
  latitude?: number | null
  longitude?: number | null
  coordinate_source?: 'database' | 'tencent_place' | 'tencent_geocoder' | 'manual' | 'preset_gcj02' | 'missing'
  coordinate_verified?: boolean
  sort_order: number
  narration_url: string
  detail_intro?: string | null
}

export interface MapGuideData {
  center: {
    latitude: number
    longitude: number
  }
  fallback_mode: 'map' | 'list'
  spots: MapGuideSpot[]
  service_pois: ServicePOI[]
}

export interface RecentRecord {
  id: number
  visitor_id?: string | null
  channel: string
  status: string
  created_at: string
  messages: Array<{
    id: number
    question_text: string
    answer_text?: string | null
    latency_ms?: number | null
    created_at: string
  }>
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
  start_spot_name?: string | null
  end_spot_name?: string | null
  pace?: string | null
  mobility_tags?: string[]
  service_needs?: string[]
  reroute_from_spot_name?: string | null
}

export interface RouteRecommendResponse {
  matched_template?: {
    id: number
    name: string
    template_type: string
    scenic_area_id: number
    priority: number
  }
  fallback_used?: boolean
  template_name?: string
  summary?: string
  spots: Array<{
    scenic_spot_id?: number | null
    name: string
    stay_minutes?: number | null
    highlight?: string | null
  }>
  match_reason?: string
  sources?: Array<Record<string, unknown>>
}

export interface WalkGuideStop extends MapPoint {
  scenic_spot_id?: number | null
  name: string
}

export interface WalkGuideLeg {
  from_name: string
  to_name: string
  distance_meters: number
  duration_minutes: number
  polyline: MapPoint[]
  provider: string
  fallback_used: boolean
}

export interface WalkGuideRequest {
  scenic_area_id?: number | null
  spots: RouteRecommendResponse['spots']
  start_location?: MapPoint | null
  service_needs?: string[]
}

export interface WalkGuideResponse {
  total_distance_meters: number
  total_duration_minutes: number
  polyline: MapPoint[]
  legs: WalkGuideLeg[]
  stops: WalkGuideStop[]
  service_pois: ServicePOI[]
  fallback_used: boolean
  warnings: string[]
}

export interface FeedbackRequest {
  session_id?: number | null
  message_id?: number | null
  sentiment: 'positive' | 'negative'
  score?: number
  content?: string
  scenic_area_id?: number | null
}

export interface FeedbackResponse {
  id: number
  status: string
}
