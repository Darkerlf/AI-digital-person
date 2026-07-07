import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

function read(path) {
  return readFileSync(new URL(`../${path}`, import.meta.url), 'utf8')
}

const touristApi = read('src/api/tourist.ts')
const apiTypes = read('src/types/api.ts')
const guideVue = read('src/pages/guide/guide.vue')

assert.match(
  apiTypes,
  /export interface DigitalHumanConfig/,
  'mini program should define the active digital human config shape',
)
assert.match(
  touristApi,
  /export function getActiveDigitalHumanConfig/,
  'tourist API should expose a helper for active digital human config',
)
assert.match(
  touristApi,
  /\/digital-humans\/active\?scenic_area_id=\$\{scenicAreaId\}/,
  'active digital human config should be requested by scenic area',
)
assert.match(
  guideVue,
  /getActiveDigitalHumanConfig/,
  'AI guide page should load the active digital human config on startup',
)
assert.match(
  guideVue,
  /guide_name=\$\{encodeURIComponent\(digitalHumanName\.value\)\}/,
  'AI guide page should pass the guide name into DH_live',
)
assert.match(
  guideVue,
  /welcome_text=\$\{encodeURIComponent\(digitalHumanWelcomeText\.value\)\}/,
  'AI guide page should pass the welcome text into DH_live',
)
assert.match(
  guideVue,
  /voice=\$\{encodeURIComponent\(digitalHumanVoice\.value\)\}/,
  'AI guide page should pass the configured TTS voice into DH_live',
)
assert.match(
  guideVue,
  /currentQuestion = pending[\s\S]+currentAutoSubmit = true[\s\S]+resetGuideUrl\(currentQuestion, currentAutoSubmit\)/,
  'AI guide page should preserve pending question handoff while active config is loading',
)
assert.match(
  guideVue,
  /isAuthenticatedFromStorage/,
  'AI guide page should check visitor login before opening DH_live',
)
assert.match(
  guideVue,
  /请先登录后使用 AI 导游/,
  'AI guide page should show a clear login-required fallback when unauthenticated',
)
assert.match(
  guideVue,
  /uni\.switchTab\(\{\s*url: LOGIN_PAGE_URL\s*\}\)/,
  'AI guide page should provide a login action instead of opening DH_live without a token',
)

console.log('active digital human config checks passed')
