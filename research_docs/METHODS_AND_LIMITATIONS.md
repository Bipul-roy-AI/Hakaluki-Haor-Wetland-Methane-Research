# Methods and methodological limitations

## Fixed-VV 2019–2025 reanalysis (Notebook 09)

The older results described below used **exploratory water screens including Otsu-based thresholds**. Those results must **not** be pooled as if they were the same as the later consistent-track fixed-VV analysis.

The later local 2019–2025 reanalysis selected **Sentinel-1 ascending relative orbit 41** (214 source images covering 84 months), tested **−19, −17 and −15 dB VV** thresholds, masked scene angles outside **30–45°**, and used focal-median spatial filtering with the **original valid-data observation mask preserved**. Annual occurrence was normalized by the **number of observed months per pixel**, rather than automatically treating missing observations as dry. Annual rasters used a projected 30 m UTM 46N grid. The June 2022 spatial departure was computed as 2022's binary screening detection minus other years' mean June screening frequency at each supported pixel. These are **unvalidated low-VV indicators, not water classification accuracy or inundation probability estimates**.

June 2022 nominal low-VV area was 162.775 km²; the median June area in the other six years was 120.099 km² (difference +42.676 km²). The distinct pixelwise **mean-frequency-equivalent** June difference was +42.164 km², which must not be conflated with the median-area departure. June 2024 (164.882 km²) and 2025 (161.269 km²) were similarly high at −17 dB; 2022 and 2024 change order between −19 and −17 dB. The maximum monthly nominal area represents about **96.4%** of the project polygon, limiting resolution of hydrologically distinct high-water states.

Notebook 10 used CHIRPS/ERA5-Land climate covariates to examine seasonal and antecedent rainfall association, and compared fixed-alpha Ridge models with simpler seasonal baselines under leave-one-year-out splits. Predictor normalization was fitted only within training years, but seasonal month indicators and seasonal rain features were penalized jointly, so coefficients do not isolate pure rainfall anomalies. The reported +0.524 three-month rainfall association was the maximum of 18 screened correlations; the three-month sum was not a standalone Ridge predictor. Notebook 11 audited TROPOMI Level-3-derived XCH4 missingness (69/84 ROI months) and coverage-sensitive associations; it **did not** audit native Level-2 soundings or estimate methane flux.

**Public availability:** Notebook source code 09–11, 14 new figures, 26 result tables/manifests and two scientific reports are now published on GitHub. Independent end-to-end reproduction and scientific validation remain outstanding. The previous notebooks/figures remain useful as earlier exploratory products; they should be clearly distinguished from the new local methods. See [findings and limitations](FINDINGS_2019_2025_AND_LIMITATIONS.md).

## Interpretation updates after the October 2026 scientific review

**Radar comparison and temporal resolution.** The prior `−17 dB` 2022 June departure is a useful descriptive comparator, not a statistical test of exceptional flood severity. June 2022, 2024 and 2025 reach similarly high nominal areas. Scene-level analysis should retain individual acquisition time in **UTC and Bangladesh time (UTC+06:00)**. The source inventory contains an alternative descending relative orbit 77 (**181 scenes; 77 distinct months**) as well as ascending orbit 41. Different radar viewing directions cannot be averaged into a single uncalibrated backscatter value. Apply angle and observation-support masks to each scene; report valid support and VV/VH distributions by pass and date. Observation-normalized low-VV detection frequency is not a validated *water hydroperiod*; first/last observed radar detections do not locate exact flood onset/recession between acquisitions.

**CHIRPS and river forcing.** Earth Engine `UCSB-CHG/CHIRPS/DAILY` rainfall is local precipitation at coarser native spatial support than Sentinel-1. The precise daily accumulation-date convention was **not verified** in this project. For scene-level comparisons, record original CHIRPS date labels, compare UTC-to-local conversion, inspect ±1-day rainfall alignment and 3-/7-day sums, and only discuss hydrological causality with additional stage/upstream forcing evidence. An empirical stage–area relation is conditional on compatible stage observations and independently supported spatial water classifications.

**Climate-model selection.** The published Ridge model uses 12 month indicators, rainfall at lags 0–2, ERA5 temperature and fixed `alpha=20`. Pooled error is not stable across years; **2022 held-out Ridge MAE 15.19 km²** versus **seasonal baseline 9.32 km²**. The observed June Ridge component +40.01 km² from rainfall is a model decomposition relative to standardized global training means, **not** a rain-anomaly effect. An exploratory `alpha=1` improvement selected after looking at held-out folds is **not a validated gain**. Any future alpha/feature choice needs nested blocked training-fold selection and a common evaluation sample. Seven year blocks limit precision.

**Atmospheric methane sampling.** The Notebook 11 calendar-month departure requires **at least three valid years**; this drops **July and August** from the correlations, leaving **49/66 (74.2%)** observations outside June–October. The observed +10.0 ppb/year approximate methane background trend and a descriptive rho near −0.08 after simple detrending **do not** recover monsoon information. The ROI-minus-ring mean is about +7.23 ppb but does not define a transport-independent background. Any additional harmonic or season-specific analyses chosen after seeing these results are sensitivity exercises, not statistically independent validation.

