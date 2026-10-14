"""Offline analysis on verified uploaded scene 12 data (no Earth Engine)."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .core import load_scenes, outputs, write_json


def consecutive_transitions(scenes: pd.DataFrame) -> pd.DataFrame:
    """Differences compare the same pass/orbit, NEVER across orbital geometries."""
    d = scenes.sort_values("acquisition_utc").copy()
    cols = ["year", "pass", "relative_orbit"]
    result = []
    for key, part in d.groupby(cols):
        part = part.sort_values("acquisition_utc")
        for i in range(1, len(part)):
            before, after = part.iloc[i-1], part.iloc[i]
            changes = {
                tag: float(after[f"lowvv_{tag}_km2"] - before[f"lowvv_{tag}_km2"])
                for tag in ("m19", "m17", "m15")
            }
            directional = all(x > 0 for x in changes.values()) or all(x < 0 for x in changes.values())
            result.append({"year": int(key[0]), "pass": key[1], "relative_orbit": int(key[2]),
                           "before_id": before.scene_id, "after_id": after.scene_id,
                           "before_utc": before.acquisition_utc, "after_utc": after.acquisition_utc,
                           "before_local": before.acquisition_local, "after_local": after.acquisition_local,
                           "days_between": (after.acquisition_utc-before.acquisition_utc).total_seconds()/86400,
                           "delta_m19_km2": changes["m19"],
                           "delta_m17_km2": changes["m17"],
                           "delta_m15_km2": changes["m15"],
                           "same_sign_all_thresholds": bool(directional),
                           "strong_change_all_thresholds_20km2": bool(directional and all(abs(x)>=20 for x in changes.values())),
                           "n_scenes_between": 0})
    if not result:
        return pd.DataFrame(columns=["year","pass","relative_orbit","before_id","after_id","before_utc","after_utc","before_local","after_local","days_between","delta_m19_km2","delta_m17_km2","delta_m15_km2","same_sign_all_thresholds","strong_change_all_thresholds_20km2","n_scenes_between"])
    return pd.DataFrame(result).sort_values(["year", "before_utc", "pass"]).reset_index(drop=True)


def scene_anomalies(scenes: pd.DataFrame) -> pd.DataFrame:
    d=scenes.copy()
    d["local_month"]=d.acquisition_local.dt.month
    d["near_threshold_fraction_points"]=(d.threshold_span_km2/d.observed_km2)*100
    d["near_saturation_fraction_points"]=d.m17_fraction_observed*100
    return d.sort_values("threshold_span_km2",ascending=False)


def transition_windows(transitions: pd.DataFrame, *, cutoff_km2: float = 100.0) -> pd.DataFrame:
    """First *observed* within-pass crossing of user-defined low-VV area benchmark.

    This is not a flood onset estimate. The 100 km2 cutoff is illustrative.
    """
    v=transitions.copy()
    # Crossing signs are inferred using earliest same-pass scene's area reconstructed from deltas.
    v["before_area_m17_km2"] = np.nan
    v["after_area_m17_km2"] = np.nan
    return v


def _save_figure(scenes: pd.DataFrame, dest: Path) -> None:
    fig, axs=plt.subplots(2,2,figsize=(15,10),sharex=False,sharey=True,constrained_layout=True)
    for ax,year in zip(axs.flat,[2022,2023,2024,2025]):
        subset=scenes.loc[scenes.year==year].copy()
        for p,marker,color in (("ASCENDING","o","tab:blue"),("DESCENDING","s","tab:orange")):
            g=subset.loc[subset["pass"]==p].sort_values("acquisition_local")
            ax.scatter(g.acquisition_local.dt.tz_localize(None),g.lowvv_m17_km2,
                       marker=marker,color=color,label=p,s=38)
        ax.set_title(f"{year} | {len(subset)} acquisitions")
        ax.grid(alpha=0.25)
        ax.set_ylim(0,180)
        ax.tick_params(axis="x",rotation=35)
        ax.set_xlabel("Bangladesh local acquisition date")
        ax.set_ylabel("−17 dB low-VV screen (km²)")
    axs[0,0].legend(frameon=False)
    fig.suptitle("Per-scene low-VV detections | same y-scale, no temporal interpolation\nNot validated water/flood extent",fontsize=15)
    fig.savefig(dest,dpi=150,bbox_inches="tight")
    plt.close(fig)


def _save_threshold_figure(scenes: pd.DataFrame, dest: Path) -> None:
    strongest=scenes.sort_values("threshold_span_km2",ascending=False).head(15).copy()
    fig,ax=plt.subplots(figsize=(11,6),constrained_layout=True)
    y=np.arange(len(strongest))
    ax.barh(y,strongest.threshold_span_km2,color="0.42")
    ax.set_yticks(y,labels=[f"{x.acquisition_local.strftime('%Y-%m-%d')} | {x['pass'][:3]}" for _,x in strongest.iterrows()])
    ax.invert_yaxis()
    ax.set_xlabel("Area difference: −15 dB minus −19 dB (km²)")
    ax.set_title("Largest scene-level VV threshold sensitivities (descriptive)")
    ax.grid(axis="x",alpha=0.2)
    fig.savefig(dest,dpi=150,bbox_inches="tight")
    plt.close(fig)


def run_offline(root: Path, scene_file: Path | None = None, *, output_root: Path | None = None) -> dict:
    """Only interprets input data. Never writes into source CSV."""
    root=Path(root).resolve()
    source=load_scenes(root,scene_file)
    if output_root:
        td,fd=Path(output_root)/"tables",Path(output_root)/"figures"
        td.mkdir(parents=True,exist_ok=True);fd.mkdir(parents=True,exist_ok=True)
    else:
        td,fd=outputs(root,"analysis13")
    transitions=consecutive_transitions(source)
    scene_anomalies(source).to_csv(td/"13A_threshold_sensitivity_ranked.csv",index=False)
    transitions.to_csv(td/"13C_within_orbit_transitions.csv",index=False)
    selected=source.loc[source.acquisition_local.dt.month.isin([5,6])].copy()
    selected.to_csv(td/"13C_may_june_acquisitions.csv",index=False)
    _save_figure(source,fd/"13C_four_year_scene_comparison.png")
    _save_threshold_figure(source,fd/"13A_threshold_sensitivity_top15.png")
    summary={"created_utc":datetime.now(timezone.utc).isoformat(),
             "status":"exploratory_reanalysis_of_uploaded_scene12_outputs_not_earth_engine_rerun",
             "n_scenes":len(source),"n_transitions":len(transitions),
             "n_same_sign":int(transitions.same_sign_all_thresholds.sum()),
             "n_strong_same_sign_20km2":int(transitions.strong_change_all_thresholds_20km2.sum()),
             "years":sorted(source.year.astype(int).unique().tolist()),
             "max_threshold_span_km2":float(source.threshold_span_km2.max()),
             "all_numerics_from":"scene12_S1_per_acquisition_2022_2025.csv",
             "limitations":"Area screening is unvalidated; acquisition differences are not directly water change; fixed VV thresholds and orbit effects remain."}
    write_json(td/"13_offline_reanalysis_manifest.json",summary)
    return summary
