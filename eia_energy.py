import requests
import pandas as pd

EIA_KEY = "QvfrW7OpyBn2OOsf1SsC2IIZvP9qkqdmrzfjmKdc"

url = "https://api.eia.gov/v2/electricity/electric-power-operational-data/data/"

params = {
    "api_key": EIA_KEY,
    "frequency": "annual",
    "data[]": "generation",
    "facets[location][]": "KS",   # just Kansas to keep it small
    "start": "2023",
    "end": "2023",
    "length": 50,
}

response = requests.get(url, params=params)
data = response.json()

print(data)