**Methane detectability gate.** XCH4 in ppb is not a flux. Before fitting any detailed event response, inspect a limited native Level-2 footprint/QA sample (time, sampling density, valid retrievals, errors), then test habitat-weighted distributed-source enhancements under multiple wind scenarios. An assumed IPCC rice emission factor must not be applied to the entire haor. A crude steady-state box estimate is an assumption check, **not** an instrument detection limit; separate random, systematic and meteorological variability. Only proceed to transport/OSSE or local inversion if observations and plausible signal amplitudes justify it.

**Statistical integrity.** Do not describe exploratory rank positions as a significance test, compare predictive errors from different 81- versus 82-month samples as if controlled, infer climate causality from lags, or equate a near-zero available-month correlation with evidence against wetland methane emission changes.

## Design and geographic scope

- Study site: Hakaluki Haor, northeastern Bangladesh.
- Study period used in current monthly processing: January 2019 to December 2025.
- Study area: Hakaluki Haor, northeastern Bangladesh, delineated by the project's boundary polygon (EPSG:4326; approximately 172.29 km² in projected measurement). All area statistics refer to this delineated study extent, not to the entire surrounding landscape.
- Google Earth Engine processing cloud project configured by the local researcher. Do not publish authentication tokens.

## Derived datasets

| Variable | Platform | Unit | Key limitations |
|---|---|---|---|
| Preliminary SAR low-VV screen | Sentinel-1 GRD | binary mask/area km² | Older Otsu-based and newer fixed-VV methods differ; monthly 1–3-scene median, possible threshold saturation, geometry sensitivity and unvalidated flooded-vegetation omissions |
| NDVI/MNDWI | Sentinel-2 surface reflectance | unitless | Cloud and cloud-shadow, compositing, tidal/seasonal effects; source image count does not equal per-pixel cloud-free coverage |
| Water, crops and flooded vegetation | Dynamic World | categorical / area km² | Classification confidence matters; June 2022 export reportedly had one source item |
| Rainfall | CHIRPS | mm/month and daily 2022 | Coarse native grid; may not capture upstream flow; day-boundary convention not established |
| 2 m air temperature | ERA5-Land | °C | Coarse native grid, model-based temperature covariate |
| Methane atmosphere | Sentinel-5P TROPOMI | XCH4 in ppb | Atmospheric column average; high monsoon missingness and transport confounding; not CH4 flux |

## Data quality already observed in processing logs

The 2019–2025 local QA reported 84 monthly rows, 84 unique periods, one processing fingerprint, zero ordering violations among reported low/base/high water-screen estimates, and no water-screen estimates greater than the ROI area. There were 69/84 ROI XCH4 monthly values (15 missing), while ROI-minus-background values were present for 68/84 months. All 84 water screens are flagged `preliminary_unvalidated`.

These are **data integrity** checks. They are not evidence of absolute flood map accuracy, methane measurement representativeness, or causal inference. Low/high water threshold outputs are **sensitivity ranges, not calibrated confidence intervals**.

## Analysis principles

1. Preserve original geographic CRS in metadata. For distances and pixel area use an appropriate projected equal-area solution or explicit geodesic/pixel-area reductions, not an unverified degree-to-square-kilometre conversion.
2. Treat masks as missing data, never automatically as non-water. Compute area based on valid observation support.
3. Do not resample coarser atmospheric and climate fields to claim 10–30 m measurements.
4. Use time-matched, comparable orbit geometry and independent reference labels for radar classification evaluation.
5. Treat Level-3 TROPOMI grid coverage as an exploratory diagnostic; check Level-2 retrieval QA, native pixel footprints, uncertainty, meteorology and atmospheric sources before attribution.
6. Fit interpretable seasonal/lag models before complex ML, use blocked-by-year and held-out event validation; quantify leakage, predictive uncertainty and baseline improvements.
7. Clearly separate concentration (ppb), emission flux (mass per area per time), and bottom-up wetland-emission model outputs.

## Primary limitations to display beside figures

- The delineated study extent defines the spatial scope of all reported area calculations.
- Neither older Otsu nor newer fixed-VV masks identify all flooded vegetation, river stage or flood mechanisms without external validation.
- One to three scenes per month are too sparse for exact flash-flood onset/recession estimates.
- Monsoon gaps reduce TROPOMI methane analyses precisely at high flood periods.
- A change in XCH4 is not automatically a local wetland flux change.
- Transfer learning from FLUXNET-CH4 cannot replace independent haor validation.

## Interpretation and future calibration

Scientific interpretation should use **low-VV detections**, **observed sampling support**, **atmospheric XCH4** and **validation status** precisely; reserve *validated inundation* for classes tested against external references and *wetland methane flux* for appropriate direct/inversion measurements. When independent data become available, new mechanisms may be tested separately from the current atmospheric screening.
