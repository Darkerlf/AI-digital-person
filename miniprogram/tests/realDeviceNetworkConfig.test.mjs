import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'

function read(path) {
  return readFileSync(new URL(`../${path}`, import.meta.url), 'utf8')
}

function readIfExists(path) {
  const url = new URL(`../${path}`, import.meta.url)
  return existsSync(url) ? readFileSync(url, 'utf8') : ''
}

const requestTs = read('src/api/request.ts')
const assetsTs = read('src/config/assets.ts')
const touristTs = read('src/api/tourist.ts')
const sseTs = read('src/utils/sse.ts')
const dhLiveBackendClient = read('../prototypes/dh-live-guide/src/backendClient.mjs')
const envFile = readIfExists('.env')
const envLocalFile = readIfExists('.env.local')
const projectConfig = JSON.parse(read('project.config.json'))
const privateProjectConfig = JSON.parse(read('project.private.config.json'))

assert.match(
  requestTs,
  /import\.meta\.env\.VITE_API_BASE_URL/,
  'mini program API base should be configurable without changing source code',
)
assert.match(
  requestTs,
  /http:\/\/127\.0\.0\.1:8000\/api/,
  'WeChat DevTools fallback should use the local backend without depending on the current WLAN address',
)
assert.doesNotMatch(
  requestTs,
  /172\.22\.115\.100/,
  'source code should not retain a stale machine-specific WLAN address',
)
assert.match(
  assetsTs,
  /import\.meta\.env\.VITE_DH_LIVE_GUIDE_URL/,
  'dynamic guide URL should be configurable for real-device HTTPS deployment',
)
assert.match(
  assetsTs,
  /http:\/\/localhost:58120\/runtime\/index\.html/,
  'WeChat DevTools should keep a localhost DH_live fallback',
)
assert.doesNotMatch(
  requestTs,
  /bypass-tunnel-reminder/,
  'mini program requests should not carry localtunnel-only headers in the local development default',
)
assert.doesNotMatch(
  touristTs,
  /TUNNEL_BYPASS_HEADERS/,
  'mini program uploadFile should not depend on localtunnel-only headers',
)
assert.doesNotMatch(
  sseTs,
  /TUNNEL_BYPASS_HEADERS/,
  'mini program chat and SSE requests should not depend on localtunnel-only headers',
)
assert.doesNotMatch(
  dhLiveBackendClient,
  /bypass-tunnel-reminder/,
  'DH_live H5 fetch requests should not depend on localtunnel-only headers',
)
assert.doesNotMatch(
  `${envFile}\n${envLocalFile}`,
  /\.loca\.lt/,
  'local environment files should not point to temporary localtunnel domains by default',
)
assert.match(
  `${envFile}\n${envLocalFile}`,
  /VITE_API_BASE_URL=http:\/\/127\.0\.0\.1:8000\/api/,
  'local environment should point mini program API calls at the local backend',
)
assert.equal(
  privateProjectConfig.setting.urlCheck,
  false,
  'local real-device debugging should disable domain validation in WeChat DevTools',
)
assert.equal(
  projectConfig.miniprogramRoot,
  'dist/build/mp-weixin/',
  'WeChat DevTools should import the built mini program package so generated utils such as routeMap.js are included',
)

console.log('real-device network config checks passed')
