import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import vm from 'node:vm'
import ts from 'typescript'

const sourcePath = path.resolve('src/utils/ttsChunking.ts')
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
const { splitTtsText, extractStreamingTtsChunk } = moduleExports

const guideText = '您好。接下来，我带您从灵山大照壁出发，先看五明桥和胜境门，再前往九龙灌浴观看动态表演。随后我们会走到灵山大佛脚下，感受佛教文化和太湖山水。'
const chunks = splitTtsText(guideText)

assert.ok(chunks[0].length >= 18, `first chunk should not be an isolated short sentence: ${chunks[0]}`)
assert.ok(chunks[0].length <= 38, `first chunk should stay quick to synthesize: ${chunks[0]}`)
assert.ok(chunks.length <= 3, `guide explanation should use fewer merged chunks: ${chunks.join('|')}`)
assert.equal(chunks.join(''), guideText, 'chunking must preserve the original text')

const firstStreamingChunk = extractStreamingTtsChunk(
  '您好。接下来，我带您从灵山大照壁出发，先看五明桥。后续内容还在生成',
  true,
  false,
)

assert.ok(firstStreamingChunk, 'streaming chunk should be ready once a natural first phrase exists')
assert.equal(
  firstStreamingChunk.chunk,
  '您好。接下来，我带您从灵山大照壁出发，先看五明桥。',
)
assert.equal(firstStreamingChunk.rest, '后续内容还在生成')

assert.equal(
  extractStreamingTtsChunk('好的。', true, false),
  null,
  'very short first sentence should wait for more text instead of creating a tiny audio file',
)

console.log('tts chunking behavior ok')
