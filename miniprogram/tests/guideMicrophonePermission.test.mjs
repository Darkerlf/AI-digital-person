import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

function read(path) {
  return readFileSync(new URL(`../${path}`, import.meta.url), 'utf8')
}

const manifest = JSON.parse(read('src/manifest.json'))
const guideVue = read('src/pages/guide/guide.vue')

assert.equal(
  manifest['mp-weixin'].permission['scope.record'].desc.length > 0,
  true,
  'AI guide should declare microphone usage for WeChat authorization prompts',
)
assert.match(
  guideVue,
  /scope\.record/,
  'AI guide page should request or check microphone permission before DH_live voice input',
)
assert.match(
  guideVue,
  /openSetting/,
  'AI guide page should offer a settings path after microphone permission is denied',
)

console.log('guide microphone permission checks passed')
