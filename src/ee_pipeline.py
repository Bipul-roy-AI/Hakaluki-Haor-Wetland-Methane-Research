"""Earth Engine processing for Hakaluki Haor; all returned values require actual EE execution.

Wetland methane flux is NOT directly observed by TROPOMI. Flood masks here are
*screening-grade* and need independent flood mapping validation before publication.
"""
from __future__ import annotations
import ee
import pandas as pd
from src.hakaluki_core import otsu_from_histogram, monthly_periods

S1_ID = 'COPERNICUS/S1_GRD'
CH4_ID = 'COPERNICUS/S5P/OFFL/L3_CH4'
CH4_BAND = 'CH4_column_volume_mixing_ratio_dry_air_bias_corrected'
ERA5_ID = 'ECMWF/ERA5_LAND/MONTHLY_AGGR'
CHIRPS_ID = 'UCSB-CHG/CHIRPS/DAILY'
S2_ID = 'COPERNICUS/S2_SR_HARMONIZED'
DW_ID = 'GOOGLE/DYNAMICWORLD/V1'


def initialize(project_id):
    if not project_id or 'REPLACE_' in project_id:
        raise ValueError('Set earth_engine_cloud_project in config/settings.json first.')
    try:
        ee.Initialize(project=project_id)
    except Exception:
        # Starts browser-driven Google OAuth in a compatible notebook session.
        ee.Authenticate()
        ee.Initialize(project=project_id)
    return ee.Number(1).getInfo() == 1


def geometry_from_geodataframe(gdf):
    geom = gdf.to_crs('EPSG:4326').geometry.union_all()
    return ee.Geometry(geom.__geo_interface__)


def s1_collection(roi, start, end, orbit_pass=None, relative_orbit=None):
    col = (ee.ImageCollection(S1_ID).filterBounds(roi).filterDate(start,end)
        .filter(ee.Filter.eq('instrumentMode', 'IW'))
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation','VV'))
        .select(['VV','angle']))
    if orbit_pass in ('ASCENDING','DESCENDING'):
        col = col.filter(ee.Filter.eq('orbitProperties_pass',orbit_pass))
    if relative_orbit is not None:
        col = col.filter(ee.Filter.eq('relativeOrbitNumber_start',int(relative_orbit)))
    return col


def choose_s1_geometry(roi, year=2022):
    """Choose most-observed pass and its most frequent relative orbit in a pilot year.

    This increases comparability but does not guarantee monthly coverage.
    """
    all_images = s1_collection(roi, f'{year}-01-01',f'{year+1}-01-01')
    pass_counts = all_images.aggregate_histogram('orbitProperties_pass').getInfo()
    if not pass_counts:
        raise RuntimeError('No Sentinel-1 IW VV images in the supplied study region/year.')
    orbit_pass = max(pass_counts,key=lambda key:pass_counts[key])
    pass_images = all_images.filter(ee.Filter.eq('orbitProperties_pass',orbit_pass))
    orbit_counts = pass_images.aggregate_histogram('relativeOrbitNumber_start').getInfo()
    # Earth Engine histogram keys may be serialized as strings such as "41.0".
    # Convert through float first to avoid ValueError from int("41.0").
    if orbit_counts:
        selected_orbit_key = max(orbit_counts, key=lambda key: orbit_counts[key])
        orbit_as_float = float(selected_orbit_key)
        if not orbit_as_float.is_integer():
            raise ValueError(f"Unexpected non-integer Sentinel-1 relative orbit: {selected_orbit_key!r}")
        relative_orbit = int(orbit_as_float)
    else:
        relative_orbit = None

    return {
        'orbit_pass': orbit_pass,
        'relative_orbit': relative_orbit,
        'pass_counts': pass_counts,
        'orbit_counts': orbit_counts,
    }


