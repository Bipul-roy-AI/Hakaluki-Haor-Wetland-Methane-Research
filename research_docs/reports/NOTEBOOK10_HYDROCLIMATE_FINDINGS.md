# Hydroclimatic context of Hakaluki Haor low-VV dynamics, 2019–2025

**Research status:** Exploratory; **not** an independently validated flood-area study.

## Data and design
- Sentinel-1 ascending orbit 41 preliminary low-VV (`VV ≤ −17 dB`) area over 84 eligible months; processing fingerprint `cf23edea0ce7f8fb`.
- CHIRPS monthly precipitation and ERA5-Land 2 m monthly temperature from the existing project CSV; 84 months have radar, rainfall, and temperature records.
- Calendar-month leave-one-year-out departures, lagged precipitation (0–3 months), threshold robustness (−19/−17/−15 dB), and seven held-out-year comparisons.

## Descriptive 2022 findings
- June 2022 low-VV area: **162.78 km²**, relative to other-year June month-matched median **120.10 km²** (difference **+42.68 km²**).
- June 2022 CHIRPS precipitation: **1041.3 mm**; other-year June median **674.2 mm** (departure **+367.2 mm**).

## Exploratory year-held-out reconstruction
- Seasonal month-median baseline: MAE **13.26 km²**, RMSE **19.15 km²** (n=82 months).
- Month + rainfall/temperature Ridge: MAE **13.65 km²**, RMSE **17.45 km²**, with the same held-out months.
- These are *year-held-out explanatory hindcasts with observed contemporaneous climate*, not forecasts. Performance may be worse than the seasonal baseline; do not assume improvement.

## Limitations
1. Low-VV screening areas have not been validated against independent inundation reference samples; flooded vegetation may remain undetected.
2. Monthly hydroclimate is spatially coarse relative to 30 m SAR mapping, and rainfall timing, water retention and terrain controls are not fully represented.
3. Only seven years are available; nearby months and mapped pixels are not independent replicates. Associations do not establish causal effects.
4. Threshold sensitivity is not a confidence interval; year-held-out skill is not flux validation.
5. No wetland methane emission flux was calculated.

## Generated figures
- `results/figures/hydro10_timeseries_rain_temperature_lowvv.png`
- `results/figures/hydro10_seasonal_cycle.png`
- `results/figures/hydro10_2022_radar_rainfall_departures.png`
- `results/figures/hydro10_deseasonalized_lag_associations.png`
- `results/figures/hydro10_leave_year_out_hindcast.png`
