import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import vm from 'node:vm'
import ts from 'typescript'

const sourcePath = path.resolve('src/utils/ttsPlaybackQueue.ts')
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
const { TTSPlaybackQueue } = moduleExports

const queue = new TTSPlaybackQueue()
const first = queue.enqueue('message-1', { audio_url: 'a.mp3', chunk_index: 0, chunk_total: 2 })
assert.equal(first.sync.audio_url, 'a.mp3')

const secondWhileBusy = queue.enqueue('message-1', { audio_url: 'b.mp3', chunk_index: 1, chunk_total: 2 })
assert.equal(secondWhileBusy, null)

const preloadable = queue.peekNextReady()
assert.equal(preloadable.sync.audio_url, 'b.mp3', 'next contiguous segment should be visible for preloading')

const secondAfterEnded = queue.markPlaybackEnded()
assert.equal(secondAfterEnded.sync.audio_url, 'b.mp3')

console.log('tts playback queue preload behavior ok')
