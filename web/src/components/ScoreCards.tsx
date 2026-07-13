// Percentile score cards, one per infrastructure dimension.

import { benchSuffix, getTier, ordinal, type Benchmark, type CountyRow } from '../lib/calc'
import { DIMENSIONS, TIER_COLORS, TIER_LABELS } from '../lib/data'

interface Props {
  row: CountyRow
  benchmark: Benchmark
}

function fmtRaw(value: number): string {
  return value.toLocaleString('en-US', { minimumFractionDigits: 1, maximumFractionDigits: 1 })
}

export function ScoreCards({ row, benchmark }: Props) {
  const suffix = benchSuffix(benchmark)
  return (
    <div className="dc-grid dc-grid-4">
      {DIMENSIONS.map((dim) => {
        const score = row[`${dim.key}_${suffix}` as keyof CountyRow] as number | null
        const rawVal = row[`${dim.key}_raw` as keyof CountyRow] as number | null
        const tier = getTier(score)

        return (
          <div key={dim.key} className="chart-card dc-card">
            <div className="card-header">{dim.label}</div>
            {tier === null || score === null ? (
              <div className="no-data-score">Data unavailable for this county</div>
            ) : (
              <>
                <div className="score-number" style={{ color: TIER_COLORS[tier] }}>
                  {Math.round(score)}
                  <span className="score-suffix">{ordinal(score)}</span>
                </div>
                <span className={`tier-pill tier-${tier}`}>{TIER_LABELS[tier]}</span>
                {rawVal === null ? (
                  <div className="raw-value">No data</div>
                ) : (
                  <div className="raw-value">
                    {dim.rawLabel}:{' '}
                    <strong>
                      {fmtRaw(rawVal)} {dim.rawUnit}
                    </strong>
                  </div>
                )}
                <div className={`insight-box insight-${tier}`}>{dim[tier]}</div>
              </>
            )}
          </div>
        )
      })}
    </div>
  )
}
