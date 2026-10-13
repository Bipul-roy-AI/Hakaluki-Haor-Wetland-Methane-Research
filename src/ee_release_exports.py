"""Resumable Google Earth Engine image exports for Hakaluki Haor.

Run inside an authenticated Python/Jupyter Earth Engine session. Export tasks are
asynchronous; a submitted task is not proof that a GeoTIFF exists or has been downloaded.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

DATASETS = {
    'SAR_water':('Sentinel-1 GRD low-VV Otsu water screening',30,'0/1 preliminary water screen'),
    'S2_NDVI':('Sentinel-2 SR NDVI',20,'unitless NDVI'),
    'S2_MNDWI':('Sentinel-2 SR MNDWI',20,'unitless MNDWI'),
    'DW_class':('Dynamic World label mode',30,'categorical 0..8'),
    'CHIRPS_rain':('CHIRPS daily precipitation sum',5500,'mm/month'),
    'ERA5_temp':('ERA5-Land monthly 2m mean temperature',11000,'degrees C'),
    'TROPOMI_CH4':('TROPOMI bias-corrected column XCH4',7000,'ppb; gridding ≠ independent retrieval size'),
}


def create_environment(root):
    import ee
    import geopandas as gpd
    from src.ee_pipeline import initialize,geometry_from_geodataframe,choose_s1_geometry
    root=Path(root)
    cfg=json.loads((root/'config'/'settings.json').read_text(encoding='utf-8'))
    boundary=root/'data'/'boundary'/'hakaluki_analysis_candidate.geojson'
    if not boundary.exists(): boundary=root/'Study area'/'Hakaluki_Haor.shp'
    if not boundary.exists(): raise FileNotFoundError('Run Notebook 00: no boundary input found.')
    gdf=gpd.read_file(boundary)
    if gdf.empty or gdf.crs is None or not gdf.geometry.is_valid.all():
        raise ValueError('Empty, invalid, or unprojected study boundary.')
    initialize(cfg['earth_engine_cloud_project'])
    roi=geometry_from_geodataframe(gdf)
    sar_info=choose_s1_geometry(roi, cfg.get('pilot_year',2022))
    return {'ee':ee,'cfg':cfg,'roi':roi,'ch4_roi':roi.buffer(cfg.get('ch4_buffer_m',30000)),
            'sar':sar_info,'boundary_path':boundary}


def _one_month(env, year, month, types):
    from src.ee_pipeline import (s1_month_water,optical_s2_month,dynamic_world_month,
            CHIRPS_ID,ERA5_ID,CH4_ID,CH4_BAND)
    ee=env['ee'];roi=env['roi'];mroi=env['ch4_roi']
    start=f'{year}-{month:02d}-01'
    end=f'{year+1}-01-01' if month==12 else f'{year}-{month+1:02d}-01'
    specs=[]
    if 'SAR_water' in types:
        img,info=s1_month_water(roi,start,end,env['sar']['orbit_pass'],env['sar']['relative_orbit'])
        if img is not None:
            specs.append(('SAR_water',img.toByte(),roi,{'threshold_db':info.get('water_threshold_db'),
                                                       's1_scenes':info.get('s1_scenes')}))
    if any(x in types for x in ['S2_NDVI','S2_MNDWI']):
        img,info=optical_s2_month(roi,start,end)
        if img is not None:
            for name,band in [('S2_NDVI','NDVI'),('S2_MNDWI','MNDWI')]:
                if name in types: specs.append((name,img.select(band).toFloat(),roi,{'s2_scenes':info.get('s2_scene_count')}))
    if 'DW_class' in types:
        img,info=dynamic_world_month(roi,start,end)
        if img is not None:specs.append(('DW_class',img.toByte(),roi,{'dw_scenes':info.get('dw_scene_count')}))
    if 'CHIRPS_rain' in types:
        col=ee.ImageCollection(CHIRPS_ID).filterBounds(roi).filterDate(start,end).select('precipitation')
        if col.size().getInfo():
            specs.append(('CHIRPS_rain',col.sum().rename('monthly_rain_mm').toFloat().clip(roi),roi,{}))
    if 'ERA5_temp' in types:
        col=ee.ImageCollection(ERA5_ID).filterBounds(roi).filterDate(start,end).select('temperature_2m')
        if col.size().getInfo():
            specs.append(('ERA5_temp',col.mean().subtract(273.15).rename('temperature_2m_c').toFloat().clip(roi),roi,{}))
    if 'TROPOMI_CH4' in types:
        col=ee.ImageCollection(CH4_ID).filterBounds(mroi).filterDate(start,end).select(CH4_BAND)
        if col.size().getInfo():
            specs.append(('TROPOMI_CH4',col.mean().toFloat().clip(mroi),mroi,
                          {'warning':'regional atmospheric XCH4, NOT methane flux; gridded pixel is not a footprint'}))
    return specs


def refresh_status(root):
    """Request current EE task states, rewriting status CSV without pretending files downloaded."""
    import ee
    path=Path(root)/'results'/'tables'/'ee_export_task_manifest.csv'
    if not path.exists():return pd.DataFrame()
    df=pd.read_csv(path).fillna('')
    for i,row in df.iterrows():
        if not row.get('task_id'):continue
        try:
            info=ee.data.getTaskStatus(str(row['task_id']))
            if info:df.loc[i,'task_state']=info[0].get('state','UNKNOWN')
        except Exception as ex:
            df.loc[i,'task_state']='QUERY_ERROR: '+type(ex).__name__
    df.to_csv(path,index=False)
    return df


def submit_batch(env,root,years=(2022,),months=(3,4,5,6,7,8,9),
                 types=('SAR_water','S2_NDVI','S2_MNDWI','DW_class','CHIRPS_rain','ERA5_temp','TROPOMI_CH4'),
                 max_new_tasks=8,dry_run=True):
    """Resumable task queue: rerun to submit the next up-to-N missing jobs.

    dry_run=True performs NO GEE image computations or job submissions.
    The manifest logs *submitted* exports only, never treats them as downloaded.
    """
    root=Path(root);config=env['cfg']
    types=list(types)
    unknown=set(types)-set(DATASETS)
    if unknown: raise ValueError(f'Unknown layer types: {unknown}')
    years=sorted(set(map(int,years)))
    months=sorted(set(map(int,months)))
    if any(m<1 or m>12 for m in months):raise ValueError('Months must be between 1 and 12.')
    all_jobs=[(y,m,k) for y in years for m in months for k in types]
    path=root/'results'/'tables'/'ee_export_task_manifest.csv';path.parent.mkdir(parents=True,exist_ok=True)
    old=pd.read_csv(path).fillna('') if path.exists() else pd.DataFrame()
    known=set(old['export_name']) if 'export_name' in old else set()
    outstanding=[(y,m,k) for y,m,k in all_jobs if f'HAKALUKI_{y}_{m:02d}_{k}' not in known]
    print(f'Planned jobs: {len(all_jobs)} | already recorded: {len(all_jobs)-len(outstanding)} | pending: {len(outstanding)}')
    if dry_run:
        return {'dry_run':True,'total':len(all_jobs),'remaining':len(outstanding),
                'preview_next':[f'HAKALUKI_{y}_{m:02d}_{k}' for y,m,k in outstanding[:max_new_tasks]]}
    from src.ee_pipeline import start_drive_geotiff_export
    submitted=[];remaining=max_new_tasks
    for year,month in sorted(set((y,m) for y,m,_ in outstanding)):
        missing=[k for y,m,k in outstanding if y==year and m==month]
        # Build only the first remaining kinds, preventing unnecessary EE operations.
        needed=missing[:remaining]
        for kind,image,region,extra in _one_month(env,year,month,needed):
            if remaining<=0:break
            name=f'HAKALUKI_{year}_{month:02d}_{kind}'
            source,scale,units=DATASETS[kind]
            task=start_drive_geotiff_export(image,region,name,drive_folder=config['ee_export_drive_folder'],
                                            scale=scale,as_byte=kind in ['SAR_water','DW_class'])
            rec={'export_name':name,'year':year,'month':month,'source':source,
                 'source_type':kind,'unit':units,'scale_m_approx':scale,
                 'drive_folder':config['ee_export_drive_folder'],
                 'expected_filename':name+'.tif','task_id':task.id,
                 'task_state':task.status().get('state','SUBMITTED'),
                 'submitted_utc':datetime.now(timezone.utc).isoformat(),
                 'notes':json.dumps(extra)}
            submitted.append(rec);remaining-=1
            print(f'Submitted {name} [{rec["task_state"]}]')
        if remaining<=0:break
    if submitted:
        updated=pd.concat([old,pd.DataFrame(submitted)],ignore_index=True)
        updated.to_csv(path,index=False)
    return {'dry_run':False,'n_new_tasks':len(submitted),'n_planned':len(all_jobs),
            'n_recorded':len(known)+len(submitted),'manifest_csv':str(path),
            'note':'A task may still be QUEUED/RUNNING/FAILED. Download successful GeoTIFFs from Google Drive.'}
