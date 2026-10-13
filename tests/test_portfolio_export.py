"""Synthetic fixture only in temporary test directories; no false results in project."""
from pathlib import Path
import json
import pandas as pd
import pytest

from src.portfolio_export import build_release
from src.ee_release_exports import submit_batch, DATASETS


def _project(tmp_path):
    (tmp_path/'config').mkdir()
    (tmp_path/'data'/'processed').mkdir(parents=True)
    (tmp_path/'results'/'tables').mkdir(parents=True)
    (tmp_path/'results'/'rasters').mkdir(parents=True)
    (tmp_path/'config'/'settings.json').write_text(json.dumps({
        'earth_engine_cloud_project':'axial-paratext-491911-b6',
        'ee_export_drive_folder':'Hakaluki_Haor_Study'}),encoding='utf-8')
    return tmp_path


def test_empty_release_is_explicit(tmp_path):
    root=_project(tmp_path)
    result=build_release(root)
    assert result['n_months']==0
    assert result['n_figures_png']==0
    assert 'None yet' in (root/'results'/'github_release'/'README.md').read_text()
    assert (root/'results'/'github_release'/'assets_manifest.json').exists()


def test_monthly_release_real_inputs(tmp_path):
    root=_project(tmp_path)
    for year in [2020,2021,2022]:
        for month in range(1,13):
            pd.DataFrame([{
                'year':year,'month':month,'period':f'{year}-{month:02d}',
                'water_area_km2':month+year%7,'rain_chirps_mm':month*4,
                'temp2m_era5_c':28+month/10,
                'ch4_xch4_ppb_roi':1850+month*0.2,
                'ch4_roi_minus_ring_ppb': month*.5,
                'ch4_l3_grid_coverage_fraction':.8,
                'cache_fingerprint':'unit_test_only',
            }]).to_csv(root/'data'/'processed'/f'monthly_{year}-{month:02d}.csv',index=False)
    info=build_release(root)
    release=root/'results'/'github_release'
    assert info['n_months']==36
    assert info['n_figures_png']>=3
    assert (release/'data'/'monthly_observations_combined.csv').exists()
    assert (release/'figures'/'01_monthly_timeseries.png').exists()
    assert '2022' in (release/'README.md').read_text()
    assert info['n_release_files']>10


def test_raster_preview_with_real_geotiff_test_fixture(tmp_path):
    rasterio=pytest.importorskip('rasterio')
    import numpy as np
    from rasterio.transform import from_origin
    root=_project(tmp_path)
    p=root/'results'/'rasters'/'HAKALUKI_2022_03_SAR_water.tif'
    with rasterio.open(p,'w',driver='GTiff',height=40,width=50,count=1,
                       dtype='uint8',crs='EPSG:4326',transform=from_origin(92.05,24.7,.0003,.0003)) as dst:
        dst.write((np.indices((40,50))[0]%3==0).astype('uint8'),1)
    info=build_release(root)
    assert info['n_tifs']==1
    assert (root/'results'/'github_release'/'figures'/'map_HAKALUKI_2022_03_SAR_water.png').is_file()


def test_gee_dry_run_no_network(tmp_path):
    root=_project(tmp_path)
    env={'cfg':{'ee_export_drive_folder':'Hakaluki_Haor_Study'}}
    result=submit_batch(env,root,years=[2022],months=[3,4],types=list(DATASETS)[:2],
                        max_new_tasks=3,dry_run=True)
    assert result['total']==4
    assert result['remaining']==4
    assert len(result['preview_next'])==3
    assert not (root/'results'/'tables'/'ee_export_task_manifest.csv').exists()
