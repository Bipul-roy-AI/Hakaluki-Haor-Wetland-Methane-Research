"""Build a provenance-conscious GitHub / portfolio release from REAL Hakaluki exports.

This module never generates artificial satellite or methane observations.
All figures and tables derive from existing Earth Engine outputs or GeoTIFFs.
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_NAME = 'Hakaluki Haor: Flood, Hydroclimate and Atmospheric Methane'
DISCLAIMER = ('PRELIMINARY; unverified wetland boundary and screening-grade SAR water maps. '
              'TROPOMI observes column XCH4, not measured wetland methane flux. '
              'No field methane calibration has been performed.')

VARIABLES = {
    'water_area_km2': ('Low-VV water screen', 'km²'),
    'rain_chirps_mm': ('CHIRPS monthly precipitation', 'mm/month'),
    'temp2m_era5_c': ('ERA5-Land 2 m air temperature', '°C'),
    'ch4_xch4_ppb_roi': ('TROPOMI atmospheric XCH₄ over ROI', 'ppb'),
    'ch4_xch4_ppb_ring': ('TROPOMI background-ring XCH₄', 'ppb'),
    'ch4_roi_minus_ring_ppb': ('ROI minus ring XCH₄', 'ppb'),
    'ch4_l3_grid_coverage_fraction': ('TROPOMI gridded sample coverage', 'fraction, not independent footprints'),
    'dw_water_km2': ('Dynamic World water class', 'km²'),
    'dw_flooded_vegetation_km2': ('Dynamic World flooded-vegetation class', 'km²'),
    'dw_crops_km2': ('Dynamic World cropland class', 'km²'),
    'ndvi_s2_mean': ('Sentinel-2 NDVI', 'unitless'),
    'mndwi_s2_mean': ('Sentinel-2 MNDWI', 'unitless'),
}


def _hash_file(file):
    h = hashlib.sha256()
    with Path(file).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def _figure(fig, folder, stem):
    folder.mkdir(parents=True, exist_ok=True)
    fig.savefig(folder / f'{stem}.png', dpi=220, bbox_inches='tight', facecolor='white')
    fig.savefig(folder / f'{stem}.svg', bbox_inches='tight', facecolor='white')
    plt.close(fig)


def _theme(ax):
    ax.grid(alpha=.18)
    ax.spines[['top','right']].set_visible(False)


def _records(root):
    files = sorted((root / 'data' / 'processed').glob('monthly_20??-??.csv'))
    rows = []
    for f in files:
        try:
            df = pd.read_csv(f)
            if not df.empty and 'period' in df:
                rows.append(df)
        except (pd.errors.EmptyDataError, UnicodeDecodeError):
            continue
    if not rows:
        return pd.DataFrame(), files
    out = pd.concat(rows, ignore_index=True)
    if 'cache_fingerprint' in out and out['cache_fingerprint'].dropna().nunique() > 1:
        raise ValueError('Monthly CSV files use different boundary/code fingerprints. Do not mix research runs.')
    if out['period'].duplicated().any():
        raise ValueError('Duplicate monthly period entries; review checkpoint folder before release.')
    out['date'] = pd.to_datetime(out['period'].astype(str) + '-01', errors='coerce')
    out = out.sort_values('date').reset_index(drop=True)
    return out, files


def _make_timeseries(df, outdir):
    panels = [v for v in ['water_area_km2','rain_chirps_mm','temp2m_era5_c',
                          'ch4_xch4_ppb_roi','ch4_roi_minus_ring_ppb'] if v in df]
    if not panels:
        return
    fig, axes = plt.subplots(len(panels), 1, figsize=(11, 2.35 * len(panels) + .8), sharex=True)
    axes = np.atleast_1d(axes)
    for ax, field in zip(axes, panels):
        arr = pd.to_numeric(df[field], errors='coerce')
        ax.plot(df['date'], arr, '.-', linewidth=1.7, markersize=4)
        ax.set_ylabel(f'{VARIABLES[field][0]}\n({VARIABLES[field][1]})', fontsize=9)
        _theme(ax)
    axes[-1].set_xlabel('Month')
    fig.suptitle('Hakaluki Haor | Satellite and hydroclimate time series (preliminary)',
                 fontweight='bold', fontsize=14)
    fig.text(.01, .01, DISCLAIMER, fontsize=7.3, alpha=.8)
    fig.tight_layout(rect=[0,.04,1,.95])
    _figure(fig, outdir, '01_monthly_timeseries')


def _make_completeness(df, outdir):
    fields = [c for c in VARIABLES if c in df]
    if not fields:
        return pd.DataFrame()
    vals = pd.DataFrame({'variable':fields,
        'available_months':[int(pd.to_numeric(df[c], errors='coerce').notna().sum()) for c in fields],
        'total_months':len(df)})
    vals['missing_months'] = vals['total_months'] - vals['available_months']
    vals['available_fraction'] = vals['available_months'] / vals['total_months']
    fig,ax = plt.subplots(figsize=(10, max(4,len(fields)*.44)))
    ax.barh(np.arange(len(fields)), vals['available_fraction']*100)
    ax.set_yticks(np.arange(len(fields)), [VARIABLES[f][0] for f in fields],fontsize=9)
    ax.set_xlim(0,105); ax.set_xlabel('Available monthly records (%)')
    ax.set_title(f'Data availability across {len(df)} exported monthly records')
    ax.invert_yaxis(); _theme(ax)
    fig.tight_layout(); _figure(fig,outdir,'02_data_completeness')
    return vals


def _make_month_climatology(df, outdir):
    if df['date'].dt.year.nunique() < 3:
        return False
    fields = [c for c in ['water_area_km2','rain_chirps_mm','ch4_xch4_ppb_roi'] if c in df]
    if not fields:
        return False
    fig, axes = plt.subplots(len(fields),1,figsize=(10,len(fields)*2.8),sharex=True)
    for ax,col in zip(np.atleast_1d(axes),fields):
        t=df[['date',col]].copy(); t[col]=pd.to_numeric(t[col],errors='coerce')
        med=t.groupby(t['date'].dt.month)[col].median()
        ax.plot(med.index,med.values,'o-')
        ax.set_ylabel(VARIABLES[col][1]); ax.set_title(VARIABLES[col][0],loc='left',fontsize=10)
        _theme(ax)
    axes[-1].set_xticks(range(1,13));axes[-1].set_xlabel('Calendar month')
    fig.suptitle('Within-calendar-month medians | Descriptive, not causal',fontweight='bold')
    fig.tight_layout();_figure(fig,outdir,'03_monthly_seasonality')
    return True


def _make_correlations(df, outdir):
    fields=[c for c in ['water_area_km2','rain_chirps_mm','temp2m_era5_c',
                        'ch4_roi_minus_ring_ppb'] if c in df]
    if len(fields)<2:
        return pd.DataFrame()
    num=df[fields].apply(pd.to_numeric,errors='coerce')
    if len(num.dropna(how='all'))<6: return pd.DataFrame()
    corr=num.corr(min_periods=6)
    fig,ax=plt.subplots(figsize=(7,6))
    im=ax.imshow(corr.to_numpy(),vmin=-1,vmax=1,cmap='coolwarm')
    ax.set_xticks(range(len(fields)),[VARIABLES[x][0] for x in fields],rotation=45,ha='right',fontsize=8)
    ax.set_yticks(range(len(fields)),[VARIABLES[x][0] for x in fields],fontsize=8)
    for i in range(len(fields)):
        for j in range(len(fields)):
            if np.isfinite(corr.iloc[i,j]):
                ax.text(j,i,f'{corr.iloc[i,j]:.2f}',ha='center',va='center',fontsize=9)
    ax.set_title('Pairwise correlations, monthly observations | Descriptive only')
    fig.colorbar(im,ax=ax,shrink=.8,label='Pearson r')
    fig.tight_layout();_figure(fig,outdir,'04_exploratory_correlations')
    return corr


def _render_raster(path, outdir, boundary_path=None):
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.plot import plotting_extent
    import geopandas as gpd
    from matplotlib.colors import ListedColormap, BoundaryNorm

    with rasterio.open(path) as src:
        if src.crs is None:
            raise ValueError(f'Missing CRS in raster {path}')
        factor = max(1,int(np.ceil(max(src.width,src.height)/1500)))
        height=max(1,int(np.ceil(src.height/factor)))
        width=max(1,int(np.ceil(src.width/factor)))
        data=src.read(1,out_shape=(height,width),masked=True,
                      resampling=Resampling.nearest if ('SAR_water' in path.name or 'DynamicWorld' in path.name) else Resampling.average)
        vals=np.ma.masked_invalid(data.astype('float64'))
        if not np.ma.count(vals):
            return {'raster':path.name,'rendered':False,'reason':'no_unmasked_pixels',
                    'crs':str(src.crs),'pixel_size_x':abs(src.res[0]),'pixel_size_y':abs(src.res[1])}
        extent=plotting_extent(src)
        fig,ax=plt.subplots(figsize=(9,7.6))
        file_lower=path.name.lower()
        if 'sar_water' in file_lower:
            cmap=ListedColormap(['#efeadb','#2876af']); norm=BoundaryNorm([-.5,.5,1.5],2)
            im=ax.imshow(vals,extent=extent,origin='upper',cmap=cmap,norm=norm,interpolation='nearest')
            cb=fig.colorbar(im,ax=ax,fraction=.034,pad=.02,ticks=[0,1]);cb.ax.set_yticklabels(['Non-water screen','Low-VV water screen'])
        elif 'dynamicworld' in file_lower or 'dw_class' in file_lower:
            cmap=ListedColormap(['#3985c4','#479155','#67ba65','#8c78af','#c2a666','#dbbc4c','#bc4b42','#8d8c8a','#c8a5d1']); norm=BoundaryNorm(np.arange(-.5,9.5),9)
            im=ax.imshow(vals,extent=extent,origin='upper',cmap=cmap,norm=norm,interpolation='nearest')
            cb=fig.colorbar(im,ax=ax,fraction=.034,pad=.02,ticks=list(range(9)))
            cb.ax.set_yticklabels(['Water','Trees','Grass','Flooded veg.','Crops','Shrub/scrub','Built','Bare','Snow/ice'])
        else:
            cmap=('BrBG' if 'mndwi' in file_lower or 'ndvi' in file_lower else
                  'Blues' if 'rain' in file_lower else 'inferno' if 'ch4' in file_lower else 'viridis')
            im=ax.imshow(vals,extent=extent,origin='upper',cmap=cmap,interpolation='nearest')
            label=('Atmospheric XCH₄ (ppb)' if 'ch4' in file_lower else
                   'Accumulated precipitation (mm)' if 'rain' in file_lower else
                   'Air temperature (°C)' if 'era5' in file_lower else 'Dataset value (native units)')
            fig.colorbar(im,ax=ax,fraction=.034,pad=.02,label=label)
        if boundary_path and Path(boundary_path).exists():
            try:
                boundary=gpd.read_file(boundary_path).to_crs(src.crs)
                boundary.boundary.plot(ax=ax,edgecolor='#e46b23',linewidth=1.3)
            except Exception as e:
                print('Boundary overlay skipped for',path.name,':',e)
        ax.set_xlabel(f'Easting / longitude ({src.crs})')
        ax.set_ylabel(f'Northing / latitude ({src.crs})')
        ax.set_title(path.stem.replace('_',' ')+'\nHakaluki Haor | Preliminary satellite-derived layer',fontweight='bold',fontsize=12)
        ax.text(.01,.01,'Preliminary · Not field-validated · Resolution reflects original satellite product',
                transform=ax.transAxes,fontsize=7.5,bbox={'facecolor':'white','alpha':.85,'edgecolor':'none'})
        fig.tight_layout()
        stem='map_'+path.stem.replace(' ','_')
        outdir.mkdir(parents=True,exist_ok=True)
        fig.savefig(outdir/(stem+'.png'),dpi=220,bbox_inches='tight',facecolor='white')
        plt.close(fig)
        return {'raster':path.name,'rendered':True,'map_file':str(Path('figures')/(stem+'.png')),
                'crs':str(src.crs),'width_pixels':src.width,'height_pixels':src.height,
                'pixel_size_x':abs(src.res[0]),'pixel_size_y':abs(src.res[1]),
                'band_count':src.count,'nodata':src.nodata,
                'preview_min':float(vals.min()),'preview_max':float(vals.max()),
                'note':'statistics from downsampled preview, not independent retrieval count'}


def _copy_if_small(source, dest, size_limit=90*1024*1024):
    if source.stat().st_size > size_limit:
        return False
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,dest)
    return True


def build_release(root, include_rasters=False):
    """Create results/github_release directory. Return build manifest dict.

    include_rasters=True copies downloaded GeoTIFFs smaller than size_limit into
    archive_rasters/, but default False is safest for GitHub's file limits.
    """
    root=Path(root).resolve()
    settings=root/'config'/'settings.json'
    if not settings.exists(): raise FileNotFoundError(f'Missing project config at {settings}')
    release=root/'results'/'github_release'
    sentinel=release/'.GENERATED_BY_HAKALUKI_EXPORT'
    if release.exists() and any(release.iterdir()) and not sentinel.exists():
        raise RuntimeError('Refusing to overwrite a non-generated release directory.')
    if release.exists():
        shutil.rmtree(release)
    (release/'figures').mkdir(parents=True)
    (release/'data').mkdir(parents=True)
    sentinel.write_text('Generated; can be overwritten on next research release rebuild.\n',encoding='utf-8')
    df,sources=_records(root)
    records=[]
    for source in sorted((root/'data'/'processed').glob('*.csv')) + sorted((root/'results'/'tables').glob('*')):
        if source.is_file() and source.suffix.lower() in ('.csv','.json'):
            target=release/'data'/source.name
            if target.exists() and _hash_file(source)!=_hash_file(target):
                raise RuntimeError(f'Data collision for {source.name}')
            copied=_copy_if_small(source,target)
            records.append({'path':str(source.relative_to(root)),'copied':copied})
    # Preserve actual analyses in one cleaned analysis table (not synthetic or gap-filled).
    if len(df):
        df.to_csv(release/'data'/'monthly_observations_combined.csv',index=False)
        _make_timeseries(df,release/'figures')
        completeness=_make_completeness(df,release/'figures')
        if len(completeness): completeness.to_csv(release/'data'/'data_completeness.csv',index=False)
        _make_month_climatology(df,release/'figures')
        corr=_make_correlations(df,release/'figures')
        if not corr.empty: corr.to_csv(release/'data'/'pairwise_monthly_correlations.csv')
    # Independent raster export outputs must be downloaded from GEE/Drive first.
    rasters=sorted((root/'results'/'rasters').rglob('*.tif')) + sorted((root/'results'/'rasters').rglob('*.tiff'))
    boundary=root/'data'/'boundary'/'hakaluki_analysis_candidate.geojson'
    if not boundary.exists():
        boundary=root/'Study area'/'Hakaluki_Haor.shp'
    layer_catalog=[]
    for raster in rasters:
        try:
            stats=_render_raster(raster,release/'figures',boundary)
            stats['source_local_path']=str(raster.relative_to(root))
            layer_catalog.append(stats)
            if include_rasters:
                stats['included_raw_geotiff']=_copy_if_small(raster,release/'archive_rasters'/raster.name)
        except Exception as e:
            layer_catalog.append({'raster':raster.name,'rendered':False,'reason':f'{type(e).__name__}: {e}'})
    with (release/'data'/'raster_catalog.csv').open('w',encoding='utf-8',newline='') as f:
        keys=sorted(set(k for row in layer_catalog for k in row)) if layer_catalog else ['raster','rendered','reason']
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(layer_catalog)
    # Reference site map is a boundary-QA product, not a flood result.
    for candidate in sorted((root/'results'/'maps').glob('*.png')):
        _copy_if_small(candidate,release/'figures'/('boundary_QA_'+candidate.name))
    field=root/'results'/'calibration'/'field_flux_template.csv'
    if field.exists(): _copy_if_small(field,release/'data'/'field_flux_template_NOT_OBSERVATIONS.csv')
    fig_paths=sorted((release/'figures').glob('*.png'))
    pngs=[f'![{p.stem}](figures/{p.name})' for p in fig_paths]
    observed_years=sorted(int(y) for y in df['date'].dt.year.dropna().unique()) if len(df) else []
    status=('Preliminary satellite-derived results; field methane flux calibration pending'
            if len(df) else 'Code and release framework only; no completed monthly observations')
    readme=f'''# {PROJECT_NAME}\n\n**Status:** {status}.\n\n**Study area:** Hakaluki Haor, northeastern Bangladesh.\n\n**Data coverage actually processed:** {', '.join(map(str,observed_years)) if observed_years else 'None yet'}.\n\n**Monthly records:** {len(df)}. **Downloaded georeferenced layers:** {len(rasters)}. **Image previews:** {len(fig_paths)}.\n\n> {DISCLAIMER}\n\n## Maps and analysis graphics\n\n{chr(10).join(pngs) if pngs else 'Figures will appear here after running the notebooks and downloading completed Earth Engine exports.'}\n\n## Outputs\n\n- `data/monthly_observations_combined.csv` — actual monthly GEE-derived observations when present.\n- `data/data_completeness.csv` — per-variable missingness when records exist.\n- `data/raster_catalog.csv` — geospatial files, coordinate reference systems, scales and preview status.\n- `figures/` — portfolio-quality PNG illustrations (plots also supplied as SVG).\n- `metadata.json` — release and acquisition metadata.\n- `assets_manifest.json` — SHA-256 inventory of published release files.\n\n## Interpretation and reproducibility\n\nWater masks use preliminary Sentinel-1 low-backscatter screening; no independent flood-map accuracy assessment yet.\nTROPOMI XCH₄ is an atmospheric column concentration, not wetland flux. The reference ring is not an atmospheric inversion or a wind-matched background.\nFor reproducible processing, refer to the full project notebooks and GEE scripts. Raw satellite images belong to their respective providers, and downloaded GeoTIFFs are generally not committed to this gallery.\n\n**Primary data:** Sentinel-1/2, Google Dynamic World, CHIRPS, ERA5-Land, Sentinel-5P (see provider citations and metadata in the project).\n\n**Planned future validation:** GIS boundary provenance confirmation; flood-class accuracy assessment; field methane flux sampling and model calibration.\n'''
    (release/'README.md').write_text(readme,encoding='utf-8')
    (release/'PORTFOLIO_CAPTIONS.md').write_text(
        '# Suggested accurate portfolio description\n\n'
        'Developed a reproducible Google Earth Engine and Python pipeline for satellite-based '
        'assessment of Hakaluki Haor wetland dynamics, integrating Sentinel-1, Sentinel-2, '
        'CHIRPS, ERA5-Land, and Sentinel-5P methane columns. Produced georeferenced previews, '
        'monthly quality-control tables, and exploratory models, with future field methane flux '
        'calibration planned. These outputs do not establish methane emissions from individual wetlands.\n\n'
        '**Do not say:** Field-validated methane emission maps, verified causal flood impacts, or '
        '10 m methane concentrations.\n',encoding='utf-8')
    metadata={
        'title':PROJECT_NAME, 'created_utc':datetime.now(timezone.utc).isoformat(),
        'project':json.loads(settings.read_text(encoding='utf-8')).get('earth_engine_cloud_project'),
        'boundary_source':'User-supplied shapefile, unverified unless independently checked',
        'processed_years':observed_years, 'n_monthly_records':int(len(df)),
        'n_geotiffs_found':len(rasters),'n_png_figures':len(fig_paths),
        'data_inclusion':records,'disclaimer':DISCLAIMER,
        'data_availability':'Only outputs present on disk are exported; missing files are never fabricated.',
        'raster_inclusion':'Rasters are catalogued; originals remain in results/rasters unless explicitly opted in.',
    }
    (release/'metadata.json').write_text(json.dumps(metadata,indent=2,ensure_ascii=False),encoding='utf-8')
    # Render a self-contained static local/GitHub Pages HTML gallery.
    cards='\n'.join(f'<figure><img src="figures/{p.name}" alt="{p.stem}"><figcaption>{p.stem.replace("_"," ")}</figcaption></figure>' for p in fig_paths)
    html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{PROJECT_NAME}</title><style>body{{font-family:system-ui,Arial,sans-serif;max-width:1100px;margin:40px auto;padding:0 24px;color:#18302a;background:#f7faf9;line-height:1.55}}h1{{line-height:1.15}}.lead{{max-width:860px;color:#516760}}.warning{{border-left:4px solid #b87f3b;padding:13px 18px;background:#fffaf0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:20px;margin-top:24px}}figure{{background:white;border:1px solid #dbe6e1;border-radius:12px;margin:0;overflow:hidden;box-shadow:0 2px 10px #d9e2de44}}img{{width:100%;height:auto;display:block}}figcaption{{font-size:13px;padding:10px 15px;color:#3f5950}}a{{color:#126c60}}</style></head><body><p>EARTH OBSERVATION · HYDROCLIMATE · REPRODUCIBLE GIS</p><h1>{PROJECT_NAME}</h1><p class="lead">Hakaluki Haor | Actual processed years: {', '.join(map(str,observed_years)) if observed_years else 'none yet'} | {len(df)} monthly records | {len(fig_paths)} published previews.</p><p class="warning">{DISCLAIMER}</p><h2>Maps & figures</h2><main class="grid">{cards if cards else '<p>Run the notebooks and the release exporter to populate this gallery with actual results.</p>'}</main><p><a href="README.md">Research notes</a> · <a href="data/raster_catalog.csv">Raster catalog</a> · <a href="metadata.json">Metadata</a></p></body></html>'''
    (release/'index.html').write_text(html,encoding='utf-8')
    file_manifest=[]
    for file in sorted(release.rglob('*')):
        if file.is_file() and file.name!='assets_manifest.json':
            file_manifest.append({'path':str(file.relative_to(release)).replace('\\','/'),
                                  'bytes':file.stat().st_size,'sha256':_hash_file(file)})
    (release/'assets_manifest.json').write_text(json.dumps(file_manifest,indent=2),encoding='utf-8')
    return {'release_dir':str(release),'n_months':len(df),'years':observed_years,
            'n_tifs':len(rasters),'n_figures_png':len(fig_paths),'n_release_files':len(file_manifest)}
