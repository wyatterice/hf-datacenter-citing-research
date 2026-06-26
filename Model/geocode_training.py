# Model/geocode_training.py
# Fills the fips column in the hyperscaler training dataset
# by matching county + state against the Census TIGER shapefile —
# the same source used to build the master dataset

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import geopandas as gpd
from fips_utils import standardize_fips, STATE_FIPS

SHAPEFILE_PATH = r"C:\Users\WYATTRICE\OneDrive - Walton Enterprises LLC\Desktop\Projects\hf-datacenter-citing-research\Land\tl_2025_us_county\tl_2025_us_county.shp"
TRAINING_INPUT  = "Model/hyperscaler_facilities.csv"
TRAINING_OUTPUT = "Model/hyperscaler_training.csv"

# ── Build county lookup from Census TIGER shapefile ───────────────────────────

print("Building FIPS lookup from Census TIGER shapefile...")
counties = gpd.read_file(SHAPEFILE_PATH)
counties = counties[["GEOID", "NAME", "STATEFP"]].copy()

# Dict: (normalized_county_name, state_fips) -> 5-digit fips
lookup = {}
for _, row in counties.iterrows():
    key = (row["NAME"].lower().strip(), row["STATEFP"])
    lookup[key] = row["GEOID"]

print(f"  Lookup built: {len(lookup)} counties")

# ── Load training dataset ─────────────────────────────────────────────────────

print("\nLoading training dataset...")
df = pd.read_csv(TRAINING_INPUT)

# Force fips column to string dtype so we can write FIPS strings into it
df["fips"] = df["fips"].astype(object)

print(f"  Facilities loaded: {len(df)} rows")

# ── Geocode: match county + state_abbr to FIPS ───────────────────────────────

print("\nGeocoding...")

matched = 0
failed = []

for i, row in df.iterrows():
    county_name = str(row["county"]).lower().strip()
    state_abbr  = str(row["state_abbr"]).strip().upper()

    # Strip suffixes so "Richland Parish" matches "Richland" in the shapefile
    for suffix in [" county", " parish", " borough", " census area"]:
        if county_name.endswith(suffix):
            county_name = county_name[: -len(suffix)]
            break

    state_fips = STATE_FIPS.get(state_abbr)
    if not state_fips:
        failed.append((i, row["company"], row["city"], row["county"], row["state_abbr"], "Unknown state abbreviation"))
        continue

    key  = (county_name, state_fips)
    fips = lookup.get(key)

    if fips:
        df.at[i, "fips"] = standardize_fips(fips)
        matched += 1
    else:
        failed.append((i, row["company"], row["city"], row["county"], row["state_abbr"], "County not found in shapefile"))

print(f"  Matched: {matched} / {len(df)}")

# ── Report failures ───────────────────────────────────────────────────────────

if failed:
    print(f"\n  !! {len(failed)} rows failed to match:")
    for row_i, company, city, county, state, reason in failed:
        print(f"    Row {row_i}: {company} | {city}, {county}, {state} — {reason}")
else:
    print("\n  All rows matched!")

# ── Save ──────────────────────────────────────────────────────────────────────

df.to_csv(TRAINING_OUTPUT, index=False)
print(f"\nSaved as {TRAINING_OUTPUT}")