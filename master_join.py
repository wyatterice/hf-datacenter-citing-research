import pandas as pd
from fips_utils import standardize_fips, noaa_id_to_fips

# ── Load all datasets ──────────────────────────────────────────────────────────

print("Loading datasets...")

# Census county list as the base - every county gets a row
from geopandas import read_file
counties_base = read_file(r"C:\Users\WYATTRICE\OneDrive - Walton Enterprises LLC\Desktop\Projects\hf-datacenter-citing-research\Land\tl_2025_us_county\tl_2025_us_county.shp")
counties_base = counties_base[~counties_base["STATEFP"].isin(["02", "15", "60", "66", "69", "72", "78"])]
counties_base = counties_base[["GEOID", "NAME", "STATEFP"]].copy()
counties_base.columns = ["fips", "county_name", "state_fips"]
print(f"  Base counties: {len(counties_base)}")

# FEMA NRI
fema = pd.read_csv("Testing/fema_nri_counties.csv")
fema["fips"] = fema["STCOFIPS"].apply(standardize_fips)
fema_cols = ["fips", "RISK_SCORE", "RISK_RATNG", "RISK_SPCTL",
             "CFLD_RISKS", "DRGT_RISKS", "ERQK_RISKS", "HRCN_RISKS",
             "IFLD_RISKS", "TRND_RISKS", "WFIR_RISKS", "WNTW_RISKS", "SWND_RISKS"]
fema = fema[fema_cols]
print(f"  FEMA NRI: {len(fema)} counties")

# NOAA Precipitation
noaa = pd.read_csv("Water/noaa_precip.csv")
noaa["fips"] = noaa["county_id"].apply(noaa_id_to_fips)
noaa = noaa[["fips", "avg_annual_precip_in"]]
print(f"  NOAA Precip: {len(noaa)} counties")

# Drought Monitor
drought = pd.read_csv("Water/drought_monitor.csv")
drought["fips"] = drought["fips"].apply(standardize_fips)
drought = drought[["fips", "pct_weeks_d1_plus", "avg_d1_coverage",
                   "avg_d2_coverage", "avg_d3_coverage"]]
print(f"  Drought Monitor: {len(drought)} counties")

# NLCD Land Cover
nlcd = pd.read_csv("Land/nlcd_land_cover.csv")
nlcd["fips"] = nlcd["fips"].apply(standardize_fips)
nlcd_cols = ["fips", "pct_open_water", "pct_developed_open", "pct_developed_low",
             "pct_developed_medium", "pct_developed_high", "pct_barren_land",
             "pct_deciduous_forest", "pct_evergreen_forest", "pct_mixed_forest",
             "pct_shrub_scrub", "pct_grassland", "pct_pasture_hay",
             "pct_cultivated_crops", "pct_woody_wetlands", "pct_emergent_wetlands",
             "pct_developed_total", "pct_forest_total", "pct_environmental_barrier",
             "pct_potentially_developable"]
nlcd = nlcd[nlcd_cols]
print(f"  NLCD Land Cover: {len(nlcd)} counties")

# EIA + FCC Combined
eia_fcc = pd.read_csv("Energy_Broadband/eia_fcc_combined.csv")
eia_fcc["fips"] = eia_fcc["GeoKey"].apply(standardize_fips)
eia_fcc = eia_fcc[["fips", "FiberCoverage100_20", "BroadbandAccessGigabit",
                    "GeneratorCount_OperatingPlanned",
                    "GeneratorCountPer1k_OperatingPlanned",
                    "NameplateCapacity_OperatingPlanned",
                    "NameplateCapacityPer1k_OperatingPlanned"]]
print(f"  EIA + FCC: {len(eia_fcc)} counties")

# ── Join all datasets ──────────────────────────────────────────────────────────

print("\nJoining datasets...")

master = counties_base.copy()
master = master.merge(fema, on="fips", how="left")
master = master.merge(noaa, on="fips", how="left")
master = master.merge(drought, on="fips", how="left")
master = master.merge(nlcd, on="fips", how="left")
master = master.merge(eia_fcc, on="fips", how="left")

print(f"\nMaster dataset: {len(master)} counties, {len(master.columns)} columns")
print(f"\nNull counts per dataset:")
print(f"  FEMA NRI (risk_score): {master['RISK_SCORE'].isna().sum()}")
print(f"  NOAA Precip: {master['avg_annual_precip_in'].isna().sum()}")
print(f"  Drought Monitor: {master['pct_weeks_d1_plus'].isna().sum()}")
print(f"  NLCD Land Cover: {master['pct_potentially_developable'].isna().sum()}")
print(f"  EIA + FCC: {master['FiberCoverage100_20'].isna().sum()}")

print("\nSample:")
print(master.head())

master.to_csv("master_county_dataset.csv", index=False)
print("\nSaved as master_county_dataset.csv!")