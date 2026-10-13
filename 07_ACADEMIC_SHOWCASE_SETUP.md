# Academic research showcase — Windows setup

Place these extension files into the project root:

`F:\Wetland Test\Hakaluki_Haor_Wetland_Test_Jupyter_GEE_Project`

**Merge** the `src/`, `notebooks/` and `tests/` folders. Keep the existing Notebook 00–06 files, data and GeoTIFFs. This add-on does not overwrite your original processing scripts or your current README.

## Run

1. Ensure Notebook 06 generated `results/github_release/figures/` and that the raster exports are in `results/rasters/`.
2. Double-click `07_build_academic_showcase.bat`, or run the supplied Notebook 07 using your current Jupyter kernel.
3. Open `README_ACADEMIC_PREVIEW.md` and `docs/index.html`. Confirm all graphics and numerical labels.
4. To publish the main repo overview: **back up/replace** the root `README.md` with the verified contents of `README_ACADEMIC_PREVIEW.md`. You may also run the optional Notebook 07 cell to publish with automatic backup.
5. Commit `docs/`, `research_docs/`, `src/academic_showcase.py`, `build_academic_showcase.py`, notebooks and validated/curated assets to GitHub. Do not commit `.venv`, Earth Engine tokens, `data/raw`, or unreviewed bulk satellite archives.
6. For GitHub Pages, use repository **Settings → Pages → Deploy from a branch → main → /docs** (confirm the UI in your account).

The script inspects **real local data only**. The three-panel SAR figure is rebuilt from your GeoTIFFs using correct longitude/latitude axes. It never fills missing XCH4 observations and does not claim calibrated methane flux.

## Expected main outputs

- `README_ACADEMIC_PREVIEW.md` — academic README, with linked images and results
- `docs/index.html` — offline-compatible and GitHub Pages gallery
- `docs/assets/figures/` — selected figures and corrected SAR comparison
- `docs/data/` — selected reproducible CSV outputs
- `docs/data_catalog.csv` — derived data catalogue
- `docs/source_manifest.csv` — SHA-256 hashes for published local figure/table files
- `docs/summary.json` — computed inventory and caveats

## If images are missing

The README includes only figures found on disk. Run Notebook 06 first, then rerun this builder. Raster-based triptych additionally requires all 3 SAR_water GeoTIFFs for March, June and October 2022.

## Crucial research limits

- Source polygon is geometrically valid, but authoritative wetland-boundary provenance has not been confirmed.
- SAR water is an Otsu low-VV screening class, not a validated flood product.
- Dynamic World June 2022 used only one scene in the submitted manifest.
- Rainfall (CHIRPS) and ERA5-Land temperature should be treated as coarse-grid climate covariates, not fine-scale maps.
- TROPOMI XCH4 is column methane and has significant missingness during monsoon months.
- Field methane flux calibration remains future work.
