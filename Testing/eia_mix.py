import requests
import pandas as pd

EIA_KEY = "QvfrW7OpyBn2OOsf1SsC2IIZvP9qkqdmrzfjmKdc"

url = "https://api.eia.gov/v2/electricity/electric-power-operational-data/data/"

# Only the fuel types we care about - avoiding double-counting subtotals
fuel_types = ["COW", "NG", "NUC", "WND", "SUN", "HYC", "GEO", "OTH"]

all_records = []
offset = 0

while True:
    params = {
        "api_key": EIA_KEY,
        "frequency": "annual",
        "data[]": "generation",
        "facets[sectorid][]": "99",   # all sectors combined
        "start": "2023",
        "end": "2023",
        "length": 5000,
        "offset": offset,
    }

    response = requests.get(url, params=params)
    data = response.json()

    rows = data["response"]["data"]
    if not rows:
        break

    all_records.extend(rows)
    print(f"Fetched {len(all_records)} records so far...")

    if len(rows) < 5000:
        break

    offset += 5000

df = pd.DataFrame(all_records)

# Filter to only the fuel types we want
df = df[df["fueltypeid"].isin(fuel_types)]

print(f"\nDone! {len(df)} rows")
print(df.head(20))