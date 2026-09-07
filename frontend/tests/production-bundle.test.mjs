import assert from 'node:assert/strict'
import { readdirSync, readFileSync } from 'node:fs'
import test from 'node:test'

test('the production bundle excludes the MSW browser runtime', () => {
  const assetDirectory = new URL('../dist/assets/', import.meta.url)
  const javascriptFiles = readdirSync(assetDirectory).filter((name) => name.endsWith('.js'))
  const bundledSource = javascriptFiles
    .map((name) => readFileSync(new URL(name, assetDirectory), 'utf8'))
    .join('\n')

  assert.doesNotMatch(bundledSource, /mockServiceWorker\.js|Mock Service Worker/)
})
