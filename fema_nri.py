import requests
import pandas as pd

url = "https://services.arcgis.com/XG15cJAlne2vxtgt/arcgis/rest/services/National_Risk_Index_Counties/FeatureServer/0/query"

fields = [
    "NRI_ID", "STATE", "STATEABBRV", "STATEFIPS", "COUNTY", "COUNTYTYPE",
    "COUNTYFIPS", "STCOFIPS", "POPULATION", "BUILDVALUE", "AREA",
    "RISK_VALUE", "RISK_SCORE", "RISK_RATNG", "RISK_SPCTL",
    "EAL_SCORE", "SOVI_SCORE", "RESL_SCORE",
    "CFLD_RISKS", "CFLD_RISKR",
    "DRGT_RISKS", "DRGT_RISKR",
    "ERQK_RISKS", "ERQK_RISKR",
    "HRCN_RISKS", "HRCN_RISKR",
    "IFLD_RISKS", "IFLD_RISKR",
    "LTNG_RISKS", "LTNG_RISKR",
    "TRND_RISKS", "TRND_RISKR",
    "WFIR_RISKS", "WFIR_RISKR",
    "WNTW_RISKS", "WNTW_RISKR",
    "SWND_RISKS", "SWND_RISKR",
]

all_records = []
offset = 0
page_size = 1000

while True:
    params = {
        "where": "1=1",
        "outFields": ",".join(fields),
        "resultRecordCount": page_size,
        "resultOffset": offset,
        "f": "json"
    }

    response = requests.get(url, params=params)
    data = response.json()

    features = data.get("features", [])
    if not features:
        break

    for feature in features:
        all_records.append(feature["attributes"])

    print(f"Fetched {offset + len(features)} records so far...")

    if len(features) < page_size:
        break

    offset += page_size

df = pd.DataFrame(all_records)
print(f"\nDone! Total counties: {len(df)}")
print(df.head())


df.to_csv("fema_nri_counties.csv", index=False)
print("Saved!")