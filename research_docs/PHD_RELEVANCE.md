# Research relevance: tropical wetlands, methane and novel satellite observations

## Independent research statement

This Hakaluki Haor study is an **independent research project in Bangladesh**, not part of and not endorsed by the University of Leeds, ESA, NASA JPL, or their staff. It is motivated in part by shared scientific questions with the **University of Leeds PhD advertisement, PGR-P-2558: _Magnitude and Controls of Tropical Wetland Methane Emissions Using Novel Satellite Data_** (details supplied by the project author; exact current funding and admission eligibility must be confirmed on the official call).

**Advertised eligibility caveat:** The supplied advert specifies **UK only** for funded applicants. Independently verify whether that restricts the funding, the full application, or both before making plans. The present research can stand on its own irrespective of eligibility.

## Connections to the advertised research questions

| Advertised PhD question | Hakaluki baseline | Extension that is scientifically meaningful | Current claim boundary |
|---|---|---|---|
| Accuracy and variability of Biomass-derived wetland extent | Sentinel-1 low-VV water screen; Sentinel-2 NDVI/MNDWI; Dynamic World; a user-provided wetland polygon | Build reference labels, stratify by vegetation, evaluate ESA Biomass P-band coverage and direct sensor agreement | No Biomass validation completed |
| Changes in wetland extent and atmospheric CH4 growth | Monthly SAR water screen, rain and TROPOMI XCH4 (2019–2025) | Retrieval QA, wind/transport-aware regional controls; if justified, atmospheric inversion | A local XCH4 anomaly is NOT a local methane flux or source attribution |
| Sensitivity of CH4 emissions to inundation versus temperature | Flood/temperature/vegetation covariates; exploratory lag and ML models | GAMM/distributed lags; calibration against independent CH4 flux/inversion; sensitivity and uncertainty | Current models address atmospheric CH4 association/prediction, not validated emission sensitivity |

## Testable next experiments

1. **Wetland map agreement:** Create independent labelled reference samples stratified by dry / open water / flooded vegetation / cropland, and report classwise accuracy, area-adjusted uncertainty, and inter-sensor disagreements. Separate permanent water from temporary flooding. Check that optical cloud masks are valid.
2. **P-band opportunity:** Search ESA MAAP for Biomass scenes covering the Hakaluki footprint after the mission launch; inspect Level-1 backscatter/geometry, acquisition times, incidence angle, polarization, radiometric comparability, and vegetation cover. Do not assume P-band improves wetland mapping in an open, shallowly vegetated haor, unlike dense tropical forest.
3. **Methane reliability:** Use native atmospheric methane retrieval quality, uncertainty and count (not only resampled L3 grid completeness); isolate missing monsoon periods, and test sensitivity to changing background regions and meteorology.
4. **Disturbance vs seasonality:** Identify floods from rain, gauges and SAR, then compare event anomalies with year/month baseline. Avoid leakage in held-out years and events.
5. **Flux constraint:** Compare independent global wetland-emission ensembles at their native grid; later use local flux or a properly justified inversion; explicitly propagate uncertainty.

## Relevant original sources

- Saunois, M. et al. (2025). *Global Methane Budget 2000–2020.* **Earth System Science Data**. https://doi.org/10.5194/essd-17-1873-2025
- ESA (2026). *ESA's Biomass goes live with data now open to all.* https://www.esa.int/Applications/Observing_the_Earth/FutureEO/Biomass/ESA_s_Biomass_goes_live_with_data_now_open_to_all
- ESA Biomass MAAP data offer: https://portal.maap.eo.esa.int/biomass/biomass-data-offer/
- ESA Sentinel-5 mission: https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-5
- Copernicus Sentinel-5P collections: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_OFFL_L3_CH4

Biomass is publicly available, but this document does **not** claim that a particular Hakaluki scene was downloaded, suitable, or processed. Sentinel-5A availability, calibration and scientific comparability must be independently audited for any future data fusion.