def mean_reduction(image, roi, band, scale):
    result = image.select([band]).reduceRegion(
        reducer=ee.Reducer.mean(),geometry=roi,scale=scale,maxPixels=1e9,
        tileScale=4,bestEffort=True).getInfo()
    return result.get(band)


def valid_pixel_fraction(image, roi, band, scale=7000):
    """Fraction of *resampled grid cells* with CH4 data, NOT independent footprints."""
    one = ee.Image.constant(1).rename('valid')
    masked = one.updateMask(image.select([band]).mask())
    numerator = masked.reduceRegion(ee.Reducer.count(),roi,scale,maxPixels=1e8,
                                    bestEffort=True,tileScale=4).getInfo().get('valid')
    denominator = one.reduceRegion(ee.Reducer.count(),roi,scale,maxPixels=1e8,
                                   bestEffort=True,tileScale=4).getInfo().get('valid')
    if not denominator or numerator is None:
        return 0.0
    return float(numerator / denominator)


def s1_month_water(roi, start, end, orbit_pass, relative_orbit,
                   histogram_scale=60, water_threshold=None):
    """Monthly Otsu VV map. Not a validated flooded-vegetation detector.

    The low-VV class may include smooth non-water surfaces; dense emergent
    vegetation can be misclassified as land. Validation is mandatory.
    """
    col = s1_collection(roi,start,end,orbit_pass,relative_orbit)
    n = col.size().getInfo()
    if n == 0:
        return None,{'s1_scenes':0,'water_area_km2':None,'sar_valid_area_km2':None,
                     'water_threshold_db':None,'water_area_low_km2':None,'water_area_high_km2':None,'sar_qc_status':'no_scenes'}
    vv = col.select('VV').median().focal_median(30,'circle','meters').rename('VV').clip(roi)
    if water_threshold is None:
        hist = vv.reduceRegion(reducer=ee.Reducer.histogram(maxBuckets=128,minBucketWidth=0.1),
                  geometry=roi,scale=histogram_scale,maxPixels=1e8,
                  bestEffort=True,tileScale=4).get('VV').getInfo()
        if not hist or not hist.get('histogram'):
            return None, {'s1_scenes':n,'water_area_km2':None,'sar_valid_area_km2':None,
                          'water_threshold_db':None,'water_area_low_km2':None,
                          'water_area_high_km2':None,'sar_qc_status':'missing_histogram'}
        try:
            threshold = otsu_from_histogram(hist)
        except ValueError:
            return None, {'s1_scenes':n,'water_area_km2':None,'sar_valid_area_km2':None,
                          'water_threshold_db':None,'water_area_low_km2':None,
                          'water_area_high_km2':None,'sar_qc_status':'invalid_histogram'}
    else:
        threshold = float(water_threshold)
    # 0=screened non-water; 1=screened water; masked=no SAR support.
    water = vv.lt(threshold).rename('water')

    def area(img, selected_only=True):
        # A water mask has valid zeroes, so area must use *values*, not just mask.
        active = img if selected_only else img.mask()
        sqm = ee.Image.pixelArea().updateMask(active)
        value = sqm.reduceRegion(ee.Reducer.sum(),roi,scale=30,maxPixels=1e9,
                                 bestEffort=True,tileScale=4).getInfo().get('area')
        return float(value)/1e6 if value is not None else 0.0

    # These bracketed thresholds are an uncalibrated sensitivity test, NOT CI.
    water_low = vv.lt(threshold - 1.5).selfMask()
    water_high = vv.lt(threshold + 1.5).selfMask()
    metrics={'s1_scenes':n,'water_threshold_db':threshold,
             'water_area_km2':area(water),
             'water_area_low_km2':area(water_low),
             'water_area_high_km2':area(water_high),
             'sar_valid_area_km2':area(vv,selected_only=False),'sar_qc_status':'screening_only_unvalidated'}
    return water, metrics


