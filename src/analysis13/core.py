"""Shared configuration, conventions, input checks and reproducibility helpers.

This package does not infer verified flood, inundation depth or methane flux from
Sentinel-1 low VV or from TROPOMI XCH4.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


THRESHOLDS_DB = (-19.0, -17.0, -15.0)
TRACKS = (("ASCENDING", 41), ("DESCENDING", 77))
YEARS = (2022, 2023, 2024, 2025)
TIMEZONE = "Asia/Dhaka"
CRS_M = "EPSG:32646"
SCALE_M = 30
ANGLE_MIN, ANGLE_MAX = 30.0, 45.0


def project_root(root: str | Path | None = None) -> Path:
    """Find the user's existing research project; never hard-code drive names."""
    if root is not None:
        p = Path(root).expanduser().resolve()
        if not p.is_dir():
            raise FileNotFoundError(f"Project root directory does not exist: {p}")
        return p
    start = Path(os.environ.get("HAKALUKI_ROOT", Path.cwd())).expanduser().resolve()
    for p in (start, *start.parents):
        if any((p / f).exists() for f in (
            "results/tables/scene12_S1_per_acquisition_2022_2025.csv",
            "Study area/Hakaluki_Haor.shp",
            "data/boundary/hakaluki_boundary.gpkg",
        )):
            return p
    raise FileNotFoundError("Project root not found. Set HAKALUKI_ROOT to the project folder.")


def find_boundary(root: Path) -> Path:
    for sub in ("data/boundary/hakaluki_boundary.gpkg", "Study area/Hakaluki_Haor.shp"):
        f = root / sub
        if f.is_file():
            return f
    raise FileNotFoundError("Boundary missing: data/boundary/hakaluki_boundary.gpkg or Study area/Hakaluki_Haor.shp")


def load_boundary(root: Path):
    import geopandas as gpd
    p = find_boundary(root)
    gdf = gpd.read_file(p).to_crs("EPSG:4326")
    if gdf.empty or gdf.geometry.isna().any() or not gdf.geometry.is_valid.all():
        raise ValueError(f"Invalid study-area geometry in {p}")
    return gdf.geometry.union_all()


def ee_initialize():
    try:
        import ee
    except ImportError as e:
        raise RuntimeError("Earth Engine missing: pip install earthengine-api; authenticate on your computer") from e
    project = os.getenv("EE_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")
    try:
        if project:
            ee.Initialize(project=project)
        else:
            ee.Initialize()
    except Exception as e:
        raise RuntimeError("Earth Engine not initialized. Run ee.Authenticate() locally and set EE_PROJECT.") from e
    return ee


def outputs(root: Path, stage: str) -> tuple[Path, Path]:
    table_dir = root / "results" / "tables" / stage
    figure_dir = root / "results" / "figures" / stage
    table_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)
    return table_dir, figure_dir


def checksum_config(settings: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(settings, sort_keys=True, default=str).encode()).hexdigest()[:14]


def write_json(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def scene12_source(root: Path, file: str | Path | None = None) -> Path:
    if file is not None:
        p = Path(file).expanduser().resolve()
        if not p.is_file():
            raise FileNotFoundError(f"Scene input not found: {p}")
        return p
    for sub in (
        "results/tables/scene12_S1_per_acquisition_2022_2025.csv",
        "docs/assets/tables/analysis_2019_2025/scene12_S1_per_acquisition_2022_2025.csv",
    ):
        f = root / sub
        if f.is_file():
            return f
    raise FileNotFoundError("Run Notebook 12 or copy scene12_S1_per_acquisition_2022_2025.csv into results/tables")


def load_scenes(root: Path, file: str | Path | None = None) -> pd.DataFrame:
    src = scene12_source(root, file)
    data = pd.read_csv(src)
    necessary = {
        "scene_id", "acquisition_utc", "pass", "relative_orbit", "year",
        "observed_km2", "lowvv_m19_km2", "lowvv_m17_km2", "lowvv_m15_km2",
    }
    if not necessary <= set(data.columns):
        raise ValueError(f"Scene CSV missing columns: {sorted(necessary-set(data.columns))}")
    if data.empty or data.scene_id.isna().any() or data.scene_id.duplicated().any():
        raise ValueError("Scene CSV empty, missing IDs or contains duplicated source scenes")
    data["acquisition_utc"] = pd.to_datetime(data["acquisition_utc"], utc=True, errors="raise")
    data["acquisition_local"] = data.acquisition_utc.dt.tz_convert(TIMEZONE)
    data["local_date"] = data.acquisition_local.dt.tz_localize(None).dt.normalize()
    for c in ("year", "relative_orbit", "observed_km2", "lowvv_m19_km2", "lowvv_m17_km2", "lowvv_m15_km2"):
        data[c] = pd.to_numeric(data[c], errors="raise")
    if data[["observed_km2", "lowvv_m19_km2", "lowvv_m17_km2", "lowvv_m15_km2"]].isna().any().any():
        raise ValueError("Unexpected null scene area; missing must not be treated as dry")
    if ((data.lowvv_m19_km2-data.lowvv_m17_km2)>0.1).any() or ((data.lowvv_m17_km2-data.lowvv_m15_km2)>0.1).any():
        raise ValueError("Threshold order violated: -19 <= -17 <= -15 areas")
    if (data.lowvv_m15_km2>data.observed_km2+0.1).any():
        raise ValueError("Screening area exceeds observed support")
    data["threshold_span_km2"] = data.lowvv_m15_km2-data.lowvv_m19_km2
    data["m17_fraction_observed"] = data.lowvv_m17_km2/data.observed_km2.replace(0, np.nan)
    return data.sort_values(["year", "pass", "acquisition_utc"]).reset_index(drop=True)


def standard_processing_config(root: Path) -> dict:
    return {
        "root_name": root.name, "vv_thresholds_db": THRESHOLDS_DB,
        "angle_deg": [ANGLE_MIN, ANGLE_MAX], "scale_m": SCALE_M,
        "crs": CRS_M, "smoothing_radius_m": 30,
        "meaning": "unvalidated_low_vv_screening_not_flood_water_classification",
    }


def preflight(root: Path, *, require_ee: bool = False) -> dict:
    result = {"root": str(root), "scene_csv": None, "boundary": None, "ee": None}
    try:
        result["scene_csv"] = str(scene12_source(root))
    except FileNotFoundError as e:
        result["scene_csv_error"] = str(e)
    try:
        result["boundary"] = str(find_boundary(root))
    except FileNotFoundError as e:
        result["boundary_error"] = str(e)
    if require_ee:
        ee_initialize()
        result["ee"] = "initialized"
    return result
