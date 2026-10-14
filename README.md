# Hakaluki Haor | Wetland Dynamics, Hydroclimate and Atmospheric Methane Observations

**Study period:** January 2019–December 2025 | **ESA Biomass P-band observations:** October 2026  
Sentinel-1 · Sentinel-2 · ESA Biomass P-band · TROPOMI XCH4 · CHIRPS · ERA5-Land · GIS · Google Earth Engine · Python

> **Research status: exploratory; independent scientific validation outstanding.** The radar-derived maps are **low-VV backscatter screening products, not verified flood maps**. TROPOMI measures atmospheric column methane (XCH4, ppb), **not wetland methane emission flux**. No field methane-flux validation, atmospheric inversion, or causal attribution has been completed.

## Main findings — and their boundaries

**Principal result:** The 2019–2025 record shows strong seasonal low-VV changes, but high June screening extents were observed in **2022, 2024 and 2025**, despite differing monthly rainfall. The radar-area metric alone cannot rank flood severity or separate rainfall timing from river-stage effects. **TROPOMI XCH4 is sparsely observed during key monsoon months**, so its available-month correlations do not establish the methane response to flooding.

| Research component | What the completed local analysis reports | What it does **not** prove |
|---|---|---|
| Radar observation support | **84/84 months** with Sentinel-1 on one ascending track (relative orbit 41), 214 scenes; one single-scene month | Independent accuracy of a water/flood classification |
| June low-VV extent (−17 dB) | **2022: 162.78 km²; 2024: 164.88 km²; 2025: 161.27 km².** June 2022 is +42.68 km² relative to the other-six-year June median | A uniquely exceptional 2022 extent or verified flood area |
| June 2022 spatial comparison | **+42.16 km²** net screening-frequency-equivalent difference from the **mean** of the other six June maps | Additional flooded area or uniqueness relative to 2024/2025 |
| June CHIRPS rainfall | **2022: 1,041.35 mm; 2024: 1,054.26 mm; 2025: 479.17 mm** | Unique 2022 rainfall or a complete catchment forcing budget |
| Exploratory climate link | Preceding-three-month rainfall sum vs. low-VV area: **Spearman rho +0.524**, n = 81; strongest of 18 screened correlations | Prespecified hypothesis test, causal lag or demonstrated predictive gain |
| Published held-out climate model | On 82 months, Ridge **RMSE 17.45** vs. baseline **19.15 km²**, but Ridge **MAE 13.65** vs. baseline **13.26 km²**. In held-out 2022, Ridge **MAE 15.19** vs. baseline **9.32 km²** | Robust year-to-year skill or isolation of rainfall anomalies |
| TROPOMI methane availability | ROI XCH4 in **69/84 months**; only **3/7 Junes**, **2/7 Julys**, **1/7 Augusts** | Representative year-round atmospheric methane measurements |
| Seasonal methane sampling imbalance | XCH4 present in **21/21** lowest-low-VV-quartile months vs. **8/21** highest-quartile months; strongly confounded by season | Effect of flooding on retrieval success or a significant causal contrast |
| Methane association | Level-3 available-month deseasonalized rho near zero; **49 of 66** main-analysis months fall outside June–October | A wet-season emission-response estimate or evidence of no flux effect |
| ESA Biomass polarimetry | Four 25 m Gamma0 P-band layers; descriptive comparison with C-band and Sentinel-2 | Superior P-band flood-detection accuracy |

**Read the detailed research findings, non-findings and remaining work:** [Findings and limitations, 2019–2025](research_docs/FINDINGS_2019_2025_AND_LIMITATIONS.md).

## What is important scientifically

### June 2022 in multi-year context: high extent, not a unique maximum

The June 2022 nominal −17 dB low-VV area was **162.775 km²**, compared with **164.882 km² in June 2024** and **161.269 km² in June 2025**. The **+42.676 km²** difference relative to the other-six-year June median is mathematically valid, but the other Junes have markedly different low- and high-extent groups. It is **not** evidence that 2022 was the only or largest high-extent June.