def climate_month(roi, start, end):
    chirps = ee.ImageCollection(CHIRPS_ID).filterBounds(roi).filterDate(start,end).select('precipitation')
    era5 = ee.ImageCollection(ERA5_ID).filterBounds(roi).filterDate(start,end).select('temperature_2m')
    output = {'rain_chirps_mm':None,'temp2m_era5_c':None,'chirps_daily_images':chirps.size().getInfo()}
    if output['chirps_daily_images']:
        output['rain_chirps_mm'] = mean_reduction(chirps.sum(),roi,'precipitation',5500)
    if era5.size().getInfo():
        temperature = mean_reduction(era5.mean(),roi,'temperature_2m',11000)
        output['temp2m_era5_c'] = (temperature - 273.15) if temperature is not None else None
    return output


def methane_month(roi, ref_ring, start, end):
    imgs = ee.ImageCollection(CH4_ID).filterBounds(roi.union(ref_ring)).filterDate(start,end).select(CH4_BAND)
    n = imgs.size().getInfo()
    output={'ch4_images_tiled':n,'ch4_xch4_ppb_roi':None,'ch4_xch4_ppb_ring':None,
            'ch4_roi_minus_ring_ppb':None,'ch4_l3_grid_coverage_fraction':0.0}
    if n:
        image = imgs.mean()
        output['ch4_l3_grid_coverage_fraction'] = valid_pixel_fraction(image,roi,CH4_BAND)
        output['ch4_xch4_ppb_roi'] = mean_reduction(image,roi,CH4_BAND,7000)
        output['ch4_xch4_ppb_ring'] = mean_reduction(image,ref_ring,CH4_BAND,7000)
        a,b=output['ch4_xch4_ppb_roi'],output['ch4_xch4_ppb_ring']
        if a is not None and b is not None:
            output['ch4_roi_minus_ring_ppb'] = a-b
    return output


def fetch_one_month(period, roi, methane_roi, methane_background,
                    orbit_pass, relative_orbit):
    row={k:period[k] for k in ['year','month','period','start','end']}
    _,water=s1_month_water(roi,period['start'],period['end'],orbit_pass,relative_orbit)
    row.update(water)
    row.update(climate_month(roi,period['start'],period['end']))
    row.update(methane_month(methane_roi,methane_background,period['start'],period['end']))
    _,habitats=dynamic_world_month(roi,period['start'],period['end'])
    row.update(habitats)
    _,optics=optical_s2_month(roi,period['start'],period['end'])
    row.update(optics)
    row['result_status']='preliminary_unvalidated'
    return row


def run_months(start_year,end_year,roi,methane_roi,methane_background,
               orbit_pass,relative_orbit,out_dir,cache_fingerprint=None):
    """Checkpoint after each completed month. A re-run skips saved months.

    A 2019-2025 project can require substantial Earth Engine compute time; it is
    intentionally invoked in year-level batches from the notebook.
    """
    from pathlib import Path
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for p in monthly_periods(start_year,end_year):
        path=out/f"monthly_{p['period']}.csv"
        if path.exists():
            row=pd.read_csv(path).iloc[0].to_dict()
            expected=cache_fingerprint or 'UNVERSIONED'
            if str(row.get('cache_fingerprint','')) != expected:
                raise ValueError(f"Stale or mismatched checkpoint {path}. "
                                 "Archive old monthly CSVs and rerun when input boundary/config/code changes.")
            print(f"Reused {p['period']}")
        else:
            print(f"Calculating {p['period']}...",flush=True)
            row=fetch_one_month(p,roi,methane_roi,methane_background,orbit_pass,relative_orbit)
            row['cache_fingerprint']=cache_fingerprint or 'UNVERSIONED'
            pd.DataFrame([row]).to_csv(path,index=False)
        rows.append(row)
    df=pd.DataFrame(rows)
    df.to_csv(out/f"monthly_{start_year}_{end_year}_combined.csv",index=False)
    return df


