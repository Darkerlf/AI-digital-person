export function createAvatarPresentation({ stage, dynamicCanvas, idleCanvas, idleImage = null }) {
  let hasIdleFrame = false
  stage.dataset.avatarMode = 'idle'

  return {
    captureIdleFrame() {
      if (hasIdleFrame) return false
      if (idleImage) {
        hasIdleFrame = captureIdleImage(idleImage, idleCanvas, dynamicCanvas)
        return hasIdleFrame
      }
      if (
        !dynamicCanvas.width
        || !dynamicCanvas.height
        || (dynamicCanvas.width === 300 && dynamicCanvas.height === 150)
        || !hasVisiblePixels(dynamicCanvas)
      ) return false

      idleCanvas.width = dynamicCanvas.width
      idleCanvas.height = dynamicCanvas.height
      const context = idleCanvas.getContext('2d')
      context.clearRect(0, 0, idleCanvas.width, idleCanvas.height)
      context.drawImage(dynamicCanvas, 0, 0)
      hasIdleFrame = true
      return true
    },

    setSpeaking(isSpeaking) {
      stage.dataset.avatarMode = isSpeaking ? 'speaking' : 'idle'
    },
  }
}

function captureIdleImage(image, canvas, dynamicCanvas) {
  if (!image.complete) return false
  if (!image.naturalWidth || !image.naturalHeight) return false

  const target = getTargetSize(dynamicCanvas, image)
  canvas.width = target.width
  canvas.height = target.height
  const context = canvas.getContext('2d')
  context.clearRect(0, 0, canvas.width, canvas.height)
  drawImageCover(context, image, canvas.width, canvas.height)
  return true
}

function getTargetSize(dynamicCanvas, image) {
  const hasDhLiveSize = (
    dynamicCanvas.width
    && dynamicCanvas.height
    && !(dynamicCanvas.width === 300 && dynamicCanvas.height === 150)
  )
  return hasDhLiveSize
    ? { width: dynamicCanvas.width, height: dynamicCanvas.height }
    : { width: image.naturalWidth, height: image.naturalHeight }
}

function drawImageCover(context, image, targetWidth, targetHeight) {
  const sourceRatio = image.naturalWidth / image.naturalHeight
  const targetRatio = targetWidth / targetHeight
  let sx = 0
  let sy = 0
  let sw = image.naturalWidth
  let sh = image.naturalHeight

  if (sourceRatio > targetRatio) {
    sw = image.naturalHeight * targetRatio
    sx = (image.naturalWidth - sw) / 2
  } else {
    sh = image.naturalWidth / targetRatio
    sy = (image.naturalHeight - sh) / 2
  }

  context.drawImage(image, sx, sy, sw, sh, 0, 0, targetWidth, targetHeight)
}

function hasVisiblePixels(canvas) {
  const context = canvas.getContext('2d', { willReadFrequently: true })
  if (!context) return false

  const pixels = context.getImageData(0, 0, canvas.width, canvas.height).data
  const sampleStep = Math.max(4, Math.floor(pixels.length / 4000 / 4) * 4)
  let sampled = 0
  let visible = 0
  for (let offset = 0; offset < pixels.length; offset += sampleStep) {
    sampled += 1
    const brightness = pixels[offset] + pixels[offset + 1] + pixels[offset + 2]
    if (pixels[offset + 3] > 8 && brightness > 36) visible += 1
  }
  const minimumVisibleSamples = Math.max(1, Math.ceil(sampled * 0.12))
  return visible >= minimumVisibleSamples
}
