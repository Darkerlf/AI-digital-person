import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import vm from 'node:vm'
import ts from 'typescript'

const sourcePath = path.resolve('src/utils/routeGuide.ts')
const source = fs.readFileSync(sourcePath, 'utf8')
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2020,
  },
}).outputText

const sandbox = { exports: {}, module: { exports: {} } }
vm.runInNewContext(compiled, sandbox, { filename: sourcePath })
const moduleExports = { ...sandbox.exports, ...sandbox.module.exports }
const {
  distanceToPolylineMeters,
  isNearScenicArea,
  isOffRoute,
  isValidMapPoint,
  nextPendingStop,
  routeProgressText,
} = moduleExports

const polyline = [
  { latitude: 31.0, longitude: 120.0 },
  { latitude: 31.001, longitude: 120.001 },
]

assert.equal(Math.round(distanceToPolylineMeters({ latitude: 31.0005, longitude: 120.0005 }, polyline)), 0)
assert.equal(isOffRoute({ latitude: 31.01, longitude: 120.01 }, polyline, 80), true)
assert.equal(isOffRoute({ latitude: 31.0005, longitude: 120.0005 }, polyline, 80), false)
assert.equal(isValidMapPoint({ latitude: 31.0, longitude: 120.0 }), true)
assert.equal(isValidMapPoint({ latitude: 31.0, longitude: 999 }), false)
assert.equal(isValidMapPoint({ latitude: Number.NaN, longitude: 120.0 }), false)
assert.equal(isNearScenicArea({ latitude: 31.428076, longitude: 120.098006 }), true)
assert.equal(isNearScenicArea({ latitude: 39.9042, longitude: 116.4074 }), false)

const stops = [
  { name: '灵山大照壁' },
  { name: '九龙灌浴' },
  { name: '灵山大佛' },
]
assert.equal(nextPendingStop(stops, 1)?.name, '九龙灌浴')
assert.equal(routeProgressText(stops, 1), '进度 1/3')

console.log('route guide helper behavior ok')
