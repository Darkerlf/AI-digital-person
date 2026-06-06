import test from 'node:test'
import assert from 'node:assert/strict'
import { createAvatarPresentation } from '../src/avatarPresentation.mjs'

test('covers the DH_live video frame with the explicit open-eyed idle image', () => {
  const draws = []
  const stage = { dataset: {} }
  const idleImage = { complete: true, naturalWidth: 1086, naturalHeight: 1536 }
  const dynamicCanvas = {
    width: 720,
    height: 1280,
    getContext() {
      throw new Error('must not inspect the speaking video when an idle still is available')
    },
  }
  const idleCanvas = {
    width: 0,
    height: 0,
    getContext() {
      return {
        clearRect() {},
        drawImage(...args) { draws.push(args) },
      }
    },
  }
  const presentation = createAvatarPresentation({ stage, dynamicCanvas, idleCanvas, idleImage })

  assert.equal(presentation.captureIdleFrame(), true)
  assert.equal(idleCanvas.width, 720)
  assert.equal(idleCanvas.height, 1280)
  assert.equal(draws.length, 1)
  assert.equal(draws[0][0], idleImage)
  assert.equal(draws[0].length, 9)
  assert.equal(draws[0][7], 720)
  assert.equal(draws[0][8], 1280)
})

test('holds one captured idle frame and reveals motion only while speaking', () => {
  const drawCalls = []
  const stage = { dataset: {} }
  const dynamicCanvas = {
    width: 360,
    height: 640,
    getContext() {
      return { getImageData() { return { data: new Uint8ClampedArray([100, 120, 150, 255]) } } }
    },
  }
  const idleCanvas = {
    width: 0,
    height: 0,
    getContext() {
      return {
        clearRect() {},
        drawImage(source) { drawCalls.push(source) },
      }
    },
  }
  const presentation = createAvatarPresentation({ stage, dynamicCanvas, idleCanvas })

  assert.equal(presentation.captureIdleFrame(), true)
  assert.equal(idleCanvas.width, 360)
  assert.equal(idleCanvas.height, 640)
  assert.equal(stage.dataset.avatarMode, 'idle')

  presentation.setSpeaking(true)
  assert.equal(stage.dataset.avatarMode, 'speaking')

  assert.equal(presentation.captureIdleFrame(), false)
  presentation.setSpeaking(false)
  assert.equal(stage.dataset.avatarMode, 'idle')
  assert.deepEqual(drawCalls, [dynamicCanvas])
})

test('does not capture an idle frame before the renderer has a visible canvas', () => {
  const stage = { dataset: {} }
  const dynamicCanvas = { width: 0, height: 0 }
  const idleCanvas = {
    getContext() {
      throw new Error('must not draw an empty frame')
    },
  }
  const presentation = createAvatarPresentation({ stage, dynamicCanvas, idleCanvas })

  assert.equal(presentation.captureIdleFrame(), false)
  assert.equal(stage.dataset.avatarMode, 'idle')
})

test('does not capture the browser default canvas before DH_live sizes its video frame', () => {
  const stage = { dataset: {} }
  const dynamicCanvas = { width: 300, height: 150 }
  const idleCanvas = {
    getContext() {
      throw new Error('must wait for the DH_live frame size')
    },
  }
  const presentation = createAvatarPresentation({ stage, dynamicCanvas, idleCanvas })

  assert.equal(presentation.captureIdleFrame(), false)
})

test('waits for an actually rendered avatar frame instead of saving a black idle screen', () => {
  let pixels = new Uint8ClampedArray([0, 0, 0, 0, 0, 0, 0, 0])
  const stage = { dataset: {} }
  const dynamicCanvas = {
    width: 720,
    height: 1080,
    getContext() {
      return { getImageData() { return { data: pixels } } }
    },
  }
  const draws = []
  const idleCanvas = {
    width: 0,
    height: 0,
    getContext() {
      return {
        clearRect() {},
        drawImage(source) { draws.push(source) },
      }
    },
  }
  const presentation = createAvatarPresentation({ stage, dynamicCanvas, idleCanvas })

  assert.equal(presentation.captureIdleFrame(), false)
  pixels = new Uint8ClampedArray([10, 40, 80, 255])
  assert.equal(presentation.captureIdleFrame(), true)
  assert.deepEqual(draws, [dynamicCanvas])
})

test('rejects a black startup frame that contains only a tiny mouth fragment', () => {
  let pixels = new Uint8ClampedArray(40 * 4)
  pixels.set([255, 180, 180, 255], 0)
  const stage = { dataset: {} }
  const dynamicCanvas = {
    width: 720,
    height: 1080,
    getContext() {
      return { getImageData() { return { data: pixels } } }
    },
  }
  const idleCanvas = {
    getContext() {
      return { clearRect() {}, drawImage() {} }
    },
  }
  const presentation = createAvatarPresentation({ stage, dynamicCanvas, idleCanvas })

  assert.equal(presentation.captureIdleFrame(), false)
  pixels = new Uint8ClampedArray(40 * 4).fill(160)
  assert.equal(presentation.captureIdleFrame(), true)
})

test('rejects a partial mouth layer even when several bright pixels are present', () => {
  const pixels = new Uint8ClampedArray(400 * 4)
  for (let index = 0; index < 30; index += 1) {
    pixels.set([220, 160, 160, 255], index * 4)
  }
  const stage = { dataset: {} }
  const dynamicCanvas = {
    width: 720,
    height: 1080,
    getContext() {
      return { getImageData() { return { data: pixels } } }
    },
  }
  const idleCanvas = {
    getContext() {
      return { clearRect() {}, drawImage() {} }
    },
  }
  const presentation = createAvatarPresentation({ stage, dynamicCanvas, idleCanvas })

  assert.equal(presentation.captureIdleFrame(), false)
})
