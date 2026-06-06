const HARD_BREAK = /[。！？!?；;]/
const SOFT_BREAK = /[，,、：:]/

export function extractPhrase(text, isFirst = false) {
  const source = text.trimStart()
  if (!source) return null

  const min = isFirst ? 8 : 26
  const hardLimit = isFirst ? 42 : 86
  let softCandidate = -1

  for (let index = 0; index < source.length; index += 1) {
    const char = source[index]
    if (SOFT_BREAK.test(char) && index >= min) softCandidate = index
    if (HARD_BREAK.test(char) && index >= min) return take(source, index + 1)
    if (index >= hardLimit) return take(source, (softCandidate > -1 ? softCandidate : index) + 1)
  }

  return null
}

export function flushPhrase(text) {
  const source = text.trim()
  return source ? { phrase: source, rest: '' } : null
}

function take(source, end) {
  return {
    phrase: source.slice(0, end).trim(),
    rest: source.slice(end).trimStart(),
  }
}