The 2022-versus-2024 ordering is also threshold-sensitive: at **−19 dB**, 2022 is **148.301 km²** and 2024 **148.271 km²**; at **−17 dB**, 2022 is **162.775 km²** and 2024 **164.882 km²**; at **−15 dB**, they are **164.771** and **167.058 km²**. No robust ranking follows from differences this small compared with threshold sensitivity.

June 2022's spatial **+42.164 km²** comparison sums differences from mean historical June *screening frequency*, not additional inundation or event severity. Much of the polygon is flagged low-VV in high months (maximum monthly screening fraction **96.4%**), creating a ceiling for areal extent and possible boundary clipping. The one-track monthly median cannot resolve rainfall-pulse timing, water depth, persistence or downstream impacts. Scene-level analysis with both tracks is the next priority.

### Hydroclimate: antecedent-rainfall association, uncertain mechanisms and prediction

After calendar-month adjustment, nominal low-VV departures had descriptive correlations with **same-month rainfall (rho +0.232)**, **one-month-lag rainfall (+0.428)** and **preceding-three-month rainfall (+0.524)**. The last value is the largest of **18 screened correlations** (three VV thresholds × six predictors), not a prespecified significance result. The published Ridge model includes rainfall at lags 0–2 and temperature, but not the three-month sum; its shrinkage also affects month indicators and complicates separation of rainfall anomalies from the seasonal cycle.

Held-out 2022 performance was **worse** than the month-median baseline (Ridge MAE **15.19**, baseline **9.32 km²**). June 2022's +39.26 km² Ridge residual is not a measurement of flood severity. June 2024 had comparably high radar extent and rainfall, whereas June 2025 had high radar extent with much less concurrent rainfall. Local CHIRPS alone may not capture antecedent wetness, upstream flow or river-stage/backwater conditions; these mechanisms need independent hydrological evidence.

### Atmospheric methane: observation gaps obstruct the key event

TROPOMI-derived ROI XCH4 was available in **69/84** months, but only **3/7 Junes, 2/7 Julys and 1/7 Augusts**. **June 2022 has no valid monthly ROI XCH4** in this Level-3-derived dataset. Availability was 21/21 in the lowest low-VV quartile and 8/21 in the highest, but this comparison is substantially confounded by season and should **not** be described as a statistically significant inundation effect.

The main monthly departure analysis retains **66** observations, **49 (74.2%) outside June–October**. It excludes July–August because fewer than three observed years are available for those calendar-month baselines. The available-month ROI correlation is approximately **−0.013** before additional support screening; removing an approximate 10.0 ppb/year linear background trend gives a descriptive rho of approximately **−0.081** on the same 66 months. This does **not** constrain a wet-season emission response, and detrending cannot recover absent observations. The ROI-minus-ring contrast also needs atmospheric and retrieval-quality interpretation.

**No methane emission flux or flood-response direction has been established.** The next step is a limited native Level-2 sampling and detectability feasibility check, not another unqualified monthly concentration–flood regression.

## Study Area and Earth Observation Results

The maps and plots below introduce the Hakaluki Haor study area and summarize the initial Earth observation analyses. Updated 2019–2025 results and ESA Biomass observations follow in the sections below.

### Hakaluki Haor study area

![Hakaluki study-area boundary](docs/assets/figures/hakaluki_boundary_audit_map.png)

### Earlier March–June–October 2022 low-backscatter screening maps

![Earlier exploratory SAR screening, March June and October 2022](docs/assets/figures/hakaluki_2022_sar_geographic_comparison.png)

### Monthly Earth-observation series, 2019–2025

![Earlier multi-source monthly series](docs/assets/figures/01_monthly_timeseries.png)

### Data completeness and seasonal patterns

![Observed data completeness](docs/assets/figures/02_data_completeness.png)

![Multi-year exploratory seasonality](docs/assets/figures/03_monthly_seasonality.png)

### Early exploratory covariate associations (not causal)

![Exploratory relationships from an earlier workflow](docs/assets/figures/04_exploratory_correlations.png)

## What we cannot claim yet

