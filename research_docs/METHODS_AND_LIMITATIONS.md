# Methods and methodological limitations

## Methods update: fixed-VV 2019–2025 reanalysis (local Notebook 09)

The older results described below used **exploratory water screens including Otsu-based thresholds**. Those results must **not** be pooled as if they were the same as the later consistent-track fixed-VV analysis.

The later local 2019–2025 reanalysis selected **Sentinel-1 ascending relative orbit 41** (214 source images covering 84 months), tested **−19, −17 and −15 dB VV** thresholds, masked scene angles outside **30–45°**, and used focal-median spatial filtering with the **original valid-data observation mask preserved**. Annual occurrence was normalized by the **number of observed months per pixel**, rather than automatically treating missing observations as dry. Annual rasters used a projected 30 m UTM 46N grid. The June 2022 spatial departure was computed as 2022's binary screening detection minus other years' mean June screening frequency at each supported pixel. These are **unvalidated low-VV indicators, not water classification accuracy or inundation probability estimates**.

June 2022 nominal low-VV area was 162.775 km²; the median June area in the other six years was 120.099 km² (difference +42.676 km²). The distinct pixelwise **mean-frequency-equivalent** June difference was +42.164 km², which must not be conflated with the median-area departure.

Local Notebook 10 used CHIRPS/ERA5-Land climate covariates to examine seasonal and antecedent rainfall association, and compared Ridge models with simpler seasonal baselines under leave-one-year-out splits. Its predictor preprocessing was fitted only within training years. Correlation, cross-validated error and residuals are **not causal evidence**. Local Notebook 11 audited TROPOMI Level-3-derived XCH4 missingness (69/84 ROI months), conditional low-VV availability and coverage-sensitive associations, but **did not** audit native Level-2 retrieval footprints or fit an atmospheric inversion.

**Public availability:** Notebook source code 09–11 is published. Their local execution results (new figures, selected CSVs, manifests and reports) are not yet in the current GitHub repository checkout. The previous notebooks/figures remain useful as earlier exploratory products; they should be clearly distinguished from the new local methods. See [findings and limitations](FINDINGS_2019_2025_AND_LIMITATIONS.md).

## Design and geographic scope

- Study site: Hakaluki Haor, northeastern Bangladesh.
- Study period used in current monthly processing: January 2019 to December 2025.
- Study area: Hakaluki Haor, northeastern Bangladesh, delineated by the project's boundary polygon (EPSG:4326; approximately 172.29 km² in projected measurement). All area statistics refer to this delineated study extent, not to the entire surrounding landscape.
- Google Earth Engine processing cloud project configured by the local researcher. Do not publish authentication tokens.

## Derived datasets

| Variable | Platform | Unit | Key limitations |
|---|---|---|---|
| Preliminary SAR water screen | Sentinel-1 GRD | binary screen/area km² | Monthly selected orbit images, commonly 1–3; low VV Otsu does not capture all flooded vegetation; requires independent classification validation |
| NDVI/MNDWI | Sentinel-2 surface reflectance | unitless | Cloud and cloud-shadow, compositing, tidal/seasonal effects; source image count does not equal per-pixel cloud-free coverage |
| Water, crops and flooded vegetation | Dynamic World | categorical / area km² | Classification confidence matters; June 2022 export reportedly had one source item |
| Rainfall | CHIRPS | mm/month | Coarse native grid; not metre-scale rainfall |
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
- Low-VV Otsu water areas cannot identify all flooded vegetation or distinguish flood mechanisms.
- One to three scenes per month are too sparse for exact flash-flood onset/recession estimates.
- Monsoon gaps reduce TROPOMI methane analyses precisely at high flood periods.
- A change in XCH4 is not automatically a local wetland flux change.
- Transfer learning from FLUXNET-CH4 cannot replace independent haor validation.

## Interpretation and future calibration

Scientific interpretation should consistently use 'classified water', 'screening-grade', 'regional XCH4', 'exploratory', and 'validation planned'. When chamber/flux observations become available, a new flux-response model can be calibrated and reported separately from the current atmospheric proxy analysis.
