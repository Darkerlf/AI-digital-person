import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

function read(path) {
  return readFileSync(new URL(`../${path}`, import.meta.url), 'utf8')
}

const touristApi = read('src/api/tourist.ts')

assert.doesNotMatch(touristApi, /export function getScenicAreas/, 'mini program tourist API should not expose admin scenic-area endpoints')
assert.doesNotMatch(touristApi, /export function getSessions/, 'mini program tourist API should not expose admin session endpoints')
assert.doesNotMatch(touristApi, /export function getSessionDetail/, 'mini program tourist API should not expose admin session detail endpoints')
assert.doesNotMatch(touristApi, /request<[^>]+>\('\/scenic-areas'/, 'mini program should use tourist-prefixed scenic APIs')
assert.doesNotMatch(touristApi, /request<[^>]+>\('\/sessions/, 'mini program should use tourist-prefixed conversation APIs')

console.log('tourist API boundary checks passed')
