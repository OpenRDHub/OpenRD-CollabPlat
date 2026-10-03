import { readdirSync } from 'node:fs'

await import('./mock-mode.test.mjs')
await import('./admin-permissions.test.mjs')

for (const filename of readdirSync(new URL('.', import.meta.url))) {
  if (filename !== 'contract-suite.test.mjs' && filename.endsWith('-contract.test.mjs')) {
    await import(`./${filename}`)
  }
}
