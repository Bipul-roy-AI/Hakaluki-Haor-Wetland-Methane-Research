"""Build a source-linked academic Hakaluki Haor project showcase.

Run locally after satellite exports. Never invent observations. Does not
connect to Google Earth Engine and never publish secrets. Generates docs/ for
GitHub Pages, and a reviewed README preview. Publishing the root README is opt-in.
"""
from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import numpy as np
import pandas as pd

ROOT_MARKER = Path('config/settings.json')
DATA_FILE = 'hakaluki_monthly_2019_2025.csv'

FIGURE_CANDIDATES = [
    ('01_monthly_timeseries.png', 'Satellite and hydroclimate time series', 'figures'),
    ('03_monthly_seasonality.png', 'Monthly seasonal climatology', 'figures'),
    ('02_data_completeness.png', 'Data availability', 'figures'),
    ('04_exploratory_correlations.png', 'Exploratory correlations', 'figures'),
    ('tropomi_l3_coverage.png', 'TROPOMI Level-3 gridded coverage', 'figures'),
    ('hakaluki_2022_methane_coverage.png', 'Methane observation coverage in 2022', 'figures'),
    ('hakaluki_2022_water_area.png', 'Preliminary water-area time series', 'figures'),
    ('hakaluki_2022_rainfall.png', 'Monthly rainfall in 2022', 'figures'),
]
CSV_CANDIDATES = [
    ('hakaluki_monthly_2019_2025.csv', 'Monthly 2019–2025 environmental dataset'),
    ('complete_data_quality_2019_2025.csv', 'Data completeness and missingness'),
    ('hakaluki_2019_2025_data_quality.csv', 'Detailed variable completeness'),
    ('monthly_lag_screen.csv', 'Exploratory month-lag correlations'),
    ('exploratory_year_holdout_models.csv', 'Preliminary model comparison'),
    ('seasonally_adjusted_anomalies.csv', 'Monthly seasonal anomaly table'),
    ('data_completeness.csv', 'Data completeness summary'),
]


def _sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _csv_path(root, basename):
    candidates = [
        root / 'data' / 'processed' / basename,
        root / 'results' / 'tables' / basename,
        root / 'results' / 'github_release' / 'data' / basename,
    ]
    return next((p for p in candidates if p.is_file()), None)


def _monthly_data(root):
    consolidated = _csv_path(root, DATA_FILE)
    if consolidated:
        df = pd.read_csv(consolidated)
    else:
        paths = sorted((root / 'data' / 'processed').glob('monthly_20??-??.csv'))
        if not paths:
            return pd.DataFrame(), None
        df = pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
    if 'period' not in df:
        raise ValueError('Monthly dataset lacks the period column.')
    if df['period'].duplicated().any():
        raise ValueError('Duplicate months. Refusing to publish inconsistent results.')
    fps = df['cache_fingerprint'].dropna().astype(str).unique() if 'cache_fingerprint' in df else []
    if len(fps) > 1:
        raise ValueError('Different processing fingerprints in monthly data; review before release.')
    df = df.sort_values('period').reset_index(drop=True)
    return df, consolidated


def _raster_inventory(root):
    paths = sorted((root / 'results' / 'rasters').glob('HAKALUKI_*.tif'))
    rows = []
    try:
        import rasterio
    except ImportError:
        rasterio = None
    for path in paths:
        item = dict(filename=path.name, bytes=path.stat().st_size, sha256=_sha256(path),
                    readable=False, crs='', valid_pixels='', width='', height='')
        if rasterio:
            try:
                with rasterio.open(path) as src:
                    item.update(readable=True, crs=str(src.crs), width=src.width, height=src.height,
                                valid_pixels=int(np.count_nonzero(src.dataset_mask())))
            except Exception as exc:
                item['error'] = str(exc)
        rows.append(item)
    return rows


def _find_boundary(root):
    for p in [root / 'data' / 'boundary' / 'hakaluki_boundary.gpkg',
              root / 'data' / 'boundary' / 'hakaluki_boundary.geojson',
              root / 'Study area' / 'Hakaluki_Haor.shp']:
        if p.exists():
            return p
    return None


