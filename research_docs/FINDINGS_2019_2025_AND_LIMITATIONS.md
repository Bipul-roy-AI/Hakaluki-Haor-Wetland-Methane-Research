# Findings, non-findings and limitations — Hakaluki Haor

**Evidence status:** Independent, exploratory research; updated 14 October 2026. These summaries come from completed *local* Jupyter Notebook 09 (Sentinel-1), 10 (hydroclimate) and 11 (TROPOMI QA) output logs. **As of this update, those notebooks, their new figures, and their generated CSV/report files have not yet been committed to this repository.** The results below should therefore be treated as documented local preliminary outputs, not yet independently reproduced from the repository checkout. Earlier notebooks and published figures may use different water-screening definitions and must not be silently pooled with Notebook 09.

## Executive summary

**What we observed:** A coherent seasonal low-backscatter radar signal over the selected Hakaluki study polygon; a particularly extensive signal during June 2022; contemporaneously exceptional June 2022 rainfall; descriptive links with rainfall in preceding months; a feasible 2026 ESA Biomass P-band SAR processing demonstration; and serious monsoon selection bias in available TROPOMI atmospheric methane observations.

**What we did not establish:** Validated flooded area, flood causality or exact flood timing, a causal climate–water relationship, a locally attributable atmospheric methane enhancement, wetland methane emission flux, or independent proof of the superior flood-detection accuracy of P-band versus C-band SAR.

## 1. Study definition and observation design

- **Location:** The analysis covers the Hakaluki Haor study area in northeastern Bangladesh, using the project boundary (approximately 172 km²). All reported area values refer to this defined mapping extent.
- **Period:** January 2019–December 2025 (84 monthly periods); a separate pilot uses 2026 images.
- **Geometry:** Approximately 172.29 km² when measured in UTM zone 46N. Notebook 09 reported an Earth Engine reference polygon area of 172.3844 km² and approximately 172.2717 km² of valid 30 m raster cells in the June 2022 spatial comparison. These are distinct measurement supports, not conflicting flood areas.
- **Notebook 09 Sentinel-1 selection:** One consistent ascending relative orbit (41), 214 source scenes in total, 84/84 months containing acquisitions and meeting the defined monthly observation-coverage criterion; 1 month had only a single scene.
- **Low-VV analysis:** Nominal threshold −17 dB, with −19 and −15 dB sensitivity screens, 30 m export grid, angle screening and spatial filtering with the original valid-data mask restored. These choices are **not independently calibrated** and are not equivalent to the earlier, more exploratory Otsu-derived water screens.

## 2. Inundation screening: observed pattern, not validated floodwater

The nominal −17 dB area is seasonally elevated around the monsoon. Compared with the median for the other six Junes (120.0993 km²), **June 2022** had **162.7751 km²** of nominal low-VV detections, a **+42.6758 km² month-matched difference**.

A separate 30 m, per-pixel comparison of June 2022 against the **mean frequency** of low-VV detections for the other six Junes reported:

| Descriptive spatial quantity | June 2022 result |
|---|---:|
| Pixels with sufficient 2022 + six-year June support | 191,413 / 191,413 |
| June 2022 nominal low-VV area on spatial grid | 162.7101 km² |
| Other-June **mean-frequency-equivalent** area | 120.5457 km² |
| Net screening-frequency-equivalent area difference | **+42.1644 km²** |
| Area of pixels with positive per-pixel difference | 113.4153 km² |
| Area of pixels with negative per-pixel difference | 3.5865 km² |
| Area of pixels with zero difference | 55.2699 km² |
| Median (2022 binary minus other-year frequency) | +0.1667 |

**Do not confuse these quantities.** The +42.6758 km² statistic compares monthly area to a *median of annual June areas*. The +42.1644 km² statistic compares a binary map to a *mean per-pixel June frequency* and sums the differences. The 113.4153 km² positive-departure footprint is the area of pixels with any positive difference, **not** additional flooded water. None is a validated flood-area estimate.

Single-orbit, threshold-dependent VV detections may misclassify smooth non-water surfaces, miss flooded vegetation, and cannot precisely time a short flash flood using only 1–3 scenes per month.

## 3. Hydroclimate: meaningful associations, limited predictability

For June 2022, the local CHIRPS-derived monthly rainfall estimate was **1,041.35 mm**, **+367.17 mm** above the six-other-year June median. This co-occurred with the +42.68 km² nominal low-VV departure. That conjunction is consistent with a rainfall-related wetland disturbance, but it does not prove flood attribution or a rainfall-driven causal effect.

Across the 2019–2025 monthly series, calendar-month-deseasonalized *Spearman* associations with nominal low-VV area were:

| Predictor | Descriptive Spearman rho | Months |
|---|---:|---:|
| Same-month rainfall | +0.232 | 84 |
| Previous-month rainfall | +0.428 | 83 |
| Sum of rainfall over preceding three months | **+0.524** | 81 |
| Same-month air temperature | −0.052 | 84 |

These are serially correlated observational time series. Testing several predictors and thresholds introduces multiple-comparison concerns. The lags reflect month-scale aggregation and are not proof of a hydrological response time.

