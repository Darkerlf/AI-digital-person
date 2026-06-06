import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import vm from 'node:vm'
import ts from 'typescript'

const sourcePath = path.resolve('src/utils/mouthSmoothing.ts')
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
const { createMouthSmoothingState, smoothMouthState, mouthVisualProfile } = moduleExports

let state = createMouthSmoothingState('closed', 0)
state = smoothMouthState(state, 'big', 50)
assert.equal(state.mouth, 'closed', 'mouth should not switch before the minimum hold time')

state = smoothMouthState(state, 'big', 80)
assert.equal(state.mouth, 'big', 'mouth should switch after the minimum hold time')

state = smoothMouthState(state, 'round', 160)
assert.equal(state.mouth, 'round', 'important mouth sequence should remain ordered')

state = smoothMouthState(state, 'small', 240)
assert.equal(state.mouth, 'small', 'narrow mouth shape should not be lost after a rounded shape')

assert.equal(JSON.stringify(mouthVisualProfile('big')), JSON.stringify({ scaleX: 1.12, scaleY: 1.28, translateY: 4 }))
assert.equal(JSON.stringify(mouthVisualProfile('round')), JSON.stringify({ scaleX: 0.92, scaleY: 1.12, translateY: 2 }))

console.log('mouth smoothing behavior ok')
