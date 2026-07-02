# Dashboard/app.py
# Heartland Forward — Datacenter Siting Research Tool
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
        "strong":     "Your grid capacity is a genuine asset. Lead with it — use energy as your opening position to extract concessions on weaker dimensions.",
        "moderate":   "Moderate grid capacity. Energy infrastructure investment is a reasonable ask in any development agreement.",
        "leverage":   "Grid capacity is your biggest gap. Push hard for substation upgrades, dedicated generation, and renewable PPA commitments as part of the deal."
    },
    {
        "key":        "land",
        "label":      "Land",
        "icon":       "🏗",
        "raw_label":  "Potentially Developable Land",
        "raw_unit":   "%",
        "strong":     "Strong land availability is a real asset you bring to the table. Hyperscalers need large contiguous sites.",
        "moderate":   "Moderate developable land. Site selection terms and land use standards are worth including in negotiations.",
        "leverage":   "Limited developable land means you can negotiate on remediation standards, greenfield development commitments, and site remediation requirements."
    },
    {
        "key":        "broadband",
        "label":      "Broadband",
        "icon":       "🌐",
        "raw_label":  "Fiber Coverage",
        "raw_unit":   "%",
        "strong":     "Strong existing fiber coverage. Less room to negotiate here, but existing infrastructure reduces the operator's buildout cost.",
        "moderate":   "Moderate fiber coverage. Broadband access agreements are a reasonable inclusion in any community benefit negotiation.",
        "leverage":   "Hyperscalers bring fiber infrastructure — your low coverage is leverage. Push for community access agreements and last-mile buildout commitments written into the deal."
    },
    {
        "key":        "water",
        "label":      "Water",
        "icon":       "💧",
        "raw_label":  "Weeks in Drought",
        "raw_unit":   "%",
        "strong":     "Low drought exposure is a genuine operational advantage for water-intensive datacenter cooling. A real asset.",
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
    <h1>⚡ Datacenter Siting Research Tool</h1>
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
            insight_html = '<div class="insight-box">EIA/FCC data is not available for this county. Score cannot be computed.</div>'
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
        if pd.isna(raw_val):
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
            <br>
            {raw_html}
            {insight_html}
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