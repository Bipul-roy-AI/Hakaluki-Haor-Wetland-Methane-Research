# Hakaluki Haor: Flood, hydroclimate and atmospheric methane workflow

## Status — 13 October 2026

This is **code and a reproducible research workspace**, not a completed satellite-data analysis. No live Earth Engine collections were processed in the creation environment (no EE authentication or network access). The only included PNG is a diagram of a government-reported approximate geographic envelope, clearly labelled **NOT A WETLAND BOUNDARY**.

**Field calibration is retained as a later stage**. The template `results/calibration/field_flux_template.csv` stores eventual methane-flux measurements; it is intentionally empty.

## Read first: important scientific distinctions

- Sentinel-1 VH/VV classifications from a simple Otsu threshold are **candidate low-backscatter water masks**, not validated open-water/flooded vegetation maps; they may miss inundation below vegetation and have false positives.
- A monthly SAR composite is not a direct observation of daily flash-flood onset or precise flood duration. Field gauge records or other higher-frequency sources are needed for event dynamics.
- TROPOMI methane in Earth Engine is dry-air column-averaged **XCH₄ in ppb**, NOT a measurement of surface methane flux. Earth Engine L3 at ~1.1 km grid cells does not imply independent retrieval resolution of ~1.1 km. Report observation support and missingness.
- A regional CH₄ reference ring does **not** correct for transport, boundary layers, or heterogeneous rice/agricultural emissions. Methane–flood correlations are exploratory.
- Global wetland flux product pixels must not be resampled to 10 m and presented as independently resolved methane fluxes.
- The candidate GIS polygon has unverified provenance. Compare it to authoritative wetland/ECA delineations before final measurements.

## Recommended workflow

1. Install Python 3.11 or 3.12. From the **project root**, create and activate a virtual environment, then run `pip install -r requirements.txt`.
2. Obtain access to [Google Earth Engine](https://earthengine.google.com/) and register a Cloud project. In `config/settings.json`, set `earth_engine_cloud_project` to its actual project ID.
3. Open `jupyter lab` and run `notebooks/00_boundary_and_gee_setup.ipynb`. It downloads a third-party polygon candidate, checks the area, and produces an inspectable outline. If you have an agency-verified boundary, place it at `data/boundary/hakaluki_verified.geojson` before running.
4. Run `notebooks/01_flood_hydroclimate_methane.ipynb` for **2022**. It saves one CSV per month and a joined yearly table, produces data-derived charts after running, previews maps, and can export 2022 water masks as GeoTIFFs to Drive.
5. First verify candidate boundary, image acquisition geometry, SAR threshold sensitivity, reference flood classification points, TROPOMI spatial support and missingness. Then set `RUN_FULL_RECORD=True` in notebook 01 to process 2019–2025 in batches. Note that pilot files are cached by month; remove them deliberately if changing any algorithm configuration or boundary.
6. Run `notebooks/02_data_qa_and_models.ipynb`. It creates genuine availability plots, seasonal adjustments, lag-correlation screening, and a model comparison **only if enough actual observations exist**.
7. When collecting methane flux data, populate the template and build **a separate calibrated flux model with actual observed flux as the target**. Do not relabel XCH₄-prediction results as flux.

Optional quicklook: paste `gee/hakaluki_2022_quicklook.js` into the [GEE Code Editor](https://code.earthengine.google.com/); the quicklook uses an approximate envelope and -17 dB demo threshold by default and should not be used as a final map.

## Outputs and limits

| Location | Output | Status before running EE |
|---|---|---|
| `results/maps/00_reference_extent_NOT_WETLAND_BOUNDARY.png` | Approximate government-coordinates extent diagram | **Created; not an empirical satellite map** |
| `data/boundary/hakaluki_analysis_candidate.geojson` | Candidate polygon | Created after notebook 00 |
| `results/maps/01_boundary_audit_candidate.png` | Boundary inspection figure | Created after notebook 00 |
| `data/processed/monthly_YYYY-MM.csv` | Monthly real satellite-derived metrics | Created after notebook 01 |
| `results/figures/hakaluki_2022_pilot_series.png` | Actual data time series | Created after notebook 01 |
| `results/tables/*.csv` | QC and benchmark analysis | Created after notebook 02 |
| Google Drive folder `Hakaluki_Haor_Study` | Earth Engine GeoTIFFs | If export tasks are enabled and completed |
| `results/calibration/field_flux_template.csv` | Blank future flux sampling template | **Created (empty)** |

## Data source IDs used in Earth Engine

- Sentinel-1 GRD: `COPERNICUS/S1_GRD`
- Sentinel-2 SR: `COPERNICUS/S2_SR_HARMONIZED`
- Surface-water occurrence: `JRC/GSW1_4/GlobalSurfaceWater` (historical baseline through 2021)
- CHIRPS daily precipitation: `UCSB-CHG/CHIRPS/DAILY`
- ERA5-Land monthly: `ECMWF/ERA5_LAND/MONTHLY_AGGR`
- TROPOMI OFFL CH₄: `COPERNICUS/S5P/OFFL/L3_CH4`
- Dynamic World (future habitat analysis): `GOOGLE/DYNAMICWORLD/V1`

## Selected source references

- Bangladesh Sylhet Government, Hakaluki Haor location / area: https://sylhet.gov.bd/pages/tourist-spot/696ca15483f6c1a51f3ab774
- Third-party candidate boundary (unverified): https://github.com/aburaihan21/Bangladesh-All-GIS-Shapefile-Data/tree/main/Hakaluki%20Haor
- DeVries et al. satellite SAR water detection method / code: https://github.com/bendv/s1flood
- Official Earth Engine Sentinel-1: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD
- Official Earth Engine TROPOMI CH4: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_OFFL_L3_CH4
- Official Earth Engine CHIRPS: https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY
- Official Earth Engine ERA5-Land monthly: https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_MONTHLY_AGGR
- Flood events in Sylhet Haors: https://doi.org/10.2166/wcc.2023.165

## Validation issues before peer-reviewed results

This is a **Phase 1 prototype**. It does not yet implement the DeVries change-detection algorithm from `s1flood`; it uses per-month Otsu-screening VV masks. This is deliberately transparent rather than misrepresenting the screening map as the peer-reviewed method. We should replace this baseline with a validated time-dependent SAR anomaly method and a separate flooded-vegetation validation before publication. Additionally, a no-field version cannot directly calibrate individual-haor flux estimates.

For further stages: verify the boundary against agency GIS maps; add hydrological station time series and upstream catchment delineation; implement independent reference labels for water/flooded vegetation; assess TROPOMI native L2 support, meteorological matching and atmospheric transport; then integrate future field CH4 measurements.

## Optional local map rendering notebook

Run `notebooks/04_exports_and_cartography.ipynb` after 00 and 01 to specify opt-in Google Drive exports for SAR water screens, Sentinel-2 indices, Dynamic World, CHIRPS, ERA5-Land, and TROPOMI XCH4. Place real exported GeoTIFFs in `results/rasters` and re-run the final cells to produce PNG maps. Exports are asynchronous and separate from the local F: drive.

**Reproducibility:** Every monthly CSV checkpoint now records a hash of its input boundary, configuration, and processing code. When these change, archive previous `data/processed/monthly_YYYY-MM.csv` files before rerunning Notebook 01.
