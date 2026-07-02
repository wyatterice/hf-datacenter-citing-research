import pandas as pd

master = pd.read_csv("master_county_dataset.csv", dtype={"fips": str})
eia    = pd.read_csv("Energy_Broadband/eia_fcc_combined.csv")

# Check Fairfax in master
fairfax_master = master[master["county_name"] == "Fairfax"]
print("Fairfax in master:")
print(fairfax_master[["fips", "county_name", "state_fips", "NameplateCapacity_OperatingPlanned", "FiberCoverage100_20"]])

# Check Fairfax in EIA/FCC
fairfax_eia = eia[eia["GeoKey"].astype(str).str.contains("51059")]
print("\nFairfax in EIA/FCC:")
print(fairfax_eia)
