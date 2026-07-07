import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

function read(path) {
  return readFileSync(new URL(`../${path}`, import.meta.url), 'utf8')
}

const guideVue = read('src/pages/guide/guide.vue')

assert.match(
  guideVue,
  /uni\.getStorageSync\('token'\)/,
  'AI guide should read the visitor token before opening DH_live',
)
assert.match(
  guideVue,
  /auth=\$\{encodeURIComponent\(token\)\}/,
  'AI guide should pass the encoded visitor token to DH_live',
)

console.log('DH live auth bridge checks passed')
