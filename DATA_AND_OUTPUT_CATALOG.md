# Hakaluki Haor — data and output catalog

## User configuration (pre-configured)

- Windows working root: `F:\Wetland Test`
- Google Cloud Earth Engine project: `axial-paratext-491911-b6`
- Pilot: 2022
- Period for multi-year extension: 2019–2025
- Cloud export destination: Google Drive folder `Hakaluki_Haor_Study`
- Local GeoTIFF directory (download Drive exports here): `results/rasters/`
- Field flux template: `results/calibration/field_flux_template.csv`

## Raw datasets (collected live from Earth Engine; not embedded in this ZIP)

| Source | Earth Engine ID | Role | Spatial caution |
| --- | --- | --- | --- |
| Sentinel-1 | `COPERNICUS/S1_GRD` | VV backscatter open-water screen | Optical-like water masks fail for many inundated vegetation types |
| Sentinel-2 SR | `COPERNICUS/S2_SR_HARMONIZED` | NDVI and MNDWI screening | Cloud cover restricts observations |
| Dynamic World | `GOOGLE/DYNAMICWORLD/V1` | Modal water / flooded vegetation / crops | Classification is not a ground-truth habitat inventory |
| CHIRPS Daily | `UCSB-CHG/CHIRPS/DAILY` | Daily and monthly precipitation | Local rainfall is not upstream river discharge |
| ERA5-Land monthly | `ECMWF/ERA5_LAND/MONTHLY_AGGR` | Air temperature | Coarse meteorological reanalysis |
| Sentinel-5P CH4 | `COPERNICUS/S5P/OFFL/L3_CH4` | Atmospheric XCH4 mixing ratio | NOT wetland methane emission flux or independent 1.1km measurements |

## What actually gets saved when notebooks are executed

- `data/boundary/`: candidate downloaded GIS files; audit JSON, candidate GeoJSON and optional user-supplied verified GeoJSON.
- `data/processed/monthly_YYYY-MM.csv`: one monthly checkpoint with an input/code fingerprint, only after successful EE computation.
- `data/processed/monthly_YYYY_YYYY_combined.csv`: collection of calculated year/month rows.
- `data/processed/CHIRPS_daily_2022.csv`: daily mean CHIRPS rainfall (only after EE computation).
- `results/maps/`: candidate boundary audit map and cartographic PNGs created from real downloaded rasters.
- `results/figures/`: pilot time series and modelling diagnostics.
- `results/tables/`: QA summaries, satellite orbit selection, model comparisons, and export task manifest.
- `results/rasters/`: exported GeoTIFFs **downloaded manually from Google Drive**; Drive export tasks do not write to F: automatically.
- `results/calibration/`: empty observed-flux template and provisional future sampling site recommendations. No sample is represented as observed.

## Interpretation and validation gate

1. **Boundary:** The public GitHub GIS file is a candidate only. A Bangladesh government website gives a geographic envelope (24°35′–24°44′N and 92°01′–92°09′E) and indicative area (181.15 km²). That does not establish a definitive GIS boundary. The analysis must be reconciled against an agency wetland delineation before reporting authoritative area estimates.
2. **Water:** The Otsu monthly Sentinel-1 VV result is only a screening classification. Validate water/non-water with independent imagery / manually interpreted points; explicitly address flooded vegetation.
3. **Dates:** Monthly composites do not resolve precise daily flood onset, duration, or response lags. Integrate gauge data and event chronology later.
4. **Methane:** XCH4 (ppb) is atmospheric concentration, not flux. L3 grid coverage does not equal retrieval counts or source attribution. More rigorous inversion and field calibration are separate later stages.
5. **Analysis:** A negative or non-significant result must not be converted into a positive emission claim. Report missingness and model out-of-year validation.

## Primary documentation

- Hakaluki geographic description (Sylhet District Administration): https://sylhet.gov.bd/pages/tourist-spot/696ca15483f6c1a51f3ab774
- Original third-party shapefile (provenance unverified): https://github.com/aburaihan21/Bangladesh-All-GIS-Shapefile-Data/tree/main/Hakaluki%20Haor
- Earth Engine authentication: https://developers.google.com/earth-engine/guides/auth
- Earth Engine Python installation: https://developers.google.com/earth-engine/guides/python_install
- Earth Engine Sentinel-5P methane collection: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_OFFL_L3_CH4
