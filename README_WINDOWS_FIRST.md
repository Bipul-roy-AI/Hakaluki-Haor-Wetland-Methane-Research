# Hakaluki Haor — Windows/Jupyter runbook

## Your exact configured paths

- Local working directory: `F:\Wetland Test`
- Google Earth Engine Cloud project: `axial-paratext-491911-b6`
- Google Drive export folder: `Hakaluki_Haor_Study`
- Study: Hakaluki Haor only
- First trial: 2022; multi-year extension: 2019–2025
- Later calibration: chamber / other measured surface CH4 flux, stored separately from atmospheric XCH4

## 1. Extract ZIP

Create `F:\Wetland Test` in File Explorer. Extract all archive entries **directly into that folder**. The correct structure is:

```
F:\Wetland Test\
  01_install_windows.bat
  02_start_jupyter.bat
  03_run_local_tests.bat
  requirements.txt
  README.md
  README_WINDOWS_FIRST.md
  config\settings.json
  src\hakaluki_core.py
  src\ee_pipeline.py
  gee\hakaluki_2022_quicklook.js
  notebooks\00_boundary_and_gee_setup.ipynb
  notebooks\01_flood_hydroclimate_methane.ipynb
  notebooks\02_data_qa_and_models.ipynb
  notebooks\03_future_field_sampling_design.ipynb
  notebooks\04_exports_and_cartography.ipynb
  results\calibration\field_flux_template.csv
```

**Do not** extract into `F:\Wetland Test\hakaluki_haor_study\...`, since notebook paths are explicitly fixed to `F:\Wetland Test`.

## 2. Install Python

Install Python 3.11 or 3.12 (64-bit). Enable the Windows Python Launcher (`py`) during installation if available. Check `py -3 --version` in Command Prompt.

Double-click `01_install_windows.bat`. It creates `.venv` **inside F:\Wetland Test**, installs Python packages and registers a dedicated notebook kernel. Installation requires internet.

If PowerShell restricts script execution, use these `.bat` files in Command Prompt instead; activation through `.bat` does not require PowerShell policy changes.

## 3. Start Jupyter

Double-click `02_start_jupyter.bat`. In the browser, open `notebooks/00_boundary_and_gee_setup.ipynb` and select the kernel **Python (Hakaluki Haor)**. The kernel executes inside `.venv` even when working with spaces in the folder name.

## 4. Authenticate Google Earth Engine

The first live Earth Engine cell will attempt `ee.Initialize(project="axial-paratext-491911-b6")`; if not authenticated it calls `ee.Authenticate()`, which requests a Google account login. Authenticate with an account allowed to access the Cloud project.

Check in Google Cloud Console that this project has the Earth Engine API enabled and is registered for EE use. Your Python EE account and project permissions must permit computation. Errors about project registration, billing or IAM must be fixed in the Cloud console by a user with the appropriate permissions.

Run this optional smoke test in a notebook:

```python
import ee
ee.Authenticate()
ee.Initialize(project='axial-paratext-491911-b6')
print(ee.Number(1).getInfo())
```

Successful output: `1`. **This is a connection test only, not a flood or methane analysis.**

## 5. Run notebooks in sequence

1. `00_boundary_and_gee_setup.ipynb`: downloads a candidate shapefile (requires GitHub connectivity), audits geometry, and checks Earth Engine collection counts. The third-party polygon is NOT an authoritative boundary; if you have an official one place it at `data\boundary\hakaluki_verified.geojson`. Inspect its provenance and spatial correspondence.
2. `01_flood_hydroclimate_methane.ipynb`: runs twelve 2022 monthly analyses, saves real Earth Engine-derived CSV files in `data\processed` and preliminary figures in `results\figures`. Also creates CHIRPS daily rainfall chart. It has opt-in cells for GEE map/GeoTIFF export and a per-observed-month low-backscatter frequency map.
3. `02_data_qa_and_models.ipynb`: audits missing observations and, after sufficient multi-year data are processed, seasonal anomaly correlations, monthly lag screening, and predictive model comparison. No dummy methane targets.
4. `03_future_field_sampling_design.ipynb`: generates PROVISIONAL site candidates for later field inspection, using Dynamic World habitats. No measurements are invented.
5. `04_exports_and_cartography.ipynb`: submits OPTIONAL Earth Engine map exports and plots local, real GeoTIFF images after they are downloaded from Drive.

## 6. Export raster maps

Go to Notebook 01 -> **Section E** (SAR water masks), or Notebook 04 -> **Section C** (multiple SAR, vegetation, climate and XCH4 map layers). and set `SUBMIT_DRIVE_EXPORTS=True` to initiate GeoTIFF tasks in Earth Engine; check their eventual status. Also set `RUN_FREQUENCY_MAP=True` then `EXPORT_FREQUENCY_MAP=True` for the 2022 per-pixel observed-month water-screen frequency; this is NOT continuous flood duration.

The GeoTIFFs export **to your Google Drive**, not automatically to `F:`. Download finished exports from Drive and save in `F:\Wetland Test\results\rasters\` (create directory if needed). Earth Engine export tasks use the authenticated Google account.

## 7. Run multi-year analysis

Only after assessing the 2022 pilot and reviewing boundary and water masks, set `RUN_FULL_RECORD=True` in Notebook 01. It calculates 2019–2025 monthly series (84 months), reusing existing per-month CSV checkpoints. If you revise boundary, class algorithms or orbital geometry, move old CSV checkpoints aside before rerunning (input/code fingerprints prevent silent mixing). Results must have a methodology/version log.

## 8. Field methane calibration remains planned

Use `results\calibration\field_flux_template.csv` when true field measurements become available. The preliminary ML task predicts regional atmospheric methane anomaly, **NOT local surface methane flux**. A separate calibration model should later use observed flux as its target, with suitable spatial-temporal alignment and independent test sites.

## Important scientific warnings

- Default SAR Otsu water maps are SCREENING classifications, not validated flood maps or inundated vegetation detection. They currently do **not** implement the DeVries flood anomaly algorithm.
- TROPOMI EE Level-3 methane is atmosphere column XCH4 in ppb, not CH4 emissions in mg m^-2 h^-1. The gridded EE display is finer than the independent retrieval footprints.
- Matching rainfall to upstream catchment inflows and local flood stage requires additional hydrology; 2022 precipitation in the wetland alone is not a flash-flood timing measurement.
- No satellite calculations have been run in this packaging environment; all results are computed after you authorize Earth Engine and execute notebooks.
- The candidate boundary could be inaccurate. Its presence in a public GitHub repository is not proof of authority.

## Official documentation

- GEE Python setup: https://developers.google.com/earth-engine/guides/python_install
- Authentication: https://developers.google.com/earth-engine/guides/auth
- Sentinel-1 GRD: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD
- Sentinel-5P CH4: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_OFFL_L3_CH4
- CHIRPS daily: https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY
- ERA5-Land monthly: https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_MONTHLY_AGGR

**Reproducibility:** Every monthly CSV checkpoint now records a hash of its input boundary, configuration, and processing code. When these change, archive previous `data/processed/monthly_YYYY-MM.csv` files before rerunning Notebook 01.
