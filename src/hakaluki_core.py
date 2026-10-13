"""Utilities for the Hakaluki Haor satellite study.

This module deliberately does not assume that any boundary is authoritative or
that satellite column-methane concentrations measure surface methane flux.
"""
from __future__ import annotations
import calendar
import json
from datetime import date
from pathlib import Path
import requests
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import box, mapping

# Source: Government of Bangladesh Sylhet District information, approximate envelope.
OFFICIAL_ENVELOPE = (92 + 1/60, 24 + 35/60, 92 + 9/60, 24 + 44/60)
OFFICIAL_REPORTED_AREA_KM2 = 181.15
GITHUB_REPO = "https://raw.githubusercontent.com/aburaihan21/Bangladesh-All-GIS-Shapefile-Data/main/Hakaluki%20Haor"
SHP_STEM = "Hakaluki_Haor_Projected"


def project_paths(root: str | Path) -> dict:
    root = Path(root).resolve()
    paths = {
        "root": root, "boundary": root / "data" / "boundary",
        "processed": root / "data" / "processed",
        "maps": root / "results" / "maps", "figures": root / "results" / "figures",
        "tables": root / "results" / "tables",
        "calibration": root / "results" / "calibration",
    }
    for p in paths.values():
        p.mkdir(parents=True, exist_ok=True)
    return paths


def download_candidate_boundary(out_dir: str | Path) -> Path:
    """Download unverified third-party polygon. Examine provenance before final use."""
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    for suffix in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
        path = target / f"{SHP_STEM}{suffix}"
        if path.exists() and path.stat().st_size > 0:
            continue
        url = f"{GITHUB_REPO}/{SHP_STEM}{suffix}"
        resp = requests.get(url, timeout=35, headers={"User-Agent": "Hakaluki-Haor-Academic-Research/1.0"})
        resp.raise_for_status()
        partial = path.with_suffix(path.suffix + ".part")
        partial.write_bytes(resp.content)
        partial.replace(path)
    return target / f"{SHP_STEM}.shp"


def load_boundary(boundary_path: str | Path) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(boundary_path)
    if gdf.empty or gdf.crs is None:
        raise ValueError("Boundary is empty or missing its CRS; inspect the shapefile/GeoJSON.")
    gdf = gdf.to_crs("EPSG:4326")
    gdf = gdf.loc[gdf.geometry.notna() & (~gdf.geometry.is_empty)].copy()
    if not gdf.geometry.is_valid.all():
        raise ValueError("Boundary has invalid geometries. Repair and document before continuing.")
    return gdf


def boundary_audit(gdf: gpd.GeoDataFrame) -> dict:
    projected = gdf.to_crs("EPSG:32646")
    area = projected.geometry.area.sum() / 1e6
    xmin, ymin, xmax, ymax = gdf.total_bounds
    refxmin, refymin, refxmax, refymax = OFFICIAL_ENVELOPE
    return {
        "area_km2": round(float(area), 3),
        "reference_area_km2": OFFICIAL_REPORTED_AREA_KM2,
        "area_ratio_to_reference": round(float(area / OFFICIAL_REPORTED_AREA_KM2), 3),
        "bounds_wgs84": [round(float(n), 5) for n in (xmin, ymin, xmax, ymax)],
        "overlaps_reference_envelope": bool((xmax > refxmin) and (xmin < refxmax) and (ymax > refymin) and (ymin < refymax)),
        "feature_count": len(gdf),
        "provenance": "Third-party GitHub candidate. NOT verified as official boundary.",
    }


def export_candidate_geojson(gdf: gpd.GeoDataFrame, destination: str | Path) -> Path:
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Dissolve all shapes into one geometry and export in geographic coordinates.
    single = gpd.GeoDataFrame({"name": ["Hakaluki Haor boundary candidate"]},
                              geometry=[gdf.geometry.union_all()], crs="EPSG:4326")
    single.to_file(target, driver="GeoJSON")
    return target


