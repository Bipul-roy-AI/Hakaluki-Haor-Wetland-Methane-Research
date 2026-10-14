"""13D: stage, upstream rain and scene-event chronology.

Never substitutes local CHIRPS for upstream discharge, and never infers a
hydrograph from SAR area without actual gauge/stage observations.
"""
from __future__ import annotations

from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .core import load_scenes, outputs, write_json
from .offline import consecutive_transitions


def stage_input(root: Path) -> Path:
    return root / "data" / "external" / "hydrology" / "observed_stage.csv"


def basin_rain_input(root: Path) -> Path:
    return root / "data" / "external" / "hydrology" / "upstream_daily_rain.csv"


def read_stage(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Actual stage data absent: {path}. Do not use template values.")
    stage=pd.read_csv(path)
    cols={"station_id","timestamp_local","water_level_m","vertical_datum","source_reference","quality_flag"}
    if not cols.issubset(stage.columns):
        raise ValueError(f"Stage CSV missing columns: {cols-set(stage.columns)}")
    if stage.empty:
        raise ValueError("Stage CSV contains no actual observations")
    # Require explicit offset so a gauge's daily observation time is not guessed.
    label=stage.timestamp_local.astype(str)
    if not label.str.contains(r"(?:Z|[+-]\d\d:\d\d)$", regex=True).all():
        raise ValueError("Stage timestamp_local needs an explicit timezone offset, e.g. 2022-06-19T06:00:00+06:00")
    stage['timestamp_local']=pd.to_datetime(stage.timestamp_local,utc=True,errors='raise').dt.tz_convert('Asia/Dhaka')
    stage['water_level_m']=pd.to_numeric(stage.water_level_m,errors='raise')
    if stage.water_level_m.isna().any():
        raise ValueError("Stage levels contain NaNs")
    if stage[['station_id','source_reference','vertical_datum','quality_flag']].isna().any().any():
        raise ValueError("All stage records require station/source/vertical datum")
    if stage.duplicated(['station_id','timestamp_local']).any():
        raise ValueError('Duplicate gauge records at the same timestamp')
    # Same station may change datum through time. Flag as interpretive limitation.
    if stage.groupby('station_id').vertical_datum.nunique().gt(1).any():
        raise ValueError("At least one station has multiple datums; harmonize levels before analysis")
    return stage.sort_values('timestamp_local').reset_index(drop=True)


def match_stage_to_sar(scenes: pd.DataFrame, stage: pd.DataFrame,
                       tolerance_hours: float = 36) -> pd.DataFrame:
    """Match closest OBSERVED gauge reading with explicit temporal separation.

    Returns a table of every scene × station. Missing stage observations stay NaN.
    No physical hydraulic connection between station and haor is assumed.
    """
    if not 0<tolerance_hours<=72:
        raise ValueError('Stage temporal-match tolerance must be in (0,72] hours')
    results=[]
    for sid,g in stage.groupby('station_id'):
        a=scenes[['scene_id','year','pass','acquisition_local','lowvv_m17_km2']].copy()
        a=a.rename(columns={'acquisition_local':'sar_local'}).sort_values('sar_local')
        b=g.sort_values('timestamp_local').copy()
        merged=pd.merge_asof(a,b,left_on='sar_local',right_on='timestamp_local',
                             direction='nearest',tolerance=pd.Timedelta(hours=tolerance_hours))
        merged['target_station_id']=sid
        merged['time_difference_hours']=(merged['sar_local']-merged['timestamp_local']).dt.total_seconds()/3600
        results.append(merged)
    return pd.concat(results,ignore_index=True)


def first_observed_threshold_crossings(scenes: pd.DataFrame, threshold_fraction: float=.85) -> pd.DataFrame:
    """Brackets first *observed* low-VV screen fraction crossing per year and orbit.

    Not inundation onset, threshold is arbitrary and intentionally configurable.
    """
    if not 0<threshold_fraction<1:
        raise ValueError('Screening fraction must be within (0,1)')
    results=[]
    for key,g in scenes.groupby(['year','pass','relative_orbit']):
        g=g.sort_values('acquisition_utc').reset_index(drop=True)
        positive=g.m17_fraction_observed>=threshold_fraction
        if not positive.any():
            results.append({'year':key[0],'pass':key[1],'relative_orbit':key[2],
                            'before_local':None,'first_above_local':None,'interval_days':np.nan,
                            'status':'no_observed_crossing'})
            continue
        i=int(np.flatnonzero(positive.to_numpy())[0])
        if i==0:
            before=None;gap=np.nan;state='already_above_at_first_scene'
        else:
            before=g.loc[i-1,'acquisition_local']
            gap=float((g.loc[i,'acquisition_utc']-g.loc[i-1,'acquisition_utc']).total_seconds()/86400)
            state='first_observed_crossing_bracket'
        results.append({'year':key[0],'pass':key[1],'relative_orbit':key[2],
                        'before_local':before,'first_above_local':g.loc[i,'acquisition_local'],
                        'interval_days':gap,'status':state})
    return pd.DataFrame(results)


def _read_upstream(path: Path) -> pd.DataFrame:
    d=pd.read_csv(path)
    required={'basin_id','date_label','rain_mm','source_reference'}
    if not required.issubset(d.columns):
        raise ValueError(f'Upstream-rain CSV lacks {required-set(d.columns)}')
    if d.empty:
        raise ValueError('No actual upstream observations')
    d['date_label']=pd.to_datetime(d.date_label,errors='raise').dt.normalize()
    d['rain_mm']=pd.to_numeric(d.rain_mm,errors='raise')
    if d.rain_mm.isna().any() or (d.rain_mm<0).any():
        raise ValueError('Invalid upstream rainfall values')
    if d.duplicated(['basin_id','date_label']).any():
        raise ValueError('Duplicated basin/date rainfall')
    return d


def run_hydrology(root: Path, *, stage_path: Path | None=None,
                   upstream_path: Path | None=None, gauge_tolerance_h: float=36) -> dict:
    root=Path(root).resolve()
    scenes=load_scenes(root)
    td,fd=outputs(root,'analysis13')
    trans=consecutive_transitions(scenes)
    trans.to_csv(td/'13D_observed_within_orbit_windows.csv',index=False)
    crossings=first_observed_threshold_crossings(scenes)
    crossings.to_csv(td/'13D_first_observed_screening_crossings.csv',index=False)
    status={'created_utc':datetime.now(timezone.utc).isoformat(),
            'status':'scene_chronology_completed_external_hydrology_pending',
            'screening_cutoff_fraction':0.85,
            'reason':'An arbitrary screening criterion is not a true flood-onset rule.',
            'stage_file':None,'upstream_file':None}
    p=Path(stage_path) if stage_path else stage_input(root)
    if p.is_file():
        stage=read_stage(p)
        matches=match_stage_to_sar(scenes,stage,tolerance_hours=gauge_tolerance_h)
        matches.to_csv(td/'13D_actual_stage_matched_to_SAR.csv',index=False)
        station_summary=(matches.groupby('target_station_id',dropna=False)
                         .agg(n_scenes=('scene_id','size'),
                              n_matched=('water_level_m','count'),
                              median_abs_time_offset_hours=('time_difference_hours',lambda x: x.abs().median()))
                         .reset_index())
        station_summary.to_csv(td/'13D_station_match_support.csv',index=False)
        fig,ax=plt.subplots(figsize=(12,5),constrained_layout=True)
        for sid,chunk in stage.groupby('station_id'):
            ax.plot(chunk.timestamp_local.dt.tz_localize(None),chunk.water_level_m,marker='.',lw=1,label=sid)
        ax.legend()
        ax.set(xlabel='Bangladesh local observation time',ylabel='Reported station level (m, datum may differ)',
               title='Observed river-stage records by station: not calibrated to wetland area')
        fig.savefig(fd/'13D_actual_station_water_levels.png',dpi=150,bbox_inches='tight')
        plt.close(fig)
        status['stage_file']=str(p)
        status['stage_matches']=int(matches.water_level_m.notna().sum())
        status['stage_quality_values']=sorted(stage.quality_flag.astype(str).unique().tolist())
        # Plot exact observations; a gauge is NOT assumed hydraulically connected.
        for sid,group in matches.groupby('target_station_id'):
            matched=group.loc[group.water_level_m.notna()].copy()
            if len(matched)<3:
                continue
            fig,ax=plt.subplots(figsize=(7,5),constrained_layout=True)
            for passage,g in matched.groupby('pass'):
                ax.scatter(g.water_level_m,g.lowvv_m17_km2,label=passage,alpha=.75)
            ax.legend()
            ax.set(xlabel=f'{sid}: station level (m, source datum)',
                   ylabel='−17 dB low-VV area (km²)',
                   title=f'Stage vs radar screen: {sid}\nGauge connectivity unverified; not stage–water area')
            fig.savefig(fd/f'13D_{sid}_stage_vs_lowVV.png',dpi=145,bbox_inches='tight')
            plt.close(fig)
        status['status']='stage_matching_completed_hydraulic_representativeness_unverified'
    else:
        status['stage_blocker']=f'No actual station data at {p}. Obtain source/datum/station metadata.'
    q=Path(upstream_path) if upstream_path else basin_rain_input(root)
    if q.is_file():
        upstream=_read_upstream(q)
        upstream.to_csv(td/'13D_upstream_observations_checked.csv',index=False)
        status['upstream_file']=str(q)
        status['upstream_basins']=sorted(upstream.basin_id.unique().tolist())
        # Preceding 3/7 complete labelled days, with ±1 label sensitivity.
        aligned=[]
        for basin,group in upstream.groupby('basin_id'):
            daily=group.set_index('date_label').sort_index().asfreq('D')
            for days in (3,7):
                daily[f'prior_{days}_day_rain_mm']=daily.rain_mm.shift(1).rolling(days,min_periods=days).sum()
            start=scenes[['scene_id','year','pass','acquisition_local','lowvv_m17_km2']].copy()
            start['local_label']=start.acquisition_local.dt.tz_localize(None).dt.normalize()
            for shift in (-1,0,1):
                target=start.local_label+pd.Timedelta(days=shift)
                for days in (3,7):
                    start[f'prior_{days}d_shift_{shift:+d}_mm']=target.map(daily[f'prior_{days}_day_rain_mm'])
            start['basin_id']=basin
            aligned.append(start)
        combined=pd.concat(aligned,ignore_index=True)
        combined.to_csv(td/'13D_upstream_rain_aligned_scene_windows.csv',index=False)
        status['upstream_scene_comparison_rows']=int(len(combined))
        status['upstream_rain_convention']='date labels only; accumulation-day convention and basin representativeness require source audit'
    else:
        status['upstream_blocker']=f'No measured/upstream basin rain data at {q}. Do not substitute local CHIRPS.'
    write_json(td/'13D_hydrology_data_availability.json',status)
    return status
