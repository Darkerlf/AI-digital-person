import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

function read(path) {
  return readFileSync(new URL(`../${path}`, import.meta.url), 'utf8')
}

const appVue = read('src/App.vue')
const pagesJson = read('src/pages.json')
const indexVue = read('src/pages/index/index.vue')
const guideVue = read('src/pages/guide/guide.vue')
const avatarVue = read('src/pages/avatar/avatar.vue')
const mapVue = read('src/pages/map/map.vue')
const routeVue = read('src/pages/route/route.vue')
const digitalHumanVue = read('src/components/DigitalHuman.vue')

for (const text of [appVue, pagesJson, indexVue, guideVue, avatarVue, mapVue, routeVue]) {
  assert.equal(/[鐏瀵鏅馃鈥�]/.test(text), false, 'visible Chinese text should not contain mojibake characters')
}

assert.match(appVue, /--guide-primary:/, 'global guide theme primary token should exist')
assert.match(appVue, /--guide-accent:/, 'global guide theme accent token should exist')
assert.match(appVue, /--guide-primary:\s*#238fa3;/, 'global primary color should use the brighter jade-cyan palette')
assert.equal(
  /#0f3f4c/i.test([appVue, pagesJson, indexVue, guideVue, avatarVue, mapVue, routeVue].join('\n')),
  false,
  'large-surface deep ink green should be removed from the mini program UI',
)
assert.match(pagesJson, /路线推荐/, 'route page title should be readable Chinese')
assert.match(pagesJson, /便民服务/, 'service page title should be readable Chinese')

assert.match(indexVue, /hero-portrait/, 'home hero should include the digital human visual asset')
assert.match(indexVue, /进入 AI 导游/, 'home page should expose a clear AI guide CTA')
assert.doesNotMatch(indexVue, /高拟真数字人/, 'home hero should not expose the separate realistic-avatar entry')
assert.doesNotMatch(indexVue, /goToRealisticGuide/, 'home hero should not keep a dead realistic-avatar click handler')
assert.match(indexVue, /#e9fbf7/, 'home page should use a brighter jade mist background')
assert.match(guideVue, /guide-live-shell/, 'AI guide page should use a dynamic guide shell layout')
assert.match(guideVue, /<web-view[\s\S]*:src="url"/, 'AI guide page should directly host the dynamic DH_live guide')
assert.match(guideVue, /dhLiveGuideUrl/, 'AI guide page should use the configured DH_live guide URL')
assert.match(guideVue, /API_BASE_URL/, 'AI guide page should pass its configured backend URL to the hosted DH_live page')
assert.match(guideVue, /api=\$\{encodeURIComponent\(API_BASE_URL\)\}/, 'hosted DH_live page should receive an explicit backend URL')
assert.match(guideVue, /setTimeout\(handleTimeout/, 'AI guide page should stop showing an endless loading card when web-view cannot open')
assert.equal(/DigitalHuman/.test(guideVue), false, 'AI guide page should not render the static layered digital human')
assert.equal(/avatar-safe-zone/.test(guideVue), false, 'AI guide page should remove the old static avatar area')
assert.equal(/avatar-glow/.test(guideVue), false, 'AI guide avatar glow layer should be removed to avoid white ghosting')
assert.match(digitalHumanVue, /showMouthLayer/, 'digital human should gate the mouth overlay')
assert.match(
  digitalHumanVue,
  /v-if="showMouthLayer"/,
  'mouth overlay should not render in idle closed-mouth state',
)
assert.match(mapVue, /map-sheet/, 'map page should use a polished bottom sheet')
assert.match(mapVue, /<scroll-view\s+scroll-y\s+class="detail-desc-scroll"/, 'map spot description should scroll inside a fixed detail area')
assert.doesNotMatch(mapVue, /展开全文|descriptionExpanded|toggleDescription|desc-toggle/, 'map spot description should not use expand/collapse controls')
assert.match(routeVue, /preference-card/, 'route page should use polished preference cards')

console.log('ui polish checks passed')
