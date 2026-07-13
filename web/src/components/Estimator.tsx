// Infrastructure Impact Estimator: translates facility scale into
// infrastructure demand, economic output, and tax exposure.

import { useState } from 'react'
import {
  computeEstimate,
  fmtDollars,
  fmtDollarsTax,
  fmtGallonsDaily,
  type Benchmark,
  type CountyRow,
  type EstimatorInputs,
} from '../lib/calc'
import { TIER_PRESETS, type FacilityType } from '../lib/data'
import { Field, NumberField, SegmentedControlRow, Select, Segmented, SliderField } from './ui'

interface Props {
  row: CountyRow
  countyName: string
  benchmark: Benchmark
}

const EFFICIENCY_OPTIONS = [
  { value: 'Conservative' as const, label: 'Conservative' },
  { value: 'Default' as const, label: 'Default' },
  { value: 'Optimistic' as const, label: 'Optimistic' },
]

const FACILITY_OPTIONS = [
  { value: 'Hyperscale (cloud/AI operator)' as FacilityType, label: 'Hyperscale (cloud/AI)' },
  { value: 'Colocation (leased/wholesale)' as FacilityType, label: 'Colocation (leased)' },
]

const COST_BASIS_OPTIONS = [
  { value: 'Shell + core' as const, label: 'Shell + core' },
  { value: 'Shell + core + AI fit-out' as const, label: 'Shell + core + AI fit-out' },
]

function round0(n: number): string {
  return Math.round(n).toLocaleString('en-US')
}

