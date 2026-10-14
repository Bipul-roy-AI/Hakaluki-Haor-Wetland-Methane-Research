# Findings, non-findings and limitations — Hakaluki Haor

**Evidence status:** Independent, exploratory research; updated 14 October 2026. These summaries come from completed *local* Jupyter Notebook 09 (Sentinel-1), 10 (hydroclimate) and 11 (TROPOMI QA) output logs. **Notebooks 09–11, 14 curated figures, 26 result tables/manifests and two scientific reports are now published on GitHub.** The results below should therefore be treated as documented local preliminary outputs, not yet independently reproduced from the repository checkout. Earlier notebooks and published figures may use different water-screening definitions and must not be silently pooled with Notebook 09.

## Executive summary

**What we observed:** Seasonal low-VV radar screening dynamics; similarly high June screening extents in 2022, 2024 and 2025 under differing local rainfall; threshold-sensitive 2022–2024 rankings; descriptive rainfall-lag associations; limited climate-model generalization; strong seasonal gaps in TROPOMI XCH4 observation support; and a separate 2026 ESA Biomass P-band processing/cross-sensor demonstration. The present measurements do **not** distinguish event damage or flood severity.

**What we did not establish:** Validated flooded area, flood causality or exact flood timing, a causal climate–water relationship, a locally attributable atmospheric methane enhancement, wetland methane emission flux, or independent proof of the superior flood-detection accuracy of P-band versus C-band SAR.

## 1. Study definition and observation design

- **Location:** The analysis covers the Hakaluki Haor study area in northeastern Bangladesh, using the project boundary (approximately 172 km²). All reported area values refer to this defined mapping extent.
- **Period:** January 2019–December 2025 (84 monthly periods); a separate pilot uses 2026 images.
- **Geometry:** Approximately 172.29 km² when measured in UTM zone 46N. Notebook 09 reported an Earth Engine reference polygon area of 172.3844 km² and approximately 172.2717 km² of valid 30 m raster cells in the June 2022 spatial comparison. These are distinct measurement supports, not conflicting flood areas.
- **Notebook 09 Sentinel-1 selection:** One consistent ascending relative orbit (41), 214 source scenes in total, 84/84 months containing acquisitions and meeting the defined monthly observation-coverage criterion; 1 month had only a single scene.
- **Low-VV analysis:** Nominal threshold −17 dB, with −19 and −15 dB sensitivity screens, 30 m export grid, angle screening and spatial filtering with the original valid-data mask restored. These choices are **not independently calibrated** and are not equivalent to the earlier, more exploratory Otsu-derived water screens.

## 2. Inundation screening: observed pattern, not validated floodwater

The nominal −17 dB area is seasonally elevated around the monsoon. Compared with the median for the other six Junes (120.0993 km²), **June 2022** had **162.7751 km²** of nominal low-VV detections, a **+42.6758 km² descriptive difference**. This reference statistic is valid but does **not** imply that 2022 was unique or the most extensive June.

**Across all thresholds, 2022 and 2024 are effectively tied relative to threshold sensitivity:**

| June year | −19 dB area (km²) | −17 dB area (km²) | −15 dB area (km²) | June CHIRPS (mm) |
|---|---:|---:|---:|---:|
| 2022 | 148.301 | 162.775 | 164.771 | 1,041.35 |
| 2024 | 148.271 | 164.882 | 167.058 | 1,054.26 |
| 2025 | 146.475 | 161.269 | 164.539 | 479.17 |

At −19 dB, 2022 exceeds 2024 by only 0.030 km², but at −17 and −15 dB, 2024 is higher. The overall monthly series reaches **166.252 km²** at the nominal threshold, **96.4%** of the Earth Engine polygon area (~172.384 km²). Such high detection fractions constrain the discriminative value of total area and may reflect clipping by the chosen mapping extent. Near-maximum low-VV area is **not** evidence of a near-completely inundated verified wetland.

The important June 2022 event can still differ in **onset, persistence, depth, routing or exposure**, which were not measured by this monthly areal screen. The 2024 and 2025 observations mean that a unique 2022 magnitude claim should not lead the study.

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