def _boundary_figure(root, output):
    """Create a context-accurate plot of the researcher-provided boundary."""
    boundary_path = _find_boundary(root)
    if not boundary_path:
        return None
    try:
        import geopandas as gpd
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        shape = gpd.read_file(boundary_path).to_crs('EPSG:4326')
        if shape.empty or not shape.geometry.is_valid.all():
            return None
        measured = shape.to_crs('EPSG:32646').area.sum()/1e6
        fig, ax = plt.subplots(figsize=(9.5,7.5))
        shape.plot(ax=ax, facecolor='#c9e5de',edgecolor='#175f72',linewidth=1.6)
        xmin,ymin,xmax,ymax=shape.total_bounds
        padx=max(.006,(xmax-xmin)*.1);pady=max(.006,(ymax-ymin)*.1)
        ax.set_xlim(xmin-padx,xmax+padx);ax.set_ylim(ymin-pady,ymax+pady)
        ax.set_aspect(1/math.cos(math.radians((ymin+ymax)/2)))
        ax.set_xlabel('Longitude (°E)');ax.set_ylabel('Latitude (°N)')
        ax.grid(alpha=.15)
        ax.set_title('Hakaluki Haor | Study-area polygon',weight='bold',fontsize=15)
        ax.text(.02,.02,f'Geometry-derived area: {measured:.2f} km²\nBoundary source: researcher-supplied; provenance pending',
                transform=ax.transAxes,va='bottom',ha='left',fontsize=9,
                bbox={'boxstyle':'round,pad=.5','facecolor':'white','alpha':.93,'edgecolor':'#cbd8dc'})
        output.parent.mkdir(parents=True,exist_ok=True)
        fig.savefig(output,dpi=220,bbox_inches='tight',facecolor='white')
        plt.close(fig)
        return output
    except Exception as e:
        print(f'Boundary figure unavailable: {e}')
        return None


