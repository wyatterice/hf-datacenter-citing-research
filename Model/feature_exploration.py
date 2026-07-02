# Model/feature_exploration.py
# Explores which features best separate hyperscaler counties from non-hyperscaler counties
# Computes point-biserial correlation and mean comparison for every numeric feature

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from scipy.stats import pointbiserialr

MASTER_PATH   = "master_county_dataset.csv"
TRAINING_PATH = "Model/hyperscaler_training.csv"

# ── Load and label ─────────────────────────────────────────────────────────────

print("Loading data...")
master   = pd.read_csv(MASTER_PATH, dtype={"fips": str})
training = pd.read_csv(TRAINING_PATH, dtype={"fips": str})

# Deduplicate training to one row per county, label as 1
positive_fips = training["fips"].dropna().unique()
master["label"] = master["fips"].isin(positive_fips).astype(int)

print(f"  Total counties:    {len(master)}")
print(f"  Positive counties: {master['label'].sum()} (unique hyperscaler counties)")
print(f"  Negative counties: {(master['label'] == 0).sum()}")

# ── Compute correlations ───────────────────────────────────────────────────────

print("\nComputing feature correlations with label...")

# Only numeric columns, drop identifiers and the label itself
exclude = ["fips", "state_fips", "label", "RISK_SPCTL"]
numeric_cols = [c for c in master.select_dtypes(include=[np.number]).columns
                if c not in exclude]

results = []

for col in numeric_cols:
    series = master[col]
    valid  = master[["label", col]].dropna()

    if len(valid) < 100:
        continue  # skip columns with too many nulls to be useful

    corr, pval = pointbiserialr(valid["label"], valid[col])

    mean_pos = valid[valid["label"] == 1][col].mean()
    mean_neg = valid[valid["label"] == 0][col].mean()
    n_valid  = len(valid)

    results.append({
        "feature":   col,
        "corr":      round(corr, 4),
        "abs_corr":  round(abs(corr), 4),
        "pval":      round(pval, 4),
        "mean_pos":  round(mean_pos, 3),
        "mean_neg":  round(mean_neg, 3),
        "n_valid":   n_valid
    })

results_df = pd.DataFrame(results).sort_values("abs_corr", ascending=False)

# ── Print results ──────────────────────────────────────────────────────────────

print(f"\n{'Feature':<45} {'Corr':>7} {'p-val':>7} {'Mean(+)':>10} {'Mean(-)':>10} {'N':>6}")
print("-" * 90)

for _, row in results_df.iterrows():
    sig = "**" if row["pval"] < 0.05 else "  "
    print(f"{sig}{row['feature']:<43} {row['corr']:>7.4f} {row['pval']:>7.4f} "
          f"{row['mean_pos']:>10.3f} {row['mean_neg']:>10.3f} {row['n_valid']:>6}")

print("\n** = statistically significant at p < 0.05")

# ── Save results ───────────────────────────────────────────────────────────────

results_df.to_csv("Model/feature_correlations.csv", index=False)
print("\nSaved as Model/feature_correlations.csv")