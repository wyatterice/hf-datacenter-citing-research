// Regenerate public/scores.json from Model/county_scores.csv.
// Run after the data pipeline updates the CSV: `npm run build:data`.
// The CSV has no quoted fields (county names contain no commas), so a plain
// split on commas is safe; keep this in sync if that ever changes.

import { readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const here = dirname(fileURLToPath(import.meta.url))
const csvPath = join(here, '..', '..', 'Model', 'county_scores.csv')
const outPath = join(here, '..', 'public', 'scores.json')

// Columns kept as strings (with zero-padding), everything else is numeric.
const PAD = { fips: 5, state_fips: 2 }
const STRING_COLS = new Set(['county_name'])

const text = readFileSync(csvPath, 'utf8').trim()
const lines = text.split(/\r?\n/)
const header = lines[0].split(',')

const rows = lines.slice(1).map((line) => {
  const cells = line.split(',')
  const row = {}
  header.forEach((col, i) => {
    const raw = cells[i]
    if (col in PAD) {
      row[col] = String(raw).padStart(PAD[col], '0')
    } else if (STRING_COLS.has(col)) {
      row[col] = raw
    } else if (raw === '' || raw === undefined) {
      row[col] = null
    } else {
      const n = Number(raw)
      row[col] = Number.isNaN(n) ? null : n
    }
  })
  return row
})

writeFileSync(outPath, JSON.stringify(rows))
console.log(`Wrote ${rows.length} rows to public/scores.json`)
