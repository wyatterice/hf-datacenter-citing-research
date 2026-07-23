# Dashboard/app.py
# Heartland Forward — Datacenter Impact Research Tool
# Streamlit dashboard for county-level infrastructure benchmarking

import sys
import os
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import streamlit as st
import pandas as pd
import numpy as np
from fips_utils import STATE_FIPS

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Datacenter Impact Research Tool",
    page_icon="⚡",
    layout="wide"
)

# ── Constants ──────────────────────────────────────────────────────────────────

SCORES_PATH = os.path.join(REPO_ROOT, "Model", "county_scores.csv")

FIPS_TO_ABBREV = {str(v).zfill(2): k for k, v in STATE_FIPS.items()}

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming"
}

DIMENSIONS = [
    {
        "key":        "energy",
        "label":      "Energy",
        "icon":       "⚡",
        "raw_label":  "Nameplate Capacity",
        "raw_unit":   "MW",
        "strong":     "Your grid capacity is an asset. Use energy as your opening position to extract concessions on weaker dimensions.",
        "moderate":   "Moderate grid capacity. Energy infrastructure investment is a reasonable ask in any development agreement.",
        "leverage":   "Grid capacity is a major shortfall. Push hard for substation upgrades, dedicated generation, and renewable PPA commitments."
    },
    {
        "key":        "land",
        "label":      "Land",
        "icon":       "🏗",
        "raw_label":  "Potentially Developable Land",
        "raw_unit":   "%",
        "strong":     "Strong land availability is an asset you bring to the table. Hyperscalers need large contiguous sites.",
        "moderate":   "Moderate developable land. Site selection terms and land use standards are worth including in negotiations.",
        "leverage":   "Limited developable land means you can negotiate on remediation standards, greenfield development commitments, and site remediation requirements."
    },
    {
        "key":        "broadband",
        "label":      "Broadband",
        "icon":       "🌐",
        "raw_label":  "Fiber Coverage",
        "raw_unit":   "%",
        "strong":     "Strong existing fiber coverage. Existing infrastructure reduces the operator's buildout cost.",
        "moderate":   "Moderate fiber coverage. Broadband access agreements are a reasonable inclusion in any community benefit negotiation.",
        "leverage":   "Fiber coverage is a gap that could be filled. Push for community access agreements and last-mile buildout commitments written into the deal."
    },
    {
        "key":        "water",
        "label":      "Water",
        "icon":       "💧",
        "raw_label":  "Weeks in Drought",
        "raw_unit":   "%",
        "strong":     "Low drought exposure is an operational advantage for water-intensive datacenter cooling.",
        "moderate":   "Moderate water stress. Water use agreements are worth including in datacenter development negotiations.",
        "leverage":   "High drought exposure is a real constraint on cooling operations. Negotiate for water recycling requirements, cooling technology standards, and annual usage caps."
    }
]

