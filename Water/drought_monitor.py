import requests
import pandas as pd
import time

states = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

all_records = []

for i, state in enumerate(states):
    url = "https://usdmdataservices.unl.edu/api/CountyStatistics/GetDroughtSeverityStatisticsByAreaPercent"
    
    params = {
        "aoi": state,
        "startdate": "1/1/2000",
        "enddate": "1/1/2024",
        "statisticsType": "1"
    }
    
    headers = {"Accept": "application/json"}
    
    for attempt in range(3):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=60)
            break
        except Exception as e:
            print(f"  Attempt {attempt+1} failed for {state}: {e}")
            time.sleep(3)
    else:
        print(f"{state}: FAILED after 3 attempts")
        continue
    
    if response.status_code == 200:
        data = response.json()
        all_records.extend(data)
        print(f"{i+1}/50 {state}: {len(data)} weekly records")
    else:
        print(f"{i+1}/50 {state}: FAILED ({response.status_code})")
    
    time.sleep(1)

# Convert to DataFrame
df_raw = pd.DataFrame(all_records)
print(f"\nTotal weekly records: {len(df_raw)}")

# Calculate summary metrics per county
summary = df_raw.groupby(["fips", "county", "state"]).agg(
    total_weeks=("mapDate", "count"),
    pct_weeks_d1_plus=("d1", lambda x: (x > 0).sum() / len(x) * 100),
    avg_d1_coverage=("d1", "mean"),
    avg_d2_coverage=("d2", "mean"),
    avg_d3_coverage=("d3", "mean"),
    max_d3_coverage=("d3", "max"),
).reset_index()

summary["pct_weeks_d1_plus"] = summary["pct_weeks_d1_plus"].round(1)
summary["avg_d1_coverage"] = summary["avg_d1_coverage"].round(1)
summary["avg_d2_coverage"] = summary["avg_d2_coverage"].round(1)
summary["avg_d3_coverage"] = summary["avg_d3_coverage"].round(1)
summary["max_d3_coverage"] = summary["max_d3_coverage"].round(1)

print(f"\nSummary: {len(summary)} counties")
print(summary.head(10))

summary.to_csv("drought_monitor.csv", index=False)
print("\nSaved!")