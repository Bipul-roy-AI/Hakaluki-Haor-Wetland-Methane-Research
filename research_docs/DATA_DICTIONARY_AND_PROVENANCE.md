# Data dictionary and provenance

The actual fields exported by the notebooks are authoritative for each product's column names. Example fields in the currently processed monthly dataset:

| Field | Meaning | Unit / warning |
|---|---|---|
| `period` | Calendar month YYYY-MM | discrete month |
| `year`, `month` | Components of month | integer |
| `s1_scenes` | Selected Sentinel-1 scenes per month | counts, **not complete daily coverage** |
| `water_area_km2` | Low VV backscatter classification water screen | km²; unvalidated |
| `water_area_low_km2`, `water_area_high_km2` | Sensitivity to threshold assumptions | km²; not statistical confidence bounds |
| `rain_chirps_mm` | Monthly accumulated CHIRPS precipitation over ROI | mm/month |
| `temp2m_era5_c` | ERA5-Land air temperature | °C, coarse native grid |
| `ch4_xch4_ppb_roi` | Resampled TROPOMI column methane average over ROI | ppb; atmospheric XCH4, not flux |
| `ch4_xch4_ppb_ring` | TROPOMI XCH4 in chosen background ring | ppb; not necessarily matched air mass |
| `ch4_roi_minus_ring_ppb` | ROI–background XCH4 difference | ppb; not independently attributable to haor emissions |
| `ch4_l3_grid_coverage_fraction` | Valid Level-3 sample grid fraction | not proportion of native independent footprints |
| `dw_water_km2` | Dynamic World monthly water-class area | km²; not field-validated |
| `dw_flooded_vegetation_km2` | Dynamic World flooded-vegetation-class area | km²; requires confidence and habitat QA |
| `ndvi_s2_mean`, `mndwi_s2_mean` | Sentinel-2 vegetation/water indices | unitless |
| `result_status` | Computation/validation status | currently `preliminary_unvalidated` |
| `cache_fingerprint` | Local processing fingerprint | not a proof of scientific accuracy |

## Raster provenance and resolution

Each GeoTIFF's coordinate reference system, raster dimensions, units and derived checksum are recorded in `docs/data_catalog.csv` and the Earth Engine task manifest. The 2022 exported test maps had different native support: Sentinel-1 screen at ~30 m export scale, optical indices ~20 m, CHIRPS at coarse several-km resolution, and ERA5-Land coarser still. Do not infer finer physical information from resampled pixels.

## Dataset source portals

- Sentinel-1 GRD: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD
- Sentinel-2 SR Harmonized: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED
- Dynamic World: https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1
- TROPOMI methane: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_OFFL_L3_CH4
- CHIRPS daily: https://developers.google.com/earth-engine/datasets/catalog/UCSB-CHG_CHIRPS_DAILY
- ERA5-Land: https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_HOURLY
- ESA Biomass MAAP: https://portal.maap.eo.esa.int/biomass/biomass-data-offer/

### Publication policy

The public release includes selected derived CSV and PNG outputs and metadata; downloaded large GeoTIFFs can remain local, or be distributed via a versioned research archive or Git LFS after reviewing licences and file size. Never include Earth Engine OAuth tokens or hidden Jupyter server tokens.
