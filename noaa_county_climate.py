import requests
import pandas as pd
import time

# Full county list parsed directly from the NOAA location document
with open("noaa_counties.txt", "r") as f:
    county_raw = f.read()

with open("noaa_counties.txt", "r") as f:
    county_raw = f.read()

# Parse the county list into IDs and names
county_lines = county_raw.strip().split("\n")
counties = []
for line in county_lines:
    line = line.strip()
    if not line:  # skip blank lines
        continue
    parts = line.split("\t")
    if len(parts) >= 2:  # skip any lines that don't have both columns
        counties.append({"county_id": parts[0].strip(), "county_name": parts[1].strip()})

print(f"Loaded {len(counties)} counties")

# Pull precipitation data for each county
results = []

for i, county in enumerate(counties):
    county_id = county["county_id"]
    county_name = county["county_name"]
    
    url = f"https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/county/time-series/{county_id}/pcp/12/0/1991-2020/data.json"
    
    # try up to 3 times before giving up
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=30)
            break
        except Exception as e:
            print(f"  Attempt {attempt+1} failed for {county_id}: {e}")
            time.sleep(2)
    else:
        print(f"{i+1}/{len(counties)} {county_id}: FAILED after 3 attempts")
        results.append({"county_id": county_id, "county_name": county_name, "avg_annual_precip_in": None})
        continue
    
    if response.status_code == 200:
        data = response.json()
        values = [v["value"] for v in data["data"].values()]
        avg_precip = round(sum(values) / len(values), 2)
        results.append({"county_id": county_id, "county_name": county_name, "avg_annual_precip_in": avg_precip})
        print(f"{i+1}/{len(counties)} {county_id}: {avg_precip} inches")
    else:
        print(f"{i+1}/{len(counties)} {county_id}: FAILED ({response.status_code})")
        results.append({"county_id": county_id, "county_name": county_name, "avg_annual_precip_in": None})
    
    time.sleep(0.2)

df = pd.DataFrame(results)
print(f"\nDone! {len(df)} counties, {df['avg_annual_precip_in'].isna().sum()} failed")
print(df.head())

df.to_csv("noaa_precip.csv", index=False)
print("Saved!")