import pandas as pd

df = pd.read_csv("Energy_Broadband/eia_fcc_combined.csv")

print(f"Rows: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nSample:")
print(df.head())
print(f"\nNull counts:")
print(df.isnull().sum())