Leave-one-year-out evaluation on 82 eligible observations compared a training-month median baseline against a month + rainfall/temperature Ridge model:

| Model | Pooled MAE (km²) | Pooled RMSE (km²) |
|---|---:|---:|
| Month-median seasonal baseline | **13.26** | 19.15 |
| Climate Ridge | 13.65 | **17.45** |

The climate model improved pooled RMSE but worsened pooled MAE; improvement was inconsistent across individual held-out years. June 2022 observed low-VV area was 162.775 km² versus a climate Ridge prediction of 123.513 km², leaving a **+39.262 km² held-out residual**. Residual magnitude is not evidence for a particular unmodelled mechanism. The Ridge model did not directly include the preceding-three-month rainfall sum as a separate predictor.

## 4. TROPOMI XCH4: seasonal observation bias and inconclusive attribution

Monthly Earth Engine Level-3-derived ROI XCH4 values existed in **69 of 84** months. Availability is highly seasonal:

| Calendar months | Months with ROI XCH4 | Availability |
|---|---:|---:|
| November–April | 42 / 42 | 100% |
| May–October | 27 / 42 | 64.3% |
| June (across seven years) | 3 / 7 | 42.9% |
| July | 2 / 7 | 28.6% |
| August | 1 / 7 | 14.3% |

The lowest quartile of monthly nominal low-VV extent had XCH4 available in **21/21** months, while the highest quartile had XCH4 available in only **8/21** months (38.1%). This is evidence of **uneven sampling conditional on the observed radar-defined wetland state**, but season and cloud/weather-related retrieval selection are competing explanations; it does not establish a direct effect of surface inundation on satellite retrieval success.

**June 2022, the key radar/rainfall episode, has no valid monthly ROI XCH4 value in the current Level-3 extraction.** August 2022 is also missing. A large number of satellite gridded image items does not establish valid independent methane footprints over this small study polygon.

For available-month, calendar-month-deseasonalized comparisons, Spearman correlations of nominal low-VV with ROI XCH4 were between about **−0.052 and −0.013** across Level-3 support filters. Correlations with ROI-minus-reference-ring XCH4 were about **+0.026 to +0.049**. Complete-case samples ranged from **62 to 66 months**, smaller than the 69 months with a simple ROI methane value. The exact reasons for exclusions need a row-level audit.

**Interpretation:** No appreciable monotonic association is evident in these available-month exploratory comparisons. This is **not** evidence that methane emissions are insensitive to flooding. XCH4 is a transported atmospheric dry-air column concentration (ppb), not a local surface flux or direct emitted mass; source mixing, retrieval error, missingness and wind conditions have not been resolved.

## 5. ESA Biomass P-band pilot: processing feasibility, not sensor validation

A separate 2 October 2026 ESA Biomass fully polarimetric P-band Level-1B scene was processed into four 25 m Gamma0 polarization layers (HH, HV, VH, VV) through the MAAP reference processing workflow and compared descriptively to Sentinel-1 C-band on 30 September and Sentinel-2 on 7 October.

The four Gamma0 layers were produced and pixel-matched processing-consistency comparisons were performed. Backscatter differences across optical MNDWI quartiles were also calculated. **None of these steps creates independent truth labels.** Different acquisition dates, P-band Gamma0 versus C-band Sigma0, incidence-angle/geometry differences, potential noise-floor behavior, and spatial autocorrelation prevent a flood-classification accuracy ranking or confident sensor-superiority claim.

See the Biomass figures and processing notes in the root README.

## 6. What remains unresolved — prioritized

1. **Independent inundation validation:** Study-area boundary metadata; stratified high-resolution or field-labelled water/non-water and flooded vegetation reference samples; confusion matrices; area-adjusted uncertainties; threshold, orbit and temporal sensitivity.
2. **Native TROPOMI Level-2 audit:** Inspect actual retrieval geolocation/footprint intersections, retrieval QA values, uncertainty and cloud/aerosol filters; document exclusions and monsoon seasonal selection. Do not infer native samples from upsampled Level-3 pixel counts.
3. **Atmospheric/background attribution:** Winds, upwind references or trajectory/transport methods; anthropogenic and regional source confounding; sampling-aware comparisons; do not report flux from XCH4 alone.
4. **Event-specific hydrology:** Daily/event-scale rainfall and hydrometric levels with actual SAR overpass dates; distinguish flash flood, seasonal expansion and permanent-water dynamics.
5. **Cross-sensor validation:** Independent reference samples for P- versus C-band, especially flooded vegetation; consistent geometry/radiometry controls and paired acquisition design.
6. **Public reproducibility:** Commit local notebooks 09–11, their manifests and reports, key derived CSVs, and sanitized figures; verify public links and suppress credentials, tokens and restricted raw data.

## 7. Data status and research integrity

These results were reported from local successful notebook executions, **not independently re-run as part of this GitHub documentation update**. As of 14 October 2026, only notebooks 00–08 were present on the GitHub default branch. The new 09–11 files and figures must be published before readers can exactly reproduce their reported numerical results from this repository.

No field methane flux observations, methane inversion, independent flood accuracy estimates, or statistically supported causal attribution are claimed. This project is independent and is not an institutional ESA or University of Leeds research collaboration.
