import geopandas as gpd
import rasterstats
import pandas as pd
import numpy as np

# NLCD land cover class codes and labels
NLCD_CLASSES = {
    11: "open_water",
    12: "perennial_ice_snow",
    21: "developed_open",
    22: "developed_low",
    23: "developed_medium",
    24: "developed_high",
    31: "barren_land",
    41: "deciduous_forest",
    42: "evergreen_forest",
    43: "mixed_forest",
    52: "shrub_scrub",
    71: "grassland",
    81: "pasture_hay",
    82: "cultivated_crops",
    90: "woody_wetlands",
    95: "emergent_wetlands"
}

NLCD_PATH = r"C:\Users\WYATTRICE\OneDrive - Walton Enterprises LLC\Desktop\Projects\hf-datacenter-citing-research\Land\Annual_NLCD_LndCov_2024_CU_C1V1\Annual_NLCD_LndCov_2024_CU_C1V1.tif"
COUNTY_PATH = r"C:\Users\WYATTRICE\OneDrive - Walton Enterprises LLC\Desktop\Projects\hf-datacenter-citing-research\Land\tl_2025_us_county\tl_2025_us_county.shp"

# Load counties
print("Loading counties...")
counties = gpd.read_file(COUNTY_PATH)

# Filter to CONUS only (exclude Alaska=02, Hawaii=15, territories)
counties = counties[~counties["STATEFP"].isin(["02", "15", "60", "66", "69", "72", "78"])]
print(f"CONUS counties: {len(counties)}")

# Reproject counties to match NLCD CRS
print("Reprojecting counties to match NLCD...")
import rasterio
with rasterio.open(NLCD_PATH) as src:
    nlcd_crs = src.crs
counties = counties.to_crs(nlcd_crs)
print(f"Reprojected to: {nlcd_crs}")

# Run zonal statistics - this is the heavy computation
print("Running zonal statistics - this will take a while...")
stats = rasterstats.zonal_stats(
    counties,
    NLCD_PATH,
    categorical=True,
    nodata=0
)

print("Zonal stats complete, building results...")

# Build results dataframe
results = []
for i, (idx, county) in enumerate(counties.iterrows()):
    row = {
        "fips": county["GEOID"],
        "name": county["NAME"],
        "state": county["STATEFP"]
    }
    
    # Get total pixel count for this county
    stat = stats[i]
    total_pixels = sum(stat.values()) if stat else 0
    
    if total_pixels > 0:
        for code, label in NLCD_CLASSES.items():
            count = stat.get(code, 0)
            row[f"pct_{label}"] = round(count / total_pixels * 100, 2)
    else:
        for code, label in NLCD_CLASSES.items():
            row[f"pct_{label}"] = None
    
    results.append(row)
    
    if i % 100 == 0:
        print(f"  Processed {i}/{len(counties)} counties...")

df = pd.DataFrame(results)

# Aggregate categories
df["pct_developed_total"] = (
    df["pct_developed_open"] + df["pct_developed_low"] +
    df["pct_developed_medium"] + df["pct_developed_high"] +
    df["pct_cultivated_crops"]
).round(2)

df["pct_forest_total"] = (
    df["pct_deciduous_forest"] + df["pct_evergreen_forest"] +
    df["pct_mixed_forest"]
).round(2)

df["pct_environmental_barrier"] = (
    df["pct_open_water"] + df["pct_perennial_ice_snow"] +
    df["pct_woody_wetlands"] + df["pct_emergent_wetlands"]
).round(2)

df["pct_potentially_developable"] = (
    df["pct_shrub_scrub"] + df["pct_grassland"] +
    df["pct_pasture_hay"] + df["pct_barren_land"]
).round(2)

# Sanity check - all categories should sum to 100
df["pct_total_check"] = (
    df["pct_developed_total"] + df["pct_forest_total"] +
    df["pct_environmental_barrier"] + df["pct_potentially_developable"]
).round(2)

print("Sanity check - should all be ~100:")
print(df["pct_total_check"].describe())

print(f"\nDone! {len(df)} counties")
print(df.head())

df.to_csv("nlcd_land_cover.csv", index=False)
print("Saved!")