# Notebook 11 — TROPOMI XCH₄ observation quality (2019–2025)

- **Status:** Preliminary Level-3 observation audit; native Level-2 retrieval verification outstanding.
- **Months in calendar:** 84.
- **ROI XCH₄ months:** 69; unavailable: 15.
- **ROI-minus-ring months:** 68.
- **L3 support proxy:** resampled grid fraction, not independent footprints or soundings.
- **Known data gap:** 26 July–31 August 2022 (Earth Engine dataset documentation).

## What cannot be inferred

Neither the Level-3 ROI XCH₄ series nor the ROI-minus-ring contrast is a measurement of Hakaluki wetland methane emissions. Retrieval availability depends on viewing/atmospheric conditions and can be systematically biased by season. Do not fill missing months for causal or flux estimation. Differences across years can reflect background atmospheric methane growth, instrument processing versions and nonlocal transport.

## Scientific requirements before methane attribution

1. Retrieve *native Level-2* methane granules; audit sounding `qa_value`, coverage, footprint intersection, per-sounding precision and supplementary retrieval flags.
2. Check reference region, land/water retrieval bias and monsoon availability, including the 2022 provider gap.
3. Check processing version consistency and bias correction; use averaging kernels/vertical sensitivity if atmospheric modelling.
4. Use meteorological winds and a defensible background or transport/inversion model. Obtain ground flux observations for local validation when feasible.
5. Reevaluate temporal associations with retrieval-count/precision weighting and seasonal missingness-aware sensitivity analyses.

## References

- https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_OFFL_L3_CH4
- https://www.tropomi.eu/data-products/methane
