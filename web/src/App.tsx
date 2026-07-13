import { useEffect, useMemo, useState } from 'react'
import { benchLabel, type Benchmark } from './lib/calc'
import { countyOptionsForState, useScores } from './lib/useScores'
import { Field, Segmented, SegmentedControlRow, Select } from './components/ui'
import { ScoreCards } from './components/ScoreCards'
import { Estimator } from './components/Estimator'
import { Footer } from './components/Footer'
import { FloatingNav } from './components/FloatingNav'

const BENCHMARK_OPTIONS = [
  { value: 'hyperscalers' as Benchmark, label: 'Hyperscaler Counties' },
  { value: 'national' as Benchmark, label: 'All US Counties' },
]

export default function App() {
  const { rows, loading, error } = useScores()
  const [stateName, setStateName] = useState<string>('')
  const [fips, setFips] = useState<string>('')
  const [benchmark, setBenchmark] = useState<Benchmark>('hyperscalers')

  const stateOptions = useMemo(() => {
    const names = Array.from(new Set(rows.map((r) => r.state_name).filter(Boolean)))
    names.sort()
    return names
  }, [rows])

  const countyOptions = useMemo(
    () => (stateName ? countyOptionsForState(rows, stateName) : []),
    [rows, stateName],
  )

  // Default to the first state once data loads.
  useEffect(() => {
    if (!stateName && stateOptions.length > 0) setStateName(stateOptions[0])
  }, [stateOptions, stateName])

  // Keep the county valid whenever the state (and thus the option list) changes.
  useEffect(() => {
    if (countyOptions.length === 0) return
    if (!countyOptions.some((c) => c.fips === fips)) setFips(countyOptions[0].fips)
  }, [countyOptions, fips])

  const row = useMemo(() => rows.find((r) => r.fips === fips), [rows, fips])
  const selectedCountyName = countyOptions.find((c) => c.fips === fips)?.countyName ?? ''

  if (loading) {
    return (
      <div className="dc-loading">
        <div className="section-loader-spinner" />
      </div>
    )
  }

  if (error) {
    return <div className="dc-loading">Failed to load county data: {error}</div>
  }

  return (
    <>
      <div className="container dc-container">
        <header className="tool-header">
          <h1>Datacenter Impact Research Tool</h1>
          <p>Heartland Forward &middot; County-level infrastructure benchmarking for datacenter investment negotiations</p>
        </header>

        <SegmentedControlRow cols={2}>
          <Field label="State">
            <Select
              value={stateName}
              options={stateOptions.map((s) => ({ value: s, label: s }))}
              onChange={setStateName}
            />
          </Field>
          <Field label="County">
            <Select
              value={fips}
              options={countyOptions.map((c) => ({ value: c.fips, label: c.displayName }))}
              onChange={setFips}
            />
          </Field>
        </SegmentedControlRow>
        <SegmentedControlRow cols={1}>
          <Field label="Benchmark against">
            <Segmented value={benchmark} options={BENCHMARK_OPTIONS} onChange={setBenchmark} />
          </Field>
        </SegmentedControlRow>

        {row ? (
          <>
            {row.is_hyperscaler === 1 ? (
              <span className="hyperscaler-badge">Active hyperscaler investment county</span>
            ) : null}

            <div id="scores" className="metrics-section dc-subsection">
              <div className="metrics-section-header">
                <h3>Percentile scores: {benchLabel(benchmark)}</h3>
              </div>
              <ScoreCards row={row} benchmark={benchmark} />
            </div>

            <Estimator row={row} countyName={selectedCountyName} benchmark={benchmark} />

            <p className="dc-methodology">
              Percentile scores show how this county ranks on each dimension relative to the selected benchmark group.
              Higher score = stronger position or leverage held. Lower score = stronger negotiating ask. Energy and
              broadband unavailable for 827 counties (EIA/FCC coverage gap). Water score is inverted: higher score
              reflects less drought exposure. Sources: EIA-860/923, FCC Broadband Map, NOAA Climate, US Drought Monitor,
              NLCD 2024, PAD-US 4.1.
            </p>
          </>
        ) : null}
      </div>
      {row ? <FloatingNav /> : null}
      <Footer />
    </>
  )
}
