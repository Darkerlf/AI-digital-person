import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

test('keeps the DOM hooks expected by the upstream DH_live loader', () => {
  const html = fs.readFileSync(path.resolve('shell/index.html'), 'utf8')

  for (const requiredId of [
    'loadingSpinner',
    'background_video',
    'avatar-idle-still',
    'canvas_video',
    'avatar-idle-frame',
    'canvas_gl',
    'canvasEl',
    'screen',
    'screen2',
    'startMessage',
    'characterDropdown',
  ]) {
    assert.match(html, new RegExp(`id="${requiredId}"`), `missing #${requiredId}`)
  }
  assert.match(html, /id="avatar-idle-still" src="assets\/idle-open-cover\.png"/)
})
