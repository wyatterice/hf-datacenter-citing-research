# Datacenter Siting Research Tool

County-level infrastructure benchmarking tool for Heartland Forward, built to help small and midsize communities understand their competitive position for hyperscale datacenter investment and negotiate community benefit agreements informed by data.

## What this does

For every CONUS county, the tool scores four infrastructure dimensions — Energy, Land, Broadband, and Water — benchmarked two ways: against the 85 counties where hyperscalers have actually built, and against all 3,109 US counties. Scores are framed as **negotiation levers, not siting filters**: a high score is leverage a community holds, a low score is leverage a community can demand from developers (grid upgrades, fiber access agreements, water use commitments, etc.).

An **Infrastructure Impact Estimator** lets a user model a hypothetical facility (by scale tier or custom MW) and see projected energy draw, water consumption, connectivity requirements, land footprint, and economic impact (jobs, construction cost) — benchmarked against the selected county's actual capacity where data allows.

## Repo structure

```
├── master_join.py                  # Builds master_county_dataset.csv from all source data
├── fips_utils.py                   # Shared FIPS standardization utilities
├── requirements.txt                # Python dependencies for Streamlit Cloud
│
├── Energy_Broadband/                
│   └── eia_fcc_combined.csv        # EIA-860/923 + FCC broadband data (Will's pipeline)
│
├── Water/
│   ├── noaa_county_climate.py      # Pulls NOAA Climate at a Glance precipitation data
│   ├── drought_monitor.py          # Pulls US Drought Monitor weekly county data
│   ├── noaa_precip.csv
│   └── drought_monitor.csv
│
├── Land/
│   ├── nlcd_overlay.py             # NLCD 2024 land cover zonal stats (needs raw raster)
│   ├── pad_overlay.py              # PAD-US 4.1 protected lands overlay (needs raw geodatabase)
│   ├── nlcd_land_cover.csv
│   └── pad_protected_lands.csv
│
├── Model/
│   ├── geocode_training.py         # Geocodes hyperscaler facility list to FIPS
│   ├── feature_exploration.py      # Correlation analysis (informed scoring approach)
│   ├── score_counties.py           # Generates percentile scores (main model output)
│   ├── hyperscaler_facilities.csv  # Raw training data: ~105 known hyperscaler sites
│   ├── hyperscaler_training.csv    # Geocoded training data
│   ├── feature_correlations.csv
│   ├── county_scores.csv           # Final scored output — feeds the dashboard
│   └── impact_estimator_sourcing.docx  # Sourcing/methodology for every constant used
│
├── Dashboard/
│   └── app.py                      # Streamlit dashboard
│
├── web/                            # React front-end (Vite + TS), CIR-branded
│   ├── src/                        # App, components, lib (ported scoring/estimator), CIR styles
│   ├── public/scores.json          # Generated from Model/county_scores.csv
│   └── scripts/build-data.mjs      # `npm run build:data` regenerates scores.json
│
└── master_county_dataset.csv       # Joined dataset, all 4 categories, ~3,100 counties
```

## Note on excluded files

`.gitignore` excludes large raw geospatial source files (NLCD raster ~15GB, Census TIGER shapefile, PAD-US geodatabase ~1.4GB). These aren't needed to run the dashboard or review the pipeline — the generated CSVs are what everything downstream uses. They're only needed if you want to re-run `nlcd_overlay.py` or `pad_overlay.py` from scratch.

If you need them:
- **NLCD 2024 land cover**: [mrlc.gov](https://www.mrlc.gov/data)
- **PAD-US 4.1**: [usgs.gov/programs/gap-analysis-project/science/pad-us-data-download](https://www.usgs.gov/programs/gap-analysis-project/science/pad-us-data-download)
- **Census TIGER county shapefile**: [census.gov/cgi-bin/geo/shapefiles](https://www.census.gov/cgi-bin/geo/shapefiles/index.php)

## Running the dashboard locally

Requires Streamlit (`pip install streamlit` — use Anaconda Prompt, not a standard terminal, if on the Anaconda distribution).

```
streamlit run Dashboard/app.py
```

## React front-end (web/)

A second front-end that matches the Heartland Forward / CIR dashboard design system (shared tokens, components, and footer CSS). Same tool, rebuilt in React because Streamlit confines all content to one centered block and can't reproduce the brand layout (full-bleed footer, fixed section nav, centered column). The Python pipeline is unchanged: the app reads `Model/county_scores.csv` through a generated `web/public/scores.json`.

```
cd web
npm install
npm run build:data   # regenerate scores.json from ../Model/county_scores.csv
npm run dev          # http://localhost:5173
```

`npm run build` outputs a static bundle to `web/dist/`. Re-run `npm run build:data` whenever `county_scores.csv` changes.

### Deployment

The React front-end deploys to GitHub Pages via `.github/workflows/deploy-pages.yml`. On every push to `main` it builds `web/` and publishes `web/dist` to `https://<owner>.github.io/hf-datacenter-citing-research/`. The build regenerates `scores.json` from `Model/county_scores.csv`, so the published data always tracks the source CSV.

One-time setup by the repo owner: Settings > Pages > Source = "GitHub Actions". The production build uses a `/hf-datacenter-citing-research/` base path (set in `web/vite.config.ts`) to match the Pages project subpath; local dev is unaffected.

## Known issues / open items

- Virginia independent cities (FIPS 51500+) create duplicate county names in some dropdowns — partial fix in place (FIPS-disambiguated display names), full fix would filter them from `master_join.py`
- EIA/FCC data covers 2,282 of 3,109 counties — the remaining 827 show as "data unavailable" for Energy and Broadband scores rather than a misleading zero. 
- Water is scored on drought exposure only; no county-level water withdrawal/supply data exists nationally, so absolute consumption (in the impact estimator) can't be shown as a % of available supply the way energy can
- Jobs numbers currently linear relationship, not accurate for mor eautomated hyperscale locaitons. Working on researching a nonlinear fix.

## Methodology notes

- Training data (105 hyperscaler facilities: Meta, Apple, Amazon, Microsoft, Google) is used as a **benchmark distribution**, not as labels for a predictive model. An earlier logistic regression approach was evaluated and set aside — see `feature_exploration.py` / `feature_correlations.csv` for that analysis — in favor of percentile benchmarking, which produces more actionable output for the tool's actual audience.
- All impact estimator constants (PUE, WUE, cost per MW, jobs per MW, etc.) are sourced in `Model/impact_estimator_sourcing.docx`, current as of July 2026. These should probably be revisited annually.
