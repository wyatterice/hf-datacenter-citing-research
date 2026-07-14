// Scoring and estimator math ported from Dashboard/app.py.

import {
  BROADBAND_MAP,
  BUILD_PER_MW,
  CONST_JOBS_AT_HIGH,
  CONST_JOBS_AT_LOW,
  CONST_JOBS_MW_HIGH,
  CONST_JOBS_MW_LOW,
  FITOUT_PER_MW,
  HOURS_PER_YEAR,
  INCENTIVE_NORM_MAP,
  INDIRECT_MULT_MAP,
  INFO_SECTOR_COPY,
  LAND_MAP,
  PERMANENT_JOBS_FIXED,
  PUE_MAP,
  TAX_WINDOW_YEARS,
  TIER_PRESETS,
  WUE_MAP,
  type FacilityType,
  type InfoSectorCopy,
  type Tier,
  type TierKey,
} from './data'

export interface CountyRow {
  fips: string
  county_name: string
  state_fips: string
  is_hyperscaler: number
  energy_raw: number | null
  energy_vs_hyperscalers: number | null
  energy_vs_national: number | null
  land_raw: number | null
  land_vs_hyperscalers: number | null
  land_vs_national: number | null
  broadband_raw: number | null
  broadband_vs_hyperscalers: number | null
  broadband_vs_national: number | null
  water_raw: number | null
  water_vs_hyperscalers: number | null
  water_vs_national: number | null
}

export type Benchmark = 'hyperscalers' | 'national'

export function benchSuffix(b: Benchmark): 'vs_hyperscalers' | 'vs_national' {
  return b === 'hyperscalers' ? 'vs_hyperscalers' : 'vs_national'
}

export function benchLabel(b: Benchmark): string {
  return b === 'hyperscalers'
    ? 'vs. counties where hyperscalers have built'
    : 'vs. all US counties'
}

export function getTier(score: number | null | undefined): Tier | null {
  if (score === null || score === undefined || Number.isNaN(score)) return null
  if (score >= 60) return 'strong'
  if (score >= 30) return 'moderate'
  return 'leverage'
}

export function ordinal(score: number): string {
  const n = Math.round(score)
  const mod100 = ((n % 100) + 100) % 100
  if (mod100 >= 11 && mod100 <= 13) return 'th'
  switch (n % 10) {
    case 1:
      return 'st'
    case 2:
      return 'nd'
    case 3:
      return 'rd'
    default:
      return 'th'
  }
}

export function mwToTierKey(mw: number): TierKey {
  if (mw <= 100) return 'small'
  if (mw <= 225) return 'medium'
  if (mw <= 400) return 'large'
  return 'hyperscale'
}

export function constructionJobsFor(mw: number): number {
  if (mw <= CONST_JOBS_MW_LOW) return CONST_JOBS_AT_LOW
  if (mw >= CONST_JOBS_MW_HIGH) return CONST_JOBS_AT_HIGH
  const frac = (mw - CONST_JOBS_MW_LOW) / (CONST_JOBS_MW_HIGH - CONST_JOBS_MW_LOW)
  return CONST_JOBS_AT_LOW + frac * (CONST_JOBS_AT_HIGH - CONST_JOBS_AT_LOW)
}

export function fmtDollars(n: number): string {
  if (n >= 1_000_000_000) return `$${(n / 1_000_000_000).toFixed(2)}B`
  return `$${(n / 1_000_000).toFixed(0)}M`
}

export function fmtDollarsTax(n: number): string {
  if (n >= 1_000_000_000) return `$${(n / 1_000_000_000).toFixed(2)}B`
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(2)}M`
  return `$${Math.round(n).toLocaleString('en-US')}`
}

export function fmtGallonsDaily(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M gallons/day`
  return `${(n / 1_000).toFixed(0)}K gallons/day`
}

// Trim a trailing ".0" so 1.5 -> "1.5" and 2 -> "2" (matches Python %g / :g).
export function g(n: number): string {
  return Number.isInteger(n) ? String(n) : String(n)
}

export interface EstimatorInputs {
  presetTier: string
  customMw: number | null
  energyEfficiency: 'Conservative' | 'Default' | 'Optimistic'
  waterEfficiency: 'Conservative' | 'Optimistic' | 'Closed-Loop'
  facilityType: FacilityType
  costBasis: 'Shell + core' | 'Shell + core + AI fit-out'
  assessedValueMode: 'estimate' | 'direct'
  assessedValueDirect: number | null
  millageRate: number
  assessmentRatio: number
  abatementPct: number
  abatementYears: number
}

