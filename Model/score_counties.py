# Model/score_counties.py
# Computes four-category percentile scores for all 3,109 CONUS counties
# Benchmarked two ways: against 85 hyperscaler counties, and against all 3,109

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np

MASTER_PATH   = "master_county_dataset.csv"
TRAINING_PATH = "Model/hyperscaler_training.csv"
OUTPUT_PATH   = "Model/county_scores.csv"

# ── Load data ──────────────────────────────────────────────────────────────────

print("Loading data...")
master   = pd.read_csv(MASTER_PATH, dtype={"fips": str})
training = pd.read_csv(TRAINING_PATH, dtype={"fips": str})

# Identify the 85 unique hyperscaler counties
hyperscaler_fips = training["fips"].dropna().unique()
is_hyperscaler   = master["fips"].isin(hyperscaler_fips)

print(f"  Master counties:      {len(master)}")
print(f"  Hyperscaler counties: {is_hyperscaler.sum()}")

hyperscaler_df = master[is_hyperscaler].copy()
national_df    = master.copy()

# ── Define scoring dimensions ──────────────────────────────────────────────────

# Each tuple: (output_name, source_column, higher_is_better)
DIMENSIONS = [
    ("energy",     "NameplateCapacity_OperatingPlanned", True),
    ("land",       "pct_potentially_developable",        True),
    ("broadband",  "FiberCoverage100_20",                True),
    ("water",      "pct_weeks_d1_plus",                  False),  # lower drought = better
]

# ── Percentile scoring function ────────────────────────────────────────────────

def compute_percentile(value, benchmark_series, higher_is_better):
    """
    Given a single value and a benchmark distribution, return the percentile
    of that value within the distribution (0-100). Returns null if value is null.
    Higher_is_better=False inverts the score so it still reads as higher = stronger.
    """
    if pd.isna(value):
        return np.nan

    clean = benchmark_series.dropna()
    if len(clean) == 0:
        return np.nan

    # Percent of benchmark counties this value is >= (or <= if inverted)
    if higher_is_better:
        pct = (clean <= value).sum() / len(clean) * 100
    else:
        pct = (clean >= value).sum() / len(clean) * 100

    return round(pct, 1)

# ── Compute scores ─────────────────────────────────────────────────────────────

print("\nComputing percentile scores...")

scores = master[["fips", "county_name", "state_fips"]].copy()

# Flag hyperscaler counties in the output
scores["is_hyperscaler"] = is_hyperscaler.astype(int)

for dim_name, col, higher_is_better in DIMENSIONS:

    # Raw indicator value (always useful to show alongside the score)
    scores[f"{dim_name}_raw"] = master[col]

    # Score vs. hyperscaler counties
    hyper_benchmark = hyperscaler_df[col]
    scores[f"{dim_name}_vs_hyperscalers"] = master[col].apply(
        lambda v: compute_percentile(v, hyper_benchmark, higher_is_better)
    )

    # Score vs. all national counties
    national_benchmark = national_df[col]
    scores[f"{dim_name}_vs_national"] = master[col].apply(
        lambda v: compute_percentile(v, national_benchmark, higher_is_better)
    )

    # Report null counts
    null_count = scores[f"{dim_name}_vs_hyperscalers"].isna().sum()
    print(f"  {dim_name:<12} nulls: {null_count}")

# ── Sanity check ───────────────────────────────────────────────────────────────

print("\nSanity check — mean scores for hyperscaler counties (should be well above 50):")
hyper_scores = scores[scores["is_hyperscaler"] == 1]
for dim_name, _, _ in DIMENSIONS:
    mean_vs_h = hyper_scores[f"{dim_name}_vs_hyperscalers"].mean()
    mean_vs_n = hyper_scores[f"{dim_name}_vs_national"].mean()
    print(f"  {dim_name:<12} vs hyperscalers: {mean_vs_h:.1f}   vs national: {mean_vs_n:.1f}")

# ── Save ───────────────────────────────────────────────────────────────────────

scores.to_csv(OUTPUT_PATH, index=False)
print(f"\nSaved as {OUTPUT_PATH}")
print(f"  {len(scores)} counties, {len(scores.columns)} columns")