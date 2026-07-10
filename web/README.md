# Datacenter Impact Tool (web)

React front-end for the datacenter impact research tool, styled with the
Heartland Forward / CIR design system. See `../README.md` for the data pipeline
and methodology.

## Develop

```
npm install
npm run build:data   # generate public/scores.json from ../Model/county_scores.csv
npm run dev          # http://localhost:5173
```

## Scripts

- `npm run dev` — Vite dev server
- `npm run build` — type-check and build to `dist/`
- `npm run build:data` — regenerate `public/scores.json` from `../Model/county_scores.csv`
- `npm run lint` — oxlint

## Structure

- `src/lib/` — data and math ported from `Dashboard/app.py` (scoring, tiers, estimator, tax)
- `src/components/` — ScoreCards, Estimator, FloatingNav, Footer, and form primitives
- `src/styles/` — CIR design system (`tokens`, `base`, `shared`, `footer`, `floating-nav`) copied verbatim, plus `tool.css` for this tool's own elements

The estimator math and scoring are a direct port of the Streamlit app and are
parity-checked against its output. `scores.json` is a build artifact; the source
of truth is `Model/county_scores.csv`.