def monthly_periods(start_year: int, end_year: int):
    """Periods [start, end) in ISO format."""
    for y in range(start_year, end_year + 1):
        for m in range(1, 13):
            start = date(y, m, 1).isoformat()
            end = date(y + 1, 1, 1).isoformat() if m == 12 else date(y, m + 1, 1).isoformat()
            yield {"year": y, "month": m, "period": f"{y}-{m:02d}", "start": start, "end": end}


def otsu_from_histogram(histogram: dict) -> float:
    """Between-class variance Otsu threshold for an EE dB histogram.

    Input keys: bucketMeans and histogram; purely local numeric function.
    """
    centers = np.asarray(histogram.get("bucketMeans", []), dtype=float)
    counts = np.asarray(histogram.get("histogram", []), dtype=float)
    if centers.shape != counts.shape or len(centers) < 3 or counts.sum() <= 0:
        raise ValueError("Histogram is empty or malformed")
    n = counts.sum()
    w0 = np.cumsum(counts)[:-1]
    w1 = n - w0
    s0 = np.cumsum(counts * centers)[:-1]
    s1 = np.sum(counts * centers) - s0
    valid = (w0 > 0) & (w1 > 0)
    score = np.full(len(w0), -np.inf)
    score[valid] = (s0[valid]/w0[valid] - s1[valid]/w1[valid])**2 * w0[valid] * w1[valid]
    i = int(np.argmax(score))
    return float((centers[i] + centers[i+1])/2.0)


def make_boundary_reference_figure(gdf: gpd.GeoDataFrame, path: str | Path):
    import matplotlib.pyplot as plt
    from shapely.geometry import box
    fig, ax = plt.subplots(figsize=(8, 7))
    ref = gpd.GeoSeries([box(*OFFICIAL_ENVELOPE)], crs="EPSG:4326")
    ref.boundary.plot(ax=ax, linestyle="--", linewidth=1.8, color="#AD5C15", label="Government-reported extent envelope")
    gdf.plot(ax=ax, facecolor="#6dbd9c", edgecolor="#24594b", linewidth=1.0, alpha=0.55)
    ax.set(xlabel="Longitude (°E)", ylabel="Latitude (°N)", title="Hakaluki Haor – boundary provenance audit")
    ax.text(0.01, 0.01, "Candidate GIS outline: unverified. NOT a final analysis boundary.",
            transform=ax.transAxes, fontsize=9, bbox={"facecolor":"white","alpha":0.8,"edgecolor":"none"})
    ax.set_aspect("equal", adjustable="datalim")
    fig.tight_layout()
    fig.savefig(path, dpi=170, bbox_inches="tight")
    plt.close(fig)


def make_reference_envelope_figure(path: str | Path):
    """Offline extent diagram with no claim to be a verified polygon or satellite map."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.4, 5.7))
    x0, y0, x1, y1 = OFFICIAL_ENVELOPE
    ax.add_patch(plt.Rectangle((x0, y0), x1-x0, y1-y0, facecolor="#b6dacc", alpha=0.45,
                               edgecolor="#336b5b", linewidth=2, linestyle="--"))
    ax.scatter([92.06419],[24.63618], c="#296f60", s=36, zorder=2)
    ax.annotate("Gazetteer location marker",(92.06419, 24.63618),xytext=(9,10),textcoords="offset points",fontsize=9)
    ax.set_xlim(x0-.035,x1+.035); ax.set_ylim(y0-.025,y1+.025)
    ax.set(xlabel="Longitude (°E)",ylabel="Latitude (°N)",title="Hakaluki Haor – geographic search envelope")
    ax.text(0.01,0.025,"Approximate envelope from Bangladesh government coordinates.\nNot a wetland boundary or satellite observation.",
            transform=ax.transAxes,fontsize=9,bbox={"facecolor":"white","alpha":0.92,"edgecolor":"none"})
    ax.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig(path,dpi=180,bbox_inches="tight"); plt.close(fig)
