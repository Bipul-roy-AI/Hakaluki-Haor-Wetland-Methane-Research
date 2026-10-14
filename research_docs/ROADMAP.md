# Research development roadmap — Hakaluki Haor

**Updated 14 October 2026 · Status: exploratory analysis published; priority shifted to event-level hydrology and methane observability.**

## Completed work: preserve, do not reinterpret

- [x] Publish Notebooks 00–11, including the 2019–2025 84-month remote-sensing analysis.
- [x] Process a consistent ascending Sentinel-1 orbit 41 series (214 scenes across 84 months) using fixed −19/−17/−15 dB VV screening thresholds. Seven annual observation-normalized low-VV frequency rasters were produced locally.
- [x] Document the June 2022 −17 dB screening departure (+42.676 km² against other-June median) and spatial frequency-equivalent departure (+42.164 km²), **without** describing either as independently validated flood area.
- [x] Verify 2022, 2024 and 2025 have comparably high June low-VV extents; 2022 versus 2024 rankings change with threshold. No unique June 2022 areal maximum is established.
- [x] Publish monthly hydroclimate lag associations and fixed-alpha, leave-one-year-out Ridge versus seasonal-baseline results; held-out 2022 performance was worse for Ridge.
- [x] Publish TROPOMI Level-3-derived monthly XCH4 availability, seasonal selection bias and coverage-sensitive comparisons; June 2022 ROI XCH4 is unavailable. The 66-month correlation sample is predominantly outside June–October.
- [x] Process and present the October 2026 ESA Biomass P-band Gamma0 polarimetric and cross-sensor investigation (not an independent validation study).
- [x] Publish 14 updated figures, 26 analysis tables/manifests and two interpretation reports from Notebooks 09–11.

[Detailed evidence and non-findings](FINDINGS_2019_2025_AND_LIMITATIONS.md) · [Methods and analysis boundaries](METHODS_AND_LIMITATIONS.md) · [Validation plan](VALIDATION_PLAN.md)

## Work package A — Scene-level inundation and event timing [first priority]

- [ ] Build a **per-acquisition**, not monthly-median, Sentinel-1 analysis for monsoon onset and persistence in **2022, 2024, 2025**, with **2023** as a low-extent comparison.
- [ ] Process **ascending orbit 41** and **descending orbit 77** separately, conserving scene ID, acquisition UTC/Bangladesh-local timestamp, VV, VH, incidence geometry and valid-pixel support. Their geometry and acquisition-time differences preclude naïve joint backscatter averaging.
- [ ] Calculate per-scene low-VV area at −19/−17/−15 dB and cross-check histograms and VH context; produce plots with CHIRPS daily and 3/7-day rainfall windows.
- [ ] Verify rainfall accumulation-day convention for the project's Earth Engine CHIRPS v2 daily series before aligning to local satellite dates. Show UTC/Bangladesh timestamps and ±1-day sensitivity.
- [ ] Calculate per-pixel **observed-scene-normalized detection frequency** and first/last *observed* low-VV dates where support is sufficient. Do not label gaps as dry or equate sparse observations with continuous hydroperiod.
- [ ] Deliver the new Notebook 12 scene-level output CSV, QA audit, plot(s), processing manifest and written comparison. **No scene-level processed results have been claimed as completed.**

## Work package B — Hydrological context and satellite validation

- [ ] Seek suitable stage/discharge observations in the regional connected river system and upstream precipitation, including relevant transboundary catchments when data are available. Do not assume a particular station represents the wetland without checking hydraulics.
- [ ] Document study-area boundary metadata and compare spatial delineations if suitable GIS reference boundaries are available; descriptive published area totals alone are not a polygon match.
- [ ] Evaluate inundation depth/duration/onset hypotheses using water levels and overpass dates; distinguish measured stages from interpolated or modelled values.
- [ ] Select **independent, date-matched** reference imagery for open water, exposed surface, flooded vegetation and rice plots; implement stratified validation and error/uncertainty reporting.
- [ ] Consider an empirical stage–area relation **only when** paired reliable stage and validated water-area observations exist. Avoid a premature complex hydrodynamic model or overinterpreting an uncertain flat-terrain DEM.

## Work package C — Methane observability feasibility gate

- [ ] Define a prospective, testable methane estimand: atmospheric XCH4 enhancement in a particular wind/season window, or habitat-weighted wetland flux. The two are not interchangeable.
- [ ] Conduct a **limited native Sentinel-5P TROPOMI Level-2 audit** of actual footprint intersections, qa flags, seasonal counts, surface classes, error terms and retrieval availability during candidate wetland states.
- [ ] Evaluate a **range** of habitat fractions, flux scenarios, winds and distributed source geometry. Label any IPCC rice factor as rice-specific; do not apply it to the whole haor.
- [ ] Distinguish systematic/background/transport errors from independent random retrieval errors. Check whether the observable Level-2 support could constrain a plausible enhancement.
- [ ] **Gate:** undertake sampling-aware transport/observing-system simulation or a regional analysis only if the Level-2 support and estimated signal-to-uncertainty justify it. Otherwise publish a careful non-detectability/observability limitation rather than a local emission claim.
- [ ] Keep Notebook 11's available-month near-zero correlations as descriptive results, not evidence of no flux response. Trend/harmonic/June–September sensitivity checks were explored after inspection and require independent reproduction and pre-specification for confirmatory interpretation.

## Work package D — Hydrological model revision

- [ ] Reevaluate predictors (month effects, local and antecedent rain, possible upstream/stage terms, temperature ablation) on one clearly defined eligible-month sample.
- [ ] Pre-specify a constrained model set; select features and Ridge alpha **inside** blocked-by-year training data, not retrospectively using held-out years.
- [ ] Publish foldwise performance and model stability against a month-of-year baseline. With only seven independent year blocks, uncertainty remains substantial; neither an α=1 exploratory improvement nor an individual-year fit demonstrates generalizable skill.
- [ ] Validate event-scale interpretation separately from retrospective monthly regression.

## Work package E — ESA Biomass and reproducibility

- [ ] Diagnose ~0.8–0.9 dB matched processor differences, registration, radiometric conventions, noise-floor and geometry differences in the 2026 P-band comparison.
- [ ] Assess P- and C-band inundation classes using independent reference labels rather than MNDWI quartiles as assumed truth.
- [ ] Eliminate machine-specific absolute Windows paths and hard-coded cloud project names from re-runnable notebooks; document a clean environment, data access and runtime.
- [ ] Consolidate duplicate Notebook 09 versions after confirming manifest provenance and update links; remove unused dependencies and expand tests for area, observation support, date alignment and departure functions.
- [ ] Retain the project as **one integrated repository**. A paper or two-paper division should follow validated research questions and adequate data, not be predetermined.

## Fieldwork and publication (later stage)

- [ ] If practical, use independent water-level, depth and ground/imagery class observations to strengthen remote-sensing validation.
- [ ] A **wetland methane flux** estimate requires field measurements or a defensible atmospheric inversion with quantified uncertainty; Level-3 XCH4 alone cannot supply one.
- [ ] Publish a frozen reproducible release/DOI when the method and scientific claims support it.

**Priority rule:** First establish whether the remotely sensed hydrological signal and atmospheric sampling are fit for their intended scientific questions. Preserve negative or inconclusive results; do not claim a new finding merely because a notebook runs successfully.
