import { API_BASE_URL, request } from './request'
import type {
  ChatRequest,
  ChatResponse,
  ScenicSpot,
  ScenicSpotNarration,
  ServicePOI,
  RouteRecommendRequest,
  RouteRecommendResponse,
  WalkGuideRequest,
  WalkGuideResponse,
  TouristHomeConfig,
  MapGuideData,
  RecentRecord,
  WxLoginRequest,
  WxLoginResponse,
  UpdateProfileRequest,
  FeedbackRequest,
  FeedbackResponse,
  DigitalHumanConfig,
} from '../types/api'

export function getTouristHomeConfig(scenicAreaId = 1) {
  return request<TouristHomeConfig>(`/tourist/home?scenic_area_id=${scenicAreaId}`)
}

export function getActiveDigitalHumanConfig(scenicAreaId = 1) {
  return request<DigitalHumanConfig>(`/digital-humans/active?scenic_area_id=${scenicAreaId}`)
}

export function getScenicSpots() {
  return request<{ items: ScenicSpot[] }>('/tourist/scenic-spots')
}

export function getScenicSpot(id: number) {
  return request<ScenicSpot>(`/tourist/scenic-spots/${id}`)
}

export function getScenicSpotNarration(id: number, mode: 'brief' | 'deep' | 'family') {
  return request<ScenicSpotNarration>(`/tourist/scenic-spots/${id}/narration?mode=${mode}`)
}

export function sendChat(data: ChatRequest) {
  return request<ChatResponse>('/tourist/chat', {
    method: 'POST',
    data,
  })
}

export function recommendRoute(data: RouteRecommendRequest) {
  return request<RouteRecommendResponse>('/tourist/routes/recommend', {
    method: 'POST',
    data,
  })
}

export function buildWalkGuide(data: WalkGuideRequest) {
  return request<WalkGuideResponse>('/tourist/routes/walk-guide', {
    method: 'POST',
    data,
  })
}

export function getMapGuideData(scenicAreaId = 1, locationAvailable = true) {
  return request<MapGuideData>(
    `/tourist/map-guide?scenic_area_id=${scenicAreaId}&location_available=${locationAvailable ? 'true' : 'false'}`,
  )
}

export function getServicePois(category?: string) {
  const query = category ? `?category=${encodeURIComponent(category)}` : ''
  return request<{ items: ServicePOI[] }>(`/tourist/service-pois${query}`)
}

export function getRecentRecords() {
  return request<{ items: RecentRecord[] }>('/tourist/recent-records')
}

export function wxLogin(data: WxLoginRequest) {
  return request<WxLoginResponse>('/tourist/wx-login', {
    method: 'POST',
    data,
  })
}

export function getProfile() {
  return request<{ visitor_id: number; nickname: string; avatar_url: string }>('/tourist/profile')
}

export function updateProfile(data: UpdateProfileRequest) {
  return request<{ visitor_id: number; nickname: string; avatar_url: string }>('/tourist/profile', {
    method: 'PUT',
    data,
  })
}

export function uploadAvatar(filePath: string) {
  return new Promise<{ visitor_id: number; nickname: string; avatar_url: string }>((resolve, reject) => {
    const token = uni.getStorageSync('token')
    if (!token) {
      reject(new Error('Unauthorized'))
      return
    }
    uni.uploadFile({
      url: `${API_BASE_URL}/tourist/profile/avatar`,
      filePath,
      name: 'avatar',
      header: {
        Authorization: `Bearer ${token}`,
      },
      success: (res) => {
        if (res.statusCode !== 200) {
          reject(new Error(`Avatar upload failed: ${res.statusCode}`))
          return
        }
        try {
          resolve(JSON.parse(res.data))
        } catch {
          reject(new Error('Avatar upload returned invalid JSON'))
        }
      },
      fail: (err) => reject(new Error(err.errMsg || 'Avatar upload failed')),
    })
  })
}

export function submitFeedback(data: FeedbackRequest) {
  return request<FeedbackResponse>('/tourist/feedback', {
    method: 'POST',
    data,
  })
}
