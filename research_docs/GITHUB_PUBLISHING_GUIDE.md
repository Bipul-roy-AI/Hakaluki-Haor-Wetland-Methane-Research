# GitHub publication guide (research-first)

## Prior to upload

1. Review `README_ACADEMIC_PREVIEW.md` and every featured image; figures are selected automatically from locally available exports.
2. Confirm only truthful status labels: *processing complete*, *preliminary classification*, *not field-calibrated*.
3. Inspect that `docs/summary.json`, `docs/data_catalog.csv`, and `docs/source_manifest.csv` reflect your real local files.
4. Check all images, boundary provenance, attribution and third-party dataset licences.
5. Remove secret tokens, user details, local credential files and irrelevant Jupyter history.
6. Back up the existing root `README.md`, then replace it with the reviewed academic preview.

## Recommended Git structure

```text
README.md                  # professor-facing executive overview and highlights
notebooks/                 # research notebooks, including 07 builder
src/                       # processing and showcase code
config/                    # non-secret settings; no OAuth data
gee/                       # exported Earth Engine source scripts
research_docs/             # hypotheses, methods, validation and roadmap
docs/
  index.html               # GitHub Pages gallery
  assets/figures/          # curated PNGs, generated from actual results
  data/                    # selected derived CSVs
  data_catalog.csv
  source_manifest.csv
  summary.json
tests/
```

Keep complete intermediate raster archives outside regular Git history if large; consider Git LFS or a versioned research data repository with a DOI. Do not silently delete essential reproducibility information: list download procedures and provenance in the README.

## GitHub Pages

Once committed to the `main` branch, use **Settings → Pages → Deploy from a branch → main → /docs** (current UI may vary). The `docs/index.html` page references only relative URLs and is also viewable locally.

## GitHub profile README

For a personal GitHub profile, create a repository matching the user account name and add a short entry pointing to the research repository and gallery. See `PROFILE_README_SNIPPET.md`. Do **not** copy all study details onto the profile: put them in the project repository.

## Reviewer honesty statement

> The current repository presents multi-year remote sensing and hydroclimate analyses and preliminary atmospheric methane associations. Sentinel-1 water masks are screening-grade. TROPOMI XCH4 is column atmospheric methane, not measured local wetland CH4 flux. Validation, vegetation inundation analysis, novel P-band integration, inversion, and field calibration remain active/future work.