| Critical gap | Work needed |
|---|---|
| **Validated flood area / flooded vegetation** | Independent high-resolution reference imagery and/or field observations; threshold and orbit sensitivity; confusion matrices and area uncertainty |
| **Event-level flood severity or cause** | Per-scene ascending/descending SAR, rainfall accumulation timing, water-level/upstream forcing, and separate depth/duration/exposure indicators |
| **Local methane emission rates** | Flux measurements or defensible atmospheric inversion; XCH4 alone cannot supply flux |
| **Local methane detection feasibility** | Brief native Level-2 sampling/QA audit and habitat-weighted detectability scenarios before attempting detailed transport/inversion; June 2022 ROI XCH4 is missing |
| **Generalizable climate prediction** | Stronger held-out evaluation, uncertainty and alternative baselines; avoid overfitting seven years of data |
| **P-band superiority** | Independent water/flooded vegetation labels, noise-floor studies, compatible calibration, temporal/geometry controls |
| **Independent reproduction** | Code, tables, figures, manifests and reports are published. An independent end-to-end rerun and validation remain to be done. |

## Next research stage

1. **Scene-level SAR (priority):** Compare 2022, 2024 and 2025 (with 2023 as a lower-extent comparator) per acquisition; keep ascending and descending track estimates separate before interleaving time series. Align with CHIRPS daily rainfall while auditing date conventions and ±1-day timing sensitivity.
2. **Hydrology and remote validation:** Seek water-level and upstream precipitation data; assess stage–area relation only if compatible stage/reference-area data exist; evaluate VV/VH thresholds and independent reference imagery.
3. **Methane observability gate:** Audit native Level-2 footprints and quality for a small defined sample, then compare habitat-weighted source scenarios against sampling/transport variability. Proceed to detailed atmospheric attribution only if support is sufficient.
4. **Model redesign:** Reevaluate hydrological predictors with year-blocked model selection and a common observation sample; keep post-hoc α and harmonic alternatives exploratory.

Existing Notebooks 09–11 and the ESA Biomass P-band study are preserved as published exploratory analyses. [Detailed findings](research_docs/FINDINGS_2019_2025_AND_LIMITATIONS.md) · [Methods](research_docs/METHODS_AND_LIMITATIONS.md) · [Roadmap](research_docs/ROADMAP.md).

## Research questions and methods

1. How does radar low-backscatter screening vary from 2019 to 2025, and how accurately can it identify actual open water and flooded vegetation?
2. How do rainfall timing, antecedent wetness and air temperature relate to the radar time series after accounting for month-of-year seasonality?
3. How does wet-season methane retrieval missingness affect what can be inferred from satellite XCH4 observations?
4. Can ESA Biomass P-band polarimetry add independently demonstrated wetland information beyond Sentinel-1 C-band?
5. What field, transport and inversion evidence is required to estimate methane **emissions**?

**Source and method navigation:** [Full findings](research_docs/FINDINGS_2019_2025_AND_LIMITATIONS.md) · [Methods and limitations](research_docs/METHODS_AND_LIMITATIONS.md) · [Validation plan](research_docs/VALIDATION_PLAN.md) · [Development roadmap](research_docs/ROADMAP.md) · [Data provenance](research_docs/DATA_DICTIONARY_AND_PROVENANCE.md).

<!-- LOCAL_2019_2025_RESULTS_START -->
## 2019–2025 Inundation, Hydroclimate and Methane Results

### Monthly low-VV screening, 2019–2025

![Monthly low-VV screening, 2019–2025](docs/assets/figures/analysis_2019_2025/inundation09_monthly_screening_timeseries.png)

*Low-VV detections are not validated flooded-water area.*

### Low-VV detections by calendar month and year

![Low-VV detections by calendar month and year](docs/assets/figures/analysis_2019_2025/inundation09_month_year_heatmap.png)

*A fixed VV threshold was used; color is an unvalidated screening statistic.*

### 2022 monthly differences relative to other years

![2022 monthly differences relative to other years](docs/assets/figures/analysis_2019_2025/inundation09_2022_month_matched_departures.png)

*Differences compare screening areas, not confirmed additional floodwater.*

### Annual observation-normalized low-VV occurrence, 2019–2025

![Annual observation-normalized low-VV occurrence, 2019–2025](docs/assets/figures/analysis_2019_2025/inundation09_annual_lowvv_frequency_2019_2025.png)

