import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'

const source = readFileSync(join(process.cwd(), 'src/api/client.ts'), 'utf8')

describe('api client configuration', () => {
  it('uses a Vite environment variable before the local fallback URL', () => {
    expect(source).toContain('import.meta.env.VITE_API_BASE_URL')
    expect(source).toContain('http://127.0.0.1:8000/api')
    expect(source).not.toContain("baseURL: 'http://127.0.0.1:8000/api'")
  })
})
