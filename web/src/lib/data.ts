// Static data and copy ported verbatim from Dashboard/app.py.
// Keeping the negotiation copy identical preserves the tool's meaning.

export const STATE_FIPS: Record<string, string> = {
  AL: '01', AK: '02', AZ: '04', AR: '05', CA: '06',
  CO: '08', CT: '09', DE: '10', FL: '12', GA: '13',
  HI: '15', ID: '16', IL: '17', IN: '18', IA: '19',
  KS: '20', KY: '21', LA: '22', ME: '23', MD: '24',
  MA: '25', MI: '26', MN: '27', MS: '28', MO: '29',
  MT: '30', NE: '31', NV: '32', NH: '33', NJ: '34',
  NM: '35', NY: '36', NC: '37', ND: '38', OH: '39',
  OK: '40', OR: '41', PA: '42', RI: '44', SC: '45',
  SD: '46', TN: '47', TX: '48', UT: '49', VT: '50',
  VA: '51', WA: '53', WV: '54', WI: '55', WY: '56',
}

export const STATE_NAMES: Record<string, string> = {
  AL: 'Alabama', AK: 'Alaska', AZ: 'Arizona', AR: 'Arkansas',
  CA: 'California', CO: 'Colorado', CT: 'Connecticut', DE: 'Delaware',
  FL: 'Florida', GA: 'Georgia', HI: 'Hawaii', ID: 'Idaho',
  IL: 'Illinois', IN: 'Indiana', IA: 'Iowa', KS: 'Kansas',
  KY: 'Kentucky', LA: 'Louisiana', ME: 'Maine', MD: 'Maryland',
  MA: 'Massachusetts', MI: 'Michigan', MN: 'Minnesota', MS: 'Mississippi',
  MO: 'Missouri', MT: 'Montana', NE: 'Nebraska', NV: 'Nevada',
  NH: 'New Hampshire', NJ: 'New Jersey', NM: 'New Mexico', NY: 'New York',
  NC: 'North Carolina', ND: 'North Dakota', OH: 'Ohio', OK: 'Oklahoma',
  OR: 'Oregon', PA: 'Pennsylvania', RI: 'Rhode Island', SC: 'South Carolina',
  SD: 'South Dakota', TN: 'Tennessee', TX: 'Texas', UT: 'Utah',
  VT: 'Vermont', VA: 'Virginia', WA: 'Washington', WV: 'West Virginia',
  WI: 'Wisconsin', WY: 'Wyoming',
}

export const FIPS_TO_ABBREV: Record<string, string> = Object.fromEntries(
  Object.entries(STATE_FIPS).map(([abbr, fips]) => [fips, abbr]),
)

export type DimensionKey = 'energy' | 'land' | 'broadband' | 'water'

export interface Dimension {
  key: DimensionKey
  label: string
  rawLabel: string
  rawUnit: string
  strong: string
  moderate: string
  leverage: string
}

export const DIMENSIONS: Dimension[] = [
  {
    key: 'energy',
    label: 'Energy',
    rawLabel: 'Nameplate Capacity',
    rawUnit: 'MW',
    strong: 'Your grid capacity is an asset. Use energy as your opening position to extract concessions on weaker dimensions.',
    moderate: 'Moderate grid capacity. Energy infrastructure investment is a reasonable ask in any development agreement.',
    leverage: 'Grid capacity is a major shortfall. Push hard for substation upgrades, dedicated generation, and renewable PPA commitments.',
  },
  {
    key: 'land',
    label: 'Land',
    rawLabel: 'Potentially Developable Land',
    rawUnit: '%',
    strong: 'Strong land availability is an asset you bring to the table. Hyperscalers need large contiguous sites.',
    moderate: 'Moderate developable land. Site selection terms and land use standards are worth including in negotiations.',
    leverage: 'Limited developable land means you can negotiate on remediation standards, greenfield development commitments, and site remediation requirements.',
  },
  {
    key: 'broadband',
    label: 'Broadband',
    rawLabel: 'Fiber Coverage',
    rawUnit: '%',
    strong: 'Strong existing fiber coverage. Existing infrastructure reduces the operator\'s buildout cost.',
    moderate: 'Moderate fiber coverage. Broadband access agreements are a reasonable inclusion in any community benefit negotiation.',
    leverage: 'Fiber coverage is a gap that could be filled. Push for community access agreements and last-mile buildout commitments written into the deal.',
  },
  {
    key: 'water',
    label: 'Water',
    rawLabel: 'Weeks in Drought',
    rawUnit: '%',
    strong: 'Low drought exposure is an operational advantage for water-intensive datacenter cooling.',
    moderate: 'Moderate water stress. Water use agreements are worth including in datacenter development negotiations.',
    leverage: 'High drought exposure is a real constraint on cooling operations. Negotiate for water recycling requirements, cooling technology standards, and annual usage caps.',
  },
]

