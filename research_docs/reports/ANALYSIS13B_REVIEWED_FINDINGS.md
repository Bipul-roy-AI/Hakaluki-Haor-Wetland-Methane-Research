# Hakaluki Haor — Analysis 13B reviewed results

## Scope and evidence

Six paired Sentinel-1 same-orbit observations were processed on a 30 m EPSG:32646 raster grid, using shared valid pixel support. The four threshold classes are mutually exclusive. All spatial areas are 30 m grid-cell accounting, not field-validated water extent. The submitted CSV has 18 rows (six pairs × three tested VV thresholds), and six accompanying spatial figures. All six comparisons have a common grid-center valid support area of 172.2717 km².

## Net low-VV screening changes (km²)

| Paired interval | −19 dB | −17 dB | −15 dB | Median ΔVV (dB) |
|---|---:|---:|---:|---:|
| `2022_may_expansion` | +119.42 | +121.26 | +116.86 | -10.17 |
| `2022_june_stable` | +16.50 | +4.38 | +3.91 | -0.99 |
| `2023_june_expansion` | +121.91 | +121.06 | +118.33 | -10.13 |
| `2024_june_early_to_mid` | -103.92 | -18.58 | +0.53 | +4.50 |
| `2024_june_mid_to_late` | +90.91 | +20.55 | +1.45 | -2.00 |
| `2025_may_june_descending` | +4.65 | +42.07 | +66.46 | -1.81 |

## Main findings

1. **Large, relatively threshold-consistent decreases in VV backscatter:** 11–23 May 2022 and 11–23 June 2023 show net gains of about 117–122 km² under all three thresholds, along with median VV drops near −10 dB. The continuous ΔVV and ΔVH maps show widespread negative changes. This is strong evidence for a major scattering transition, not independently verified expansion of inundated area.
2. **June 2022 high-screening conditions were comparatively stable:** 4–28 June gained only +4.38 km² at −17 dB, although the −19 dB estimate is +16.50 km². Stability refers to total screening area, not necessarily all pixel states.
3. **June 2024 shifts are threshold-fragile:** 5–17 June ranges from −103.92 km² to +0.53 km² across thresholds. The 17–29 June recovery ranges from +90.91 to +1.45 km². Broad shifts in VV with different VH behavior make a simple flood-recession/recovery reading unsupported.
4. **May–June 2025 contains substantial spatial turnover:** At −17 dB, newly screened area is 64.12 km² and no-longer-screened area is 22.05 km², leaving +42.07 km² net. At −19 dB net change is only +4.65 km², and at −15 dB it is +66.46 km². Thus net extent hides opposing transitions and is threshold-sensitive.

## Quality checks

- Six named pairs; each has three thresholds.
- All CSV class areas sum to shared observed support within 0.002 km², allowing for rounding.
- New minus lost low-VV area reproduces net area within 0.002 km².
- The researcher reported the notebook passed finite-value checks and produced all six maps.
- The `RuntimeWarning: invalid value encountered in subtract` arises at eager NumPy subtraction within `np.where`; this is consistent with NaN/Inf in masked raster cells but does not by itself establish whether the valid-pixel mask is correctly constructed. Audit `good` and use `np.subtract(..., where=finite_valid_mask, out=...)` before a strict publication claim about all continuous deltas.

## Limits and next work

- Threshold agreement uses nested VV masks, **not independent validation**.
- Spatially coherent darkening can arise from water, wet soil, vegetation or sensor/processing conditions.
- Multiple epochs and exact interval lengths are required to infer timing; no day-exact flood onset is claimed.
- Next critical step: independent date-matched Sentinel-2/reference interpretation and a documented stratified confusion matrix (13E).
- 13D upstream rainfall and river-stage attribution requires real external data. 13F hypothetical methane-detectability scenarios are not measured emission flux or an actual native TROPOMI L2 QA audit.

## Figure index

| Map | Role |
|---|---|
| [13B_2022_may_expansion_spatial_change.png](13B_2022_may_expansion_spatial_change.png) | Four −17 dB transition classes and continuous ΔVV/ΔVH; descriptive only |
| [13B_2022_june_stable_spatial_change.png](13B_2022_june_stable_spatial_change.png) | Four −17 dB transition classes and continuous ΔVV/ΔVH; descriptive only |
| [13B_2023_june_expansion_spatial_change.png](13B_2023_june_expansion_spatial_change.png) | Four −17 dB transition classes and continuous ΔVV/ΔVH; descriptive only |
| [13B_2024_june_early_to_mid_spatial_change.png](13B_2024_june_early_to_mid_spatial_change.png) | Four −17 dB transition classes and continuous ΔVV/ΔVH; descriptive only |
| [13B_2024_june_mid_to_late_spatial_change.png](13B_2024_june_mid_to_late_spatial_change.png) | Four −17 dB transition classes and continuous ΔVV/ΔVH; descriptive only |
| [13B_2025_may_june_descending_spatial_change.png](13B_2025_may_june_descending_spatial_change.png) | Four −17 dB transition classes and continuous ΔVV/ΔVH; descriptive only |
