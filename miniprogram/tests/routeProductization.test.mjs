import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

function read(path) {
  return readFileSync(new URL(`../${path}`, import.meta.url), 'utf8')
}

const pagesJson = read('src/pages.json')
const routeVue = read('src/pages/route/route.vue')
const mapVue = read('src/pages/map/map.vue')
const routeGuideVue = read('src/pages/route-guide/route-guide.vue')
const touristApi = read('src/api/tourist.ts')
const apiTypes = read('src/types/api.ts')

assert.match(routeVue, /mobilityOptions/, 'route page should expose mobility-aware personalization options')
assert.match(routeVue, /serviceNeedOptions/, 'route page should allow service-stop personalization')
assert.match(routeVue, /startSpotName/, 'route page should collect a preferred start point')
assert.match(routeVue, /endSpotName/, 'route page should collect an end preference')
assert.match(routeVue, /getScenicSpots/, 'route page should load scenic spots for endpoint suggestions')
assert.match(routeVue, /startSpotSuggestions/, 'route page should expose start-point suggestions')
assert.match(routeVue, /endSpotSuggestions/, 'route page should expose end-point suggestions')
assert.match(routeVue, /selectStartSpot/, 'route page should allow choosing a suggested start point')
assert.match(routeVue, /selectEndSpot/, 'route page should allow choosing a suggested end point')
assert.match(routeVue, /duration_breakdown/, 'route page should render route duration breakdown')
assert.match(routeVue, /last_route_request/, 'route page should persist the last route request for rerouting')
assert.match(routeVue, /reroute_from_spot_name/, 'route page should prefill reroute context from the map')

assert.match(pagesJson, /pages\/route-guide\/route-guide/, 'mini program should register a dedicated walk-guide page')
assert.match(routeVue, /开始步行导览/, 'route page should start the dedicated walk guide')
assert.match(routeVue, /navigateTo\(\{\s*url: '\/pages\/route-guide\/route-guide'/, 'route page should navigate to route-guide instead of the tab map')
assert.match(touristApi, /buildWalkGuide/, 'tourist API should expose walk guide builder')

assert.match(routeGuideVue, /routePolyline/, 'route-guide page should render real walking polyline')
assert.match(routeGuideVue, /nextStop/, 'route-guide page should track the next route stop')
assert.match(routeGuideVue, /arriveAtNextStop/, 'route-guide page should support marking a stop as arrived')
assert.match(routeGuideVue, /skipNextStop/, 'route-guide page should support skipping a stop')
assert.match(routeGuideVue, /rerouteFromCurrentLocation/, 'route-guide page should support rerouting from current location')
assert.match(routeGuideVue, /offRouteCount/, 'route-guide page should detect repeated off-route positioning')

assert.doesNotMatch(mapVue, /routeMatchedSpots|arriveAtNextStop|skipNextStop|rerouteFromCurrentStop/, 'map page should not own route-guide progress controls')

for (const field of [
  'start_spot_name',
  'end_spot_name',
  'pace',
  'mobility_tags',
  'service_needs',
  'reroute_from_spot_name',
]) {
  assert.match(apiTypes, new RegExp(`${field}\\??:`), `RouteRecommendRequest should include ${field}`)
}

assert.match(apiTypes, /duration_breakdown\??:/, 'RouteRecommendResponse should include duration breakdown')
for (const field of ['total_minutes', 'visit_minutes', 'walking_minutes', 'buffer_minutes']) {
  assert.match(apiTypes, new RegExp(`${field}:\\s*number`), `Duration breakdown should include ${field}`)
  assert.match(
    routeVue,
    new RegExp(`duration_breakdown\\.${field}\\s*}}分钟`),
    `Route page should display ${field} with minutes unit`,
  )
}

for (const typeName of [
  'MapPoint',
  'WalkGuideRequest',
  'WalkGuideResponse',
  'WalkGuideLeg',
  'WalkGuideStop',
]) {
  assert.match(apiTypes, new RegExp(`interface ${typeName}`), `api types should include ${typeName}`)
}

console.log('route productization checks passed')
