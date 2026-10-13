# Methods and methodological limitations

## Design and geographic scope

- Study site: Hakaluki Haor, northeastern Bangladesh.
- Study period used in current monthly processing: January 2019 to December 2025.
- Study boundary: user-provided polygon in EPSG:4326; geometry audit reported valid, nonempty; projected area ~172.2907 km². This is a **study geometry**, not a verified hydrologic boundary, and not permanent water area.
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

- Geometric polygon validity is not administrative/authoritative boundary provenance.
- Low-VV Otsu water areas cannot identify all flooded vegetation or distinguish flood mechanisms.
- One to three scenes per month are too sparse for exact flash-flood onset/recession estimates.
- Monsoon gaps reduce TROPOMI methane analyses precisely at high flood periods.
- A change in XCH4 is not automatically a local wetland flux change.
- Transfer learning from FLUXNET-CH4 cannot replace independent haor validation.

## Interpretation and future calibration

Scientific interpretation should consistently use 'classified water', 'screening-grade', 'regional XCH4', 'exploratory', and 'validation planned'. When chamber/flux observations become available, a new flux-response model can be calibrated and reported separately from the current atmospheric proxy analysis.