def start_drive_geotiff_export(image, roi, description, drive_folder='Hakaluki_Haor_Study',scale=30, as_byte=True):
    image = image.toByte() if as_byte else image.toFloat()
    task=ee.batch.Export.image.toDrive(
        image=image,description=description,folder=drive_folder,
        fileNamePrefix=description,region=roi,scale=scale,
        maxPixels=1e10,fileFormat='GeoTIFF')
    task.start()
    return task


def dynamic_world_month(roi, start, end):
    """Cloud-limited label modes for habitat *screening*; not validated ground truth.

    Dynamic World flooded_vegetation is class 3; water class 0.
    A monthly mode is not a direct map of inundation duration or methane source area.
    """
    col=ee.ImageCollection(DW_ID).filterBounds(roi).filterDate(start,end).select('label')
    n=col.size().getInfo()
    base={'dw_scene_count':n,'dw_water_km2':None,'dw_flooded_vegetation_km2':None,
          'dw_crops_km2':None,'dw_valid_class_area_km2':None}
    if n==0:return None,base
    cls=col.mode().rename('dw_class').clip(roi)

    def count_class(value):
        band=ee.Image.pixelArea().updateMask(cls.eq(value)).rename('area')
        result=band.reduceRegion(ee.Reducer.sum(),roi,scale=30,maxPixels=1e9,
                                 tileScale=4,bestEffort=True).getInfo().get('area')
        return float(result or 0)/1e6

    area_valid=(ee.Image.pixelArea().updateMask(cls.mask()).rename('area')
        .reduceRegion(ee.Reducer.sum(),roi,scale=30,maxPixels=1e9,
                      tileScale=4,bestEffort=True).getInfo().get('area'))
    base.update({'dw_water_km2':count_class(0),
                 'dw_flooded_vegetation_km2':count_class(3),
                 'dw_crops_km2':count_class(4),
                 'dw_valid_class_area_km2':float(area_valid or 0)/1e6})
    return cls,base


def optical_s2_month(roi,start,end):
    """S2 cloud-masked NDVI and MNDWI diagnostics; no artificial gap filling."""
    col=ee.ImageCollection(S2_ID).filterBounds(roi).filterDate(start,end)
    n=col.size().getInfo()
    if not n:return None,{'s2_scene_count':0,'ndvi_s2_mean':None,'mndwi_s2_mean':None}
    def mask_clouds(im):
        scl=im.select('SCL')
        okay=(scl.neq(3).And(scl.neq(8)).And(scl.neq(9))
              .And(scl.neq(10)).And(scl.neq(11)).And(scl.neq(0)))
        return im.updateMask(okay)
    med=col.map(mask_clouds).median().clip(roi)
    ndvi=med.normalizedDifference(['B8','B4']).rename('NDVI')
    mndwi=med.normalizedDifference(['B3','B11']).rename('MNDWI')
    derived=ndvi.addBands(mndwi)
    return derived,{'s2_scene_count':n,
                    'ndvi_s2_mean':mean_reduction(ndvi,roi,'NDVI',20),
                    'mndwi_s2_mean':mean_reduction(mndwi,roi,'MNDWI',20)}


def chirps_daily_time_series(roi,start,end):
    """Daily CHIRPS rainfall spatial means (mm/day) in one EE request."""
    col=ee.ImageCollection(CHIRPS_ID).filterBounds(roi).filterDate(start,end).select('precipitation')
    def set_mean(im):
        scalar=im.reduceRegion(ee.Reducer.mean(),roi,scale=5500,maxPixels=1e8,
                               bestEffort=True,tileScale=4).get('precipitation')
        return im.set('roi_mm',scalar)
    col=col.map(set_mean)
    dates=col.aggregate_array('system:time_start').getInfo()
    values=col.aggregate_array('roi_mm').getInfo()
    df=pd.DataFrame({'date':pd.to_datetime(dates,unit='ms',utc=True).tz_convert(None),
                     'rain_chirps_mm_day':values})
    return df.sort_values('date').reset_index(drop=True)
