"""Optional Sentinel-2 reference *candidate* search for independent image interpretation.

Automated Sentinel-2 SCL water classification is NOT independent truth. Cloud,
shadow, submerged vegetation and date mismatch need manual review. No accuracy
claim is made by downloading reference imagery.
"""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path
import numpy as np
import pandas as pd

from .core import ee_initialize, load_boundary, outputs, write_json


def candidate_s2(root: Path, scene_local_time: str, *, window_days: int=10,
                 maximum_catalog_cloud_percent: float=85, max_items: int=30):
    root=Path(root).resolve()
    target=pd.Timestamp(scene_local_time)
    if target.tzinfo is None:
        raise ValueError('scene_local_time must contain timezone offset')
    target_utc=target.tz_convert('UTC')
    ee=ee_initialize()
    polygon=load_boundary(root)
    roi=ee.Geometry(polygon.__geo_interface__)
    t0=(target_utc-pd.Timedelta(days=window_days)).strftime('%Y-%m-%d')
    t1=(target_utc+pd.Timedelta(days=window_days+2)).strftime('%Y-%m-%d')
    coll=(ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
          .filterBounds(roi).filterDate(t0,t1)
          .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE',float(maximum_catalog_cloud_percent))))
    n=int(coll.size().getInfo())
    if n>300:
        raise RuntimeError('Unexpected candidate count; tighten search window')
    c=coll.sort('system:time_start').limit(max_items)
    ids=c.aggregate_array('system:index').getInfo()
    times=c.aggregate_array('system:time_start').getInfo()
    clouds=c.aggregate_array('CLOUDY_PIXEL_PERCENTAGE').getInfo()
    if not(len(ids)==len(times)==len(clouds)):
        raise RuntimeError('Inconsistent candidate metadata arrays')
    table=pd.DataFrame({'image_id':ids,
                        'acquisition_utc':pd.to_datetime(times,unit='ms',utc=True),
                        'catalog_tile_cloud_percent':clouds})
    if len(table):
        table['signed_offset_hours']=(table.acquisition_utc-target_utc).dt.total_seconds()/3600
        table['abs_offset_hours']=table.signed_offset_hours.abs()
        table['warning']='Catalog cloud percent is NOT study-area clear fraction or reference truth'
        table=table.sort_values(['abs_offset_hours','catalog_tile_cloud_percent'])
    td,_=outputs(root,'analysis13')
    name=target.strftime('%Y%m%dT%H%M')
    dest=td/f'13E_S2_candidates_for_{name}.csv'
    table.to_csv(dest,index=False)
    return table


def export_s2_review_candidate(root: Path, image_id: str, *, output_file: Path | None=None) -> Path:
    """Download 20-m reflectance bands plus SCL for human optical interpretation.

    User must inspect real cloud cover and acquisition timing. The 20m product
    does NOT substitute for independent class labels or same-day validation.
    """
    import requests
    import rasterio
    ee=ee_initialize()
    polygon=load_boundary(Path(root))
    roi=ee.Geometry(polygon.__geo_interface__)
    image=ee.Image('COPERNICUS/S2_SR_HARMONIZED/'+image_id)
    # Original surface reflectance scales by 1e4; B2/B3/B4/B8 at native 10m,
    # B11/B12 and SCL at 20m. All exports on an explicitly documented 20m grid.
    refl=image.select(['B2','B3','B4','B8','B11','B12']).toFloat().divide(10000)
    scl=image.select('SCL').toFloat().rename('SCL_CLASS')
    composite=ee.Image.cat([refl,scl]).clip(roi)
    url=composite.getDownloadURL({'region':roi,'crs':'EPSG:32646','scale':20,
                                  'format':'GEO_TIFF','filePerBand':False})
    resp=requests.get(url,timeout=240)
    resp.raise_for_status()
    if output_file is None:
        output_file=Path(root)/'data'/'external'/'reference_imagery'/f'S2_{image_id}_20m.tif'
    output_file=Path(output_file)
    output_file.parent.mkdir(parents=True,exist_ok=True)
    output_file.write_bytes(resp.content)
    with rasterio.open(output_file) as src:
        if src.count!=7 or src.crs.to_epsg()!=32646:
            raise RuntimeError('Downloaded optical reference candidate failed CRS/band QA')
    return output_file