export type Tier = 'strong' | 'moderate' | 'leverage'

export const TIER_LABELS: Record<Tier, string> = {
  strong: 'Strong position',
  moderate: 'Moderate',
  leverage: 'Negotiate here',
}

// Score-number colors, aligned with the brand status tokens
export const TIER_COLORS: Record<Tier, string> = {
  strong: '#15803D',
  moderate: '#B45309',
  leverage: '#B91C1C',
}

export const TIER_PRESETS: Record<string, number> = {
  'Small (50 MW)': 50,
  'Medium (150 MW)': 150,
  'Large (300 MW)': 300,
  'Hyperscale (500 MW)': 500,
}

export type TierKey = 'small' | 'medium' | 'large' | 'hyperscale'

export const BROADBAND_MAP: Record<TierKey, { range: string; note: string }> = {
  small: { range: '10-40 Gbps', note: 'Small facilities rely on existing regional carriers.' },
  medium: { range: '40-100 Gbps', note: 'Medium facilities typically require carrier-grade interconnects.' },
  large: { range: '100-400 Gbps', note: 'Large facilities often require dedicated carrier agreements.' },
  hyperscale: { range: '400 Gbps - 1 Tbps+', note: 'Hyperscalers typically build their own fiber infrastructure.' },
}

export const LAND_MAP: Record<TierKey, string> = {
  small: '10-20 acres',
  medium: '50-100 acres',
  large: '100-200 acres',
  hyperscale: '200-1,000+ acres',
}

export type FacilityType = 'Hyperscale (cloud/AI operator)' | 'Colocation (leased/wholesale)'

export const INDIRECT_MULT_MAP: Record<FacilityType, number> = {
  'Hyperscale (cloud/AI operator)': 2.27,
  'Colocation (leased/wholesale)': 1.05,
}

export const INCENTIVE_NORM_MAP: Record<FacilityType, number> = {
  'Hyperscale (cloud/AI operator)': 2,
  'Colocation (leased/wholesale)': 62,
}

export interface InfoSectorCopy {
  number: string
  unit: string
  context: string
  ask: string
}

export const INFO_SECTOR_COPY: Record<FacilityType, InfoSectorCopy> = {
  'Hyperscale (cloud/AI operator)': {
    number: '23%',
    unit: 'information-sector employment gain - but only in counties with 4+ facilities',
    context:
      'A single hyperscale facility shows no statistically significant ecosystem employment effect. ' +
      'Counties that have accumulated 4 or more hyperscale facilities show a 23% information-sector ' +
      'employment gain - this is a facility-clustering effect, not a single-build outcome ' +
      '(Bahar & Wright, 2026, synthetic control study).',
    ask:
      'Don\'t let "tech ecosystem jobs" justify incentives for a single build - the employment upside ' +
      'only materializes with facility clustering. If ecosystem jobs are part of the pitch, tie incentives ' +
      'to follow-on investment commitments rather than this facility alone.',
  },
  'Colocation (leased/wholesale)': {
    number: 'No sig. effect',
    unit: 'information-sector employment impact',
    context:
      'No statistically significant information-sector employment effect was found for colocation ' +
      'facilities, regardless of how many are built in a county (Bahar & Wright, 2026, synthetic ' +
      'control study).',
    ask:
      'Ecosystem job creation is not a reliable justification for colocation incentive requests - anchor ' +
      'negotiating asks on lease revenue, property tax base, and direct facility jobs instead.',
  },
}

// Efficiency + economic constants
export const PUE_MAP: Record<string, number> = { Conservative: 1.56, Default: 1.30, Optimistic: 1.09 }
export const WUE_MAP: Record<string, number> = { Conservative: 1.90, Default: 1.80, Optimistic: 0.15 }

export const HOURS_PER_YEAR = 8760
export const BUILD_PER_MW = 11_300_000
export const FITOUT_PER_MW = 25_000_000
export const PERM_PER_MW = 1.5
export const CONST_PER_MW = 10.0
export const TAX_WINDOW_YEARS = 10
