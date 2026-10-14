"""Tests for the new scene-level analysis utilities; no Earth Engine access needed."""
import pandas as pd
import pytest
from src.scene12_utils import (
    attach_rain_to_scenes, check_scene_areas, normalize_daily_rain,
)


def test_rain_windows_are_strictly_prior_dates():
    input_data = pd.DataFrame({
        "date": pd.date_range("2022-06-01", periods=10, freq="D"),
        "rain_mm_day": list(range(1, 11)),
    })
    daily = normalize_daily_rain(input_data)
    june_05 = daily.set_index("date").loc[pd.Timestamp("2022-06-05")]
    assert june_05.rain_mm_day == 5
    assert june_05.rain_previous_1d_mm == 4
    assert june_05.rain_previous_3d_mm == 2 + 3 + 4
    assert pd.isna(june_05.rain_previous_7d_mm)


def test_missing_day_not_silently_zero_filled():
    input_data = pd.DataFrame({
        "date": ["2022-06-01", "2022-06-03", "2022-06-04", "2022-06-05"],
        "rain_mm_day": [2.0, 4.0, 3.0, 5.0],
    })
    daily = normalize_daily_rain(input_data)
    assert pd.isna(daily.set_index("date").loc[pd.Timestamp("2022-06-02"), "rain_mm_day"])
    assert pd.isna(daily.set_index("date").loc[pd.Timestamp("2022-06-05"), "rain_previous_3d_mm"])


def test_local_acquisition_date_and_day_label_offsets():
    scenes = pd.DataFrame({
        "acquisition_local": pd.to_datetime(
            ["2022-06-19 05:47:00+06:00", "2022-06-16 17:56:00+06:00"]
        )
    })
    rain = normalize_daily_rain(pd.DataFrame({
        "date": pd.date_range("2022-06-01", "2022-06-30"),
        "rain_mm_day": range(1, 31),
    }))
    paired = attach_rain_to_scenes(scenes, rain)
    assert paired.loc[0, "acquisition_local_date"] == pd.Timestamp("2022-06-19")
    assert paired.loc[0, "rain_mm_day_label_shift_+0"] == 19
    assert paired.loc[0, "rain_mm_day_label_shift_-1"] == 18
    assert paired.loc[0, "rain_previous_3d_mm_label_shift_+0"] == 16 + 17 + 18


def test_threshold_area_validation():
    valid = pd.DataFrame({"observed_km2": [90], "lowvv_m19_km2": [20],
                          "lowvv_m17_km2": [35], "lowvv_m15_km2": [45]})
    check_scene_areas(valid, reference_km2=100)
    invalid = valid.copy()
    invalid.loc[0, "lowvv_m19_km2"] = 40
    with pytest.raises(ValueError, match="ordering"):
        check_scene_areas(invalid, reference_km2=100)

def test_scene_support_summary_groups_by_inventory_pass():
    from src.scene12_utils import describe_scene_support
    scenes = pd.DataFrame({
        "year": [2022, 2022], "pass": ["ASCENDING", "DESCENDING"],
        "relative_orbit": [41, 77], "scene_id": ["a", "b"],
        "eligible": [True, False], "acquisition_utc": pd.to_datetime(
            ["2022-06-16T11:56:00Z", "2022-06-18T23:47:00Z"], utc=True),
        "observed_fraction": [1.0, 0.8], "lowvv_m17_km2": [160.0, 155.0],
    })
    out = describe_scene_support(scenes)
    assert set(out["pass"]) == {"ASCENDING", "DESCENDING"}
    assert out.loc[out["pass"] == "ASCENDING", "n_eligible"].iloc[0] == 1
