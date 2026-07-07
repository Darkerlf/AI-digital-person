import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'

test('supports mini program question handoff through URL parameters', () => {
  const source = fs.readFileSync(path.resolve('src/app.mjs'), 'utf8')

  assert.match(source, /searchParams\.get\('question'\)/)
  assert.match(source, /searchParams\.get\('auto'\)/)
  assert.match(source, /requestGuideSubmit/)
})

test('uses digital human URL parameters for name welcome text and voice', () => {
  const source = fs.readFileSync(path.resolve('src/app.mjs'), 'utf8')

  assert.match(source, /searchParams\.get\('guide_name'\)/)
  assert.match(source, /searchParams\.get\('welcome_text'\)/)
  assert.match(source, /searchParams\.get\('voice'\)/)
  assert.match(source, /digitalHumanName/)
  assert.match(source, /digitalHumanWelcomeText/)
  assert.match(source, /digitalHumanVoice/)
  assert.match(source, /createBackendClient\(apiBase,[\s\S]*digitalHumanVoice/)
})

test('uses the guide name as assistant speaker badge in chat messages', () => {
  const source = fs.readFileSync(path.resolve('src/app.mjs'), 'utf8')
  const shell = fs.readFileSync(path.resolve('shell/index.html'), 'utf8')
  const runtime = fs.readFileSync(path.resolve('runtime/index.html'), 'utf8')

  assert.match(source, /const digitalHumanBadge = normalizeGuideBadge\(digitalHumanName\)/)
  assert.match(source, /function normalizeGuideBadge/)
  assert.match(source, /querySelectorAll\('\.message-speaker'\)[\s\S]+digitalHumanBadge/)
  assert.match(source, /querySelector\('\.message-speaker'\)[\s\S]+digitalHumanBadge/)
  assert.match(shell, /<span class="message-speaker" aria-hidden="true">灵<\/span>/)
  assert.match(runtime, /<span class="message-speaker" aria-hidden="true">灵<\/span>/)
  assert.doesNotMatch(runtime, /<span class="message-speaker" aria-hidden="true">声<\/span>/)
})

test('runtime page uses the latest guide app script version', () => {
  const runtime = fs.readFileSync(path.resolve('runtime/index.html'), 'utf8')

  assert.match(runtime, /src="\.\.\/src\/app\.mjs\?v=live-guide-12"/)
})

test('unlocks web-view audio on submit before async speech synthesis playback', () => {
  const source = fs.readFileSync(path.resolve('src/app.mjs'), 'utf8')

  assert.match(source, /await bridge\.unlock\?\.\(\)/)
  assert.match(source, /await bridge\.unlock\?\.\(\)[\s\S]+client\.streamAnswer/)
})

test('falls back to native mini program voice capture when web-view microphone is denied', () => {
  const source = fs.readFileSync(path.resolve('src/app.mjs'), 'utf8')

  assert.match(source, /openNativeVoiceCapture/)
  assert.match(source, /wx\?\.miniProgram\?\.navigateTo/)
  assert.match(source, /\/pages\/voice-capture\/voice-capture/)
  assert.match(source, /NotAllowedError[\s\S]+openNativeVoiceCapture/)
})