*The denominator is the number of valid observed months per pixel; not an inundation probability.*

### June 2022 spatial difference from historical June screening frequency

![June 2022 spatial difference from historical June screening frequency](docs/assets/figures/analysis_2019_2025/inundation09_june2022_spatial_lowvv_departure.png)

*Per-pixel binary-minus-frequency departure; not a flood-area-change map.*

### Rainfall, temperature and low-VV screening series

![Rainfall, temperature and low-VV screening series](docs/assets/figures/analysis_2019_2025/hydro10_timeseries_rain_temperature_lowvv.png)

*Monthly covariates, not causal drivers or flood verification.*

### Seasonal cycle of hydroclimate and low-VV screening

![Seasonal cycle of hydroclimate and low-VV screening](docs/assets/figures/analysis_2019_2025/hydro10_seasonal_cycle.png)

*Descriptive monthly aggregation.*

### 2022 radar and rainfall departures

![2022 radar and rainfall departures](docs/assets/figures/analysis_2019_2025/hydro10_2022_radar_rainfall_departures.png)

*Coincidence does not establish causal flooding.*

### Deseasonalized hydroclimatic associations

![Deseasonalized hydroclimatic associations](docs/assets/figures/analysis_2019_2025/hydro10_deseasonalized_lag_associations.png)

*Serial correlation and multiple comparisons limit inference.*

### Out-of-year climate-model hindcasts versus seasonal baseline

![Out-of-year climate-model hindcasts versus seasonal baseline](docs/assets/figures/analysis_2019_2025/hydro10_leave_year_out_hindcast.png)

*Predictive performance is mixed across years.*

### TROPOMI XCH4 month-by-month availability and Level-3 grid support

![TROPOMI XCH4 month-by-month availability and Level-3 grid support](docs/assets/figures/analysis_2019_2025/methane11_availability_and_grid_support.png)

*Level-3 coverage does not equal native Level-2 retrieval footprints.*

### Atmospheric XCH4 inside the ROI and in a reference ring

![Atmospheric XCH4 inside the ROI and in a reference ring](docs/assets/figures/analysis_2019_2025/methane11_roi_ring_time_series.png)

*Column concentrations are not local methane emissions.*

### Methane observation availability across low-VV screening conditions

![Methane observation availability across low-VV screening conditions](docs/assets/figures/analysis_2019_2025/methane11_observation_selection_bias.png)

*Wet-season missingness creates observational selection bias.*

### Available-month XCH4 versus low-VV anomalies

![Available-month XCH4 versus low-VV anomalies](docs/assets/figures/analysis_2019_2025/methane11_coverage_sensitive_scatter.png)

*Near-zero associations cannot rule out wetland methane flux responses.*

### Reproducible analysis notebooks

- [09_inundation_dynamics_2019_2025_QA_v2.ipynb](notebooks/09_inundation_dynamics_2019_2025_QA_v2.ipynb)
- [10_hydroclimatic_controls_2019_2025.ipynb](notebooks/10_hydroclimatic_controls_2019_2025.ipynb)
- [11_tropomi_methane_qa_2019_2025.ipynb](notebooks/11_tropomi_methane_qa_2019_2025.ipynb)

### Scientific interpretation reports

- [NOTEBOOK10_HYDROCLIMATE_FINDINGS.md](research_docs/reports/NOTEBOOK10_HYDROCLIMATE_FINDINGS.md)
- [NOTEBOOK11_TROPOMI_QA_FINDINGS.md](research_docs/reports/NOTEBOOK11_TROPOMI_QA_FINDINGS.md)

### Analysis result tables

