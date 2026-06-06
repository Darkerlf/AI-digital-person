import type { MapPoint, WalkGuideStop } from '../types/api'

const METERS_PER_DEGREE_LAT = 111_320
export const DEFAULT_SCENIC_CENTER: MapPoint = { latitude: 31.428076, longitude: 120.098006 }
export const DEFAULT_SCENIC_RADIUS_METERS = 8000

export function routeProgressText(stops: WalkGuideStop[], progressIndex: number): string {
  const total = stops.length
  const done = Math.min(Math.max(progressIndex, 0), total)
  return `进度 ${done}/${total}`
}

export function nextPendingStop(stops: WalkGuideStop[], progressIndex: number): WalkGuideStop | null {
  return stops[progressIndex] || null
}

export function isOffRoute(point: MapPoint | null, polyline: MapPoint[], thresholdMeters = 80): boolean {
  const validPolyline = polyline.filter(isValidMapPoint)
  if (!isValidMapPoint(point) || validPolyline.length === 0) return false
  return distanceToPolylineMeters(point, validPolyline) > thresholdMeters
}

export function distanceToPolylineMeters(point: MapPoint, polyline: MapPoint[]): number {
  const validPolyline = polyline.filter(isValidMapPoint)
  if (!isValidMapPoint(point) || validPolyline.length === 0) return Number.POSITIVE_INFINITY
  if (validPolyline.length === 1) {
    return distanceMeters(point, validPolyline[0])
  }
  return Math.min(
    ...validPolyline.slice(1).map((end, index) => distanceToSegmentMeters(point, validPolyline[index], end)),
  )
}

export function distanceMeters(start: MapPoint, end: MapPoint): number {
  const earthRadiusMeters = 6_371_000
  const lat1 = toRadians(start.latitude)
  const lat2 = toRadians(end.latitude)
  const dLat = toRadians(end.latitude - start.latitude)
  const dLng = toRadians(end.longitude - start.longitude)
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) * Math.sin(dLng / 2)
  return earthRadiusMeters * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

export function isValidMapPoint(point: MapPoint | null | undefined): point is MapPoint {
  return !!point &&
    Number.isFinite(point.latitude) &&
    Number.isFinite(point.longitude) &&
    point.latitude >= -90 &&
    point.latitude <= 90 &&
    point.longitude >= -180 &&
    point.longitude <= 180
}

export function isNearScenicArea(
  point: MapPoint | null | undefined,
  center: MapPoint = DEFAULT_SCENIC_CENTER,
  radiusMeters = DEFAULT_SCENIC_RADIUS_METERS,
): boolean {
  return isValidMapPoint(point) && isValidMapPoint(center) && distanceMeters(point, center) <= radiusMeters
}

function distanceToSegmentMeters(point: MapPoint, start: MapPoint, end: MapPoint): number {
  const originLat = toRadians(point.latitude)
  const [x1, y1] = project(start, originLat)
  const [x2, y2] = project(end, originLat)
  const [xp, yp] = project(point, originLat)
  const dx = x2 - x1
  const dy = y2 - y1
  if (dx === 0 && dy === 0) return Math.hypot(xp - x1, yp - y1)
  const ratio = Math.max(0, Math.min(1, ((xp - x1) * dx + (yp - y1) * dy) / (dx * dx + dy * dy)))
  return Math.hypot(xp - (x1 + ratio * dx), yp - (y1 + ratio * dy))
}

function project(point: MapPoint, originLat: number): [number, number] {
  return [
    point.longitude * METERS_PER_DEGREE_LAT * Math.cos(originLat),
    point.latitude * METERS_PER_DEGREE_LAT,
  ]
}

function toRadians(value: number): number {
  return (value * Math.PI) / 180
}
