import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import vm from 'node:vm'
import ts from 'typescript'

const sourcePath = path.resolve('src/utils/routeMap.ts')
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
const { buildRouteMatchedSpots, buildRoutePolylinePoints, findNextRouteStop } = moduleExports

const guideSpots = [
  { id: 10, name: '灵山大佛', latitude: 31.430266, longitude: 120.096427, sort_order: 1, narration_url: '' },
  { id: 11, name: '灵山梵宫', latitude: 31.428867, longitude: 120.102472, sort_order: 2, narration_url: '' },
  { id: 12, name: '五印坛城', latitude: null, longitude: null, sort_order: 3, narration_url: '' },
]

const routeStops = [
  { scenic_spot_id: 11, name: '梵宫别名' },
  { scenic_spot_id: null, name: '灵山大佛' },
  { scenic_spot_id: 12, name: '五印坛城' },
  { scenic_spot_id: 99, name: '暂未入库点' },
]

const matched = buildRouteMatchedSpots(routeStops, guideSpots, 1, [11])

assert.deepEqual(
  matched.map((spot) => ({
    routeName: spot.routeName,
    guideSpotId: spot.guideSpot?.id ?? null,
    status: spot.status,
    hasCoords: spot.hasCoords,
  })),
  [
    { routeName: '梵宫别名', guideSpotId: 11, status: 'arrived', hasCoords: true },
    { routeName: '灵山大佛', guideSpotId: 10, status: 'next', hasCoords: true },
    { routeName: '五印坛城', guideSpotId: 12, status: 'pending', hasCoords: false },
    { routeName: '暂未入库点', guideSpotId: null, status: 'pending', hasCoords: false },
  ],
)

assert.deepEqual(JSON.parse(JSON.stringify(buildRoutePolylinePoints(matched))), [
  { latitude: 31.428867, longitude: 120.102472 },
  { latitude: 31.430266, longitude: 120.096427 },
])

assert.equal(findNextRouteStop(matched)?.routeName, '灵山大佛')

console.log('route map helper behavior ok')
