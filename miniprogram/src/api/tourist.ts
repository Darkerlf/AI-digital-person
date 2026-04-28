import { request } from './request'
import type {
  ChatRequest,
  ChatResponse,
  ScenicArea,
  ScenicSpot,
  Session,
  ConversationTurn,
  RouteRecommendRequest,
  RouteRecommendResponse,
} from '../types/api'

export function getScenicAreas() {
  return request<{ items: ScenicArea[] }>('/scenic-areas')
}

export function getScenicSpots() {
  return request<{ items: ScenicSpot[] }>('/scenic-spots')
}

export function getScenicSpot(id: number) {
  return request<ScenicSpot>(`/scenic-spots/${id}`)
}

export function sendChat(data: ChatRequest) {
  return request<ChatResponse>('/tourist/chat', {
    method: 'POST',
    data,
  })
}

export function getSessions() {
  return request<{ items: Session[] }>('/sessions')
}

export function getSessionDetail(id: number) {
  return request<{ session: Session; messages: ConversationTurn[] }>(`/sessions/${id}`)
}

export function recommendRoute(data: RouteRecommendRequest) {
  return request<RouteRecommendResponse>('/route-recommendations/generate', {
    method: 'POST',
    data,
  })
}
