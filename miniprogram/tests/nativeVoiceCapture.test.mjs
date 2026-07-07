import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

function read(path) {
  return readFileSync(new URL(`../${path}`, import.meta.url), 'utf8')
}

const pagesJson = read('src/pages.json')
const page = read('src/pages/voice-capture/voice-capture.vue')

assert.match(
  pagesJson,
  /pages\/voice-capture\/voice-capture/,
  'mini program should register a native voice capture fallback page',
)
assert.match(page, /uni\.getRecorderManager\(\)/, 'native voice fallback should use the mini program recorder manager')
assert.match(page, /uni\.uploadFile/, 'native voice fallback should upload recorded audio for ASR')
assert.match(page, /\/tourist\/voice\/asr/, 'native voice fallback should call the tourist ASR endpoint')
assert.match(page, /Authorization: `Bearer \$\{token\}`/, 'native voice fallback should forward visitor auth')
assert.match(page, /uni\.setStorageSync\('pending_question', text\)/, 'recognized text should be handed back to DH_live')
assert.match(page, /uni\.switchTab\(\{\s*url: '\/pages\/guide\/guide'/, 'native voice fallback should return to the DH_live guide tab')

console.log('native voice capture fallback checks passed')
