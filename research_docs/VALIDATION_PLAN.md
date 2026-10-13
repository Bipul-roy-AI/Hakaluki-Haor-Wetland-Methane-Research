# Validation and uncertainty plan

This checklist is designed for the eventual paper and for reviewers assessing reproducibility.

| Activity | Action | Acceptance criteria / outputs | Current status |
|---|---|---|---|
| Study area documentation | Record boundary file source, date, spatial resolution and extent | transparent GIS boundary metadata | Geometry prepared; metadata to be documented |
| SAR water classification | Stratified independent water/non-water reference labels across dry and monsoon conditions | confusion matrices, producer/user accuracy, area-adjusted CI, sensitivity across thresholds | Not done |
| Flooded vegetation | Compare optical, C-band SAR, and any ESA P-band scenes in vegetated classes | habitat-specific errors and omission analysis | Planned |
| Temporal representativeness | Record exact acquisition dates, valid observation counts and temporal interpolation assumptions | event uncertainty, acquisition time plots | Sparse 1–3 SAR scenes/month |
| Optical data quality | QA masking and valid composite fraction by month/pixel | cloud coverage and masking evaluation | Planned |
| Methane QA | Native L2 retrieval QA, errors, area/time sampling, clouds, background region | native-footprint support and uncertainty, no imputation of absent months | Preliminary L3 only |
| Atmospheric transport | Wind/trajectory or formal chemical-transport sensitivity tests | directional attribution sensitivity | Not done |
| Model evaluation | Held-out years/events and simpler seasonal benchmarks | folds, metrics, uncertainty intervals, ablation for flooding/temperature | Exploratory only |
| Flux calibration | Local chamber, eddy covariance, published comparable sites or valid inverse flux | independent observations and predictive errors (appropriate units) | Future |
| Data archiving | Complete code and metadata; immutable data version/hashes | release note, reproducibility record | Partially complete |

**No stage is automatically marked validated by successful export, a cache fingerprint, a perfect in-sample fit, or high raster coverage.**
