"""Pure, testable utilities for Notebook 12 scene-level comparisons.

CHIRPS daily date labels are not asserted to equal Bangladesh midnight-to-midnight
accumulation windows. These functions preserve labels and expose ±1-day tests.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def normalize_daily_rain(frame: pd.DataFrame, date_col: str = "date",
                         rain_col: str = "rain_mm_day") -> pd.DataFrame:
    """Complete the labelled daily calendar; missing rainfall stays NaN, never zero."""
    if date_col not in frame or rain_col not in frame:
        raise ValueError(f"Missing daily rainfall columns: {date_col}, {rain_col}")
    original = frame[[date_col, rain_col]].copy()
    original["date"] = pd.to_datetime(original[date_col], errors="raise", utc=True).dt.tz_localize(None).dt.normalize()
    original["rain_mm_day"] = pd.to_numeric(original[rain_col], errors="coerce")
    if original.date.duplicated().any():
        raise ValueError("Duplicate daily rainfall date labels")
    if (original.rain_mm_day.dropna() < 0).any():
        raise ValueError("Negative rainfall invalid for daily CHIRPS")
    if original.empty:
        raise ValueError("No daily rainfall")
    out = original.set_index("date")[["rain_mm_day"]].asfreq("D")
    # Fully preceding labelled dates; the acquisition-day rainfall is separate.
    out["rain_previous_1d_mm"] = out.rain_mm_day.shift(1)
    out["rain_previous_3d_mm"] = out.rain_mm_day.shift(1).rolling(3, min_periods=3).sum()
    out["rain_previous_7d_mm"] = out.rain_mm_day.shift(1).rolling(7, min_periods=7).sum()
    return out.reset_index()


def attach_rain_to_scenes(scene_frame: pd.DataFrame, daily_frame: pd.DataFrame) -> pd.DataFrame:
    """Join rainfall to acquisition *local date*, with labelled-day offsets -1, 0, +1.

    Offsets are sensitivity diagnostics, not proof of the CHIRPS accumulation day.
    """
    if "acquisition_local" not in scene_frame:
        raise ValueError("Scenes must contain timezone-aware acquisition_local")
    rain = daily_frame.set_index("date")
    if rain.index.duplicated().any():
        raise ValueError("Duplicated daily rain labels")
    out = scene_frame.copy()
    local = pd.to_datetime(out.acquisition_local)
    if local.dt.tz is None:
        raise ValueError("acquisition_local must carry an explicit timezone")
    out["acquisition_local_date"] = local.dt.tz_localize(None).dt.normalize()
    for day_offset in (-1, 0, 1):
        dates = out.acquisition_local_date + pd.Timedelta(days=day_offset)
        for c in ("rain_mm_day", "rain_previous_3d_mm", "rain_previous_7d_mm"):
            out[f"{c}_label_shift_{day_offset:+d}"] = dates.map(rain[c]).to_numpy()
    return out


def check_scene_areas(frame: pd.DataFrame, reference_km2: float,
                      tolerance_km2: float = 0.05) -> None:
    """Fail on impossible area order or outside-reference observation support."""
    if reference_km2 <= 0:
        raise ValueError("Reference area must be positive")
    keys = ["observed_km2", "lowvv_m19_km2", "lowvv_m17_km2", "lowvv_m15_km2"]
    if frame[keys].isna().any().any():
        raise ValueError("Missing EE area return(s); do not coerce to zero")
    if (frame[keys] < -tolerance_km2).any().any():
        raise ValueError("Negative area")
    if (frame.observed_km2 > reference_km2 + tolerance_km2).any():
        raise ValueError("Observed support exceeds reference area")
    if (frame.lowvv_m15_km2 > frame.observed_km2 + tolerance_km2).any():
        raise ValueError("Screening extent exceeds observed area")
    if not ((frame.lowvv_m19_km2 <= frame.lowvv_m17_km2 + tolerance_km2) &
            (frame.lowvv_m17_km2 <= frame.lowvv_m15_km2 + tolerance_km2)).all():
        raise ValueError("Unexpected low-VV threshold area ordering")


def describe_scene_support(frame: pd.DataFrame) -> pd.DataFrame:
    """Descriptive summaries; do not label maximum low-VV area as maximum flood."""
    return (frame.groupby(["year", "orbit_pass", "relative_orbit"], dropna=False)
            .agg(n_scenes=("scene_id", "nunique"),
                 n_eligible=("eligible", "sum"),
                 first_acquisition_utc=("acquisition_utc", "min"),
                 last_acquisition_utc=("acquisition_utc", "max"),
                 median_observed_fraction=("observed_fraction", "median"),
                 min_nominal_km2=("lowvv_m17_km2", "min"),
                 max_nominal_km2=("lowvv_m17_km2", "max"))
            .reset_index())
