import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

test('uses the stage-first A layout for the dynamic guide page', () => {
  const html = fs.readFileSync(path.resolve('shell/index.html'), 'utf8')
  const css = fs.readFileSync(path.resolve('src/styles.css'), 'utf8')

  assert.match(html, /class="guide-layout stage-first-layout"/)
  assert.doesNotMatch(html, /class="stage-topbar"/, 'mini program already has a navigation bar')
  assert.doesNotMatch(
    html,
    /<div class="panel-heading">\s*<p class="eyebrow">/,
    'guide panel should not show the synchronisation eyebrow copy',
  )
  assert.match(html, /data-stage-action="sound"/)
  assert.match(html, /data-stage-action="fullscreen"/)
  assert.match(html, /id="assistant-message-template"/)
  assert.match(html, /class="feedback-actions"/)
  assert.match(html, /id="feedback-modal"/)
  assert.match(html, /class="star-rating"/)
  assert.match(html, /class="[^"]*\bguide-panel\b[^"]*"/)
  assert.match(html, /class="panel-transcript"/)
  assert.match(html, /class="[^"]*\bprompt-card\b[^"]*"/)
  assert.match(html, /id="voice-mode-toggle"/)
  assert.match(html, /id="hold-to-talk"/)
  assert.match(html, /id="text-mode-toggle"/)
  assert.match(html, />输入<\/button>/)

  assert.match(css, /\.stage-first-layout\s*{[\s\S]*position:\s*relative;/)
  assert.doesNotMatch(css, /\.stage-topbar\b/)
  assert.match(css, /\.eyebrow\b/)
  assert.match(css, /@media \(max-width:\s*900px\)\s*{[\s\S]*\.stage-first-layout\s*{[\s\S]*display:\s*block;/)
  assert.match(css, /\.guide-panel\s*{[\s\S]*position:\s*absolute;[\s\S]*bottom:\s*0;/)
  assert.match(css, /@media \(max-width:\s*900px\)\s*{[\s\S]*\.avatar-surface\s*{[\s\S]*height:\s*58vh;/)
  assert.match(css, /\.status-pill\s*{[\s\S]*top:\s*16px;[\s\S]*right:\s*16px;/)
  assert.match(css, /\.feedback-modal\s*{[\s\S]*position:\s*fixed;/)
  assert.match(css, /\.feedback-sheet\s*{[\s\S]*border-radius:\s*24px 24px 0 0;/)
  assert.match(css, /\.hold-to-talk\.is-cancelling/)
})
