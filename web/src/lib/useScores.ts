// Loads the county scores dataset (generated from Model/county_scores.csv).

import { useEffect, useState } from 'react'
import type { CountyRow } from './calc'
import { FIPS_TO_ABBREV, STATE_NAMES } from './data'

export interface CountyRecord extends CountyRow {
  state_abbr: string
  state_name: string
}

export interface ScoresData {
  rows: CountyRecord[]
  loading: boolean
  error: string | null
}

export function useScores(): ScoresData {
  const [rows, setRows] = useState<CountyRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    fetch(`${import.meta.env.BASE_URL}scores.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`Failed to load scores (${r.status})`)
        return r.json()
      })
      .then((data: CountyRow[]) => {
        if (!active) return
        const enriched = data.map((row) => {
          const stateFips = String(row.state_fips).padStart(2, '0')
          const abbr = FIPS_TO_ABBREV[stateFips] ?? ''
          return {
            ...row,
            fips: String(row.fips).padStart(5, '0'),
            state_fips: stateFips,
            state_abbr: abbr,
            state_name: STATE_NAMES[abbr] ?? '',
          }
        })
        setRows(enriched)
        setLoading(false)
      })
      .catch((e: unknown) => {
        if (!active) return
        setError(e instanceof Error ? e.message : 'Failed to load scores')
        setLoading(false)
      })
    return () => {
      active = false
    }
  }, [])

  return { rows, loading, error }
}

// Build the disambiguated county display list for a state, mirroring app.py:
// duplicate county names within a state get their FIPS appended.
export interface CountyOption {
  fips: string
  countyName: string
  displayName: string
}

export function countyOptionsForState(rows: CountyRecord[], stateName: string): CountyOption[] {
  const inState = rows
    .filter((r) => r.state_name === stateName)
    .sort((a, b) => a.county_name.localeCompare(b.county_name))
  const counts = new Map<string, number>()
  inState.forEach((r) => counts.set(r.county_name, (counts.get(r.county_name) ?? 0) + 1))
  return inState.map((r) => ({
    fips: r.fips,
    countyName: r.county_name,
    displayName: (counts.get(r.county_name) ?? 0) > 1 ? `${r.county_name} (${r.fips})` : r.county_name,
  }))
}