export function Estimator({ row, countyName, benchmark }: Props) {
  const [inputs, setInputs] = useState<EstimatorInputs>({
    presetTier: Object.keys(TIER_PRESETS)[0],
    customMw: null,
    energyEfficiency: 'Default',
    waterEfficiency: 'Default',
    closedLoop: false,
    facilityType: 'Hyperscale (cloud/AI operator)',
    costBasis: 'Shell + core',
    millageRate: 20,
    assessmentRatio: 100,
    abatementPct: 0,
    abatementYears: 10,
  })

  const set = <K extends keyof EstimatorInputs>(key: K, value: EstimatorInputs[K]) =>
    setInputs((prev) => ({ ...prev, [key]: value }))

  const e = computeEstimate(row, countyName, benchmark, inputs)

  const econItems: { label: string; number: string; note: string }[] = [
    { label: 'Shell + core cost', number: fmtDollars(e.constructionCost), note: 'at $11.3M per MW' },
    { label: 'With AI fit-out', number: fmtDollars(e.aiTotalCost), note: 'at $36.3M per MW' },
    { label: 'Permanent jobs', number: round0(e.permanentJobs), note: 'at 1.5 jobs/MW (hyperscale automation)' },
    { label: 'Construction jobs', number: round0(e.constructionJobs), note: 'at 10 workers/MW (peak build)' },
    {
      label: 'Indirect jobs',
      number: round0(e.indirectJobs),
      note: `${e.indirectMult}x permanent jobs (${e.facilityTypeLabel}, Bahar & Wright 2026)`,
    },
  ]

  return (
    <section className="pillar-section dc-section">
      <div className="est-header">
        <h2>Infrastructure Impact Estimator</h2>
        <p>Translate facility scale into infrastructure demand and economic output, framed as negotiation leverage.</p>
      </div>

      <div className="dc-panel">
      <SegmentedControlRow>
        <Field label="Facility scale">
          <Select
            value={inputs.presetTier}
            options={Object.keys(TIER_PRESETS).map((k) => ({ value: k, label: k }))}
            onChange={(v) => set('presetTier', v)}
          />
        </Field>
        <Field label="Custom IT load (MW), overrides preset">
          <NumberField
            value={inputs.customMw}
            onChange={(v) => set('customMw', v)}
            min={1}
            max={2000}
            allowEmpty
            placeholder="preset"
          />
        </Field>
      </SegmentedControlRow>

      <SegmentedControlRow cols={2}>
        <Field label="Energy efficiency scenario">
          <Segmented
            value={inputs.energyEfficiency}
            options={EFFICIENCY_OPTIONS}
            onChange={(v) => set('energyEfficiency', v)}
          />
        </Field>
        <Field label="Water efficiency scenario">
          <Segmented
            value={inputs.waterEfficiency}
            options={EFFICIENCY_OPTIONS}
            onChange={(v) => set('waterEfficiency', v)}
            disabled={inputs.closedLoop}
          />
        </Field>
      </SegmentedControlRow>

      <SegmentedControlRow cols={2}>
        <Field label="Facility type">
          <Segmented value={inputs.facilityType} options={FACILITY_OPTIONS} onChange={(v) => set('facilityType', v)} />
        </Field>
        <Field label="Water cooling" hint="Closed-loop overrides to WUE 0.0">
          <label className="dc-checkbox">
            <input
              type="checkbox"
              checked={inputs.closedLoop}
              onChange={(ev) => set('closedLoop', ev.target.checked)}
            />
            Closed-loop system (no evaporative water use)
          </label>
        </Field>
      </SegmentedControlRow>
      </div>

      {/* Infrastructure demand */}
      <div id="demand" className="metrics-section dc-subsection">
        <div className="metrics-section-header">
          <h3>
            Infrastructure demand: {round0(e.itLoadMw)} MW IT load &middot; PUE {e.pue} &middot; WUE {e.wue} L/kWh
          </h3>
        </div>
        <div className="dc-grid dc-grid-4">
          <div className="chart-card dc-card">
            <div className="card-header">Energy demand</div>
            <div className="impact-number">{round0(e.gridDrawMw)}</div>
            <div className="impact-unit">MW grid draw (IT load x PUE {e.pue})</div>
            <div className="impact-context">{e.capacityNote}</div>
            <div className="impact-ask">
              Require operator to fund grid improvements (substation upgrades, dedicated feeders, or new generation) as
              a condition of the development agreement.
            </div>
          </div>
          <div className="chart-card dc-card">
            <div className="card-header">Water demand</div>
            <div className="impact-number">{(e.annualGallons / 1_000_000).toFixed(1)}M</div>
            <div className="impact-unit">
              gallons per year ({Math.round(e.annualLiters / 1_000_000)}M liters)
            </div>
            <div className="impact-sub">
              {fmtGallonsDaily(e.dailyGallons)}, large facilities can reach 5M gallons/day
            </div>
            <div className="impact-ask">
              Negotiate water recycling requirements, closed-loop cooling standards, and annual usage caps into the
              permit or development agreement.
            </div>
          </div>
          <div className="chart-card dc-card">
            <div className="card-header">Connectivity demand</div>
            <div className="impact-number impact-number-sm">{e.bbRange}</div>
            <div className="impact-unit">estimated connectivity requirement</div>
            <div className="impact-context">{e.bbNote}</div>
            <div className="impact-ask">{e.bbAsk}</div>
          </div>
          <div className="chart-card dc-card">
            <div className="card-header">Land footprint</div>
            <div className="impact-number impact-number-sm">{e.landRange}</div>
            <div className="impact-unit">estimated site footprint</div>
            <div className="impact-ask">
              Site selection terms, land use standards, and greenfield development commitments are all reasonable asks
              in a development agreement.
            </div>
          </div>
        </div>
      </div>

      {/* Economic impact */}
      <div id="economics" className="metrics-section dc-subsection">
        <div className="metrics-section-header">
          <h3>Economic impact</h3>
        </div>
        <div className="dc-grid dc-grid-5">
          {econItems.map((item) => (
            <div key={item.label} className="chart-card dc-card">
              <div className="econ-label">{item.label}</div>
              <div className="econ-number">{item.number}</div>
              <div className="impact-unit">{item.note}</div>
            </div>
          ))}
        </div>

        <div className="chart-card dc-card dc-card-wide">
          <div className="card-header">Information-sector job creation, {e.facilityTypeLabel}</div>
          <div className="impact-number impact-number-md">{e.infoCopy.number}</div>
          <div className="impact-unit">{e.infoCopy.unit}</div>
          <div className="impact-context">{e.infoCopy.context}</div>
          <div className="impact-ask">{e.infoCopy.ask}</div>
        </div>

        <div className="est-caveat">
          Nameplate capacity is theoretical maximum generation; available headroom depends on existing load,
          transmission constraints, and grid operator scheduling. A single datacenter facility creates modest permanent
          employment: hyperscale automation limits on-site staff to roughly 1.5 jobs per MW. Ecosystem employment
          concentrates in hyperscale clusters over time, not in a single facility's direct hire (Brookings, 2026).
        </div>
      </div>

      {/* Tax and incentive estimator */}
      <div id="tax" className="metrics-section dc-subsection">
        <div className="metrics-section-header">
          <h3>Tax &amp; incentive estimator</h3>
        </div>

        <div className="dc-panel">
        <SegmentedControlRow cols={1}>
          <Field label="Cost basis for assessed value">
            <Segmented value={inputs.costBasis} options={COST_BASIS_OPTIONS} onChange={(v) => set('costBasis', v)} />
          </Field>
        </SegmentedControlRow>

        <SegmentedControlRow cols={4}>
          <Field label="Millage rate (per $1,000)">
            <NumberField value={inputs.millageRate} onChange={(v) => set('millageRate', v ?? 0)} min={0} step={0.5} />
          </Field>
          <Field label="Assessment ratio (%)">
            <NumberField
              value={inputs.assessmentRatio}
              onChange={(v) => set('assessmentRatio', v ?? 1)}
              min={1}
              max={100}
              step={1}
            />
          </Field>
          <Field label="Abatement (%)">
            <SliderField value={inputs.abatementPct} onChange={(v) => set('abatementPct', v)} min={0} max={100} suffix="%" />
          </Field>
          <Field label="Abatement term (years)">
            <NumberField
              value={inputs.abatementYears}
              onChange={(v) => set('abatementYears', v ?? 0)}
              min={0}
              max={50}
              step={1}
            />
          </Field>
        </SegmentedControlRow>
        </div>

        <div className="dc-grid dc-grid-3">
          <div className="chart-card dc-card">
            <div className="card-header">Annual tax, full rate</div>
            <div className="impact-number impact-number-md">{fmtDollarsTax(e.annualTaxFull)}</div>
            <div className="impact-unit">
              assessed value {fmtDollarsTax(e.assessedValue)} x {inputs.millageRate} mills
            </div>
          </div>
          <div className="chart-card dc-card">
            <div className="card-header">Annual tax, during abatement</div>
            <div className="impact-number impact-number-md">{fmtDollarsTax(e.annualTaxAbated)}</div>
            <div className="impact-unit">
              at {inputs.abatementPct}% abatement for {inputs.abatementYears} year(s)
            </div>
          </div>
          <div className="chart-card dc-card">
            <div className="card-header">10-year revenue gap</div>
            <div className="impact-number impact-number-md">{fmtDollarsTax(e.revenueGap)}</div>
            <div className="impact-unit">
              {fmtDollarsTax(e.revenueWithAbatement)} with abatement vs. {fmtDollarsTax(e.revenueWithoutAbatement)}{' '}
              without
            </div>
            <div className="impact-context">
              Your modeled abatement is {inputs.abatementPct}% of assessed value. Bahar &amp; Wright (2026) find
              incentives average ~{e.incentiveNormPct}% of investment in {e.facilityTypeLabel.toLowerCase()} deals, use
              that as a real-world benchmark for this facility type.
            </div>
          </div>
        </div>

        <div className="est-caveat">
          Sales tax exemptions on equipment purchases (servers, cooling, switchgear) are common in datacenter incentive
          packages and are not modeled above. Virginia's data center sales-tax exemption alone cost an estimated $1.6B
          in FY2025, confirm whether an equivalent exemption applies in your state before finalizing incentive
          comparisons.
        </div>
      </div>
    </section>
  )
}
