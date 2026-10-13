# Research development roadmap — Hakaluki Haor

## October 2026 progress update (local notebooks 09–11)

**Completed locally but not yet committed to Git:** 2019–2025 consistent-orbit Sentinel-1 low-VV monthly screening (84/84 periods), seven observation-normalized annual frequency rasters, June 2022 month-matched and spatial departures, CHIRPS/ERA5-Land rainfall-lag and leave-year-out modelling, and TROPOMI Level-3-derived observation availability/selection analysis. See [findings and limitations](FINDINGS_2019_2025_AND_LIMITATIONS.md).

**Completed and publicly presented:** ESA Biomass P-band 2026 pilot with four Gamma0 polarizations, aligned Sentinel-1/Sentinel-2 comparisons, and processor consistency diagnostics. **No independent flood-map accuracy or sensor-superiority results.**

**Still outstanding:** validated inundation reference classes; formal uncertainty; boundary metadata; native TROPOMI Level-2 footprints/retrieval QA and atmospheric transport/source inference; methane surface-flux measurement/inversion; Git upload of local 09–11 artifacts.

## Completed processing / exploratory evidence

- [x] Imported and geometrically checked the Hakaluki Haor project study-area boundary.
- [x] Processed monthly Sentinel-1, optical, hydrometeorological and atmospheric methane covariates for 2019–2025.
- [x] Produced 84 monthly environmental records with one cache fingerprint.
- [x] Exported and locally verified 18 thematic GeoTIFFs for March, June and October 2022.
- [x] Generated a first exploratory GitHub/portfolio gallery with data and figures.
- [x] Prepared preliminary statistical and ML screening analyses (not emission-flux validation).

## Stage A — Mapping and independent validation [priority: highest]

- [ ] Document the Hakaluki study-area boundary data source, date and geographic scope.
- [ ] Produce independent reference labels and multi-date stratified validation.
- [ ] Audit monthly Sentinel-1 acquisition geometry and image footprints.
- [ ] Quantify water classification sensitivity and cloud/no-data effects.
- [ ] Disaggregate vegetated inundation, permanent water and flooded rice plots.

## Stage B — Dynamic wetland products

- [ ] Export full-resolution monthly maps or reproducible on-demand mosaics.
- [x] Compute 2019–2025 **observation-normalized preliminary low-VV screening frequency** (local Notebook 09; unvalidated; public upload pending).
- [x] Produce descriptive 2022 month-matched and spatial June low-VV departures (local Notebook 09; not flood truth).
- [ ] Determine independently dated flash-flood event windows from gauges, rain and image sequences.

## Stage C — Novel sensors

- [x] Query ESA Biomass MAAP and process a valid October 2026 fully polarimetric P-band pilot covering the selected study polygon.
- [ ] Compare candidate P-band wetland indicators with Sentinel-1 C-band and independently labelled wetlands.
- [ ] Test whether open/vegetated haor ecology supports the same added value as forested tropical wetlands; publish negative findings if relevant.
- [ ] Explore Sentinel-5A coverage and retrieval product maturity; do not splice datasets without cross-calibration.

## Stage D — Methane process inference

- [x] Audit **Level-3-derived** monthly ROI methane availability and its seasonal/low-VV selection bias (local Notebook 11).
- [ ] Audit native **Level-2** methane retrieval footprints, QA, counts and uncertainties around events.
- [x] Compare month-baseline and climate Ridge predictions with leave-one-year-out testing (local Notebook 10; mixed accuracy).
- [ ] Test transport- and meteorology-aware methane background differences with native retrieval quality and blocked validation.
- [ ] Assess inundation and temperature contributions via GAM / distributed lag with confidence intervals and robustness checks.
- [ ] Where practical, use an established atmospheric inversion for emissions rather than equating XCH4 concentration with methane flux.

## Stage E — Ground calibration and publication

- [ ] Design site stratification and sample-size/power assessment for field flux campaigns.
- [ ] Integrate independent measured flux into calibrated models.
- [ ] Publish uncertainty-aware maps, processed tables, reproducible workflow and a data DOI.

Use GitHub Issues or a Project board to track stages A–E. Avoid posting an exact completion date before available observation quality and feasibility are established.
