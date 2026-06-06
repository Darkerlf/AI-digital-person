import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import vm from 'node:vm'
import ts from 'typescript'

const sourcePath = path.resolve('src/utils/authGuard.ts')
const source = fs.readFileSync(sourcePath, 'utf8')
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2020,
  },
}).outputText

const storage = new Map()
const calls = []
const sandbox = {
  exports: {},
  module: { exports: {} },
  uni: {
    getStorageSync: (key) => storage.get(key) || '',
    showModal: (options) => calls.push(['modal', options]),
    switchTab: (options) => {
      calls.push(['switchTab', options.url])
      options.complete?.()
    },
    addInterceptor: (method, interceptor) => calls.push(['interceptor', method, interceptor]),
  },
  getCurrentPages: () => [{ route: 'pages/index/index' }],
}
vm.runInNewContext(compiled, sandbox, { filename: sourcePath })
const moduleExports = { ...sandbox.exports, ...sandbox.module.exports }

const {
  LOGIN_PAGE_URL,
  canAccessPage,
  guardCurrentPage,
  installAuthNavigationGuards,
  isAuthenticatedFromStorage,
  normalizeRoutePath,
} = moduleExports

assert.equal(LOGIN_PAGE_URL, '/pages/my/my')
assert.equal(normalizeRoutePath('/pages/index/index?id=1'), 'pages/index/index')
assert.equal(normalizeRoutePath('pages/my/my'), 'pages/my/my')
assert.equal(isAuthenticatedFromStorage(), false)
assert.equal(canAccessPage('/pages/my/my'), true)
assert.equal(canAccessPage('/pages/index/index'), true)
assert.equal(canAccessPage('/pages/map/map'), false)

guardCurrentPage()
assert.equal(calls[0][0], 'modal')
assert.equal(calls[0][1].confirmText, '去登陆')
assert.equal(calls.some((call) => call[0] === 'switchTab'), false)
calls[0][1].success({ confirm: true })
assert.deepEqual(calls[1], ['switchTab', '/pages/my/my'])

installAuthNavigationGuards()
const switchTabGuard = calls.find((call) => call[0] === 'interceptor' && call[1] === 'switchTab')[2]
calls.length = 0
assert.equal(switchTabGuard.invoke({ url: '/pages/map/map' }), false)
assert.equal(calls[0][0], 'modal')
assert.equal(calls.some((call) => call[0] === 'switchTab'), false)
assert.equal(switchTabGuard.invoke({ url: '/pages/my/my' }), true)

storage.set('token', 'token-value')
storage.set('visitor_db_id', '12')
assert.equal(isAuthenticatedFromStorage(), true)
assert.equal(canAccessPage('/pages/index/index'), true)
assert.equal(switchTabGuard.invoke({ url: '/pages/map/map' }), true)

console.log('auth guard behavior ok')
