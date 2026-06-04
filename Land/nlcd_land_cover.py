import pandas as pd
import geopandas as gpd
import rasterio
import rasterstats

# Test loading the county shapefile
counties = gpd.read_file("Land/tl_2025_us_county/tl_2025_us_county.shp")
print(f"Counties loaded: {len(counties)} rows")
print(counties.head())
print(f"CRS: {counties.crs}")

# Test loading the NLCD raster - update the path to match your actual filename
with rasterio.open(r"C:\Users\WYATTRICE\OneDrive - Walton Enterprises LLC\Desktop\Projects\hf-datacenter-citing-research\Land\Annual_NLCD_LndCov_2024_CU_C1V1\Annual_NLCD_LndCov_2024_CU_C1V1.tif") as src:
    print(f"NLCD loaded successfully")
    print(f"CRS: {src.crs}")
    print(f"Resolution: {src.res}")
    print(f"Shape: {src.shape}")
# Check FIPS formats across datasets
print("=== Census Shapefile ===")
print(counties["GEOID"].head())

print("\n=== Drought Monitor ===")
drought = pd.read_csv("Water/drought_monitor.csv")
print(drought["fips"].head())

print("\n=== NOAA Precip ===")
noaa = pd.read_csv("Water/noaa_precip.csv")
print(noaa["county_id"].head())

print("\n=== FEMA NRI ===")
fema = pd.read_csv("Testing/fema_nri_counties.csv")
print(fema["STCOFIPS"].head())