- [inundation09_s1_scene_inventory.csv](docs/assets/tables/analysis_2019_2025/inundation09_s1_scene_inventory.csv)
- [inundation09_track_selection.csv](docs/assets/tables/analysis_2019_2025/inundation09_track_selection.csv)
- [inundation09_processing_parameters.json](docs/assets/tables/analysis_2019_2025/inundation09_processing_parameters.json)
- [inundation09_monthly_2019_2025.csv](docs/assets/tables/analysis_2019_2025/inundation09_monthly_2019_2025.csv)
- [inundation09_annual_coverage_qa.csv](docs/assets/tables/analysis_2019_2025/inundation09_annual_coverage_qa.csv)
- [inundation09_2022_month_matched_departures.csv](docs/assets/tables/analysis_2019_2025/inundation09_2022_month_matched_departures.csv)
- [inundation09_annual_raster_coverage_qa.csv](docs/assets/tables/analysis_2019_2025/inundation09_annual_raster_coverage_qa.csv)
- [inundation09_june2022_spatial_qa.csv](docs/assets/tables/analysis_2019_2025/inundation09_june2022_spatial_qa.csv)
- [inundation09_june2022_spatial_summary.csv](docs/assets/tables/analysis_2019_2025/inundation09_june2022_spatial_summary.csv)
- [inundation09_run_manifest.json](docs/assets/tables/analysis_2019_2025/inundation09_run_manifest.json)
- [hydro10_merged_monthly_2019_2025.csv](docs/assets/tables/analysis_2019_2025/hydro10_merged_monthly_2019_2025.csv)
- [hydro10_annual_input_qa.csv](docs/assets/tables/analysis_2019_2025/hydro10_annual_input_qa.csv)
- [hydro10_monthly_seasonal_climatology.csv](docs/assets/tables/analysis_2019_2025/hydro10_monthly_seasonal_climatology.csv)
- [hydro10_2022_month_matched_departures.csv](docs/assets/tables/analysis_2019_2025/hydro10_2022_month_matched_departures.csv)
- [hydro10_deseasonalized_associations.csv](docs/assets/tables/analysis_2019_2025/hydro10_deseasonalized_associations.csv)
- [hydro10_leave_year_out_predictions.csv](docs/assets/tables/analysis_2019_2025/hydro10_leave_year_out_predictions.csv)
- [hydro10_leave_year_out_model_metrics.csv](docs/assets/tables/analysis_2019_2025/hydro10_leave_year_out_model_metrics.csv)
- [hydro10_2022_context_and_heldout_residuals.csv](docs/assets/tables/analysis_2019_2025/hydro10_2022_context_and_heldout_residuals.csv)
- [hydro10_processing_manifest.json](docs/assets/tables/analysis_2019_2025/hydro10_processing_manifest.json)
- [methane11_annual_availability.csv](docs/assets/tables/analysis_2019_2025/methane11_annual_availability.csv)
- [methane11_monthly_availability.csv](docs/assets/tables/analysis_2019_2025/methane11_monthly_availability.csv)
- [methane11_seasonal_availability.csv](docs/assets/tables/analysis_2019_2025/methane11_seasonal_availability.csv)
- [methane11_selection_bias_strata.csv](docs/assets/tables/analysis_2019_2025/methane11_selection_bias_strata.csv)
- [methane11_coverage_sensitive_associations.csv](docs/assets/tables/analysis_2019_2025/methane11_coverage_sensitive_associations.csv)
- [methane11_monthly_qa_joined.csv](docs/assets/tables/analysis_2019_2025/methane11_monthly_qa_joined.csv)
- [methane11_qa_manifest.json](docs/assets/tables/analysis_2019_2025/methane11_qa_manifest.json)
<!-- LOCAL_2019_2025_RESULTS_END -->

<!-- BIOMASS_2026_START -->
## ESA Biomass P-band SAR — 2026 Observations and Cross-Sensor Analysis

**Status:** Preliminary analysis; independent validation ongoing.

The analysis uses a fully polarimetric ESA Biomass Level-1B acquisition from
**2 October 2026**, alongside Sentinel-1 C-band SAR from
**30 September 2026** and Sentinel-2 optical observations from
**7 October 2026**.

### Methods

ESA Biomass Level-1B amplitudes, annotation metadata, and
NetCDF radiometry/geolocation lookup tables were examined.
The MAAP-Project Gamma0 processor generated projected
25 m linear Gamma0 imagery.

The four polarization products (HH, HV, VH, VV) were clipped
to the Hakaluki study boundary. Sentinel-1 VV/VH and
Sentinel-2 reflectance indices were prepared on a common
25 m EPSG:32646 grid.

