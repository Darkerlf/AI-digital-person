import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const mapVue = readFileSync(new URL('../src/pages/map/map.vue', import.meta.url), 'utf8')
const touristApi = readFileSync(new URL('../../backend/app/api/routers/tourist_chat.py', import.meta.url), 'utf8')
const touristService = readFileSync(new URL('../../backend/app/services/tourist_experience_service.py', import.meta.url), 'utf8')

assert.match(mapVue, /targetPoi\s*=\s*ref<ServicePOI \| null>/, 'map page should keep target service POI in state')
assert.match(mapVue, /SERVICE_POI_MARKER_ID/, 'service POI marker id should be isolated from scenic spot ids')
assert.match(mapVue, /targetPoiMarker/, 'map page should create a dedicated service POI marker')
assert.match(mapVue, /targetPoiMarker\.value/, 'map markers should include the selected service POI marker')
assert.match(mapVue, /targetPoiCoords/, 'include-points should prioritize selected service POI coordinates')
assert.match(mapVue, /onShow/, 'tabBar map page should consume service POI target every time it is shown')
assert.match(mapVue, /consumeTargetPoiFromStorage/, 'target POI storage handling should be reusable across mount and show lifecycles')
assert.match(mapVue, /selectedSpot\.value\s*=\s*null/, 'selecting a service POI should clear the previously selected scenic spot')
assert.match(mapVue, /v-if="selectedServiceInfo"/, 'map sheet should show selected service POI details')
assert.match(mapVue, /v-else-if="selectedSpotInfo"/, 'old scenic detail should not remain visible while a service POI is selected')
assert.match(mapVue, /serviceDescriptionText/, 'selected service POI should render its own description instead of stale scenic text')
assert.match(mapVue, /if \(!targetPoi\.value && res\.center\)/, 'scenic center must not overwrite a selected service POI center')

const expectedCoordinates = [
  '31.421872',
  '120.103365',
  '31.42034',
  '120.10355',
  '31.428762',
  '120.102357',
  '31.42349',
  '120.104927',
]

for (const coordinate of expectedCoordinates) {
  assert.match(touristApi, new RegExp(coordinate), `tourist API fallback should include coordinate ${coordinate}`)
  assert.match(touristService, new RegExp(coordinate), `tourist experience fallback should include coordinate ${coordinate}`)
}

console.log('service POI map target checks passed')