export interface EstimatorResult {
  itLoadMw: number
  pue: number
  wue: number
  facilityTypeLabel: string
  // Energy
  gridDrawMw: number
  capacityNote: string
  // Water
  annualLiters: number
  annualGallons: number
  dailyGallons: number
  // Broadband / land
  bbRange: string
  bbNote: string
  bbAsk: string
  landRange: string
  // Economics
  constructionCost: number
  aiTotalCost: number
  permanentJobs: number
  constructionJobs: number
  indirectJobs: number
  indirectMult: number
  infoCopy: InfoSectorCopy
  // Tax
  selectedTotalCost: number
  assessedValue: number
  annualTaxFull: number
  annualTaxAbated: number
  revenueWithoutAbatement: number
  revenueWithAbatement: number
  revenueGap: number
  incentiveNormPct: number
}

export function computeEstimate(
  row: CountyRow,
  countyName: string,
  benchmark: Benchmark,
  inputs: EstimatorInputs,
): EstimatorResult {
  const facilityTypeLabel = inputs.facilityType.startsWith('Hyperscale') ? 'Hyperscale' : 'Colocation'
  const itLoadMw = inputs.customMw !== null ? inputs.customMw : TIER_PRESETS[inputs.presetTier]
  const tierKey = mwToTierKey(itLoadMw)

  const pue = PUE_MAP[inputs.energyEfficiency]
  const wue = WUE_MAP[inputs.waterEfficiency]

  const indirectMult = INDIRECT_MULT_MAP[inputs.facilityType]

  // Energy
  const gridDrawMw = itLoadMw * pue
  const energyRawVal = row.energy_raw
  let capacityNote: string
  if (energyRawVal !== null && !Number.isNaN(energyRawVal) && energyRawVal > 0) {
    const pctOfCounty = (gridDrawMw / energyRawVal) * 100
    capacityNote =
      `${pctOfCounty.toFixed(1)}% of ${countyName}'s ` +
      `${Math.round(energyRawVal).toLocaleString('en-US')} MW nameplate capacity. ` +
      'Nameplate is theoretical maximum, not available headroom.'
  } else {
    capacityNote =
      'County nameplate capacity data not available. Nameplate is theoretical maximum, not available headroom.'
  }

  // Water
  const itLoadKw = itLoadMw * 1000
  const annualLiters = itLoadKw * HOURS_PER_YEAR * wue
  const annualGallons = annualLiters / 3.785
  const dailyGallons = annualGallons / 365

  // Broadband
  const { range: bbRange, note: bbNote } = BROADBAND_MAP[tierKey]
  const broadbandScore = row[`broadband_${benchSuffix(benchmark)}` as keyof CountyRow] as number | null
  let bbAsk: string
  if (getTier(broadbandScore) === 'leverage' || tierKey === 'hyperscale') {
    bbAsk =
      'Low local fiber coverage is leverage - push for community access agreements and last-mile buildout written into the development deal.'
  } else {
    bbAsk = 'Require fiber access and community connectivity terms as part of the development agreement.'
  }

  // Land
  const landRange = LAND_MAP[tierKey]

  // Economics
  const constructionCost = itLoadMw * BUILD_PER_MW
  const aiTotalCost = itLoadMw * (BUILD_PER_MW + FITOUT_PER_MW)
  const permanentJobs = PERMANENT_JOBS_FIXED
  const constructionJobs = constructionJobsFor(itLoadMw)
  const indirectJobs = permanentJobs * indirectMult
  const infoCopy = INFO_SECTOR_COPY[inputs.facilityType]

  // Tax
  const selectedTotalCost = inputs.costBasis === 'Shell + core' ? constructionCost : aiTotalCost
  const assessedValue =
    inputs.assessedValueMode === 'direct'
      ? inputs.assessedValueDirect ?? 0
      : selectedTotalCost * (inputs.assessmentRatio / 100)
  const annualTaxFull = assessedValue * (inputs.millageRate / 1000)
  const annualTaxAbated = annualTaxFull * (1 - inputs.abatementPct / 100)
  const abatedYearsInWindow = Math.min(inputs.abatementYears, TAX_WINDOW_YEARS)
  const fullYearsInWindow = TAX_WINDOW_YEARS - abatedYearsInWindow
  const revenueWithoutAbatement = annualTaxFull * TAX_WINDOW_YEARS
  const revenueWithAbatement = annualTaxAbated * abatedYearsInWindow + annualTaxFull * fullYearsInWindow
  const revenueGap = revenueWithoutAbatement - revenueWithAbatement
  const incentiveNormPct = INCENTIVE_NORM_MAP[inputs.facilityType]

  return {
    itLoadMw,
    pue,
    wue,
    facilityTypeLabel,
    gridDrawMw,
    capacityNote,
    annualLiters,
    annualGallons,
    dailyGallons,
    bbRange,
    bbNote,
    bbAsk,
    landRange,
    constructionCost,
    aiTotalCost,
    permanentJobs,
    constructionJobs,
    indirectJobs,
    indirectMult,
    infoCopy,
    selectedTotalCost,
    assessedValue,
    annualTaxFull,
    annualTaxAbated,
    revenueWithoutAbatement,
    revenueWithAbatement,
    revenueGap,
    incentiveNormPct,
  }
}