Single-orbit, threshold-dependent VV detections may misclassify smooth non-water surfaces and miss flooded vegetation. Median composites of 1–3 scenes per month cannot resolve individual rainfall pulses. The inventory includes descending relative orbit 77 (181 scenes over 77 months) alongside ascending orbit 41 (214 scenes over 84 months); the passes must be screened **separately first** because viewing geometry and local acquisition times differ. Per-scene detection frequency, first/last *observed* low-VV dates and temporal transitions are candidate follow-ups, **not** exact continuous hydroperiod, depth or flood extent.

## 3. Hydroclimate: meaningful associations, limited predictability

For June 2022, the CHIRPS-derived rainfall estimate was **1,041.35 mm**, +367.17 mm above the six-other-year June median, while **June 2024 had 1,054.26 mm** and June 2025 had **479.17 mm**, despite similarly high 2025 low-VV area. Local precipitation remains relevant but is **incomplete hydrological forcing**: upstream inflows, river-stage/backwater effects and antecedent water storage may matter, and have not yet been quantified. The rainfall products and scene dates can support a daily event comparison, but CHIRPS accumulation-day alignment must be checked first.

Across the 2019–2025 monthly series, calendar-month-deseasonalized *Spearman* associations with nominal low-VV area were:

| Predictor | Descriptive Spearman rho | Months |
|---|---:|---:|
| Same-month rainfall | +0.232 | 84 |
| Previous-month rainfall | +0.428 | 83 |
| Sum of rainfall over preceding three months | **+0.524** | 81 |
| Same-month air temperature | −0.052 | 84 |

The reported +0.524 is the **largest among 18 screened associations** (three thresholds × six predictors), selected from serially correlated observational time series; it was not a prespecified, multiplicity-adjusted discovery. The lags reflect calendar-month aggregation and are not proof of a hydrological response time.

Leave-one-year-out evaluation on 82 eligible observations compared a training-month median baseline against a month + rainfall/temperature Ridge model:

| Model | Pooled MAE (km²) | Pooled RMSE (km²) |
|---|---:|---:|
| Month-median seasonal baseline | **13.26** | 19.15 |
| Climate Ridge | 13.65 | **17.45** |

The climate model improved pooled RMSE but worsened pooled MAE. In **held-out 2022**, the median baseline had **MAE 9.32 km² / RMSE 14.47 km²**, while Ridge had **MAE 15.19 km² / RMSE 19.52 km²**. June 2022 observed low-VV was 162.775 km² versus a Ridge prediction of 123.513 km², leaving a **+39.262 km²** residual; the residual does not identify any unmodelled mechanism.

Notebook 10 used calendar-month indicators, current and 1–2-month-lag rainfall, and temperature with fixed **Ridge alpha=20**; no standalone three-month rainfall sum was included. June 2022's 2022-held-out prediction decomposes into approximately **80.12 km² intercept, +1.55 June indicator, +40.01 rainfall predictors and +1.83 temperature**. These model contributions are defined relative to training-year feature standardization, not to normal June rainfall, and penalizing month indicators alongside raw seasonal rainfall complicates seasonal interpretation.

Post-hoc alternative alpha values and predictor subsets may lower error but cannot be reported as validated gains until hyperparameter/feature decisions are restricted to training folds, using an identical eligible-month sample. With seven years, even nested blocked validation will have substantial uncertainty.

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

**June 2022 has no valid monthly ROI XCH4 value in the current Level-3 extraction.** August 2022 is also missing. A large number of gridded satellite image items does not establish valid independent Level-2 footprints over the study area.

For available-month, calendar-month-deseasonalized comparisons, Spearman correlations of nominal low-VV with ROI XCH4 were between about **−0.052 and −0.013** across Level-3 support filters. Correlations with ROI-minus-reference-ring XCH4 were about **+0.026 to +0.049**. Complete-case samples ranged from **62 to 66 months**, fewer than the 69 with a simple ROI value.

