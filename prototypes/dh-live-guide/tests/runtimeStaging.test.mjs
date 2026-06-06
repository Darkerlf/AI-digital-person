import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { spawnSync } from 'node:child_process'

test('stages the wasm binary required by the DH_live loader', () => {
  const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'dh-live-stage-'))
  const source = path.join(scratch, 'static')
  const output = path.join(scratch, 'runtime')
  const files = [
    'DHLiveMini.wasm',
    'js/DHLiveMini.js',
    'js/MiniMateLoader.js',
    'js/MiniLive2.js',
    'js/pako.min.js',
    'assets/01.mp4',
    'assets/combined_data.json.gz',
    'assets/idle-open-cover.png',
    'background/bg.mp4',
  ]
  for (const relativePath of files) {
    const target = path.join(source, relativePath)
    fs.mkdirSync(path.dirname(target), { recursive: true })
    fs.writeFileSync(target, relativePath)
  }

  const script = path.resolve('scripts/stage-dh-live-runtime.ps1')
  const result = spawnSync(
    'powershell.exe',
    ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', script, '-SourceStaticDir', source, '-RuntimeDir', output],
    { encoding: 'utf8' },
  )

  assert.equal(result.status, 0, result.stderr || result.stdout)
  assert.equal(fs.readFileSync(path.join(output, 'DHLiveMini.wasm'), 'utf8'), 'DHLiveMini.wasm')
  assert.equal(fs.readFileSync(path.join(output, 'assets/idle-open-cover.png'), 'utf8'), 'assets/idle-open-cover.png')
})
