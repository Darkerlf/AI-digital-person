import type { MapGuideSpot, RouteRecommendResponse } from '../types/api'

export type RouteStop = RouteRecommendResponse['spots'][number]

export interface MapPoint {
  latitude: number
  longitude: number
}

export type RouteSpotStatus = 'arrived' | 'skipped' | 'next' | 'pending'

export interface RouteMatchedSpot {
  routeIndex: number
  routeName: string
  routeStop: RouteStop
  guideSpot: MapGuideSpot | null
  coords: MapPoint | null
  hasCoords: boolean
  status: RouteSpotStatus
}

export function getGuideSpotCoords(spot: MapGuideSpot | null | undefined): MapPoint | null {
  if (typeof spot?.latitude === 'number' && typeof spot.longitude === 'number') {
    return { latitude: spot.latitude, longitude: spot.longitude }
  }
  return null
}

export function buildRouteMatchedSpots(
  routeStops: RouteStop[] = [],
  guideSpots: MapGuideSpot[] = [],
  progressIndex = 0,
  arrivedGuideSpotIds: number[] = [],
  skippedRouteIndexes: number[] = [],
): RouteMatchedSpot[] {
  return routeStops.map((routeStop, routeIndex) => {
    const guideSpot = findGuideSpot(routeStop, guideSpots)
    const coords = getGuideSpotCoords(guideSpot)
    const arrivedBySpot = guideSpot ? arrivedGuideSpotIds.includes(guideSpot.id) : false
    const skipped = skippedRouteIndexes.includes(routeIndex)
    const status = skipped
      ? 'skipped'
      : arrivedBySpot || routeIndex < progressIndex
        ? 'arrived'
        : routeIndex === progressIndex
          ? 'next'
          : 'pending'

    return {
      routeIndex,
      routeName: routeStop.name,
      routeStop,
      guideSpot,
      coords,
      hasCoords: coords !== null,
      status,
    }
  })
}

export function buildRoutePolylinePoints(routeMatchedSpots: RouteMatchedSpot[]): MapPoint[] {
  return routeMatchedSpots.flatMap((spot) => (spot.coords ? [spot.coords] : []))
}

export function findNextRouteStop(routeMatchedSpots: RouteMatchedSpot[]): RouteMatchedSpot | null {
  return routeMatchedSpots.find((spot) => spot.status === 'next') || null
}

function findGuideSpot(routeStop: RouteStop, guideSpots: MapGuideSpot[]): MapGuideSpot | null {
  if (typeof routeStop.scenic_spot_id === 'number') {
    const byId = guideSpots.find((spot) => spot.id === routeStop.scenic_spot_id)
    if (byId) return byId
  }
  const routeName = normalizeSpotName(routeStop.name)
  return guideSpots.find((spot) => normalizeSpotName(spot.name) === routeName) || null
}

function normalizeSpotName(value: string): string {
  return value.trim().toLowerCase()
}
