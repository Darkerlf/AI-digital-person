import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

function read(path) {
  return readFileSync(new URL(`../${path}`, import.meta.url), 'utf8')
}

const indexVue = read('src/pages/index/index.vue')

assert.match(
  indexVue,
  /getActiveDigitalHumanConfig/,
  'home page should load the active digital human config',
)
assert.match(
  indexVue,
  /const guideName = ref\('灵灵'\)/,
  'home page should default the guide name to 灵灵',
)
assert.match(
  indexVue,
  /getActiveDigitalHumanConfig\(1\)/,
  'home page should request the active guide config for the scenic area',
)
assert.match(
  indexVue,
  /AI 导游\s*\{\{\s*guideName\s*\}\}/,
  'home page guide intro should visibly show the guide name',
)
assert.doesNotMatch(
  indexVue,
  /你好，我是\{\{\s*guideName\s*\}\}/,
  'home page should not prepend a duplicate self-introduction before configured welcome text',
)
assert.match(
  indexVue,
  /<text class="hero-subtitle">\{\{\s*welcomeMessage\s*\}\}<\/text>/,
  'home page should render the configured welcome message as-is',
)

console.log('home digital human name checks passed')
