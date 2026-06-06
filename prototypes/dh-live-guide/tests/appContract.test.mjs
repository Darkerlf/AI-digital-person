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