def _sar_triptych(root, output):
    """Render true raster classifications with geographic axes, not fake eastings."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.colors import ListedColormap, BoundaryNorm
        from matplotlib.patches import Patch
        import rasterio
        from rasterio.plot import plotting_extent
    except ImportError:
        return None
    paths = [root / 'results' / 'rasters' / f'HAKALUKI_2022_{m}_SAR_water.tif'
             for m in ('03', '06', '10')]
    if not all(p.is_file() for p in paths):
        return None
    boundary_path = _find_boundary(root)
    bgdf = None
    if boundary_path:
        try:
            import geopandas as gpd
            bgdf = gpd.read_file(boundary_path)
        except Exception:
            bgdf = None
    vals = []
    bounds = []
    for p in paths:
        with rasterio.open(p) as src:
            if str(src.crs).upper() != 'EPSG:4326':
                # Require reprojected map rendering rather than mislabel axes.
                return None
            arr = src.read(1, masked=True)
            good = (~np.ma.getmaskarray(arr)) & np.isin(np.ma.getdata(arr), [0,1])
            vals.append(np.ma.array(np.ma.getdata(arr), mask=~good))
            bounds.append(plotting_extent(src))
    xlo=min(b[0] for b in bounds); xhi=max(b[1] for b in bounds)
    ylo=min(b[2] for b in bounds); yhi=max(b[3] for b in bounds)
    fig, axes=plt.subplots(1,3,figsize=(15.5,6.5),layout='constrained')
    cmap=ListedColormap(['#eceff0','#2077b4']); cmap.set_bad('white')
    norm=BoundaryNorm([-.5,.5,1.5],2)
    for ax, p, arr, extent, label in zip(axes,paths,vals,bounds,['March','June','October']):
        ax.imshow(arr,extent=extent,origin='upper',cmap=cmap,norm=norm,interpolation='nearest')
        if bgdf is not None:
            b=bgdf.to_crs('EPSG:4326')
            b.boundary.plot(ax=ax,edgecolor='#17272c',linewidth=.8)
        ax.set_xlim(xlo,xhi);ax.set_ylim(ylo,yhi)
        ax.set_aspect(1/math.cos(math.radians((ylo+yhi)/2)))
        ax.set_title(f'{label} 2022',fontweight='bold')
        ax.set_xlabel('Longitude (°E)')
        ax.grid(alpha=.12)
    axes[0].set_ylabel('Latitude (°N)')
    fig.suptitle('Hakaluki Haor | Preliminary Sentinel-1 water classification',fontsize=16,weight='bold')
    fig.legend(handles=[Patch(facecolor='#2077b4',label='Low-VV water screen'),
                        Patch(facecolor='#eceff0',label='Other valid pixels'),
                        Patch(facecolor='white',edgecolor='#aaaaaa',label='NoData')],
               loc='lower center',ncol=3,bbox_to_anchor=(.5,-.02))
    fig.text(.5,-.055,'Screening-grade classification, NOT validated flood extent. Monthly composites use sparse Sentinel-1 acquisitions.',
             ha='center',fontsize=9,color='#465b66')
    output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(output,dpi=220,bbox_inches='tight',facecolor='white')
    plt.close(fig)
    return output


def _copy_figure(root, assets, name):
    candidates=[root/'results'/'github_release'/'figures'/name,
                root/'results'/'figures'/name,
                root/'results'/'maps'/'portfolio'/name]
    src=next((p for p in candidates if p.is_file()),None)
    if src:
        assets.mkdir(parents=True,exist_ok=True)
        dest=assets/src.name
        if src.resolve()!=dest.resolve():
            shutil.copy2(src,dest)
        return dest
    return None


def _metric(n):
    return 'Not calculated' if n is None else str(n)


def _readme(root, df, rasters, featured, tables, dst):
    nmonths=len(df) if not df.empty else None
    years = f"{int(df['year'].min())}–{int(df['year'].max())}" if not df.empty and 'year' in df else 'Pending export'
    methane = int(pd.to_numeric(df['ch4_xch4_ppb_roi'],errors='coerce').notna().sum()) if not df.empty and 'ch4_xch4_ppb_roi' in df else None
    nrf = len(rasters)
    done = bool(not df.empty and {'year','month','period'}.issubset(df.columns))
    top = (
        '# Hakaluki Haor | Wetland inundation and atmospheric methane dynamics\n\n'
        '**Reproducible Earth Observation research in northeastern Bangladesh**  \n'
        'Sentinel-1 SAR · Sentinel-2 · Dynamic World · TROPOMI XCH₄ · CHIRPS · ERA5-Land · GIS · Python · Google Earth Engine\n\n'
        '> **Research status: exploratory / ongoing.** Flood masks are low-VV screening products, not validated flood maps. '
        'TROPOMI measures atmospheric column methane (XCH₄), not wetland surface methane flux. '
        'Local field flux calibration and atmospheric inversion have not yet been completed.\n\n'
        '## Research at a glance\n\n'
        '| Indicator | Currently documented |\n|---|---|\n'
        f'| Study period | {years} |\n'
        f'| Monthly records | {_metric(nmonths)} |\n'
        f'| Local GeoTIFF exports inventoried | {nrf} (not necessarily committed to Git) |\n'
        f'| Months with an ROI XCH₄ value | {_metric(methane)} / {_metric(nmonths)}; retrieval-quality screening remains essential |\n'
        '| Study-area polygon | User-provided, topologically valid; source accuracy not independently confirmed |\n'
        '| Field methane flux observations | Not yet collected |\n\n'
        '## Featured results\n\n'
    )
    if not featured:
        top+='Figures will appear here after running the local portfolio builder with completed raster and figure exports.\n\n'
    else:
        ordered = ['hakaluki_boundary_audit_map.png', 'hakaluki_2022_sar_geographic_comparison.png','01_monthly_timeseries.png',
                   '03_monthly_seasonality.png','02_data_completeness.png','04_exploratory_correlations.png']
        indexed={p.name:p for p in featured}
        titles={
            'hakaluki_boundary_audit_map.png':'Study-area boundary (researcher-supplied; provenance pending)',
            'hakaluki_2022_sar_geographic_comparison.png':'Seasonal water-screen comparison: March, June and October 2022',
            '01_monthly_timeseries.png':'2019–2025 time series: water screen, hydroclimate and XCH₄',
            '03_monthly_seasonality.png':'Multi-year descriptive seasonality',
            '02_data_completeness.png':'Observational completeness and uncertainty',
            '04_exploratory_correlations.png':'Exploratory pairwise relationships (not causal)',
        }
        for k in ordered:
            if k in indexed:
                top+=f"### {titles[k]}\n\n![{titles[k]}](docs/assets/figures/{k})\n\n"
    top+=(
        '## Scientific questions\n\n'
 '1. **Inundation mapping:** How do apparent open-water extent and flooded vegetation vary seasonally and during flood disturbances, and how accurate are different sensors?\n'
 '2. **Atmospheric methane:** When quality-controlled data exist, are regional XCH₄ anomalies associated with flood extent and hydroclimate after accounting for observation gaps and atmospheric transport?\n'
 '3. **Process controls:** How do inundation, temperature and vegetation jointly explain observed variability, and what would be required to infer methane surface flux?\n\n'
 'These questions parallel the themes of the University of Leeds PhD advertisement *Magnitude and Controls of Tropical Wetland Methane Emissions Using Novel Satellite Data* (PGR-P-2558). '
 '**This project is independent and is not presented as a University of Leeds or ESA collaboration.**\n\n'
 '## Available outputs\n\n'
 f'- [Interactive/static project gallery](docs/index.html)\n'
 '- [Data catalogue](docs/data_catalog.csv) and [source/output inventory](docs/source_manifest.csv)\n'
 '- [Methods and limitations](research_docs/METHODS_AND_LIMITATIONS.md)\n'
 '- [Research questions and PhD alignment](research_docs/PHD_RELEVANCE.md)\n'
 '- [Validation strategy](research_docs/VALIDATION_PLAN.md)\n'
 '- [Current research roadmap](research_docs/ROADMAP.md)\n'
 '- [Data dictionary and provenance](research_docs/DATA_DICTIONARY_AND_PROVENANCE.md)\n\n'
 '### Curated analysis tables\n\n'
    )
    if tables:
        for p, descr in tables:
            top+=f'- [{descr}](docs/data/{quote(p.name)})\n'
    else:
        top+='Analysis tables will be linked here after local export.\n'
    top+=(
        '\n## Reproducibility\n\n'
 'Source processing notebooks are in `notebooks/`; reusable modules in `src/`; GEE scripts in `gee/`. '
 'The original unedited boundary, potentially large rasters, authenticated settings, and intermediate datasets may remain local or be published in a suitable versioned research archive. '
 'Do not assume that the complete Earth Engine archive is included in a GitHub clone. '
 'See [`research_docs/GITHUB_PUBLISHING_GUIDE.md`](research_docs/GITHUB_PUBLISHING_GUIDE.md).\n\n'
 '## What has been established versus what is next\n\n'
 '| Current status | Evidence / next experiment |\n|---|---|\n'
 f'| **Processed** | {nmonths if nmonths is not None else "Pending"} monthly environmental records; {nrf} GeoTIFF exports inventoried locally |\n'
 '| **Preliminary** | Satellite-derived low-VV water-screen patterns; exploratory XCH₄ statistics and machine-learning benchmarks |\n'
 '| **Validation needed** | Independent flood labels, vegetated inundation detection, SAR sensitivity, cloud/retrieval QA, spatial and temporal generalization |\n'
 '| **Planned** | ESA Biomass P-band coverage and pilot comparison; Sentinel-5A feasibility; meteorology-informed methane transport/inversion |\n'
 '| **Future calibration** | Local chamber/flux measurements and independent site-based methane model evaluation |\n\n'
 '## Relevant literature and mission documentation\n\n'
 '- [Saunois et al. (2025), *Global Methane Budget 2000–2020*](https://doi.org/10.5194/essd-17-1873-2025)\n'
 '- [ESA Biomass data open to researchers (26 January 2026)](https://www.esa.int/Applications/Observing_the_Earth/FutureEO/Biomass/ESA_s_Biomass_goes_live_with_data_now_open_to_all)\n'
 '- [ESA Biomass MAAP product catalogue](https://portal.maap.eo.esa.int/biomass/biomass-data-offer/)\n'
 '- [ESA Sentinel-5 mission](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-5)\n\n'
 '## Attribution and research integrity\n\n'
 'Satellite data remain subject to their providers’ terms. Maps are derived products, not official flood maps. '
 'No claim is made of field-validated methane flux, local emission inventories, or causal attribution. '
 'See the output manifest for reproducible file hashes.\n'
    )
    dst.write_text(top, encoding='utf-8')


def _make_html(assets, table_names, root_docs, summary):
    images=sorted((assets/'figures').glob('*.png'))
    items='\n'.join(f'<article><a href="assets/figures/{quote(p.name)}"><img loading="lazy" src="assets/figures/{quote(p.name)}" alt="{html.escape(p.stem)}"></a><h3>{html.escape(p.stem.replace("_"," "))}</h3><p>Research-derived, exploratory figure; consult methodology and source metadata.</p></article>' for p in images)
    datalinks='\n'.join(f'<li><a href="data/{quote(p.name)}">{html.escape(p.name)}</a></li>' for p in table_names)
    doc=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hakaluki Haor | Research gallery</title><style>
:root{{color-scheme:light;--ink:#142b37;--bg:#f4f7f8;--card:#fff;--line:#dce4e8;--sub:#49606c}}
*{{box-sizing:border-box}}body{{font-family:system-ui,-apple-system,Segoe UI,sans-serif;color:var(--ink);background:var(--bg);margin:0;line-height:1.55}}
header{{background:#142b37;color:#fff;padding:4rem 6vw 3rem}}header p{{max-width:850px;color:#d8e6ec}}main{{max-width:1250px;margin:auto;padding:2.2rem 3vw}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem;margin:1.5rem 0}}.kpis div,article,section.info{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:1rem}}.kpis strong{{display:block;font-size:1.65rem}}.kpis small{{color:var(--sub)}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:1rem}}article img{{width:100%;height:235px;object-fit:contain;background:#fff}}article h3{{font-size:1rem}}article p{{color:var(--sub);font-size:.85rem}}
a{{color:#13759b}}header a{{color:#8fe5ff}}footer{{padding:2rem;color:var(--sub);text-align:center}}
</style></head><body><header><small>INDEPENDENT · ONGOING · REPRODUCIBLE</small><h1>Hakaluki Haor<br>Wetland inundation &amp; atmospheric methane dynamics</h1><p>Satellite, GIS and hydroclimatic analyses spanning 2019–2025. Preliminary, unvalidated water classification. Atmospheric XCH₄ is not surface methane flux.</p></header>
<main><div class="kpis"><div><strong>{summary['months']}</strong><small>Monthly dataset records</small></div><div><strong>{summary['rasters']}</strong><small>Local raster products</small></div><div><strong>{summary['methane_available']}</strong><small>Months with recorded ROI XCH₄ values (not QA-approved)</small></div></div>
<h2>Featured analysis and maps</h2><div class="gallery">{items or '<p>Run the local builder after GeoTIFF/PNG export to populate images.</p>'}</div>
<section class="info"><h2>Downloads and documentation</h2><p>These are derived research data, not verified ground measurements.</p><ul>{datalinks}</ul><p><a href="data_catalog.csv">View dataset catalogue</a> · <a href="source_manifest.csv">View SHA-256 source manifest</a></p></section>
<section class="info"><h2>Next experiments</h2><p>Inundation validation, ESA Biomass P-band feasibility over Hakaluki, meteorology-aware CH₄ analysis, interpretable temperature-versus-inundation response modelling, and future field flux calibration.</p></section></main><footer>Independent exploratory research. No affiliation with or endorsement by University of Leeds, ESA, or NASA is implied.</footer></body></html>'''
    (root_docs/'index.html').write_text(doc,encoding='utf-8')


def build(root: Path, publish_root_readme: bool=False):
    root=Path(root).resolve()
    if not (root/ROOT_MARKER).is_file():
        raise FileNotFoundError(f'Missing {ROOT_MARKER}; select the top-level research project: {root}')
    doc=root/'docs'
    figs=doc/'assets'/'figures'
    tabdir=doc/'data'
    tabdir.mkdir(parents=True,exist_ok=True)
    figs.mkdir(parents=True,exist_ok=True)
    df, source = _monthly_data(root)
    rasters=_raster_inventory(root)
    outboundary=_boundary_figure(root,figs/'hakaluki_boundary_audit_map.png')
    outtrip=_sar_triptych(root,figs/'hakaluki_2022_sar_geographic_comparison.png')
    featured=[p for p in (outboundary,outtrip) if p is not None]
    for fn,_,_ in FIGURE_CANDIDATES:
        f=_copy_figure(root,figs,fn)
        if f: featured.append(f)
    # Include all existing satellite map figures in the Pages gallery, but
    # keep coarse climate fields out of the README's headline map selection.
    gallery_source=root/'results'/'github_release'/'figures'
    if gallery_source.is_dir():
        for path in sorted(gallery_source.glob('map_HAKALUKI_*.png')):
            dest=figs/path.name
            shutil.copy2(path,dest)
            featured.append(dest)
    tables=[]
    for name,descr in CSV_CANDIDATES:
        path=_csv_path(root,name)
        if path:
            dest=tabdir/name
            if path.resolve()!=dest.resolve(): shutil.copy2(path,dest)
            tables.append((dest,descr))
    # The full raw processing cache and field template are intentionally not in docs.
    catalog=[]
    for item in rasters:
        catalog.append({'name':item['filename'],'kind':'raster','status':'locally_available_not_validated',
                        'source':'GEE export','public_file':'NO: raster stays in results/rasters',
                        'sha256':item['sha256'],'notes':'See original Earth Engine task manifest'})
    for p,descr in tables:
        catalog.append({'name':p.name,'kind':'derived_table','status':'exploratory',
                        'source':'local analysis pipeline','public_file':f'docs/data/{p.name}',
                        'sha256':_sha256(p),'notes':descr})
    for p in featured:
        catalog.append({'name':p.name,'kind':'figure','status':'exploratory',
                        'source':'local analysis pipeline','public_file':f'docs/assets/figures/{p.name}',
                        'sha256':_sha256(p),'notes':'Check caption, axis, coverage and processing constraints'})
    fields=['name','kind','status','source','public_file','sha256','notes']
    with (doc/'data_catalog.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(catalog)
    inventory=[]
    for p in sorted(list(figs.glob('*.png'))+list(tabdir.glob('*.csv'))):
        inventory.append({'relative_path':p.relative_to(root).as_posix(),
                          'bytes':p.stat().st_size,'sha256':_sha256(p)})
    with (doc/'source_manifest.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['relative_path','bytes','sha256']);w.writeheader();w.writerows(inventory)
    summary={
        'months':int(len(df)) if not df.empty else 0,
        'methane_available':int(pd.to_numeric(df['ch4_xch4_ppb_roi'],errors='coerce').notna().sum()) if not df.empty and 'ch4_xch4_ppb_roi' in df else None,
        'rasters':len(rasters),
        'featured_figures':len(featured),
        'curated_csv':len(tables),
        'source_monthly_csv':str(source.relative_to(root)) if source else 'monthly checkpoints / none',
        'cache_fingerprint':df['cache_fingerprint'].dropna().iloc[0] if not df.empty and 'cache_fingerprint' in df and df['cache_fingerprint'].notna().any() else None,
        'generated_utc':datetime.now(timezone.utc).isoformat(),
        'methane_note':'XCH4 missingness counted, not vetted for native-footprint retrieval quality',
        'status':'exploratory_not_field_calibrated',
    }
    (doc/'summary.json').write_text(json.dumps(summary,indent=2,default=str),encoding='utf-8')
    _make_html(figs,[p for p,_ in tables],doc,summary)
    preview=root/'README_ACADEMIC_PREVIEW.md'
    _readme(root,df,rasters,featured,tables,preview)
    if publish_root_readme:
        readme=root/'README.md'
        if readme.exists():
            backup=root/'README.before_academic_showcase.md'
            if not backup.exists(): shutil.copy2(readme,backup)
        shutil.copy2(preview,readme)
    return dict(preview=str(preview),gallery=str(doc/'index.html'),docs=str(doc),
                **summary,published_root_readme=bool(publish_root_readme))


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--publish-root-readme',action='store_true')
    args=parser.parse_args()
    print(json.dumps(build(args.root,args.publish_root_readme),indent=2,default=str))
