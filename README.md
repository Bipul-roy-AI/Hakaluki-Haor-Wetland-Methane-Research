# Hakaluki Haor | Satellite Wetland Dynamics, Hydroclimate and Methane Observability

**Location:** Hakaluki Haor, northeastern Bangladesh  
**Primary study:** January 2019–December 2025  
**Additional sensor experiment:** ESA Biomass P-band, October 2026  
**Methods:** Sentinel-1 SAR, Sentinel-2 multispectral imagery, CHIRPS, ERA5-Land, Sentinel-5P TROPOMI, ESA Biomass, GIS, Google Earth Engine and Python.

> **Study status:** Exploratory satellite research. Low-VV screening is **not a validated water/flood map**. Changes in radar backscatter do **not** independently establish water depth, event severity, or hydrological cause. Atmospheric XCH₄ column observations and hypothetical enhancement scenarios are **not methane emission measurements**. No ground-truth water-class labels or field methane-flux measurements were available.

## Main findings — reviewed Analysis 13

Per-acquisition analysis of Sentinel-1 data for May–September 2022–2025 shows that the timing and spatial pattern of radar change vary between years. Six paired same-orbit scene comparisons were aligned on a common 30 m grid, with only pixels observed in both scenes included in spatial differences. The following are **net changes in the area satisfying a low-VV screening threshold**, not changes in validated flooded area.

| Within-orbit acquisition pair | −19 dB (km²) | −17 dB (km²) | −15 dB (km²) | Median ΔVV (dB) |
|---|---:|---:|---:|---:|
| 11–23 May 2022 | +119.42 | +121.26 | +116.86 | −10.17 |
| 4–28 June 2022 | +16.50 | +4.38 | +3.91 | −0.99 |
| 11–23 June 2023 | +121.91 | +121.06 | +118.33 | −10.13 |
| 5–17 June 2024 | −103.92 | −18.58 | +0.53 | +4.50 |
| 17–29 June 2024 | +90.91 | +20.55 | +1.45 | −2.00 |
| 22 May–3 June 2025 (descending) | +4.65 | +42.07 | +66.46 | See detailed table |

All areas are based on the paired-screening grid; the common observed grid support for these pairs is approximately **172.27 km²**. The summary values describe six selected scene pairs, not all acquisition intervals. The three thresholds operate on the same VV data and are **not independent confirmations**.

**Interpretation:** The 2022 May and 2023 June comparisons show widespread co-occurring changes in VV and VH and large increases in low-VV detections across all three thresholds. June 2022 shows a much smaller net change. The June 2024 comparisons exhibit strong threshold sensitivity and opposing polarization responses, so they should not be interpreted as independently confirmed water recession or reflooding. May–June 2025 is also threshold-sensitive.

![May 2022 same-orbit radar change](docs/assets/figures/analysis13/13B_2022_may_expansion_spatial_change.png)

*May 2022: −17 dB detection-state transitions and continuous ΔVV/ΔVH; no independent water labels.*

![June 2023 same-orbit radar change](docs/assets/figures/analysis13/13B_2023_june_expansion_spatial_change.png)

*June 2023: spatially coherent radar changes, not a validated flood map.*

![June 2024 early-to-mid radar change](docs/assets/figures/analysis13/13B_2024_june_early_to_mid_spatial_change.png)

*June 2024: widespread VV increase with threshold-sensitive screening changes.*

The other three comparison maps, all three VV-threshold results per pair, and complete scene identifiers are available in the [paired transition table](docs/assets/tables/analysis13/13B_paired_spatial_transitions.csv).

### Radiometric sensitivity and temporal chronology

The 13A radiometric diagnostics examined 11 scenes at 550 fixed coordinates, and 13C assessed a **94-acquisition** May–September 2022–2025 record with **86 within-orbit intervals**. Twelve intervals have same-direction low-VV screening changes of at least 20 km² at all three thresholds. Acquisition gaps mean that these are **observed intervals**, not exact transition onset dates.