**The difference is explained in the published code:** `calendar_month_departure` requires three observed years per month, excluding **all July and August** XCH4 departures; the main 66-month sample therefore includes **49 months (74.2%) outside June–October**. This is a selected available-month association, not a fair wet-season response test.

An additional descriptive linear-trend sensitivity calculation using the same 66 observations gives roughly **+10.02 ppb/year**, background-departure standard deviation decreasing from **24.28 to 13.39 ppb**, and Spearman low-VV/XCH4 rho shifting from **−0.013 to −0.081**. Such a trend adjustment does not recover missing wet-season data or establish a flux effect. The 68 available ROI-minus-ring values average about **+7.23 ppb** (sample SD ~9.05 ppb); without transport and retrieval diagnostics, the ring must **not** be regarded as a validated atmospheric background.

Further harmonic-fit alternatives and monsoon-only correlations considered after inspecting the data are **unpublished exploratory sensitivity checks**, not confirmed findings; their uncertainty and observation selection preclude any signed methane–flooding conclusion.

**Interpretation:** No appreciable monotonic association is evident in these available-month exploratory comparisons. This is **not** evidence that methane emissions are insensitive to flooding. XCH4 is a transported atmospheric dry-air column concentration (ppb), not a local surface flux or direct emitted mass; source mixing, retrieval error, missingness and wind conditions have not been resolved.

## 5. ESA Biomass P-band pilot: processing feasibility, not sensor validation

An October 2026 ESA Biomass fully polarimetric P-band Level-1B scene was processed into four 25 m Gamma0 polarization layers (HH, HV, VH, VV) through the MAAP reference processing workflow and compared descriptively to Sentinel-1 C-band on 30 September and Sentinel-2 on 7 October.

The four Gamma0 layers were produced and pixel-matched processing-consistency comparisons were performed. Backscatter differences across optical MNDWI quartiles were also calculated. **None of these steps creates independent truth labels.** Different acquisition dates, P-band Gamma0 versus C-band Sigma0, incidence-angle/geometry differences, potential noise-floor behavior, and spatial autocorrelation prevent a flood-classification accuracy ranking or confident sensor-superiority claim.

See the Biomass figures and processing notes in the root README.

## 6. Next work — priority and decision gates

1. **Per-scene wetland dynamics:** Compare June–September 2022 with 2024/2025 and a contrasting low-extent year, preserving actual acquisition times and separate ascending/descending geometry. Use daily CHIRPS rain with explicit accumulation-day uncertainty and ±1-day timing sensitivity. Do not claim exact flood onset from discrete overpasses.
2. **Hydrologic context and remote reference validation:** Obtain river stage/discharge and upstream precipitation when available; document catchment relevance and boundary spatial scope. Validate SAR low-VV and flooded-vegetation classifications against independently interpreted imagery across dates. Stage–area calibration requires defensible paired stage and mapped-water measurements.
3. **Methane feasibility gate:** Conduct a small native Level-2 footprint/QA sampling audit, specify habitat-weighted methane source/transport scenarios, and compare expected XCH4 enhancements with sampling-aware random and systematic uncertainties. Pursue detailed Level-2 transport/inversion work only if supported.
4. **Hydrological model redesign:** Predefine candidate stage/rainfall predictors and fit a seasonal baseline versus alternatives on identical data, with feature and alpha selection inside held-out-year training folds. Seven year blocks still limit uncertainty estimation.
5. **Cross-sensor and reproducibility:** Independently test ESA Biomass versus Sentinel-1 on aligned acquisition geometry/land classes, diagnose Gamma0 processor differences, and verify clean reruns without local Windows/GEE-account hardcoding.

All outputs above remain exploratory; absence of detectability evidence is not evidence that methane flux is zero.

## 7. Data status and research integrity

These results were reported from local successful notebook executions, **not independently re-run as part of this GitHub documentation update**. Notebook source files 09–11 are now on GitHub. The selected locally generated figures, tables and reports are now published. Public source code and outputs do not themselves establish independent reproduction or scientific validation.

No field methane flux observations, methane inversion, independent flood accuracy estimates, or statistically supported causal attribution are claimed. This project is independent and is not an institutional ESA or University of Leeds research collaboration.
