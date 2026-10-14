"""13F: methane observing-support audit and *conditional* feasibility screening.

No TROPOMI Level-2 data are shipped. A scenario XCH4 increment is a physical
assumption illustration, NOT measured flux, satellite precision or detection.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .core import load_boundary, load_scenes, outputs, write_json

# Molar masses kg/mol, dry-air column mass kg/m2 are approximate.
M_CH4=0.016043
M_DRY_AIR=0.028965
AIR_COLUMN_KG_M2=10330.0


def box_column_enhancement_ppb(flux_mg_m2_day: float, source_area_km2: float,
                               wind_m_s: float, *, crosswind_width_m: float | None=None,
                               air_column_kg_m2: float=AIR_COLUMN_KG_M2) -> float:
    """Order-of-magnitude steady, uniform distributed-source column increment.

    Assumes a uniformly emitting square of side sqrt(area) oriented crosswind,
    an effective full-column mixing, constant wind, steady state, no chemistry.
    Does not simulate a sounding's weighted averaging kernel or footprint.
    """
    if flux_mg_m2_day<0 or source_area_km2<=0 or wind_m_s<=0 or air_column_kg_m2<=0:
        raise ValueError('Flux>=0, area>0, wind>0, and air column>0 required')
    area=source_area_km2*1e6
    width=crosswind_width_m if crosswind_width_m is not None else float(np.sqrt(area))
    if width<=0:
        raise ValueError('Crosswind width must be positive')
    emission_kg_s=flux_mg_m2_day*1e-6*area/86400
    methane_column_kg_m2=emission_kg_s/(wind_m_s*width)
    mole_fraction=(methane_column_kg_m2/M_CH4)/(air_column_kg_m2/M_DRY_AIR)
    return mole_fraction*1e9


def scenarios_from_csv(path: Path) -> pd.DataFrame:
    d=pd.read_csv(path)
    needed={'scenario_id','flux_mg_m2_day','emitting_fraction_of_roi','wind_m_s','scenario_basis'}
    if not needed.issubset(d.columns) or d.empty:
        raise ValueError(f'Scenario file missing {needed-set(d.columns)} or empty')
    for key in ('flux_mg_m2_day','emitting_fraction_of_roi','wind_m_s'):
        d[key]=pd.to_numeric(d[key],errors='raise')
    if d[list(needed)].isna().any().any():
        raise ValueError('Scenario rows have missing data')
    if (d.flux_mg_m2_day<0).any() or (d.wind_m_s<=0).any() or \
       (~d.emitting_fraction_of_roi.between(0.001,1)).any():
        raise ValueError('Invalid scenario flux, source fraction or wind')
    return d


def run_detectability(root: Path, scenarios: Path, *, scene_file: Path | None=None) -> dict:
    """Feasibility-first box screen; no threshold of successful detection claimed."""
    root=Path(root).resolve()
    td,fd=outputs(root,'analysis13')
    scene=load_scenes(root,scene_file)
    # Scene area used only as an explicitly approximate, researcher-defined ROI;
    # it does not prove that the entire area is methane-emitting habitat.
    roi_km2=float(scene.observed_km2.median())
    if not 10<=roi_km2<=500:
        raise ValueError('Unexpected ROI area in actual scene data')
    design=scenarios_from_csv(Path(scenarios))
    values=[]
    for row in design.itertuples(index=False):
        actual_area=roi_km2*float(row.emitting_fraction_of_roi)
        signal=box_column_enhancement_ppb(float(row.flux_mg_m2_day),actual_area,float(row.wind_m_s))
        values.append({'scenario_id':row.scenario_id,
                       'assumption_source':row.scenario_basis,
                       'scenario_not_observed':True,
                       'wetland_ROI_km2':roi_km2,
                       'hypothetical_emitting_area_km2':actual_area,
                       'flux_mg_m2_day':float(row.flux_mg_m2_day),
                       'wind_m_s':float(row.wind_m_s),
                       'expected_full_column_increment_ppb':signal})
    result=pd.DataFrame(values)
    result.to_csv(td/'13F_hypothetical_flux_to_XCH4_scenario_screen.csv',index=False)
    fig,ax=plt.subplots(figsize=(9,5),constrained_layout=True)
    for wind,group in result.groupby('wind_m_s'):
        g=group.sort_values('hypothetical_emitting_area_km2')
        # Display variable source area assumptions without inventing retrieval noise.
        ax.scatter(g.flux_mg_m2_day,g.expected_full_column_increment_ppb,label=f'wind {wind:g} m/s')
    ax.set(xlabel='Assumed flux (mg CH4 m−2 day−1)',ylabel='Illustrative ΔXCH4 (ppb)',
           title='Methane source-area/wind sensitivity | not an instrument detectability test')
    ax.legend()
    fig.savefig(fd/'13F_flux_area_wind_box_screen.png',dpi=145,bbox_inches='tight')
    plt.close(fig)
    manifest={'created_utc':datetime.now(timezone.utc).isoformat(),
              'status':'illustrative_box_model_only_NO_L2_sampling_and_NO_flux_estimate',
              'n_scenarios':len(result),'ROI_area_km2':roi_km2,
              'can_infer_local_methane_flux':False,
              'independent_retrieval_random_noise':None,
              'systematic_transport_errors':None,
              'L2_footprint_sampling_available':False,
              'next_gate':'Audit actual native L2 footprints and product QA before any claim of detectability; a monthly XCH4 residual SD is NOT a per-sounding noise model.',
              'model_assumptions':'uniform constant emission and wind over square source; perfect column mixing; no spatial dilution or averaging-kernel treatment.'}
    write_json(td/'13F_box_model_manifest.json',manifest)
    return manifest


def _find_l2_var(ds, names):
    for name in names:
        if name in ds.variables:
            return np.asarray(ds[name].values)
    return None


def _flat_matching(a, shape, name):
    if a is None:
        return None
    data=np.asarray(a).squeeze()
    if data.shape!=shape:
        raise ValueError(f'{name} shape {data.shape} does not match latitude {shape}')
    return data.ravel()


def audit_single_l2_nc(path: Path, roi):
    """Inspect native S5P L2 CH4 PRODUCT group plus corner coordinates when present.

    Footprints are intersected if product latitude/longitude bounds are available;
    otherwise only CENTER-IN-ROI counts can be reported (not footprints).
    The L2 format varies by processor; missing key variables fail loudly.
    """
    try:
        import xarray as xr
        from shapely.geometry import Point,Polygon
    except ImportError as e:
        raise RuntimeError('Install xarray and netCDF4 for native methane L2 audit') from e
    product=xr.open_dataset(path,group='PRODUCT',engine='netcdf4')
    try:
        lat=_find_l2_var(product,['latitude'])
        lon=_find_l2_var(product,['longitude'])
        qa=_find_l2_var(product,['qa_value'])
        methane=_find_l2_var(product,['methane_mixing_ratio_bias_corrected',
                                      'methane_mixing_ratio'])
        precision=_find_l2_var(product,['methane_mixing_ratio_precision',
                                        'methane_mixing_ratio_bias_corrected_precision'])
        if any(a is None for a in (lat,lon,qa,methane)):
            raise RuntimeError(f'Native PRODUCT missing latitude/longitude/QA/methane: {path.name}')
        shape=np.asarray(lat).squeeze().shape
        lat=np.asarray(lat).squeeze().ravel()
        lon=_flat_matching(lon,shape,'longitude')
        qa=_flat_matching(qa,shape,'qa_value')
        methane=_flat_matching(methane,shape,'methane')
        precision=_flat_matching(precision,shape,'precision')
        try:
            geo=xr.open_dataset(path,group='PRODUCT/SUPPORT_DATA/GEOLOCATIONS',engine='netcdf4')
        except Exception:
            geo=None
        try:
            latitude_bounds=(_find_l2_var(geo,['latitude_bounds','latitude_corners']) if geo is not None else None)
            longitude_bounds=(_find_l2_var(geo,['longitude_bounds','longitude_corners']) if geo is not None else None)
            if latitude_bounds is not None and latitude_bounds.squeeze().size!=lat.size*4:
                latitude_bounds=None
            if longitude_bounds is not None and longitude_bounds.squeeze().size!=lon.size*4:
                longitude_bounds=None
            use_footprint=latitude_bounds is not None and longitude_bounds is not None
            if use_footprint:
                lat_bounds=np.asarray(latitude_bounds).reshape(-1,4)
                lon_bounds=np.asarray(longitude_bounds).reshape(-1,4)
            minx,miny,maxx,maxy=roi.bounds
            # Bounding-box candidate filter reduces intersections across orbit swath.
            ix=np.flatnonzero(np.isfinite(lat)&np.isfinite(lon)&
                              (lat>miny-0.35)&(lat<maxy+0.35)&
                              (lon>minx-0.35)&(lon<maxx+0.35))
            rows=[]
            for i in ix:
                inside=roi.contains(Point(float(lon[i]),float(lat[i])))
                intersected=None
                if use_footprint:
                    corners=list(zip(lon_bounds[i],lat_bounds[i]))
                    if np.isfinite(np.asarray(corners)).all():
                        footprint=Polygon(corners)
                        intersected=bool(footprint.is_valid and footprint.intersects(roi))
                    else:
                        intersected=False
                if not (inside or intersected):
                    continue
                rows.append({'product_file':path.name,
                             'centre_in_roi':bool(inside),
                             'true_footprint_intersects_roi':intersected,
                             'geometry_support':'native_bounds' if use_footprint else 'centre_only_NOT_footprint',
                             'qa_value':float(qa[i]),
                             'valid_qa_over_0p5':bool(np.isfinite(qa[i]) and qa[i]>0.5),
                             'xch4_ppb':float(methane[i]) if np.isfinite(methane[i]) else np.nan,
                             'single_sounding_precision_ppb':float(precision[i]) if precision is not None and np.isfinite(precision[i]) else np.nan,
                             'longitude':float(lon[i]),'latitude':float(lat[i])})
            if not rows:
                return pd.DataFrame(columns=['product_file','centre_in_roi','true_footprint_intersects_roi',
                                             'geometry_support','qa_value','valid_qa_over_0p5',
                                             'xch4_ppb','single_sounding_precision_ppb','longitude','latitude'])
            return pd.DataFrame(rows)
        finally:
            if geo is not None:
                geo.close()
    finally:
        product.close()


def run_l2_audit(root: Path, l2_dir: Path) -> dict:
    """Run only on independently acquired native Sentinel-5P L2 CH4 NetCDF files."""
    root=Path(root).resolve()
    l2_dir=Path(l2_dir).expanduser().resolve()
    files=sorted(l2_dir.glob('*.nc')) if l2_dir.is_dir() else []
    if not files:
        raise FileNotFoundError(f'No native L2 methane NetCDF files at {l2_dir}; L3 month coverage does not substitute')
    polygon=load_boundary(root)
    td,_=outputs(root,'analysis13')
    all_found=[]
    inventory=[]
    for f in files:
        print('Inspect L2:',f.name)
        found=audit_single_l2_nc(f,polygon)
        inventory.append({'product_file':f.name,'n_roi_candidates':len(found),
                          'native_footprint_bounds_available':bool(len(found) and (found.geometry_support=='native_bounds').all()),
                          'n_qa_valid':int(found.valid_qa_over_0p5.sum()) if len(found) else 0})
        if len(found):
            all_found.append(found)
    pd.DataFrame(inventory).to_csv(td/'13F_native_L2_product_support_inventory.csv',index=False)
    if all_found:
        rows=pd.concat(all_found,ignore_index=True)
        rows.to_csv(td/'13F_native_L2_footprints_or_centres_QA.csv',index=False)
        real_footprints=bool((rows.geometry_support=='native_bounds').all())
        good=rows.loc[rows.valid_qa_over_0p5 & rows.xch4_ppb.notna()]
        n_good=int(len(good))
    else:
        n_good=0;real_footprints=False
    status={'created_utc':datetime.now(timezone.utc).isoformat(),
            'status':'native_L2_product_input_audited_NOT_flux_or_detectability',
            'n_products':len(files),'n_QA_valid_observations_in_selected_roi_support':n_good,
            'all_geometry_uses_native_footprint_bounds':real_footprints,
            'qa_cutoff':'qa_value > 0.5; product-version dependent, verify against current ATBD',
            'mandatory_next_steps':'crosswind/source geometry, background, winds, retrieval random+systematic uncertainties, independent source flux priors.',
            'warning':'Products provided may not cover every date; missing product files are not zero retrievals. Centre-only support cannot be called footprint intersections.'}
    write_json(td/'13F_L2_audit_manifest.json',status)
    return status
