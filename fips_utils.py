# fips_utils.py
# Standardizes FIPS codes across all datasets to 5-digit zero-padded strings

# State abbreviation to FIPS lookup table
STATE_FIPS = {
    "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06",
    "CO": "08", "CT": "09", "DE": "10", "FL": "12", "GA": "13",
    "HI": "15", "ID": "16", "IL": "17", "IN": "18", "IA": "19",
    "KS": "20", "KY": "21", "LA": "22", "ME": "23", "MD": "24",
    "MA": "25", "MI": "26", "MN": "27", "MS": "28", "MO": "29",
    "MT": "30", "NE": "31", "NV": "32", "NH": "33", "NJ": "34",
    "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39",
    "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45",
    "SD": "46", "TN": "47", "TX": "48", "UT": "49", "VT": "50",
    "VA": "51", "WA": "53", "WV": "54", "WI": "55", "WY": "56"
}

def standardize_fips(value):
    """Convert any FIPS format to 5-digit zero-padded string"""
    return str(value).zfill(5)

def noaa_id_to_fips(noaa_id):
    """Convert NOAA county ID (e.g. AL-001) to 5-digit FIPS (e.g. 01001)"""
    parts = noaa_id.split("-")
    state_abbr = parts[0]
    county_code = parts[1]
    state_fips = STATE_FIPS.get(state_abbr, "")
    return state_fips + county_code

# Quick test
print(standardize_fips(1001))      # should print 01001
print(standardize_fips("40075"))   # should print 40075
print(noaa_id_to_fips("AL-001"))   # should print 01001
print(noaa_id_to_fips("AR-143"))   # should print 05143