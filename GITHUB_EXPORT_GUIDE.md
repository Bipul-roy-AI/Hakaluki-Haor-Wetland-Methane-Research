# Hakaluki Haor — Export every available result to a GitHub portfolio

## Paths in your Windows installation

Project: `F:\Wetland Test\Hakaluki_Haor_Wetland_Test_Jupyter_GEE_Project`

Google Earth Engine Cloud Project: `axial-paratext-491911-b6`

User-provided study polygon: `Study area\Hakaluki_Haor.shp` (not independently validated)

## One-time installation

1. Extract this update ZIP **into the existing project folder**, merging the `src/`, `notebooks/`, `tests/` folders. It does not overwrite notebooks 00–04.
2. Run `04_install_portfolio_dependencies.bat` (adds Rasterio and notebook utilities).
3. Launch Jupyter using `02_start_jupyter.bat`.

## Run order

1. Notebook `00_boundary_and_gee_setup.ipynb` — create audited polygon, initialize GEE.
2. Notebook `01_flood_hydroclimate_methane.ipynb` — 2022 monthly observations; optionally set `RUN_FULL_RECORD=True` for all 2019–2025.
3. Notebook `02_data_qa_and_models.ipynb` — analysis tables and models only when enough observations exist.
4. Notebook `04_exports_and_cartography.ipynb` — existing handpicked mapping layers (optional; the new batch notebook also exports maps).
5. **New** Notebook `05_batch_gee_map_exports.ipynb` — make a monthly raster-export plan, enable task submission, repeat for next batch.
6. Download completed `.tif` files from the Google Drive folder `Hakaluki_Haor_Study` into `results\rasters`.
7. **New** Notebook `06_github_portfolio_release.ipynb` **OR** `05_build_github_release.bat` — generate shareable maps/charts/CSV and an HTML+Markdown gallery.

You can rerun steps 5–7 whenever new GEE jobs or field measurements become available. The release builder can be run without GEE access: it reads only **completed real files** from your disk.

## Running Notebook 05 safely

- First run with `DRY_RUN=True` to preview jobs.
- Set `DRY_RUN=False` to submit at most `MAX_NEW_TASKS` tasks (default 8).
- Run it again after reviewing tasks to submit more jobs. Previously submitted names in `results/tables/ee_export_task_manifest.csv` are skipped.
- Select `YEARS=[2022]` and `MONTHS=[3,4,5,6,7,8,9]` for the initial flood-season pilot.
- To make the full temporal collection use `YEARS=list(range(2019,2026))` and `MONTHS=list(range(1,13))`. **Be mindful:** this can imply hundreds of jobs, quota limits, and significant processing time.
- Layer types include `SAR_water`, `S2_NDVI`, `S2_MNDWI`, `DW_class`, `CHIRPS_rain`, `ERA5_temp`, and `TROPOMI_CH4`.
- `TROPOMI_CH4` rasters represent *atmospheric* XCH4, not wetland emissions. `SAR_water` is an unvalidated surface water proxy, not vegetation flooding or methane flux.
- Export image pixel size is specified for visual mapping; it is not native independent TROPOMI measurement resolution.
- The CSV task manifest indicates EE task submissions, not file completion. Review the task states and download successfully generated files from Google Drive.

## Where all outputs appear

| Folder | Contents |
|---|---|
| `data/processed/` | Original monthly CSV checkpoints from Notebook 01 |
| `results/tables/` | Raw analysis tables and Earth Engine export task log |
| `results/figures/` | Notebook-generated statistical figures |
| `results/maps/` | Boundary QA and hand-crafted map figures |
| `results/rasters/` | **All downloaded full-resolution GeoTIFFs** (keep locally or archival storage) |
| **`results/github_release/`** | **Self-contained GitHub/portfolio directory** with every available small derived CSV, figure/gallery PNG, charts SVG, QA and metadata |

The portfolio release rebuilds from scratch and writes a SHA-256 manifest. All downloaded rasters are catalogued; raster originals remain in `results/rasters/`. Publishing every GeoTIFF directly on GitHub is not recommended because they may be very large. Use Google Drive, Zenodo, or another archive for complete rasters, record dataset licenses, and link the archive from the GitHub README. Do not publish Earth Engine login tokens, service-account keys, or other credentials.

## Upload to GitHub

Create an empty public repository, then **upload the contents** of `results/github_release/`, such that `README.md`, `index.html`, `data/`, `figures/` are in the repository root. This makes image links render automatically in the GitHub README.

Git command alternative in the `results/github_release` folder:

```bat
cd /d "F:\Wetland Test\Hakaluki_Haor_Wetland_Test_Jupyter_GEE_Project\results\github_release"
git init
git add .
git commit -m "Add Hakaluki preliminary research figures and data"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Replace the example remote URL with your real repository URL, and ensure it is empty. Do **not** execute this command verbatim with the placeholder URL. You can use GitHub's web uploader instead.

Optionally enable GitHub Pages (Settings → Pages → deploy from `main`/root) to publish `index.html` as a portfolio page. Public Pages availability depends on your GitHub account and repository settings.

## Scientific integrity and publication status

- No satellite raster/maps are bundled as empirical research results. Earth Engine must execute the processing.
- `results/github_release/` only contains data actually found in local outputs, never synthetic observations.
- User-provided wetland boundary requires source confirmation, geometry QC, and appropriate map scale.
- Low-VV Sentinel-1 maps are **screening results** requiring accuracy validation.
- TROPOMI XCH4 is **column concentration**, not methane flux or attributed wetland emissions.
- The reference-ring comparison is not a wind-matched background or atmospheric transport inversion.
- Field methane measurements can be integrated later through the original Notebook 03. No chamber observations are invented.
