import geopandas as gpd
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

GDB_PATH = r"C:\Users\WYATTRICE\OneDrive - Walton Enterprises LLC\Desktop\Projects\hf-datacenter-citing-research\Land\PADUS4_1Geodatabase\PADUS4_1Geodatabase.gdb"
COUNTY_PATH = r"C:\Users\WYATTRICE\OneDrive - Walton Enterprises LLC\Desktop\Projects\hf-datacenter-citing-research\Land\tl_2025_us_county\tl_2025_us_county.shp"

# Load counties
print("Loading counties...")
counties = gpd.read_file(COUNTY_PATH)
counties = counties[~counties["STATEFP"].isin(["02", "15", "60", "66", "69", "72", "78"])]
counties = counties[["GEOID", "NAME", "STATEFP", "ALAND", "geometry"]].copy()
print(f"CONUS counties: {len(counties)}")

# Load PAD-US combined layer
print("Loading PAD-US...")
pad = gpd.read_file(GDB_PATH, layer="PADUS4_1Combined_Proclamation_Marine_Fee_Designation_Easement")

# Filter to only GAP 1, 2, 3
pad = pad[pad["GAP_Sts"].isin(["1", "2", "3"])]
pad = pad[["GAP_Sts", "geometry"]].copy()

# Fix invalid geometries
print("Fixing invalid geometries...")
pad["geometry"] = pad.geometry.buffer(0)
pad = pad[pad.geometry.is_valid]
print(f"Protected features after cleaning: {len(pad)}")

# Reproject counties to match PAD-US CRS
print("Reprojecting counties...")
counties = counties.to_crs(pad.crs)

# Calculate county areas in square meters
counties["county_area_m2"] = counties.geometry.area

print("Running spatial overlay - this will take a while...")

results = []

for i, county in counties.iterrows():
    row = {
        "fips": county["GEOID"],
        "county_name": county["NAME"],
        "state_fips": county["STATEFP"]
    }
    
    county_geom = county.geometry
    county_area = county["county_area_m2"]
    
    # Find all PAD features that intersect this county
    candidates = pad[pad.intersects(county_geom)]
    
    if len(candidates) == 0:
        row["pct_gap1"] = 0.0
        row["pct_gap2"] = 0.0
        row["pct_gap3"] = 0.0
        row["pct_gap1_2"] = 0.0
        row["pct_gap1_2_3"] = 0.0
    else:
        # Clip to county boundary
        clipped = candidates.copy()
        clipped["geometry"] = candidates.intersection(county_geom)
        clipped = clipped[~clipped.geometry.is_empty]
        
        # Calculate area by GAP status
        clipped["area_m2"] = clipped.geometry.area
        gap_areas = clipped.groupby("GAP_Sts")["area_m2"].sum()
        
        gap1 = gap_areas.get("1", 0)
        gap2 = gap_areas.get("2", 0)
        gap3 = gap_areas.get("3", 0)
        
        row["pct_gap1"] = round(gap1 / county_area * 100, 2)
        row["pct_gap2"] = round(gap2 / county_area * 100, 2)
        row["pct_gap3"] = round(gap3 / county_area * 100, 2)
        row["pct_gap1_2"] = round((gap1 + gap2) / county_area * 100, 2)
        row["pct_gap1_2_3"] = round((gap1 + gap2 + gap3) / county_area * 100, 2)
    
    results.append(row)
    
    if i % 100 == 0:
        print(f"  Processed {len(results)}/{len(counties)} counties...")

df = pd.DataFrame(results)
print(f"\nDone! {len(df)} counties")
print(df.head(10))

df.to_csv("Land/pad_protected_lands.csv", index=False)
print("Saved!")