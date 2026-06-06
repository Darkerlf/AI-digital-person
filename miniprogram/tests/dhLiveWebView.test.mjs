import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import vm from 'node:vm'
import ts from 'typescript'

const sourcePath = path.resolve('src/utils/dhLiveWebView.js')
const source = fs.readFileSync(sourcePath, 'utf8')
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    allowJs: true,
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2020,
  },
}).outputText
const guideVue = fs.readFileSync(path.resolve('src/pages/guide/guide.vue'), 'utf8')
const avatarVue = fs.readFileSync(path.resolve('src/pages/avatar/avatar.vue'), 'utf8')

const sandbox = { exports: {}, module: { exports: {} } }
vm.runInNewContext(compiled, sandbox, { filename: sourcePath })
const moduleExports = { ...sandbox.exports, ...sandbox.module.exports }
const { isSafeDhLiveWebViewUrl, webViewBlockedReason } = moduleExports

assert.match(guideVue, /\.\.\/\.\.\/utils\/dhLiveWebView\.js/, 'guide page should import the JS module emitted for WeChat runtime')
assert.match(avatarVue, /\.\.\/\.\.\/utils\/dhLiveWebView\.js/, 'avatar page should import the JS module emitted for WeChat runtime')
assert.equal(
  isSafeDhLiveWebViewUrl('https://guide.example.com/runtime/index.html', 'ios'),
  true,
  'real devices should allow HTTPS business-domain web-view URLs',
)
assert.equal(
  isSafeDhLiveWebViewUrl('http://localhost:58120/runtime/index.html', 'devtools'),
  true,
  'WeChat DevTools should keep local DH_live runtime debugging available',
)
assert.equal(
  isSafeDhLiveWebViewUrl('http://localhost:58120/runtime/index.html', 'windows'),
  false,
  'PC WeChat real runtime must not try to open localhost web-view URLs',
)
assert.equal(
  isSafeDhLiveWebViewUrl('http://192.168.1.20:58120/runtime/index.html', 'android'),
  false,
  'real-device web-view should not use plain HTTP LAN URLs',
)
assert.match(
  webViewBlockedReason('http://localhost:58120/runtime/index.html', 'windows'),
  /HTTPS/,
  'blocked local URLs should tell operators to configure HTTPS',
)

console.log('DH live web-view URL checks passed')
