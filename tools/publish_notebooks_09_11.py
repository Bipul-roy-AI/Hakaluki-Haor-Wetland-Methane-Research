#!/usr/bin/env python3
"""Publish existing *local* Notebook 09–11 outputs into the GitHub repository.

Copy only curated analysis artifacts (no raw scenes, GeoTIFFs, or secrets).
Figures are embedded in the root README only if the corresponding files exist.
Run from a cloned GitHub repository, with the original analysis project given by
--source. By default this prepares files; --commit-and-push additionally pushes
only the files produced by this script using your configured Git identity.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

FIGURES = {
    "inundation09_monthly_screening_timeseries.png": ("Monthly low-VV screening, 2019–2025", "Low-VV detections are not validated flooded-water area."),
    "inundation09_month_year_heatmap.png": ("Low-VV detections by calendar month and year", "A fixed VV threshold was used; color is an unvalidated screening statistic."),
    "inundation09_2022_month_matched_departures.png": ("2022 monthly differences relative to other years", "Differences compare screening areas, not confirmed additional floodwater."),
    "inundation09_annual_lowvv_frequency_2019_2025.png": ("Annual observation-normalized low-VV occurrence, 2019–2025", "The denominator is the number of valid observed months per pixel; not an inundation probability."),
    "inundation09_june2022_spatial_lowvv_departure.png": ("June 2022 spatial difference from historical June screening frequency", "Per-pixel binary-minus-frequency departure; not a flood-area-change map."),
    "hydro10_timeseries_rain_temperature_lowvv.png": ("Rainfall, temperature and low-VV screening series", "Monthly covariates, not causal drivers or flood verification."),
    "hydro10_seasonal_cycle.png": ("Seasonal cycle of hydroclimate and low-VV screening", "Descriptive monthly aggregation."),
    "hydro10_2022_radar_rainfall_departures.png": ("2022 radar and rainfall departures", "Coincidence does not establish causal flooding."),
    "hydro10_deseasonalized_lag_associations.png": ("Deseasonalized hydroclimatic associations", "Serial correlation and multiple comparisons limit inference."),
    "hydro10_leave_year_out_hindcast.png": ("Out-of-year climate-model hindcasts versus seasonal baseline", "Predictive performance is mixed across years."),
    "methane11_availability_and_grid_support.png": ("TROPOMI XCH4 month-by-month availability and Level-3 grid support", "Level-3 coverage does not equal native Level-2 retrieval footprints."),
    "methane11_roi_ring_time_series.png": ("Atmospheric XCH4 inside the ROI and in a reference ring", "Column concentrations are not local methane emissions."),
    "methane11_observation_selection_bias.png": ("Methane observation availability across low-VV screening conditions", "Wet-season missingness creates observational selection bias."),
    "methane11_coverage_sensitive_scatter.png": ("Available-month XCH4 versus low-VV anomalies", "Near-zero associations cannot rule out wetland methane flux responses."),
}

TABLES = [
    "inundation09_s1_scene_inventory.csv",
    "inundation09_track_selection.csv",
    "inundation09_processing_parameters.json",
    "inundation09_monthly_2019_2025.csv",
    "inundation09_annual_coverage_qa.csv",
    "inundation09_2022_month_matched_departures.csv",
    "inundation09_annual_raster_coverage_qa.csv",
    "inundation09_june2022_spatial_qa.csv",
    "inundation09_june2022_spatial_summary.csv",
    "inundation09_run_manifest.json",
    "hydro10_merged_monthly_2019_2025.csv",
    "hydro10_annual_input_qa.csv",
    "hydro10_monthly_seasonal_climatology.csv",
    "hydro10_2022_month_matched_departures.csv",
    "hydro10_deseasonalized_associations.csv",
    "hydro10_leave_year_out_predictions.csv",
    "hydro10_leave_year_out_model_metrics.csv",
    "hydro10_2022_context_and_heldout_residuals.csv",
    "hydro10_processing_manifest.json",
    "methane11_annual_availability.csv",
    "methane11_monthly_availability.csv",
    "methane11_seasonal_availability.csv",
    "methane11_selection_bias_strata.csv",
    "methane11_coverage_sensitive_associations.csv",
    "methane11_monthly_qa_joined.csv",
    "methane11_qa_manifest.json",
]

REPORTS = ["NOTEBOOK10_HYDROCLIMATE_FINDINGS.md", "NOTEBOOK11_TROPOMI_QA_FINDINGS.md"]
NOTEBOOK_CHOICES = {
    "09": ["09_inundation_dynamics_2019_2025_QA_v3_export_fixed.ipynb",
           "09_inundation_dynamics_2019_2025_QA_v2.ipynb"],
    "10": ["10_hydroclimatic_controls_2019_2025.ipynb"],
    "11": ["11_tropomi_methane_qa_2019_2025.ipynb"],
}
BEGIN = "<!-- LOCAL_2019_2025_RESULTS_START -->"
END = "<!-- LOCAL_2019_2025_RESULTS_END -->"


def find_notebook(source: Path, candidates: list[str]) -> Path | None:
    for folder in (source / "notebooks", source):
        for name in candidates:
            path = folder / name
            if path.is_file():
                return path
    return None


def copy_checked(src: Path, dst: Path) -> None:
    if not src.is_file():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() in {".json", ".csv", ".md", ".ipynb"}:
        data = src.read_text(encoding="utf-8-sig")
        if "-----BEGIN PRIVATE KEY-----" in data or "-----BEGIN OPENSSH PRIVATE KEY-----" in data:
            raise ValueError("Private key detected; refusing to publish " + str(src))
        if src.suffix.lower() == ".ipynb":
            book = json.loads(data)
            for cell in book.get("cells", []):
                if cell.get("cell_type") == "code":
                    cell["outputs"] = []
                    cell["execution_count"] = None
                    # Repair two display/manifest labels in Notebook 09 export copy.
                    if "09_inundation" in src.name:
                        s = "".join(cell.get("source", []))
                        s = s.replace("axes.flat.tolist()", "list(axes.flat)")
                        s = s.replace('"notebook": "09_inundation_dynamics_2019_2025_QA_v2.ipynb"',
                                      '"notebook": "09_inundation_dynamics_2019_2025_QA_v3_export_fixed.ipynb"')
                        cell["source"] = s.splitlines(keepends=True)
            data = json.dumps(book, ensure_ascii=False, indent=1) + "\n"
        dst.write_text(data, encoding="utf-8")
    else:
        if src.suffix.lower() != ".png":
            raise ValueError("Not an approved image format: " + str(src))
        shutil.copy2(src, dst)


def run_git(repo: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], text=True,
                          encoding="utf-8", stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=False)


def prepare_readme(repo: Path, images: list[str], notebooks: list[str], tables: list[str], reports: list[str]) -> bool:
    path = repo / "README.md"
    original = path.read_text(encoding="utf-8")
    if original.count(BEGIN) != original.count(END):
        raise ValueError("Existing README has unbalanced result-gallery markers")

    lines = ["## Updated 2019–2025 results: published source files",
             "", "These figures and tables come from local Notebooks 09–11 and remain "
             "**exploratory observations**, not independent validation of inundation, "
             "methane flux, or causation.", ""]
    for image in images:
        name, note = FIGURES[image]
        lines += ["### " + name, "",
                  "![" + name + "](docs/assets/figures/analysis_2019_2025/" + image + ")",
                  "", "*" + note + "*", ""]
    if notebooks:
        lines += ["### Reproducible analysis notebooks", ""]
        for name in notebooks:
            lines.append("- [" + name + "](notebooks/" + name + ")")
        lines.append("")
    if reports:
        lines += ["### Scientific interpretation reports", ""]
        for name in reports:
            lines.append("- [" + name + "](research_docs/reports/" + name + ")")
        lines.append("")
    if tables:
        lines += ["### Analysis result tables", ""]
        for name in tables:
            lines.append("- [" + name + "](docs/assets/tables/analysis_2019_2025/" + name + ")")
        lines.append("")
    gallery = BEGIN + "\n" + "\n".join(lines).rstrip() + "\n" + END

    if BEGIN in original:
        revised = original[:original.index(BEGIN)] + gallery + original[original.index(END)+len(END):]
    else:
        # The earlier README names local-only plots in this particular paragraph.
        # Leave all other narrative and the separate Biomass section unchanged.
        text = re.sub(r"\*\*Newer figures generated locally but not yet uploaded:\*\*.*?\n\nThese will be embedded once their files are committed\. No broken placeholder image links are used here\.",
                      "New Notebook 09–11 figures, code and derived tables are embedded in the published results section below.",
                      original, flags=re.DOTALL)
        marker = "<!-- BIOMASS_2026_START -->"
        if marker in text:
            revised = text.replace(marker, gallery + "\n\n" + marker, 1)
        else:
            revised = text.rstrip() + "\n\n" + gallery + "\n"
        revised = revised.replace(
            "**Those notebooks, their final CSVs and their newest figures have not yet been committed to this GitHub repository** as of 14 October 2026.",
            "**Notebooks 09–11, selected CSVs and figures are now published below.** The code and results remain exploratory and have not undergone independent validation.")
        revised = revised.replace("**not yet committed to this GitHub repository**", "**published below**")
        revised = revised.replace("Current public processing notebooks are **00–08** in `notebooks/`; the updated 09–11 notebooks are **local-only** pending upload.",
                                  "Current public processing notebooks include **09–11** in `notebooks/` alongside earlier analyses.")
        revised = revised.replace("**Those notebooks, their final CSVs and their newest figures have not yet been committed to this GitHub repository** as of 14 October 2026.",
                                  "**Notebooks 09–11, selected CSVs and figures are now published in the repository.**")
        revised = revised.replace("Current public processing notebooks are **00–08** in `notebooks/`; the updated 09–11 notebooks are **local-only** pending upload.",
                                  "Current public processing notebooks include **09–11** in `notebooks/` alongside earlier analyses.")
        revised = revised.replace("**Those notebooks, their final CSVs and their newest figures have not yet been committed to this GitHub repository** as of 14 October 2026.",
                                  "**Notebooks 09–11, selected CSVs and figures are now published in the repository.**")
        revised = revised.replace("**Entirely public reproduction** | Upload local notebooks 09–11, their sanitized manifests, figures, derived tables, and reports",
                                  "**Independent reproduction** | Re-run published notebooks with compatible software and Earth Engine access; externally verify the derived outputs")
    if revised != original:
        path.write_text(revised, encoding="utf-8")
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, required=True, help="Original Windows project containing the executed outputs")
    ap.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1], help="Local GitHub clone")
    ap.add_argument("--commit-and-push", action="store_true", help="Stage ONLY curated outputs, commit, and push to origin/main")
    opts = ap.parse_args()
    source = opts.source.resolve()
    repo = opts.repo.resolve()
    if not (repo / "README.md").is_file() and not repo.exists():
        print("Cloning public GitHub repository to:", repo)
        clone = subprocess.run(
            ["git", "clone",
             "https://github.com/Bipul-roy-AI/Hakaluki-Haor-Wetland-Methane-Research.git",
             str(repo)], text=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, check=False)
        if clone.returncode:
            ap.error("Git clone failed: " + clone.stderr)
    if not (repo / "README.md").is_file():
        ap.error("No README.md at GitHub repository root: " + str(repo))
    if opts.commit_and_push:
        sync = run_git(repo, ["pull", "--ff-only", "origin", "main"])
        if sync.returncode:
            ap.error("Could not fast-forward local GitHub clone. Use a clean cloned folder or resolve local changes: " + sync.stderr)
    if not (source / "results").is_dir():
        ap.error("Source directory has no results/ folder: " + str(source))
    if repo == source and opts.commit_and_push and not (repo / ".git").is_dir():
        ap.error("The source folder is not a Git clone. Clone the repository and use --repo.")

    modified: list[Path] = []
    published_images: list[str] = []
    published_tables: list[str] = []
    published_reports: list[str] = []
    published_notebooks: list[str] = []
    missing: list[str] = []

    for _, choices in NOTEBOOK_CHOICES.items():
        src = find_notebook(source, choices)
        if src:
            dst = repo / "notebooks" / src.name
            copy_checked(src, dst)
            modified.append(dst)
            published_notebooks.append(dst.name)
        else:
            missing.append("Notebook: " + " or ".join(choices))

    for name in FIGURES:
        src = source / "results" / "figures" / name
        if not src.is_file():
            missing.append("Figure: " + name)
            continue
        dst = repo / "docs" / "assets" / "figures" / "analysis_2019_2025" / name
        copy_checked(src, dst)
        modified.append(dst)
        published_images.append(name)

    for name in TABLES:
        src = source / "results" / "tables" / name
        if not src.is_file():
            missing.append("Table: " + name)
            continue
        dst = repo / "docs" / "assets" / "tables" / "analysis_2019_2025" / name
        copy_checked(src, dst)
        modified.append(dst)
        published_tables.append(name)

    for name in REPORTS:
        src = source / "results" / "reports" / name
        if not src.is_file():
            missing.append("Report: " + name)
            continue
        dst = repo / "research_docs" / "reports" / name
        copy_checked(src, dst)
        modified.append(dst)
        published_reports.append(name)

    if prepare_readme(repo, published_images, published_notebooks, published_tables, published_reports):
        modified.append(repo / "README.md")

    # Update publication-status statements in supporting documents as well.
    for relative in ("research_docs/FINDINGS_2019_2025_AND_LIMITATIONS.md",
                     "research_docs/ROADMAP.md",
                     "research_docs/METHODS_AND_LIMITATIONS.md"):
        page = repo / relative
        if not page.is_file():
            continue
        before = page.read_text(encoding="utf-8")
        after = before
        after = re.sub(
            r"As of 14 October 2026, only notebooks 00–08 were present on the GitHub default branch\. The new 09–11 files and figures must be published before readers can exactly reproduce their reported numerical results from this repository\.",
            "The new Notebooks 09–11 and selected output figures/tables are now published on the default branch. Public availability does not constitute independent verification of the results.", after)
        after = after.replace(
            "As of this update, those notebooks, their new figures, and their generated CSV/report files have not yet been committed to this repository.",
            "Notebooks 09–11, selected figures, CSV files and reports are now committed to the repository.")
        after = after.replace(
            "**As of this update, those notebooks, their new figures, and their generated CSV/report files have not yet been committed to this repository.**",
            "**Notebooks 09–11 and selected outputs are published. They have not been independently re-run or validated.**")
        after = after.replace(
            "**Completed locally but not yet committed to Git:**",
            "**Completed and published (selected notebooks and derived outputs):**")
        after = after.replace(
            "**Public availability as of 14 October 2026:** Notebooks 09–11 and the new derived figures/tables are still local and are not part of the current GitHub repository checkout.",
            "**Public availability:** Notebooks 09–11 and selected figures/tables are now published in the repository; independent scientific validation remains outstanding.")
        if after != before:
            page.write_text(after, encoding="utf-8")
            modified.append(page)

    print("\nPUBLISHING PREPARATION")
    print("  Notebooks:", len(published_notebooks), "Figures:", len(published_images),
          "Tables:", len(published_tables), "Reports:", len(published_reports))
    print("  Latest charts are embedded in README only if copied successfully.")
    print("  Large GeoTIFFs/raw data are deliberately excluded from ordinary Git commits.")
    if missing:
        print("\nNot located; skipped (do not claim published):")
        for item in missing:
            print("  -", item)

    if not opts.commit_and_push:
        print("\nFiles prepared in:", repo)
        print("Review results, then run this script again with --commit-and-push to publish.")
        return 0

    if len(published_notebooks) < 3:
        print("\nERROR: fewer than all three notebooks were located. Not committing incomplete portfolio.", file=sys.stderr)
        return 2
    if not published_images:
        print("\nERROR: no actual new figures found. Not committing a gallery without figures.", file=sys.stderr)
        return 2
    staged_before = run_git(repo, ["diff", "--cached", "--name-only"])
    if staged_before.returncode or staged_before.stdout.strip():
        print("ERROR: other staged Git changes exist. Commit/unstage them first to prevent accidental inclusion.", file=sys.stderr)
        return 2
    head = run_git(repo, ["branch", "--show-current"])
    if head.returncode != 0 or head.stdout.strip() != "main":
        print("ERROR: switch your Git checkout to 'main' before --commit-and-push", file=sys.stderr)
        return 2
    for group in [modified[i:i+30] for i in range(0, len(modified), 30)]:
        staged = run_git(repo, ["add", "--", *[str(p.relative_to(repo)) for p in group]])
        if staged.returncode:
            print("Git staging failed:", staged.stderr, file=sys.stderr)
            return 2
    diff = run_git(repo, ["diff", "--cached", "--quiet"])
    if diff.returncode == 0:
        print("No changes to commit; existing published files already match.")
        return 0
    commit = run_git(repo, ["commit", "-m", "Publish notebooks 09–11 and curated 2019–2025 findings"])
    if commit.returncode:
        print("Git commit failed:", commit.stderr, file=sys.stderr)
        return 2
    push = run_git(repo, ["push", "origin", "main"])
    if push.returncode:
        print("Git push failed; commit remains local. Resolve the Git error and retry:",
              push.stderr, file=sys.stderr)
        return 2
    print("\nPUBLISHED to GitHub origin/main successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())