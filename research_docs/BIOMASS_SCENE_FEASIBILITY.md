# ESA Biomass P-band feasibility for Hakaluki Haor

**Status: analysis designed, coverage not yet checked.** Public data availability does not guarantee valid scenes for this particular wetland or successful flood mapping.

ESA announced open Biomass data access in January 2026, following the April 2025 launch. ESA Biomass MAAP advertises Level 1A–1C SAR and Level 2A/B products. Start with geographic/time coverage and acquisition metadata before committing to direct backscatter comparison.

- Official ESA commissioning announcement: https://www.esa.int/Applications/Observing_the_Earth/FutureEO/Biomass/ESA_s_Biomass_goes_live_with_data_now_open_to_all
- ESA MAAP Biomass data offer: https://portal.maap.eo.esa.int/biomass/biomass-data-offer/
- ESA mission description: https://www.esa.int/Applications/Observing_the_Earth/FutureEO/Biomass

## Feasibility audit workflow

1. Search ESA MAAP catalog for imagery with coverage intersecting Hakaluki Haor (rough bounds: E 91.9524–92.1217°, N 24.5781–24.7348°), dates after the mission launch.
2. Obtain product identifiers, acquisition timestamps, scene footprint GeoJSON, product class, orbit/geometry, polarizations, radiometric conventions, and quality flags.
3. Export **footprints only** to `data/raw/biomass_scene_footprints.geojson`. Do not put login tokens in the GeoJSON or commit non-permitted product metadata.
4. Run `notebooks/08_biomass_pband_feasibility.ipynb` to calculate footprint overlap and scene list. This notebook is a **metadata audit**, not a P-band land-cover classifier.
5. If valid Level-1 scenes exist, decide whether to compare standardized backscatter/polarimetric features to independent flood labels. Time-match Sentinel-1 acquisitions carefully and state date differences.
6. Compare water/vegetation mapping skill against a held-out, stratified independent reference set. Report when open-haor conditions do not benefit from P-band penetration.

Do not extrapolate a 2025+ Biomass acquisition back to 2019–2024, claim the same sensor geometry as Sentinel-1 C-band, or imply actual P-band wetland maps already exist.
