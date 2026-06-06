import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

test('mobile layout keeps the avatar head visible in mini program web-view', () => {
  const css = fs.readFileSync(path.resolve('src/styles.css'), 'utf8')

  assert.match(css, /height:\s*100vh;/, 'mobile layout needs a 100vh fallback for WeChat XWeb')
  assert.match(css, /\.avatar-surface\s*{[\s\S]*height:\s*58vh;/)
  assert.match(css, /#canvas_video,\s*#avatar-idle-frame\s*{[\s\S]*object-fit:\s*contain;/)
  assert.doesNotMatch(css, /background-image:\s*url\("\.\.\/runtime\/assets\/idle-open-cover\.png"\);/)
  assert.doesNotMatch(css, /lingshan-stage-backdrop\.png/, 'stage sides should use a clean pale jade color')
  assert.match(css, /\.avatar-stage\s*{[\s\S]*background-color:\s*#dff4f1;/)
  assert.match(css, /#background_video\s*{[^}]*display:\s*none !important;/)
  assert.match(css, /\.avatar-stage\s*{[\s\S]*min-height:\s*380px;/)
})
