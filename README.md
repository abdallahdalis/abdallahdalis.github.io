# Abdallah Dalis — Portfolio

Personal site + interactive analysis. M.S. Economics & Quantitative Analysis (DePaul, 2026).

**Live site:** [abdallahdalis.github.io](https://abdallahdalis.github.io) — or open locally with any static server:

```bash
python3 -m http.server 8765
# then visit http://localhost:8765
```

## Flagship: Chicago food-access map

A logistic model of low-income / low-access ("food desert") status across **791 Chicago
census tracts**, built from the USDA Food Access Research Atlas (2019). Each tract is shaded
by its predicted probability of being a food desert; click a tract to see the drivers, or
toggle to the actual USDA designation.

- **Outcome:** USDA LILA-at-½-mile flag
- **Covariates:** % Black, % Hispanic, log median family income, % SNAP, % no-vehicle households
- **Headline:** holding income constant, a 1-point rise in % Black population raises
  food-desert probability by ≈0.38 pp (p < 1e-7); Roseland's tracts are food deserts at
  71% vs 26% citywide.
- **Stack:** Python / Stata (model), Leaflet (map)

> Team practicum (ECO 575, DePaul). My contribution: the logit specification,
> marginal-effects analysis, and this visualization.

### Reproducing the map data

The raw inputs are not committed (see below). With them in `data/`, run:

```bash
pip install pandas numpy
python3 build_map_data.py   # writes tracts.geojson
```

Inputs:
- `data/chicago_food_access.dta` — USDA FARA (2019), Cook County, merged to Chicago
  community areas.
- `data/tracts_raw.geojson` — City of Chicago 2010 census tract boundaries
  ([data.cityofchicago.org dataset `74p9-q2aq`](https://data.cityofchicago.org/resource/74p9-q2aq.geojson?$limit=1000)).

## Other work

- **Monetary Policy & Local Labor Markets** — shift-share DiD across 2,887 U.S. counties;
  VAR/SVAR + Jordà local projections with high-frequency FOMC surprises.
- **Production-Function Estimation, Productivity & Markups** — Olley–Pakes across six
  estimators on a 2,971-firm panel (R).
- **Housing & Tax Inequality in Chicago's COVID-19 Recovery** — 2nd place, Columbia CIC
  Graduate Cohort; presented at the Federal Reserve Bank of Chicago.

## Data sources & credits

USDA Food Access Research Atlas (2019); City of Chicago open data (tract boundaries).
Basemap © OpenStreetMap, © CARTO.