The analyses include radiometric-processing consistency checks,
descriptive polarization contrasts, optical wetness-index
stratification, and observation-quality assessment.

### Result 1 — ESA Biomass P-band observations

![Reference-processed HH, HV, VH and VV Gamma0 maps of Hakaluki Haor.](docs/assets/figures/biomass_2026/biomass_20261002_reference_gamma0_four_polarizations.png)

*Reference-processed HH, HV, VH and VV Gamma0 maps of Hakaluki Haor.*


The four polarization layers provide complete numerical coverage
of the mapped study-area pixels. Their spatially varying radar
responses are not yet assigned to validated land-cover or
inundation classes.

### Result 2 — Multi-sensor observations

![P-band, C-band and Sentinel-2 observations acquired on different dates.](docs/assets/figures/biomass_2026/biomass_08W_multisensor_comparison.png)

*P-band, C-band and Sentinel-2 observations acquired on different dates.*


P-band and C-band observations show spatially varying
backscatter patterns. Sentinel-2 provides complementary
optical evidence, subject to cloud masking and the temporal
offset between acquisitions.

### Result 3 — Polarization contrasts

![Within-sensor polarization contrasts for P-band and C-band radar.](docs/assets/figures/biomass_2026/biomass_08W_polarization_contrast.png)

*Within-sensor polarization contrasts for P-band and C-band radar.*


The median within-sensor contrasts were approximately
8.16 dB for P-band HH minus HV and 11.00 dB for
C-band VV minus VH. These differences do not establish
that one sensor is more accurate for flood detection.

### Result 4 — Radar response across optical MNDWI

![Radar backscatter relationships with Sentinel-2 MNDWI.](docs/assets/figures/biomass_2026/biomass_08X_radar_mndwi_relationships.png)

*Radar backscatter relationships with Sentinel-2 MNDWI.*


Across the observed optical-index quartiles, median
backscatter was lower in the higher-MNDWI group:

| Radar channel | High minus low MNDWI median |
|---|---:|
| P-band HH | -5.79 dB |
| P-band HV | -2.70 dB |
| P-band VH | -2.55 dB |
| P-band VV | -5.79 dB |
| C-band VV | -8.39 dB |
| C-band VH | -14.45 dB |

MNDWI quartiles are descriptive categories, not validated
water or dry-land reference classes. Pixels are spatially
autocorrelated, and observation dates differ.

### Result 5 — Processing consistency

![Differences between reconstructed and MAAP reference Gamma0 observations.](docs/assets/figures/biomass_2026/biomass_08S_gamma0_processor_difference_histograms.png)

*Differences between reconstructed and MAAP reference Gamma0 observations.*


| Polarization | Matched samples | Median absolute difference | Pearson r |
|---|---:|---:|---:|
| HH | 19,045 | 0.869 dB | 0.931 |
| HV | 19,045 | 0.816 dB | 0.878 |
| VH | 19,045 | 0.805 dB | 0.869 |
| VV | 19,045 | 0.877 dB | 0.938 |

The processor comparison indicates internal consistency
between two processing approaches. It does not constitute
independent radiometric or spatial validation.

### Data and reproducibility

- [Cross-sensor statistics](docs/assets/tables/biomass_2026/biomass_08W_cross_sensor_statistics.csv)
- [Polarization contrast statistics](docs/assets/tables/biomass_2026/biomass_08W_polarization_contrasts.csv)
- [Radar–MNDWI statistics](docs/assets/tables/biomass_2026/biomass_08X_mndwi_stratified_radar_statistics.csv)
- [Gamma0 processor comparison](docs/assets/tables/biomass_2026/biomass_08S_matched_gamma0_processor_comparison.csv)
- [ESA Biomass MAAP](https://portal.maap.eo.esa.int/)
- [MAAP reference processor](https://github.com/MAAP-Project/esa-biomass-gamma0)

### Remaining scientific limitations

Independent image registration, radiometric-quality assessment,
noise-floor evaluation, temporal change assessment, and
independently interpreted water/vegetation reference observations
are still required.

**No methane flux estimates, validated flooded-vegetation map,
or sensor-superiority claim are presented from this experiment.**

<!-- BIOMASS_2026_END -->
