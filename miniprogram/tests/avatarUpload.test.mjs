import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

function read(path) {
  return readFileSync(new URL(`../${path}`, import.meta.url), 'utf8')
}

const touristApi = read('src/api/tourist.ts')
const authStore = read('src/stores/auth.ts')
const myPage = read('src/pages/my/my.vue')

assert.match(touristApi, /export function uploadAvatar\(filePath: string\)/, 'tourist API should expose avatar upload')
assert.match(touristApi, /uni\.uploadFile\(/, 'avatar upload should use the mini-program upload API')
assert.match(touristApi, /\/tourist\/profile\/avatar/, 'avatar upload should call the authenticated backend endpoint')
assert.match(touristApi, /Authorization:\s*`Bearer \$\{token\}`/, 'avatar upload should send the visitor token')
assert.match(authStore, /async function uploadAvatar\(filePath: string\)/, 'auth store should adopt the stable avatar URL')
assert.match(authStore, /function normalizeAvatarUrl\(/, 'auth store should discard expired cached avatar paths')
assert.match(authStore, /wxfile:\\\/\\\/|http:\\\/\\\/tmp\\\/|https:\\\/\\\/tmp\\\/|__tmp__/, 'temporary avatar path patterns should be filtered')
assert.match(myPage, /selectedAvatarPath/, 'profile page should distinguish a selected temporary avatar from the saved URL')
assert.match(myPage, /await authStore\.uploadAvatar\(selectedAvatarPath\.value\)/, 'profile save should upload the selected avatar first')
assert.doesNotMatch(
  myPage,
  /avatar_url:\s*draftAvatarUrl\.value/,
  'profile save must not send a temporary chooseAvatar path to the profile endpoint',
)

console.log('avatar upload contract checks passed')
