# Hakaluki Haor | Wetland inundation and atmospheric methane dynamics

**Reproducible Earth Observation research in northeastern Bangladesh**  
Sentinel-1 SAR · Sentinel-2 · Dynamic World · TROPOMI XCH₄ · CHIRPS · ERA5-Land · GIS · Python · Google Earth Engine

> **Research status: exploratory / ongoing.** Flood masks are low-VV screening products, not validated flood maps. TROPOMI measures atmospheric column methane (XCH₄), not wetland surface methane flux. Local field flux calibration and atmospheric inversion have not yet been completed.

## Research at a glance

| Indicator | Currently documented |
|---|---|
| Study period | 2019–2025 |
| Monthly records | 84 |
| Local GeoTIFF exports inventoried | 18 (not necessarily committed to Git) |
| Months with an ROI XCH₄ value | 69 / 84; retrieval-quality screening remains essential |
| Study-area polygon | User-provided, topologically valid; source accuracy not independently confirmed |
| Field methane flux observations | Not yet collected |

## Featured results

### Study-area boundary (researcher-supplied; provenance pending)

![Study-area boundary (researcher-supplied; provenance pending)](docs/assets/figures/hakaluki_boundary_audit_map.png)

### Seasonal water-screen comparison: March, June and October 2022

![Seasonal water-screen comparison: March, June and October 2022](docs/assets/figures/hakaluki_2022_sar_geographic_comparison.png)

### 2019–2025 time series: water screen, hydroclimate and XCH₄

![2019–2025 time series: water screen, hydroclimate and XCH₄](docs/assets/figures/01_monthly_timeseries.png)

### Multi-year descriptive seasonality

![Multi-year descriptive seasonality](docs/assets/figures/03_monthly_seasonality.png)

### Observational completeness and uncertainty

![Observational completeness and uncertainty](docs/assets/figures/02_data_completeness.png)

### Exploratory pairwise relationships (not causal)

![Exploratory pairwise relationships (not causal)](docs/assets/figures/04_exploratory_correlations.png)

## Scientific questions

1. **Inundation mapping:** How do apparent open-water extent and flooded vegetation vary seasonally and during flood disturbances, and how accurate are different sensors?
2. **Atmospheric methane:** When quality-controlled data exist, are regional XCH₄ anomalies associated with flood extent and hydroclimate after accounting for observation gaps and atmospheric transport?
3. **Process controls:** How do inundation, temperature and vegetation jointly explain observed variability, and what would be required to infer methane surface flux?

These questions parallel the themes of the University of Leeds PhD advertisement *Magnitude and Controls of Tropical Wetland Methane Emissions Using Novel Satellite Data* (PGR-P-2558). **This project is independent and is not presented as a University of Leeds or ESA collaboration.**

## Available outputs

- [Interactive/static project gallery](docs/index.html)
- [Data catalogue](docs/data_catalog.csv) and [source/output inventory](docs/source_manifest.csv)
- [Methods and limitations](research_docs/METHODS_AND_LIMITATIONS.md)
- [Research questions and PhD alignment](research_docs/PHD_RELEVANCE.md)
- [Validation strategy](research_docs/VALIDATION_PLAN.md)
- [Current research roadmap](research_docs/ROADMAP.md)
- [Data dictionary and provenance](research_docs/DATA_DICTIONARY_AND_PROVENANCE.md)

### Curated analysis tables

- [Monthly 2019–2025 environmental dataset](docs/data/hakaluki_monthly_2019_2025.csv)
- [Data completeness and missingness](docs/data/complete_data_quality_2019_2025.csv)
- [Detailed variable completeness](docs/data/hakaluki_2019_2025_data_quality.csv)
- [Exploratory month-lag correlations](docs/data/monthly_lag_screen.csv)
- [Preliminary model comparison](docs/data/exploratory_year_holdout_models.csv)
- [Monthly seasonal anomaly table](docs/data/seasonally_adjusted_anomalies.csv)
- [Data completeness summary](docs/data/data_completeness.csv)

## Reproducibility

Source processing notebooks are in `notebooks/`; reusable modules in `src/`; GEE scripts in `gee/`. The original unedited boundary, potentially large rasters, authenticated settings, and intermediate datasets may remain local or be published in a suitable versioned research archive. Do not assume that the complete Earth Engine archive is included in a GitHub clone. See [`research_docs/GITHUB_PUBLISHING_GUIDE.md`](research_docs/GITHUB_PUBLISHING_GUIDE.md).

## What has been established versus what is next

| Current status | Evidence / next experiment |
|---|---|
| **Processed** | 84 monthly environmental records; 18 GeoTIFF exports inventoried locally |
| **Preliminary** | Satellite-derived low-VV water-screen patterns; exploratory XCH₄ statistics and machine-learning benchmarks |
| **Validation needed** | Independent flood labels, vegetated inundation detection, SAR sensitivity, cloud/retrieval QA, spatial and temporal generalization |
| **Planned** | ESA Biomass P-band coverage and pilot comparison; Sentinel-5A feasibility; meteorology-informed methane transport/inversion |
| **Future calibration** | Local chamber/flux measurements and independent site-based methane model evaluation |

## Relevant literature and mission documentation

- [Saunois et al. (2025), *Global Methane Budget 2000–2020*](https://doi.org/10.5194/essd-17-1873-2025)
- [ESA Biomass data open to researchers (26 January 2026)](https://www.esa.int/Applications/Observing_the_Earth/FutureEO/Biomass/ESA_s_Biomass_goes_live_with_data_now_open_to_all)
- [ESA Biomass MAAP product catalogue](https://portal.maap.eo.esa.int/biomass/biomass-data-offer/)
- [ESA Sentinel-5 mission](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-5)

## Attribution and research integrity

Satellite data remain subject to their providers’ terms. Maps are derived products, not official flood maps. No claim is made of field-validated methane flux, local emission inventories, or causal attribution. See the output manifest for reproducible file hashes.