![VV threshold sensitivity](docs/assets/figures/analysis13/13A_threshold_sensitivity_top15.png)

![Per-acquisition 2022–2025 record](docs/assets/figures/analysis13/13C_four_year_scene_comparison.png)

### Hydrological forcing and event timing

13D documents first-observed low-VV screening-crossing intervals and the availability of hydrological inputs. **No historical upstream rainfall series or measured river-stage time series was incorporated in the reviewed 13D outputs.** Screening chronology alone cannot attribute the radar changes to upstream flooding, rainfall or backwater effects. Earlier CHIRPS-based monthly associations are exploratory rather than causal.

### Independent satellite-reference feasibility

13E identified and checked Sentinel-2 candidate scenes near the radar acquisitions and calculated same-optical-date usable-point coverage using the Sentinel-2 scene classification layer (SCL). This is **observability screening, not classification validation**. Approximately 550 fixed diagnostic points were checked; cloud-free coverage is incomplete and some monsoon SAR dates had zero usable points among the tested candidates. No independently interpreted water/non-water reference labels, confusion matrix, overall accuracy or area-adjusted flood estimate have been established. SCL water classes were **not used as independent truth labels**.

### Methane observability

13F explored **27 hypothetical** source-area, methane-flux and wind scenarios to assess the possible order of magnitude of full-column enhancements. These scenarios are assumptions, not site-measured fluxes or detected methane plumes. Native TROPOMI Level-2 retrieval sampling/QA has not been demonstrated by the reviewed results. Earlier monthly TROPOMI analysis also found substantial monsoon retrieval gaps. **No Hakaluki-specific methane emission rate or flood-to-methane response is claimed.**

## Methods and reproducibility

- [13A — VV/VH radiometric diagnostics](notebooks/13A_VV_VH_Radiometric_Diagnostics.ipynb)
- [13B — Paired spatial change detection](notebooks/13B_Paired_Spatial_Change_Detection.ipynb)
- [13C — Per-acquisition chronology](notebooks/13C_Event_Chronology_Threshold_Robustness.ipynb)
- [13D — Hydrology and data availability](notebooks/13D_Stage_and_Upstream_Hydrology.ipynb)
- [13E — Satellite-reference workflow](notebooks/13E_Independent_Satellite_Validation.ipynb)
- [13E — Tile-union and reference design continuation](notebooks/13E_continue_tile_union_and_reference_design.ipynb)
- [13F — Hypothetical methane observability](notebooks/13F_TROPOMI_Methane_Observability.ipynb)
- [Reusable analysis source](src/analysis13/)
- [Analysis 13 unit tests](tests/test_analysis13.py)
- [Analysis 13 tables and manifests](docs/assets/tables/analysis13/)
- [Analysis 13 figures](docs/assets/figures/analysis13/)
- [Reviewed 13B findings](research_docs/reports/ANALYSIS13B_REVIEWED_FINDINGS.md)
- [Publication status and limitations](research_docs/reports/ANALYSIS13_PUBLICATION_STATUS.md)

The earlier [2019–2025 monthly analysis](research_docs/FINDINGS_2019_2025_AND_LIMITATIONS.md), [methods](research_docs/METHODS_AND_LIMITATIONS.md), [roadmap](research_docs/ROADMAP.md), and the descriptive ESA Biomass P-band experiment are retained for provenance. Some earlier exploratory map products may be superseded for event interpretation and must not be treated as independently validated flood extents.

## Known limits and future verification

Independent optical image interpretation for an explicitly defined reference population is required before reporting water-class accuracy. Suitable historical river-stage records and basin-wide forcing are needed for hydrological attribution. Retrieval-level sampling and atmospheric transport evidence are required before evaluating local methane enhancements, and measured fluxes or a defensible atmospheric inversion are required before estimating emissions. The present repository reports what the satellite data and completed analyses actually support, without inventing unavailable field measurements.