# ── Custom CSS ─────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .tool-header {
        background: #0F2640;
        color: white;
        padding: 2rem 2.5rem;
        border-radius: 10px;
        margin-bottom: 1.75rem;
    }
    .tool-header h1 {
        font-size: 1.6rem;
        font-weight: 800;
        margin: 0 0 0.3rem 0;
        color: white;
        letter-spacing: -0.02em;
    }
    .tool-header p {
        font-size: 0.9rem;
        margin: 0;
        color: #7FA8CC;
    }

    .controls-row {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.5rem;
    }

    .section-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94A3B8;
        margin-bottom: 1rem;
    }

    .score-card {
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.5rem 1.4rem;
        background: white;
        height: 100%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .card-header {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #64748B;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .score-number {
        font-size: 3.2rem;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.03em;
        margin-bottom: 0.3rem;
    }
    .score-suffix {
        font-size: 1.1rem;
        font-weight: 500;
        opacity: 0.7;
    }
    .tier-pill {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.2rem 0.65rem;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 1.1rem;
    }
    .tier-strong   { background: #DCFCE7; color: #15803D; }
    .tier-moderate { background: #FEF9C3; color: #A16207; }
    .tier-leverage { background: #FEE2E2; color: #B91C1C; }

    .raw-value {
        font-size: 0.82rem;
        color: #64748B;
        margin-bottom: 0.9rem;
        padding-bottom: 0.9rem;
        border-bottom: 1px solid #F1F5F9;
    }
    .raw-value strong { color: #1E293B; }

    .insight-box {
        font-size: 0.78rem;
        line-height: 1.5;
        color: #334155;
        background: #F8FAFC;
        border-left: 3px solid #CBD5E1;
        padding: 0.65rem 0.8rem;
        border-radius: 0 6px 6px 0;
    }
    .insight-box.insight-strong   { border-color: #4ADE80; }
    .insight-box.insight-moderate { border-color: #FCD34D; }
    .insight-box.insight-leverage { border-color: #FCA5A5; }

    .no-data-score {
        font-size: 0.82rem;
        color: #94A3B8;
        font-style: italic;
        margin-bottom: 1rem;
    }

    .hyperscaler-badge {
        background: #0F2640;
        color: #7FA8CC;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────────

@st.cache_data
def load_scores():
    df = pd.read_csv(SCORES_PATH, dtype={"fips": str})
    df["state_fips"] = df["state_fips"].astype(str).str.zfill(2)
    df["state_abbr"] = df["state_fips"].map(FIPS_TO_ABBREV)
    df["state_name"] = df["state_abbr"].map(STATE_NAMES)
    return df

scores = load_scores()

# ── Header ─────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="tool-header">
    <h1>⚡ Datacenter Impact Research Tool</h1>
    <p>Heartland Forward &nbsp;·&nbsp; County-level infrastructure benchmarking for datacenter investment negotiations</p>
</div>
""", unsafe_allow_html=True)

# ── Controls ───────────────────────────────────────────────────────────────────

col_state, col_county, col_gap, col_bench = st.columns([2, 2, 0.5, 3])

with col_state:
    state_options = sorted(scores["state_name"].dropna().unique())
    selected_state = st.selectbox("State", state_options)

with col_county:
    state_counties = (
        scores[scores["state_name"] == selected_state]
        .sort_values("county_name")
        .copy()
    )
    # Disambiguate duplicate names within a state by appending FIPS
    name_counts = state_counties["county_name"].value_counts()
    state_counties["display_name"] = state_counties.apply(
        lambda r: f"{r['county_name']} ({r['fips']})"
        if name_counts[r["county_name"]] > 1
        else r["county_name"],
        axis=1
    )
    display_options = state_counties["display_name"].tolist()
    selected_display = st.selectbox("County", display_options)

    # Map display name back to the actual row
    selected_county = state_counties[
        state_counties["display_name"] == selected_display
    ]["county_name"].iloc[0]
    selected_fips = state_counties[
        state_counties["display_name"] == selected_display
    ]["fips"].iloc[0]

with col_bench:
    benchmark = st.radio(
        "Benchmark against",
        ["Hyperscaler Counties", "All US Counties"],
        horizontal=True
    )

bench_suffix = "vs_hyperscalers" if benchmark == "Hyperscaler Counties" else "vs_national"
bench_label  = "vs. counties where hyperscalers have built" if benchmark == "Hyperscaler Counties" else "vs. all US counties"

# ── Selected county row ────────────────────────────────────────────────────────

row = scores[scores["fips"] == selected_fips].iloc[0]

# Hyperscaler badge
if row["is_hyperscaler"] == 1:
    st.markdown(
        '<span class="hyperscaler-badge">✓ Active hyperscaler investment county</span>',
        unsafe_allow_html=True
    )

st.markdown(
    f'<div class="section-label">Percentile scores — {bench_label}</div>',
    unsafe_allow_html=True
)

# ── Helper functions ───────────────────────────────────────────────────────────

def get_tier(score):
    if pd.isna(score): return None
    if score >= 60:    return "strong"
    if score >= 30:    return "moderate"
    return "leverage"

TIER_LABELS = {
    "strong":   "Strong position",
    "moderate": "Moderate",
    "leverage": "Negotiate here"
}

TIER_COLORS = {
    "strong":   "#15803D",
    "moderate": "#A16207",
    "leverage": "#B91C1C"
}

# ── Score cards ────────────────────────────────────────────────────────────────

cols = st.columns(4)

for i, dim in enumerate(DIMENSIONS):
    score   = row.get(f"{dim['key']}_{bench_suffix}")
    raw_val = row.get(f"{dim['key']}_raw")
    tier    = get_tier(score)

    with cols[i]:
        # Build score HTML
        if pd.isna(score):
            score_html = '<div class="no-data-score">Data unavailable for this county</div>'
            tier_html  = ""
            insight_html = ""
        else:
            color = TIER_COLORS[tier]
            n = int(round(score))
            if 11 <= (n % 100) <= 13:
                suffix = "th"
            elif n % 10 == 1:
                suffix = "st"
            elif n % 10 == 2:
                suffix = "nd"
            elif n % 10 == 3:
                suffix = "rd"
            else:
                suffix = "th"
            score_html = (
                f'<div class="score-number" style="color:{color}">'
                f'{score:.0f}<span class="score-suffix">{suffix}</span>'
                f'</div>'
            )
            tier_html = (
                f'<span class="tier-pill tier-{tier}">'
                f'{TIER_LABELS[tier]}'
                f'</span>'
            )
            insight_html = (
                f'<div class="insight-box insight-{tier}">'
                f'{dim[tier]}'
                f'</div>'
            )

        # Build raw value HTML
        if pd.isna(score):
            raw_html = ""
        elif pd.isna(raw_val):
            raw_html = '<div class="raw-value">No data</div>'
        else:
            raw_html = (
                f'<div class="raw-value">'
                f'{dim["raw_label"]}: <strong>{raw_val:,.1f} {dim["raw_unit"]}</strong>'
                f'</div>'
            )

        st.markdown(f"""
        <div class="score-card">
            <div class="card-header">{dim['icon']} {dim['label']}</div>
            {score_html}
            {tier_html}
            {raw_html}
            {insight_html}
        </div>
        """, unsafe_allow_html=True)

# ── Infrastructure Impact Estimator ───────────────────────────────────────────

st.markdown("""
<style>
    .est-header {
        background: #0F2640;
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-top: 2.5rem;
        margin-bottom: 1.25rem;
    }
    .est-header h2 {
        font-size: 1.2rem;
        font-weight: 800;
        margin: 0 0 0.25rem 0;
        color: white;
        letter-spacing: -0.02em;
    }
    .est-header p {
        font-size: 0.85rem;
        margin: 0;
        color: #7FA8CC;
    }
    .impact-number {
        font-size: 2.4rem;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.02em;
        color: #0F2640;
        margin-bottom: 0.2rem;
    }
    .impact-unit {
        font-size: 0.8rem;
        color: #64748B;
        font-weight: 500;
        margin-bottom: 0.6rem;
    }
    .impact-sub {
        font-size: 0.78rem;
        color: #475569;
        margin-bottom: 0.5rem;
    }
    .impact-context {
        font-size: 0.76rem;
        color: #334155;
        background: #F8FAFC;
        border-left: 3px solid #CBD5E1;
        padding: 0.55rem 0.75rem;
        border-radius: 0 6px 6px 0;
        line-height: 1.5;
        margin-top: 0.6rem;
    }
    .impact-ask {
        font-size: 0.76rem;
        color: #7C2D12;
        background: #FFF7ED;
        border-left: 3px solid #F59E0B;
        padding: 0.55rem 0.75rem;
        border-radius: 0 6px 6px 0;
        line-height: 1.5;
        margin-top: 0.5rem;
    }
    .econ-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #64748B;
        margin-bottom: 0.6rem;
    }
    .econ-number {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.02em;
        color: #0F2640;
        margin-bottom: 0.2rem;
    }
    .est-caveat {
        font-size: 0.74rem;
        color: #94A3B8;
        font-style: italic;
        line-height: 1.55;
        margin-top: 1.25rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="est-header">
    <h2>🏭 Infrastructure Impact Estimator</h2>
    <p>Translate facility scale into infrastructure demand and economic output — framed as negotiation leverage.</p>
</div>
""", unsafe_allow_html=True)

# — Controls —
TIER_PRESETS = {
    "Small (50 MW)":        50,
    "Medium (150 MW)":     150,
    "Large (300 MW)":      300,
    "Hyperscale (500 MW)": 500,
}

est_c1, est_c2 = st.columns([1, 1])

with est_c1:
    selected_tier = st.selectbox(
        "Facility scale",
        list(TIER_PRESETS.keys()),
        key="est_tier"
    )

with est_c2:
    custom_mw_raw = st.number_input(
        "Custom IT load (MW) — overrides preset",
        min_value=1,
        max_value=2000,
        value=None,
        key="est_custom_mw"
    )

est_c3, est_c4, est_c5 = st.columns([1, 1.3, 1.3])

with est_c3:
    energy_efficiency = st.radio(
        "Energy efficiency scenario",
        ["Conservative", "Default", "Optimistic"],
        index=1,
        horizontal=True,
        key="est_energy_efficiency"
    )

with est_c4:
    water_efficiency = st.radio(
        "Water efficiency scenario",
        ["Conservative", "Optimistic", "Closed-Loop"],
        index=0,
        horizontal=True,
        key="est_water_efficiency"
    )

with est_c5:
    facility_type = st.radio(
        "Facility type",
        ["Hyperscale (cloud/AI operator)", "Colocation (leased/wholesale)"],
        index=0,
        key="est_facility_type"
    )

facility_type_label = "Hyperscale" if facility_type.startswith("Hyperscale") else "Colocation"

it_load_mw = float(custom_mw_raw) if custom_mw_raw is not None else float(TIER_PRESETS[selected_tier])

# Derive tier key from actual MW for broadband/land range lookups
def mw_to_tier_key(mw):
    if mw <= 100:  return "small"
    if mw <= 225:  return "medium"
    if mw <= 400:  return "large"
    return "hyperscale"

tier_key = mw_to_tier_key(it_load_mw)

# — Efficiency constants —
PUE_MAP = {"Conservative": 1.56, "Default": 1.30, "Optimistic": 1.09}
# Closed-loop floors at 0.02 L/kWh, not 0.0 — real makeup water needs (evaporation
# losses, blowdown, refill) persist even in closed-loop systems.
WUE_MAP = {"Conservative": 1.80, "Optimistic": 0.15, "Closed-Loop": 0.02}

pue = PUE_MAP[energy_efficiency]
wue = WUE_MAP[water_efficiency]

HOURS_PER_YEAR  = 8_760
BUILD_PER_MW    = 11_300_000
FITOUT_PER_MW   = 25_000_000

# Permanent on-site staffing — Bahar & Wright (2026): automation decouples staffing
# from facility size, so headcount is fixed per facility (observed range 50-200) rather
# than scaling with MW.
PERMANENT_JOBS_FIXED = 150

# Peak construction jobs — linear interpolation from 500 jobs at 50 MW to 3,000 jobs
# at 500 MW, clamped at both ends. The 3,000 upper bound is anchored to Meta's disclosed
# ~3,000 peak construction jobs for its 1GW Alberta AI campus.
CONST_JOBS_MW_LOW,   CONST_JOBS_MW_HIGH   = 50, 500
CONST_JOBS_AT_LOW,   CONST_JOBS_AT_HIGH   = 500, 3_000

def construction_jobs_for(mw):
    if mw <= CONST_JOBS_MW_LOW:
        return float(CONST_JOBS_AT_LOW)
    if mw >= CONST_JOBS_MW_HIGH:
        return float(CONST_JOBS_AT_HIGH)
    frac = (mw - CONST_JOBS_MW_LOW) / (CONST_JOBS_MW_HIGH - CONST_JOBS_MW_LOW)
    return CONST_JOBS_AT_LOW + frac * (CONST_JOBS_AT_HIGH - CONST_JOBS_AT_LOW)

# Indirect jobs multiplier — Bahar & Wright (2026) synthetic control study
INDIRECT_MULT_MAP = {
    "Hyperscale (cloud/AI operator)": 2.27,
    "Colocation (leased/wholesale)":  1.05,
}
indirect_mult = INDIRECT_MULT_MAP[facility_type]

# — Energy —
grid_draw_mw = it_load_mw * pue
energy_raw_val = row.get("energy_raw")
if not pd.isna(energy_raw_val) and float(energy_raw_val) > 0:
    pct_of_county = (grid_draw_mw / float(energy_raw_val)) * 100
    capacity_note = (
        f"{pct_of_county:.1f}% of {selected_county}'s "
        f"{float(energy_raw_val):,.0f} MW nameplate capacity. "
        "Nameplate is theoretical maximum, not available headroom."
    )
else:
    capacity_note = "County nameplate capacity data not available. Nameplate is theoretical maximum, not available headroom."

# — Water —
it_load_kw     = it_load_mw * 1_000
annual_liters  = it_load_kw * HOURS_PER_YEAR * wue
annual_gallons = annual_liters / 3.785
daily_gallons  = annual_gallons / 365

def fmt_gallons_daily(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M gallons/day"
    return f"{n/1_000:.0f}K gallons/day"

# — Broadband —
BROADBAND_MAP = {
    "small":      ("10–40 Gbps",         "Small facilities rely on existing regional carriers."),
    "medium":     ("40–100 Gbps",        "Medium facilities typically require carrier-grade interconnects."),
    "large":      ("100–400 Gbps",       "Large facilities often require dedicated carrier agreements."),
    "hyperscale": ("400 Gbps – 1 Tbps+", "Hyperscalers typically build their own fiber infrastructure."),
}
bb_range, bb_note = BROADBAND_MAP[tier_key]

broadband_score = row.get(f"broadband_{bench_suffix}")
if get_tier(broadband_score) == "leverage" or tier_key == "hyperscale":
    bb_ask = "Low local fiber coverage is leverage — push for community access agreements and last-mile buildout written into the development deal."
else:
    bb_ask = "Require fiber access and community connectivity terms as part of the development agreement."

# — Land —
LAND_MAP = {
    "small":      "10–20 acres",
    "medium":     "50–100 acres",
    "large":      "100–200 acres",
    "hyperscale": "200–1,000+ acres",
}
land_range = LAND_MAP[tier_key]

# — Economics —
def fmt_dollars(n):
    if n >= 1_000_000_000:
        return f"${n/1_000_000_000:.2f}B"
    return f"${n/1_000_000:.0f}M"

construction_cost = it_load_mw * BUILD_PER_MW
ai_total_cost     = it_load_mw * (BUILD_PER_MW + FITOUT_PER_MW)
permanent_jobs    = float(PERMANENT_JOBS_FIXED)
construction_jobs = construction_jobs_for(it_load_mw)
indirect_jobs     = permanent_jobs * indirect_mult

# — Infrastructure demand cards —
st.markdown(
    f'<div class="section-label" style="margin-top:1.25rem">'
    f'Infrastructure demand — {it_load_mw:.0f} MW IT load'
    f'&nbsp;·&nbsp; PUE {pue}&nbsp;·&nbsp; WUE {wue} L/kWh'
    f'</div>',
    unsafe_allow_html=True
)

icols = st.columns(4)

with icols[0]:
    st.markdown(f"""
    <div class="score-card">
        <div class="card-header">⚡ Energy demand</div>
        <div class="impact-number">{grid_draw_mw:,.0f}</div>
        <div class="impact-unit">MW grid draw (IT load × PUE {pue})</div>
        <div class="impact-context">{capacity_note}</div>
        <div class="impact-ask">Require operator to fund grid improvements — substation upgrades, dedicated feeders, or new generation — as a condition of the development agreement.</div>
    </div>
    """, unsafe_allow_html=True)

with icols[1]:
    st.markdown(f"""
    <div class="score-card">
        <div class="card-header">💧 Water demand</div>
        <div class="impact-number">{annual_gallons/1_000_000:.1f}M</div>
        <div class="impact-unit">gallons per year ({annual_liters/1_000_000:.0f}M liters)</div>
        <div class="impact-sub">{fmt_gallons_daily(daily_gallons)} — large facilities can reach 5M gallons/day</div>
        <div class="impact-ask">Negotiate water recycling requirements, closed-loop cooling standards, and annual usage caps into the permit or development agreement.</div>
    </div>
    """, unsafe_allow_html=True)

with icols[2]:
    st.markdown(f"""
    <div class="score-card">
        <div class="card-header">🌐 Connectivity demand</div>
        <div class="impact-number" style="font-size:1.5rem;margin-bottom:0.3rem">{bb_range}</div>
        <div class="impact-unit">estimated connectivity requirement</div>
        <div class="impact-context">{bb_note}</div>
        <div class="impact-ask">{bb_ask}</div>
    </div>
    """, unsafe_allow_html=True)

with icols[3]:
    st.markdown(f"""
    <div class="score-card">
        <div class="card-header">🏗 Land footprint</div>
        <div class="impact-number" style="font-size:1.5rem;margin-bottom:0.3rem">{land_range}</div>
        <div class="impact-unit">estimated site footprint</div>
        <div class="impact-ask">Site selection terms, land use standards, and greenfield development commitments are all reasonable asks in a development agreement.</div>
    </div>
    """, unsafe_allow_html=True)

# — Economic impact cards —
st.markdown(
    '<div class="section-label" style="margin-top:1.75rem">Economic impact</div>',
    unsafe_allow_html=True
)

ecols = st.columns(5)
econ_items = [
    ("Shell + core cost",  fmt_dollars(construction_cost), "at $11.3M per MW"),
    ("With AI fit-out",    fmt_dollars(ai_total_cost),     "at $36.3M per MW"),
    ("Permanent jobs",     f"{permanent_jobs:,.0f}",        "fixed ~150 on-site staff — doesn't scale with MW (Bahar & Wright 2026)"),
    ("Construction jobs",  f"{construction_jobs:,.0f}",     "500 at 50 MW → 3,000 at 500 MW (Meta 1GW Alberta anchor)"),
    ("Indirect jobs",      f"{indirect_jobs:,.0f}",         f"{indirect_mult:g}× permanent jobs ({facility_type_label}, Bahar & Wright 2026)"),
]

for j, (label, number, note) in enumerate(econ_items):
    with ecols[j]:
        st.markdown(f"""
        <div class="score-card">
            <div class="econ-label">{label}</div>
            <div class="econ-number">{number}</div>
            <div class="impact-unit">{note}</div>
        </div>
        """, unsafe_allow_html=True)

# — Information-sector job creation (ecosystem employment effect) —
INFO_SECTOR_COPY = {
    "Hyperscale (cloud/AI operator)": {
        "number":  "23%",
        "unit":    "information-sector employment gain — but only in counties with 4+ facilities",
        "context": (
            "A single hyperscale facility shows no statistically significant ecosystem employment effect. "
            "Counties that have accumulated 4 or more hyperscale facilities show a 23% information-sector "
            "employment gain — this is a facility-clustering effect, not a single-build outcome "
            "(Bahar & Wright, 2026, synthetic control study)."
        ),
        "ask": (
            "Don't let \"tech ecosystem jobs\" justify incentives for a single build — the employment upside "
            "only materializes with facility clustering. If ecosystem jobs are part of the pitch, tie incentives "
            "to follow-on investment commitments rather than this facility alone."
        ),
    },
    "Colocation (leased/wholesale)": {
        "number":  "No sig. effect",
        "unit":    "information-sector employment impact",
        "context": (
            "No statistically significant information-sector employment effect was found for colocation "
            "facilities, regardless of how many are built in a county (Bahar & Wright, 2026, synthetic "
            "control study)."
        ),
        "ask": (
            "Ecosystem job creation is not a reliable justification for colocation incentive requests — anchor "
            "negotiating asks on lease revenue, property tax base, and direct facility jobs instead."
        ),
    },
}
info_copy = INFO_SECTOR_COPY[facility_type]

st.markdown(f"""
<div class="score-card" style="margin-top:1rem">
    <div class="card-header">📊 Information-sector job creation — {facility_type_label}</div>
    <div class="impact-number" style="font-size:1.8rem">{info_copy['number']}</div>
    <div class="impact-unit">{info_copy['unit']}</div>
    <div class="impact-context">{info_copy['context']}</div>
    <div class="impact-ask">{info_copy['ask']}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="est-caveat">
    ⚠ Nameplate capacity is theoretical maximum generation; available headroom depends on existing load,
    transmission constraints, and grid operator scheduling.
    A single datacenter facility creates modest permanent employment — on-site operational staffing is modeled
    as a fixed ~150 people per facility (observed range 50–200), since data centers are highly automated and
    staffing doesn't scale with size (Bahar & Wright, 2026). Peak construction employment scales from 500 jobs
    at 50 MW to 3,000 jobs at 500 MW, anchored to Meta's disclosed ~3,000 peak construction jobs for its 1GW
    Alberta AI campus — multi-gigawatt megacampuses like Meta's 5GW Richland Parish expansion (7,500+ peak
    construction jobs) sit at a different negotiating scale entirely and aren't modeled here. Ecosystem
    employment concentrates in hyperscale clusters over time, not in a single facility's direct hire
    (Brookings, 2026).
</div>
""", unsafe_allow_html=True)

# — Tax & Incentive Estimator —
st.markdown(
    '<div class="section-label" style="margin-top:1.75rem">Tax & incentive estimator</div>',
    unsafe_allow_html=True
)

cost_basis = st.radio(
    "Cost basis for assessed value",
    ["Shell + core", "Shell + core + AI fit-out"],
    index=0,
    horizontal=True,
    key="est_cost_basis"
)
selected_total_cost = construction_cost if cost_basis == "Shell + core" else ai_total_cost

tax_i1, tax_i2, tax_i3, tax_i4 = st.columns(4)

with tax_i1:
    millage_rate = st.number_input(
        "Local millage rate ($ per $1,000 assessed value)",
        min_value=0.0,
        value=20.0,
        step=0.5,
        key="est_millage"
    )

with tax_i2:
    assessment_ratio = st.number_input(
        "Assessment ratio (%)",
        min_value=1.0,
        max_value=100.0,
        value=100.0,
        step=1.0,
        key="est_assess_ratio"
    )

with tax_i3:
    abatement_pct = st.slider(
        "Abatement (%)",
        min_value=0,
        max_value=100,
        value=0,
        step=1,
        key="est_abatement_pct"
    )

with tax_i4:
    abatement_years = st.number_input(
        "Abatement duration (years)",
        min_value=0,
        max_value=50,
        value=10,
        step=1,
        key="est_abatement_years"
    )

def fmt_dollars_tax(n):
    if n >= 1_000_000_000:
        return f"${n/1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"${n/1_000_000:.2f}M"
    return f"${n:,.0f}"

assessed_value     = selected_total_cost * (assessment_ratio / 100)
annual_tax_full     = assessed_value * (millage_rate / 1000)
annual_tax_abated   = annual_tax_full * (1 - abatement_pct / 100)

TAX_WINDOW_YEARS         = 10
abated_years_in_window   = min(abatement_years, TAX_WINDOW_YEARS)
full_years_in_window     = TAX_WINDOW_YEARS - abated_years_in_window
revenue_without_abatement = annual_tax_full * TAX_WINDOW_YEARS
revenue_with_abatement    = (annual_tax_abated * abated_years_in_window) + (annual_tax_full * full_years_in_window)
revenue_gap               = revenue_without_abatement - revenue_with_abatement

INCENTIVE_NORM_MAP = {
    "Hyperscale (cloud/AI operator)": 2,
    "Colocation (leased/wholesale)":  62,
}
incentive_norm_pct = INCENTIVE_NORM_MAP[facility_type]

tax_cols = st.columns(3)

with tax_cols[0]:
    st.markdown(f"""
    <div class="score-card">
        <div class="card-header">💰 Annual tax — full rate</div>
        <div class="impact-number" style="font-size:1.8rem">{fmt_dollars_tax(annual_tax_full)}</div>
        <div class="impact-unit">assessed value {fmt_dollars_tax(assessed_value)} × {millage_rate:g} mills</div>
    </div>
    """, unsafe_allow_html=True)

with tax_cols[1]:
    st.markdown(f"""
    <div class="score-card">
        <div class="card-header">🏷 Annual tax — during abatement</div>
        <div class="impact-number" style="font-size:1.8rem">{fmt_dollars_tax(annual_tax_abated)}</div>
        <div class="impact-unit">at {abatement_pct}% abatement for {abatement_years} year(s)</div>
    </div>
    """, unsafe_allow_html=True)

with tax_cols[2]:
    st.markdown(f"""
    <div class="score-card">
        <div class="card-header">📉 10-year revenue gap</div>
        <div class="impact-number" style="font-size:1.8rem">{fmt_dollars_tax(revenue_gap)}</div>
        <div class="impact-unit">{fmt_dollars_tax(revenue_with_abatement)} with abatement vs. {fmt_dollars_tax(revenue_without_abatement)} without</div>
        <div class="impact-context">Your modeled abatement is {abatement_pct}% of assessed value. Bahar & Wright (2026) find incentives average
        ~{incentive_norm_pct}% of investment in {facility_type_label.lower()} deals — use that as a real-world benchmark for this facility type.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="est-caveat">
    ℹ Sales tax exemptions on equipment purchases (servers, cooling, switchgear) are common in datacenter
    incentive packages and are not modeled above. Virginia's data center sales-tax exemption alone cost an
    estimated $1.6B in FY2025 — confirm whether an equivalent exemption applies in your state before finalizing
    incentive comparisons.
</div>
""", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)
st.caption(
    "Percentile scores show how this county ranks on each dimension relative to the selected benchmark group. "
    "Higher score = stronger position or leverage held. Lower score = stronger negotiating ask. "
    "Energy and broadband unavailable for 827 counties (EIA/FCC coverage gap). "
    "Water score is inverted — higher score reflects less drought exposure. "
    "Sources: EIA-860/923, FCC Broadband Map, NOAA Climate, US Drought Monitor, NLCD 2024, PAD-US 4.1."
)