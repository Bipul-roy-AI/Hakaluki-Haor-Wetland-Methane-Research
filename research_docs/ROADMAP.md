# Research development roadmap — Hakaluki Haor

## Completed processing / exploratory evidence

- [x] Imported and geometrically audited a user-provided Hakaluki study polygon (source provenance outstanding).
- [x] Processed monthly Sentinel-1, optical, hydrometeorological and atmospheric methane covariates for 2019–2025.
- [x] Produced 84 monthly environmental records with one cache fingerprint.
- [x] Exported and locally verified 18 thematic GeoTIFFs for March, June and October 2022.
- [x] Generated a first exploratory GitHub/portfolio gallery with data and figures.
- [x] Prepared preliminary statistical and ML screening analyses (not emission-flux validation).

## Stage A — Mapping and independent validation [priority: highest]

- [ ] Verify Hakaluki boundary provenance against a primary institutional dataset.
- [ ] Produce independent reference labels and multi-date stratified validation.
- [ ] Audit monthly Sentinel-1 acquisition geometry and image footprints.
- [ ] Quantify water classification sensitivity and cloud/no-data effects.
- [ ] Disaggregate vegetated inundation, permanent water and flooded rice plots.

## Stage B — Dynamic wetland products

- [ ] Export full-resolution monthly maps or reproducible on-demand mosaics.
- [ ] Compute 2019–2025 **observation-normalized** water occurrence, not nominal number-of-month hydroperiod without coverage checks.
- [ ] Produce seasonal reference maps and 2022 anomalies.
- [ ] Determine independently dated flash-flood event windows from gauges, rain and image sequences.

## Stage C — Novel sensors

- [ ] Query ESA Biomass MAAP for valid Hakaluki footprint coverage and downloadable P-band scenes.
- [ ] Compare candidate P-band wetland indicators with Sentinel-1 C-band and independently labelled wetlands.
- [ ] Test whether open/vegetated haor ecology supports the same added value as forested tropical wetlands; publish negative findings if relevant.
- [ ] Explore Sentinel-5A coverage and retrieval product maturity; do not splice datasets without cross-calibration.

## Stage D — Methane process inference

- [ ] Profile Level-2 methane retrieval counts, QA and missingness around events.
- [ ] Test transport- and meteorology-aware background differences, blocked validation, and baseline models.
- [ ] Assess inundation and temperature contributions via GAM / distributed lag with confidence intervals and robustness checks.
- [ ] Where practical, use an established atmospheric inversion for emissions rather than equating XCH4 concentration with methane flux.

## Stage E — Ground calibration and publication

- [ ] Design site stratification and sample-size/power assessment for field flux campaigns.
- [ ] Integrate independent measured flux into calibrated models.
- [ ] Publish uncertainty-aware maps, processed tables, reproducible workflow and a data DOI.

Use GitHub Issues or a Project board to track stages A–E. Avoid posting an exact completion date before available observation quality and feasibility are established.
