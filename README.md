# Hakaluki Haor | Wetland Dynamics, Hydroclimate and Atmospheric Methane Observations

**Study area:** Hakaluki Haor, northeastern Bangladesh  
**Main observation period:** 2019–2025 · **Additional ESA Biomass P-band analysis:** October 2026  
**Tools and data:** Sentinel-1 SAR · Sentinel-2 · CHIRPS · ERA5-Land · Sentinel-5P TROPOMI · ESA Biomass · Google Earth Engine · Python · GIS

## Research overview

This research examines seasonal wetland conditions in Hakaluki Haor using satellite radar, hydroclimatic observations, and atmospheric methane data. The main focus is on understanding **which changes are observable with the available sensors** and which require independent hydrological or land-cover evidence.

The initial monthly analysis (Notebooks 09–11) has been followed by **per-acquisition Sentinel-1 analysis (Notebook 12)** and local **Analysis 13A–13F** workflows. We are consolidating and reviewing those newer analyses before publishing a final set of figures, tables and findings.

**Current status:** Research in progress. The results presented by the radar screen are *low-backscatter observations*, **not independently validated inundation maps**. TROPOMI atmospheric methane column concentrations (XCH₄) do **not directly measure wetland methane emissions**.

## Established findings from the reviewed analysis

The following observations are supported by the publicly available earlier results and by local Analysis 13A–13C outputs reviewed to date. They are **exploratory** rather than independently validated hydrological conclusions.

- **Timing matters:** Per-scene radar observations from May–September 2022–2025 show large low-VV screening changes occurring in different observation intervals. Some within-orbit changes have consistent direction across the tested VV thresholds; they do not establish exact flood onset or recession.
- **Threshold sensitivity matters:** Several scenes, particularly in June 2024 and June 2025, produce substantially different screened areas at −19, −17 and −15 dB. Similar monthly screening areas are not sufficient evidence of similar flood severity.
- **Radar polarization carries additional information:** Fixed-coordinate VV/VH comparisons show differing scattering changes between selected scene pairs. These differences have not yet been assigned to independently validated water or vegetation classes.
- **The monthly analysis cannot uniquely identify a June 2022 flood-area maximum:** June 2022 and June 2024 had similarly high nominal low-VV screening extents, and their relative ranking changes with the VV threshold.
- **Methane attribution is unresolved:** Atmospheric XCH₄ observation gaps during the monsoon and the absence of direct flux observations prevent reliable conclusions about local wetland methane emission responses. Native Level-2 feasibility and atmospheric detectability analyses are separate research questions.

**No field measurements are being represented as available.** Independent satellite reference-image interpretation, publicly available water-level records, and satellite retrieval-quality checks can be pursued without field visits; their results should be presented only after evaluation.

## Research components

| Component | Analysis | Evidence / publication status |
|---|---|---|
| **01 — Monthly Earth observation** | 2019–2025 low-VV screening, climate associations and atmospheric XCH₄ availability | Earlier notebooks and derived results preserved; conclusions subject to the later scene-level checks |
| **02 — Scene-level radar diagnostics** | Sentinel-1 ascending/descending observations, VV/VH statistics, threshold sensitivity and within-orbit chronology | Notebook 12 source and selected results published; local Analysis 13A–13C outputs reviewed; final curated outputs not yet uploaded |
| **03 — Hydrological context** | Upstream rainfall, potential river-stage observations and event timing | Analysis 13D completed locally according to the researcher; outputs not yet independently reviewed for the README |
| **04 — Independent satellite reference assessment** | Date-matched optical/reference images, reference labels and radar classification quality | Analysis 13E completed locally according to the researcher; outputs not yet independently reviewed for the README |
| **05 — Methane observability** | TROPOMI sampling, uncertainty and detectability scenarios | Analysis 13F completed locally according to the researcher; outputs not yet independently reviewed for the README |
| **06 — ESA Biomass P-band** | 2026 polarimetric processing and descriptive P-/C-band/optical comparisons | Earlier processing results retained; independent comparative classification accuracy not established |

## Research files

- [Per-scene Sentinel-1 notebook (12)](notebooks/12_scene_level_wetland_dynamics_2022_2025.ipynb)
- [Earlier Sentinel-1 notebook (09)](notebooks/09_inundation_dynamics_2019_2025_QA_v3_export_fixed.ipynb)
- [Hydroclimate notebook (10)](notebooks/10_hydroclimatic_controls_2019_2025.ipynb)
- [Atmospheric methane availability notebook (11)](notebooks/11_tropomi_methane_qa_2019_2025.ipynb)
- [Published 94-scene screening dataset](docs/assets/tables/analysis_2019_2025/scene12_S1_per_acquisition_2022_2025.csv)
- [Existing scientific findings and qualifications](research_docs/FINDINGS_2019_2025_AND_LIMITATIONS.md)
- [Methods and limitations](research_docs/METHODS_AND_LIMITATIONS.md)
- [Research development roadmap](research_docs/ROADMAP.md)

The repository retains earlier exploratory figures, tables, maps and ESA Biomass outputs for traceability. **They have been removed from the README gallery, not deleted from the research record.** Some earlier methods and visualizations are superseded for event-level interpretation; do not combine them with newer scene-level outputs without checking their definitions.

## Next publication update

The researcher has completed local Analysis 13A–13F. Before publishing an updated results gallery and final interpretation, the remaining work is to **review the outputs and provenance of 13D–13F**, incorporate the completed 13B paired-scene spatial comparisons, and ensure that all reported classification or methane claims reflect the actual validation and observability evidence.

A new results summary, validated figure selection and reproducibility index will be added **after** the final local data, reports and notebooks have been checked and committed.

---

**Interpretation rule:** Report satellite **observations** separately from **classification accuracy**, **hydrological mechanisms**, and **methane emission estimates**. A completed computation or plausible physical explanation is not by itself independent validation.
